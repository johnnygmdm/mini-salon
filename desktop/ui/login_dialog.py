"""
Mini Salon Desktop App - 로그인 및 회원가입 다이얼로그
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QThread
from services.auth_service import AuthService
from config import is_configured, SUPABASE_URL, CLIENT_NAME, CLIENT_SUBTITLE, LOGO_ICON


class AuthWorker(QThread):
    """백그라운드에서 Supabase 인증 요청 처리"""
    success = Signal(dict)
    failure = Signal(str)

    def __init__(self, mode: str, email: str, password: str):
        super().__init__()
        self.mode = mode
        self.email = email
        self.password = password

    def run(self):
        try:
            if self.mode == "signin":
                res = AuthService.sign_in(self.email, self.password)
            else:
                res = AuthService.sign_up(self.email, self.password)

            if res.get("success"):
                self.success.emit(res)
            else:
                self.failure.emit(res.get("error", "인증 실패"))
        except Exception as e:
            self.failure.emit(str(e))


class LoginDialog(QDialog):
    """로그인 / 회원가입 모달 다이얼로그"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{LOGO_ICON} {CLIENT_NAME} - 로그인")
        self.setFixedSize(400, 480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.worker: AuthWorker | None = None
        self.logged_in_user = None

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(16)

        # 헤더 타이틀
        title_label = QLabel(f"{LOGO_ICON} {CLIENT_NAME}")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        sub_label = QLabel(f"{CLIENT_SUBTITLE} (원장님 전용)")
        sub_label.setObjectName("subtitleLabel")
        sub_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(sub_label)

        main_layout.addSpacing(8)

        # Supabase 설정 여부 체크 안내
        if not is_configured():
            warning_label = QLabel(
                "⚠️ Supabase 환경 변수가 설정되지 않았습니다.\n"
                ".env 파일에 SUPABASE_URL 및 SUPABASE_ANON_KEY를 입력해주세요."
            )
            warning_label.setStyleSheet("color: #b91c1c; background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 10px;")
            warning_label.setWordWrap(True)
            main_layout.addWidget(warning_label)

        # 탭 (로그인 / 회원가입)
        self.tabs = QTabWidget()
        self.signin_tab = self._create_form_tab(is_signup=False)
        self.signup_tab = self._create_form_tab(is_signup=True)
        self.tabs.addTab(self.signin_tab, "로그인")
        self.tabs.addTab(self.signup_tab, "회원가입")
        main_layout.addWidget(self.tabs)

        # 상태/에러 메시지 표시 레이블
        self.msg_label = QLabel("")
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setStyleSheet("color: #dc2626; font-size: 12px; font-weight: 500;")
        self.msg_label.setWordWrap(True)
        main_layout.addWidget(self.msg_label)

    def _create_form_tab(self, is_signup: bool) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(12)

        # 이메일 입력
        email_label = QLabel("이메일")
        email_label.setStyleSheet("font-weight: 600; color: #334155;")
        layout.addWidget(email_label)

        email_input = QLineEdit()
        email_input.setPlaceholderText("salon@example.com")
        layout.addWidget(email_input)

        # 비밀번호 입력
        pw_label = QLabel("비밀번호")
        pw_label.setStyleSheet("font-weight: 600; color: #334155;")
        layout.addWidget(pw_label)

        pw_input = QLineEdit()
        pw_input.setEchoMode(QLineEdit.Password)
        pw_input.setPlaceholderText("6자 이상 입력")
        layout.addWidget(pw_input)

        layout.addSpacing(10)

        # 버튼
        btn_text = "회원가입 완료" if is_signup else "로그인"
        submit_btn = QPushButton(btn_text)
        submit_btn.setObjectName("primaryBtn")
        submit_btn.setFixedHeight(38)
        layout.addWidget(submit_btn)

        layout.addStretch()

        if is_signup:
            self.signup_email = email_input
            self.signup_pw = pw_input
            self.signup_btn = submit_btn
            submit_btn.clicked.connect(lambda: self._handle_auth("signup"))
            pw_input.returnPressed.connect(lambda: self._handle_auth("signup"))
        else:
            self.signin_email = email_input
            self.signin_pw = pw_input
            self.signin_btn = submit_btn
            submit_btn.clicked.connect(lambda: self._handle_auth("signin"))
            pw_input.returnPressed.connect(lambda: self._handle_auth("signin"))

        return widget

    def _handle_auth(self, mode: str):
        if not is_configured():
            QMessageBox.critical(
                self,
                "설정 오류",
                "Supabase 접속 정보가 설정되지 않았습니다.\n"
                "desktop/.env 파일에 SUPABASE_URL 및 SUPABASE_ANON_KEY를 먼저 설정해주세요."
            )
            return

        email = self.signup_email.text() if mode == "signup" else self.signin_email.text()
        password = self.signup_pw.text() if mode == "signup" else self.signin_pw.text()

        email = email.strip()
        password = password.strip()

        if not email:
            self.msg_label.setText("이메일을 입력해주세요.")
            return
        if not password:
            self.msg_label.setText("비밀번호를 입력해주세요.")
            return
        if len(password) < 6:
            self.msg_label.setText("비밀번호는 최소 6자 이상이어야 합니다.")
            return

        self.msg_label.setStyleSheet("color: #4f46e5; font-size: 12px; font-weight: 500;")
        self.msg_label.setText("인증 처리 중입니다. 잠시만 기다려주세요...")

        self.signin_btn.setEnabled(False)
        self.signup_btn.setEnabled(False)

        self.worker = AuthWorker(mode, email, password)
        self.worker.success.connect(self._on_auth_success)
        self.worker.failure.connect(self._on_auth_failure)
        self.worker.start()

    def _on_auth_success(self, res: dict):
        self.signin_btn.setEnabled(True)
        self.signup_btn.setEnabled(True)
        self.logged_in_user = res.get("user")

        if self.tabs.currentIndex() == 1 and not res.get("session"):
            # 회원가입 완료 후 이메일 확인이 필요한 경우
            QMessageBox.information(
                self,
                "회원가입 완료",
                "가입이 완료되었습니다!\n이메일 인증이 필요한 경우 확인 메일을 확인 후 로그인해주세요."
            )
            self.tabs.setCurrentIndex(0)
            self.msg_label.setText("")
        else:
            self.accept()

    def _on_auth_failure(self, error_msg: str):
        self.signin_btn.setEnabled(True)
        self.signup_btn.setEnabled(True)
        self.msg_label.setStyleSheet("color: #dc2626; font-size: 12px; font-weight: 500;")

        # Supabase 오류 메시지 한글 친화 변환
        if "Invalid login credentials" in error_msg:
            friendly_msg = "이메일 또는 비밀번호가 올바르지 않습니다."
        elif "User already registered" in error_msg:
            friendly_msg = "이미 등록된 이메일 주소입니다."
        elif "Database error saving new user" in error_msg:
            friendly_msg = "신규 회원가입이 차단되었습니다. (관리자 전용)"
        else:
            friendly_msg = f"인증 실패: {error_msg}"

        self.msg_label.setText(friendly_msg)
