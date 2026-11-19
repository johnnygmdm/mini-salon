"""
Mini Salon Desktop App - 시술 내역 등록 다이얼로그
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QDateEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from services.treatment_service import TreatmentService


class TreatmentDialog(QDialog):
    """시술 내역 추가를 위한 다이얼로그"""

    COMMON_SERVICES = [
        "남성 컷",
        "여성 컷",
        "학생 컷",
        "디자인 펌",
        "열펌 / 세팅펌",
        "볼륨 매직",
        "전체 염색",
        "뿌리 염색",
        "탈색",
        "모발 클리닉",
        "두피 스케일링",
        "다운펌",
        "드라이 / 스타일링"
    ]

    def __init__(self, parent=None, customer_id: str = "", customer_name: str = ""):
        super().__init__(parent)
        self.customer_id = customer_id
        self.customer_name = customer_name

        self.setWindowTitle(f"시술 내역 등록 - {customer_name}")
        self.setFixedSize(400, 380)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # 상단 안내
        header = QLabel(f"💇 {self.customer_name} 고객님 시술 내역 등록")
        header.setObjectName("cardTitle")
        layout.addWidget(header)

        # 1. 시술일자
        date_label = QLabel("시술일자 *")
        date_label.setStyleSheet("font-weight: 600; color: #334155;")
        layout.addWidget(date_label)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.date_input)

        # 2. 시술 항목/명칭 (콤보박스 편집 가능)
        service_label = QLabel("시술 항목 *")
        service_label.setStyleSheet("font-weight: 600; color: #334155;")
        layout.addWidget(service_label)

        self.service_combo = QComboBox()
        self.service_combo.setEditable(True)
        self.service_combo.addItems(self.COMMON_SERVICES)
        self.service_combo.setCurrentIndex(0)
        layout.addWidget(self.service_combo)

        # 3. 시술 금액
        price_label = QLabel("시술 금액 (원) *")
        price_label.setStyleSheet("font-weight: 600; color: #334155;")
        layout.addWidget(price_label)

        self.price_spin = QSpinBox()
        self.price_spin.setRange(0, 100_000_000)
        self.price_spin.setSingleStep(5000)
        self.price_spin.setValue(25000)
        self.price_spin.setGroupSeparatorShown(True)
        self.price_spin.setSuffix(" 원")
        layout.addWidget(self.price_spin)

        layout.addSpacing(8)

        # 하단 액션 버튼
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        cancel_btn = QPushButton("취소")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("등록 완료")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save_treatment)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _save_treatment(self):
        service_name = self.service_combo.currentText().strip()
        price = self.price_spin.value()
        treated_at = self.date_input.date().toString("yyyy-MM-dd")

        if not service_name:
            QMessageBox.warning(self, "입력 오류", "시술 항목을 입력하거나 선택해주세요.")
            self.service_combo.setFocus()
            return

        try:
            TreatmentService.create_treatment(
                customer_id=self.customer_id,
                service_name=service_name,
                price=price,
                treated_at=treated_at
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "등록 실패", f"시술 내역 저장 중 오류가 발생했습니다:\n{str(e)}")
