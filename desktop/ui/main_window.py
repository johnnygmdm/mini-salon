"""
Mini Salon Desktop App - 메인 윈도우
고객 관리(CRUD, 검색) 및 시술 내역(1:N 조회/등록/삭제) 통합 뷰
"""

from typing import Optional, Dict, Any, List
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter, QFrame, QMessageBox, QStatusBar,
    QStackedWidget, QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer
from services.customer_service import CustomerService
from services.treatment_service import TreatmentService
from services.auth_service import AuthService
from ui.customer_dialog import CustomerDialog
from ui.treatment_dialog import TreatmentDialog
from ui.update_dialog import UpdateDialog
from services.updater_service import CURRENT_VERSION, UpdateCheckWorker


class MainWindow(QMainWindow):
    """미니 미용실 메인 윈도우"""

    def __init__(self, current_user_email: str = ""):
        super().__init__()
        self.current_user_email = current_user_email
        self.selected_customer: Optional[Dict[str, Any]] = None
        self.customers_cache: List[Dict[str, Any]] = []

        self.setWindowTitle("Mini Salon CRM - 고객 & 시술 관리")
        self.resize(1180, 750)
        self.setMinimumSize(960, 600)

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_search)

        self.update_worker: Optional[UpdateCheckWorker] = None

        self._init_ui()
        self.refresh_customers()

        # 앱 실행 1.5초 후 백그라운드 자동 업데이트 확인
        QTimer.singleShot(1500, self._check_update_silently)

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(12)

        # 1. 상단 글로벌 네비게이션/헤더 바
        header_bar = self._create_header_bar()
        main_layout.addWidget(header_bar)

        # 2. 메인 스플리터 (좌: 고객 목록 / 우: 시술 내역 상세)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(4)

        # 좌측 패널 (고객 관리)
        left_panel = self._create_customer_panel()
        self.splitter.addWidget(left_panel)

        # 우측 패널 (시술 내역 및 고객 상세)
        right_panel = self._create_detail_panel()
        self.splitter.addWidget(right_panel)

        # 스플리터 비율 (좌: 48%, 우: 52%)
        self.splitter.setSizes([540, 600])
        main_layout.addWidget(self.splitter, 1)

        # 3. 하단 상태바
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("준비 완료")

    def _create_header_bar(self) -> QWidget:
        header = QFrame()
        header.setObjectName("cardFrame")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 10, 16, 10)

        # 로고 & 타이틀
        title_box = QVBoxLayout()
        title_label = QLabel("✂️ Mini Salon CRM")
        title_label.setObjectName("titleLabel")
        sub_title = QLabel("클라우드 실시간 동기화 (Supabase)")
        sub_title.setObjectName("subtitleLabel")
        title_box.addWidget(title_label)
        title_box.addWidget(sub_title)
        layout.addLayout(title_box)

        layout.addStretch()

        # 우측 사용자 정보 & 제어 버튼
        user_info = QLabel(f"👤 {self.current_user_email}")
        user_info.setStyleSheet("font-weight: 600; color: #475569; padding-right: 8px;")
        layout.addWidget(user_info)

        # 버전 정보 및 업데이트 확인 버튼
        self.ver_btn = QPushButton(f"v{CURRENT_VERSION}")
        self.ver_btn.setToolTip("클릭하여 최신 버전 업데이트 확인")
        self.ver_btn.setStyleSheet("font-weight: 600; color: #4f46e5; background-color: #eef2ff; border: 1px solid #c7d2fe;")
        self.ver_btn.clicked.connect(self._check_update_manually)
        layout.addWidget(self.ver_btn)

        refresh_btn = QPushButton("🔄 새로고침")
        refresh_btn.setToolTip("고객 및 시술 내역 새로고침")
        refresh_btn.clicked.connect(self.refresh_customers)
        layout.addWidget(refresh_btn)

        logout_btn = QPushButton("로그아웃")
        logout_btn.setObjectName("dangerBtn")
        logout_btn.clicked.connect(self._handle_logout)
        layout.addWidget(logout_btn)

        return header

    # =========================================================================
    # 좌측: 고객 관리 영역
    # =========================================================================
    def _create_customer_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("cardFrame")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # 상단 헤더 & 고객 등록 버튼
        top_bar = QHBoxLayout()
        self.customer_count_label = QLabel("고객 목록")
        self.customer_count_label.setObjectName("cardTitle")
        top_bar.addWidget(self.customer_count_label)

        top_bar.addStretch()

        add_cust_btn = QPushButton("＋ 신규 고객")
        add_cust_btn.setObjectName("primaryBtn")
        add_cust_btn.clicked.connect(self._open_add_customer_dialog)
        top_bar.addWidget(add_cust_btn)
        layout.addLayout(top_bar)

        # 실시간 검색창
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 고객명 또는 전화번호 검색...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input)

        # 고객 목록 테이블
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(["고객명", "연락처", "메모", "등록일"])
        self.customer_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.customer_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.customer_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.customer_table.verticalHeader().setVisible(False)
        self.customer_table.horizontalHeader().setStretchLastSection(False)
        self.customer_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.customer_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.customer_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.customer_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.customer_table.itemSelectionChanged.connect(self._on_customer_row_selected)
        self.customer_table.doubleClicked.connect(self._open_edit_customer_dialog)
        layout.addWidget(self.customer_table, 1)

        # 하단 고객 수정/삭제 버튼
        bottom_actions = QHBoxLayout()
        self.edit_cust_btn = QPushButton("✏️ 정보 수정")
        self.edit_cust_btn.setEnabled(False)
        self.edit_cust_btn.clicked.connect(self._open_edit_customer_dialog)
        bottom_actions.addWidget(self.edit_cust_btn)

        self.del_cust_btn = QPushButton("🗑️ 고객 삭제")
        self.del_cust_btn.setObjectName("dangerBtn")
        self.del_cust_btn.setEnabled(False)
        self.del_cust_btn.clicked.connect(self._delete_selected_customer)
        bottom_actions.addWidget(self.del_cust_btn)

        layout.addLayout(bottom_actions)
        return panel

    # =========================================================================
    # 우측: 시술 내역 및 고객 상세 영역 (1:N)
    # =========================================================================
    def _create_detail_panel(self) -> QWidget:
        self.detail_stack = QStackedWidget()

        # 1. 미선택 시 플레이스홀더 화면
        empty_widget = QFrame()
        empty_widget.setObjectName("cardFrame")
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)

        empty_icon = QLabel("💇‍♂️")
        empty_icon.setStyleSheet("font-size: 48px;")
        empty_icon.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_icon)

        empty_label = QLabel("좌측 목록에서 고객을 선택해주세요")
        empty_label.setObjectName("cardTitle")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_label)

        empty_sub = QLabel("고객의 상세 프로필과 1:N 시술 내역을 확인하고 등록할 수 있습니다.")
        empty_sub.setObjectName("subtitleLabel")
        empty_sub.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_sub)

        self.detail_stack.addWidget(empty_widget)

        # 2. 고객 선택 시 활성화되는 메인 상세 화면
        detail_widget = QFrame()
        detail_widget.setObjectName("cardFrame")
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(14, 14, 14, 14)
        detail_layout.setSpacing(12)

        # 고객 요약 카드
        summary_card = QFrame()
        summary_card.setObjectName("detailHeaderFrame")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(12, 12, 12, 12)
        summary_layout.setSpacing(8)

        # 고객 이름 및 연락처
        info_row = QHBoxLayout()
        self.detail_name_label = QLabel("고객명")
        self.detail_name_label.setObjectName("cardTitle")
        info_row.addWidget(self.detail_name_label)

        self.detail_phone_label = QLabel("연락처")
        self.detail_phone_label.setStyleSheet("color: #475569; font-weight: 500; font-size: 13px;")
        info_row.addWidget(self.detail_phone_label)
        info_row.addStretch()
        summary_layout.addLayout(info_row)

        # 고객 메모
        self.detail_memo_label = QLabel("특이사항 없음")
        self.detail_memo_label.setStyleSheet("color: #64748b; font-size: 12px; line-height: 1.4;")
        self.detail_memo_label.setWordWrap(True)
        summary_layout.addWidget(self.detail_memo_label)

        # 통계 지표 박스 (총 방문, 누적 매출, 최근 시술)
        stats_box = QHBoxLayout()
        stats_box.setSpacing(16)

        # 총 방문 횟수
        cnt_box = QVBoxLayout()
        self.stat_count_val = QLabel("0회")
        self.stat_count_val.setObjectName("statValue")
        cnt_lbl = QLabel("총 방문 횟수")
        cnt_lbl.setObjectName("statLabel")
        cnt_box.addWidget(self.stat_count_val)
        cnt_box.addWidget(cnt_lbl)
        stats_box.addLayout(cnt_box)

        # 누적 이용 금액
        sum_box = QVBoxLayout()
        self.stat_total_val = QLabel("0원")
        self.stat_total_val.setObjectName("statValue")
        sum_lbl = QLabel("누적 시술 금액")
        sum_lbl.setObjectName("statLabel")
        sum_box.addWidget(self.stat_total_val)
        sum_box.addWidget(sum_lbl)
        stats_box.addLayout(sum_box)

        # 최근 방문일
        date_box = QVBoxLayout()
        self.stat_date_val = QLabel("-")
        self.stat_date_val.setObjectName("statValue")
        self.stat_date_val.setStyleSheet("font-size: 18px;")
        date_lbl = QLabel("최근 시술 일자")
        date_lbl.setObjectName("statLabel")
        date_box.addWidget(self.stat_date_val)
        date_box.addWidget(date_lbl)
        stats_box.addLayout(date_box)

        stats_box.addStretch()
        summary_layout.addLayout(stats_box)
        detail_layout.addWidget(summary_card)

        # 시술 내역 타이틀 & 등록 버튼 바
        treatment_bar = QHBoxLayout()
        self.treatment_title = QLabel("시술 내역 (0건)")
        self.treatment_title.setObjectName("cardTitle")
        treatment_bar.addWidget(self.treatment_title)

        treatment_bar.addStretch()

        add_treatment_btn = QPushButton("＋ 시술 등록")
        add_treatment_btn.setObjectName("successBtn")
        add_treatment_btn.clicked.connect(self._open_add_treatment_dialog)
        treatment_bar.addWidget(add_treatment_btn)
        detail_layout.addLayout(treatment_bar)

        # 시술 내역 테이블
        self.treatment_table = QTableWidget()
        self.treatment_table.setColumnCount(4)
        self.treatment_table.setHorizontalHeaderLabels(["시술일자", "시술 항목", "금액", "관리"])
        self.treatment_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.treatment_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.treatment_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treatment_table.verticalHeader().setVisible(False)
        self.treatment_table.horizontalHeader().setStretchLastSection(False)
        self.treatment_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.treatment_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.treatment_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.treatment_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        detail_layout.addWidget(self.treatment_table, 1)

        self.detail_stack.addWidget(detail_widget)
        return self.detail_stack

    # =========================================================================
    # 비즈니스 로직 및 이벤트 핸들러
    # =========================================================================
    def refresh_customers(self):
        """고객 목록 다시 로드"""
        self.status_bar.showMessage("고객 데이터를 불러오는 중...")
        try:
            query = self.search_input.text().strip() if hasattr(self, "search_input") else ""
            customers = CustomerService.get_customers(query)
            self.customers_cache = customers
            self._render_customers_table(customers)
            self.status_bar.showMessage(f"총 {len(customers)}명의 고객 목록을 불러왔습니다.")

            # 현재 선택된 고객이 여전히 목록에 있는지 확인
            if self.selected_customer:
                matched = next((c for c in customers if c["id"] == self.selected_customer["id"]), None)
                if matched:
                    self.selected_customer = matched
                    self._load_customer_treatments(matched)
                else:
                    self.selected_customer = None
                    self.detail_stack.setCurrentIndex(0)
                    self.edit_cust_btn.setEnabled(False)
                    self.del_cust_btn.setEnabled(False)
        except Exception as e:
            self.status_bar.showMessage("데이터 로드 실패")
            QMessageBox.critical(self, "오류", f"고객 목록을 불러오지 못했습니다:\n{str(e)}")

    def _render_customers_table(self, customers: List[Dict[str, Any]]):
        self.customer_count_label.setText(f"고객 목록 ({len(customers)}명)")
        self.customer_table.setRowCount(len(customers))

        selected_row = -1
        for row, cust in enumerate(customers):
            # 고객명
            name_item = QTableWidgetItem(cust.get("name", ""))
            name_item.setData(Qt.UserRole, cust)
            self.customer_table.setItem(row, 0, name_item)

            # 연락처
            phone_item = QTableWidgetItem(cust.get("phone", ""))
            self.customer_table.setItem(row, 1, phone_item)

            # 메모
            memo_str = (cust.get("memo") or "").replace("\n", " ")
            memo_item = QTableWidgetItem(memo_str)
            self.customer_table.setItem(row, 2, memo_item)

            # 등록일자 (YYYY-MM-DD)
            created_at = cust.get("created_at", "")
            date_str = created_at[:10] if created_at else "-"
            date_item = QTableWidgetItem(date_str)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.customer_table.setItem(row, 3, date_item)

            if self.selected_customer and cust.get("id") == self.selected_customer.get("id"):
                selected_row = row

        if selected_row >= 0:
            self.customer_table.selectRow(selected_row)

    def _on_search_changed(self, text: str):
        # 300ms 디바운스로 검색 성능 최적화
        self._search_timer.start(300)

    def _do_search(self):
        self.refresh_customers()

    def _on_customer_row_selected(self):
        selected_rows = self.customer_table.selectionModel().selectedRows()
        if not selected_rows:
            self.selected_customer = None
            self.detail_stack.setCurrentIndex(0)
            self.edit_cust_btn.setEnabled(False)
            self.del_cust_btn.setEnabled(False)
            return

        row = selected_rows[0].row()
        item = self.customer_table.item(row, 0)
        if item:
            cust = item.data(Qt.UserRole)
            self.selected_customer = cust
            self.edit_cust_btn.setEnabled(True)
            self.del_cust_btn.setEnabled(True)
            self._load_customer_treatments(cust)

    def _load_customer_treatments(self, cust: Dict[str, Any]):
        """선택된 고객의 시술 내역 및 통계 로드"""
        self.detail_stack.setCurrentIndex(1)

        # 프로필 카드 반영
        self.detail_name_label.setText(f"👤 {cust.get('name', '')}")
        self.detail_phone_label.setText(f"📞 {cust.get('phone', '')}")
        memo = cust.get("memo")
        self.detail_memo_label.setText(f"📝 {memo}" if memo else "특이사항 없음")

        # 시술 데이터 및 통계 조회
        try:
            summary = TreatmentService.get_customer_treatment_summary(cust["id"])
            treatments = TreatmentService.get_treatments_by_customer(cust["id"])

            self.stat_count_val.setText(f"{summary['count']}회")
            self.stat_total_val.setText(f"{summary['total_amount']:,}원")
            self.stat_date_val.setText(summary["latest_date"])

            self._render_treatments_table(treatments)
        except Exception as e:
            QMessageBox.critical(self, "오류", f"시술 내역을 불러오지 못했습니다:\n{str(e)}")

    def _render_treatments_table(self, treatments: List[Dict[str, Any]]):
        self.treatment_title.setText(f"시술 내역 ({len(treatments)}건)")
        self.treatment_table.setRowCount(len(treatments))

        for row, t in enumerate(treatments):
            # 시술일자
            date_item = QTableWidgetItem(t.get("treated_at", "-"))
            date_item.setTextAlignment(Qt.AlignCenter)
            self.treatment_table.setItem(row, 0, date_item)

            # 시술 항목명
            name_item = QTableWidgetItem(t.get("service_name", ""))
            self.treatment_table.setItem(row, 1, name_item)

            # 금액
            price = t.get("price", 0)
            price_item = QTableWidgetItem(f"{price:,} 원")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.treatment_table.setItem(row, 2, price_item)

            # 삭제 버튼 셀
            del_btn = QPushButton("삭제")
            del_btn.setObjectName("dangerBtn")
            del_btn.setFixedHeight(26)
            treatment_id = t["id"]
            del_btn.clicked.connect(lambda _, tid=treatment_id: self._delete_treatment(tid))
            self.treatment_table.setCellWidget(row, 3, del_btn)

    # -------------------------------------------------------------------------
    # 고객 추가 / 수정 / 삭제
    # -------------------------------------------------------------------------
    def _open_add_customer_dialog(self):
        dialog = CustomerDialog(self)
        if dialog.exec():
            self.status_bar.showMessage("새 고객이 등록되었습니다.", 4000)
            self.refresh_customers()

    def _open_edit_customer_dialog(self):
        if not self.selected_customer:
            return
        dialog = CustomerDialog(self, customer_data=self.selected_customer)
        if dialog.exec():
            self.status_bar.showMessage("고객 정보가 수정되었습니다.", 4000)
            self.refresh_customers()

    def _delete_selected_customer(self):
        if not self.selected_customer:
            return

        cust_name = self.selected_customer.get("name", "해당 고객")
        confirm = QMessageBox.question(
            self,
            "고객 삭제 확인",
            f"정말로 '{cust_name}' 고객을 삭제하시겠습니까?\n\n"
            "⚠️ 고객을 삭제하면 관련된 모든 시술 내역도 함께 영구 삭제됩니다.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                CustomerService.delete_customer(self.selected_customer["id"])
                self.status_bar.showMessage(f"'{cust_name}' 고객 및 시술 내역이 삭제되었습니다.", 4000)
                self.selected_customer = None
                self.refresh_customers()
            except Exception as e:
                QMessageBox.critical(self, "삭제 실패", f"고객 삭제 중 오류가 발생했습니다:\n{str(e)}")

    # -------------------------------------------------------------------------
    # 시술 내역 등록 / 삭제
    # -------------------------------------------------------------------------
    def _open_add_treatment_dialog(self):
        if not self.selected_customer:
            return
        dialog = TreatmentDialog(
            self,
            customer_id=self.selected_customer["id"],
            customer_name=self.selected_customer.get("name", "")
        )
        if dialog.exec():
            self.status_bar.showMessage("시술 내역이 등록되었습니다.", 4000)
            self._load_customer_treatments(self.selected_customer)

    def _delete_treatment(self, treatment_id: str):
        confirm = QMessageBox.question(
            self,
            "시술 내역 삭제 확인",
            "선택한 시술 내역을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                TreatmentService.delete_treatment(treatment_id)
                self.status_bar.showMessage("시술 내역이 삭제되었습니다.", 4000)
                if self.selected_customer:
                    self._load_customer_treatments(self.selected_customer)
            except Exception as e:
                QMessageBox.critical(self, "삭제 실패", f"시술 삭제 중 오류가 발생했습니다:\n{str(e)}")

    # -------------------------------------------------------------------------
    # 로그아웃
    # -------------------------------------------------------------------------
    def _handle_logout(self):
        confirm = QMessageBox.question(
            self,
            "로그아웃",
            "정말 로그아웃 하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            AuthService.sign_out()
            self.close()

    # -------------------------------------------------------------------------
    # 자동 업데이트 확인
    # -------------------------------------------------------------------------
    def _check_update_silently(self):
        """앱 시작 시 조용히 업데이트 확인 (새 버전 발견 시에만 팝업)"""
        self.update_worker = UpdateCheckWorker()
        self.update_worker.update_available.connect(self._show_update_dialog)
        self.update_worker.start()

    def _check_update_manually(self):
        """버튼 클릭 시 수동 업데이트 확인"""
        self.status_bar.showMessage("최신 업데이트를 확인하는 중입니다...")
        self.update_worker = UpdateCheckWorker()
        self.update_worker.update_available.connect(self._show_update_dialog)
        self.update_worker.no_update.connect(lambda: QMessageBox.information(
            self, "업데이트 확인", f"현재 최신 버전(v{CURRENT_VERSION})을 사용하고 있습니다."
        ))
        self.update_worker.check_failed.connect(lambda err: QMessageBox.warning(
            self, "확인 실패", f"업데이트 확인 중 오류가 발생했습니다:\n{err}"
        ))
        self.update_worker.start()

    def _show_update_dialog(self, update_info: dict):
        dialog = UpdateDialog(self, update_info=update_info)
        dialog.exec()

