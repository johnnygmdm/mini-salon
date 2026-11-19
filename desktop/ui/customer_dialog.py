"""
Mini Salon Desktop App - 고객 등록/수정 다이얼로그
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from services.customer_service import CustomerService


class CustomerDialog(QDialog):
    """고객 등록 및 수정을 위한 다이얼로그"""

    def __init__(self, parent=None, customer_data: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.customer_data = customer_data
        self.is_edit = customer_data is not None

        title = "고객 정보 수정" if self.is_edit else "신규 고객 등록"
        self.setWindowTitle(title)
        self.setFixedSize(420, 430)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._init_ui()
        if self.is_edit:
            self._load_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # 다이얼로그 상단 헤더
        header_title = QLabel("고객 정보 수정" if self.is_edit else "새로운 고객 등록")
        header_title.setObjectName("cardTitle")
        layout.addWidget(header_title)

        # 1. 이름 입력
        name_label = QLabel("고객명 *")
        name_label.setStyleSheet("font-weight: 600; color: #334155;")
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("예: 홍길동")
        layout.addWidget(self.name_input)

        # 2. 연락처 입력
        phone_label = QLabel("연락처 *")
        phone_label.setStyleSheet("font-weight: 600; color: #334155;")
        layout.addWidget(phone_label)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("예: 010-1234-5678")
        self.phone_input.textChanged.connect(self._format_phone)
        layout.addWidget(self.phone_input)

        # 3. 특이사항/메모
        memo_label = QLabel("고객 특이사항 / 메모")
        memo_label.setStyleSheet("font-weight: 600; color: #334155;")
        layout.addWidget(memo_label)

        self.memo_input = QTextEdit()
        self.memo_input.setPlaceholderText("선호 스타일, 알레르기 유무, 모발 상태 등 자유 메모...")
        self.memo_input.setFixedHeight(90)
        layout.addWidget(self.memo_input)

        layout.addSpacing(6)

        # 하단 버튼 레이아웃
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        cancel_btn = QPushButton("취소")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("저장 완료" if self.is_edit else "등록")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save_customer)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _format_phone(self, text: str):
        """휴대폰 번호 자동 하이픈 포맷팅"""
        digits = "".join(filter(str.isdigit, text))
        formatted = ""
        if len(digits) <= 3:
            formatted = digits
        elif len(digits) <= 7:
            formatted = f"{digits[:3]}-{digits[3:]}"
        elif len(digits) <= 11:
            formatted = f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        else:
            formatted = f"{digits[:3]}-{digits[3:7]}-{digits[7:11]}"

        if formatted != text:
            # 커서 위치 보호를 위해 시그널 일시 차단 후 재할당
            self.phone_input.blockSignals(True)
            self.phone_input.setText(formatted)
            self.phone_input.setCursorPosition(len(formatted))
            self.phone_input.blockSignals(False)

    def _load_data(self):
        """수정 모드 데이터 바인딩"""
        if not self.customer_data:
            return
        self.name_input.setText(self.customer_data.get("name", ""))
        self.phone_input.setText(self.customer_data.get("phone", ""))
        self.memo_input.setPlainText(self.customer_data.get("memo", "") or "")

    def _save_customer(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        memo = self.memo_input.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "입력 오류", "고객명을 입력해주세요.")
            self.name_input.setFocus()
            return

        if not phone:
            QMessageBox.warning(self, "입력 오류", "연락처를 입력해주세요.")
            self.phone_input.setFocus()
            return

        try:
            if self.is_edit:
                customer_id = self.customer_data["id"]
                CustomerService.update_customer(customer_id, name, phone, memo)
            else:
                CustomerService.create_customer(name, phone, memo)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "저장 실패", f"고객 정보 저장 중 오류가 발생했습니다:\n{str(e)}")
