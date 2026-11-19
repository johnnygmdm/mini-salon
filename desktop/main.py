"""
Mini Salon Desktop App - 엔트리포인트 (main.py)
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.styles import APP_STYLESHEET
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow
from services.auth_service import AuthService


def main():
    # 고해상도 DPI 스케일링 설정
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("MiniSalonCRM")
    app.setStyleSheet(APP_STYLESHEET)

    while True:
        current_email = ""
        # 1. 자동 로그인 시도 (저장된 세션 복원)
        restored = AuthService.restore_session()
        if restored:
            current_email = restored.get("email", "")
        else:
            # 2. 로그인 다이얼로그 표시
            login_dialog = LoginDialog()
            if login_dialog.exec() != LoginDialog.Accepted:
                # 사용자가 로그인 창을 닫거나 취소한 경우 앱 종료
                break
            if login_dialog.logged_in_user:
                current_email = login_dialog.logged_in_user.email or ""

        # 3. 메인 윈도우 실행
        main_win = MainWindow(current_user_email=current_email)
        main_win.show()
        app.exec()

        # 로그아웃 여부 확인: 만약 로그아웃된 상태라면 다시 루프 시작(로그인 창 표시), 아니면 루프 종료
        user = AuthService.get_current_user()
        if user is not None:
            # 창 닫기로 정상 종료된 경우
            break

    sys.exit(0)


if __name__ == "__main__":
    main()
