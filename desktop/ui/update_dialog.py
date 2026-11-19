"""
Mini Salon Desktop App - 업데이트 알림 및 다운로드 다이얼로그
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt
from services.updater_service import (
    CURRENT_VERSION, DownloadWorker, apply_update_and_restart
)


class UpdateDialog(QDialog):
    """새 버전 발견 시 업데이트 알림 및 다운로드 진행 다이얼로그"""

    def __init__(self, parent=None, update_info: dict = None):
        super().__init__(parent)
        self.update_info = update_info or {}
        self.download_worker: DownloadWorker | None = None

        self.setWindowTitle("Mini Salon CRM - 새 버전 업데이트 알림")
        self.setFixedSize(440, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # 상단 아이콘 & 헤더
        header_layout = QHBoxLayout()
        icon_label = QLabel("🚀")
        icon_label.setStyleSheet("font-size: 32px;")
        header_layout.addWidget(icon_label)

        title_box = QVBoxLayout()
        title_label = QLabel("새로운 버전이 출시되었습니다!")
        title_label.setObjectName("cardTitle")
        title_box.addWidget(title_label)

        new_ver = self.update_info.get("version", "최신 버전")
        rel_date = self.update_info.get("releaseDate", "")
        ver_sub = QLabel(f"현재 버전: v{CURRENT_VERSION}  ➔  새 버전: v{new_ver} ({rel_date})")
        ver_sub.setStyleSheet("color: #4f46e5; font-weight: 600; font-size: 12px;")
        title_box.addWidget(ver_sub)
        header_layout.addLayout(title_box)
        layout.addLayout(header_layout)

        # 변경 사항 안내 박스
        changelog_title = QLabel("주요 업데이트 내용:")
        changelog_title.setStyleSheet("font-weight: 600; color: #334155; font-size: 12px;")
        layout.addWidget(changelog_title)

        changelog_text = self.update_info.get("changelog", "안정성 향상 및 버그 수정")
        self.changelog_box = QLabel(changelog_text)
        self.changelog_box.setStyleSheet(
            "background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; color: #475569; font-size: 12px;"
        )
        self.changelog_box.setWordWrap(True)
        layout.addWidget(self.changelog_box, 1)

        # 프로그레스 바 (다운로드 중일 때 표시)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                text-align: center;
                background-color: #f1f5f9;
                height: 18px;
                font-size: 11px;
                font-weight: 600;
            }
            QProgressBar::chunk {
                background-color: #4f46e5;
                border-radius: 5px;
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # 상태 안내 문구
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #64748b; font-size: 11px; text-align: center;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.hide()
        layout.addWidget(self.status_label)

        # 하단 액션 버튼
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(10)

        self.later_btn = QPushButton("나중에 하기")
        self.later_btn.clicked.connect(self.reject)
        self.btn_layout.addWidget(self.later_btn)

        self.update_btn = QPushButton("지금 자동 업데이트")
        self.update_btn.setObjectName("primaryBtn")
        self.update_btn.clicked.connect(self._start_download)
        self.btn_layout.addWidget(self.update_btn)

        layout.addLayout(self.btn_layout)

    def _start_download(self):
        download_url = self.update_info.get("downloadUrl", "")
        if not download_url:
            QMessageBox.warning(self, "오류", "다운로드 경로를 찾을 수 없습니다.")
            return

        # UI 전환
        self.update_btn.setEnabled(False)
        self.later_btn.setEnabled(False)
        self.progress_bar.show()
        self.status_label.show()
        self.status_label.setText("최신 실행 파일을 다운로드하는 중입니다...")

        # 백그라운드 다운로드 시작
        self.download_worker = DownloadWorker(download_url)
        self.download_worker.progress.connect(self._on_progress)
        self.download_worker.download_finished.connect(self._on_finished)
        self.download_worker.download_failed.connect(self._on_failed)
        self.download_worker.start()

    def _on_progress(self, percent: int):
        self.progress_bar.setValue(percent)
        self.status_label.setText(f"다운로드 진행 중... ({percent}%)")

    def _on_finished(self, downloaded_file_path: str):
        self.status_label.setText("다운로드 완료! 프로그램을 재시작하여 교체합니다...")
        self.progress_bar.setValue(100)

        QMessageBox.information(
            self,
            "업데이트 준비 완료",
            "다운로드가 완료되었습니다!\n확인을 누르면 프로그램이 자동으로 재시작되며 새 버전이 적용됩니다."
        )

        apply_update_and_restart(downloaded_file_path)

    def _on_failed(self, error_msg: str):
        self.update_btn.setEnabled(True)
        self.later_btn.setEnabled(True)
        self.status_label.setText("다운로드 실패")
        QMessageBox.critical(
            self,
            "다운로드 실패",
            f"업데이트 파일 다운로드 중 오류가 발생했습니다:\n{error_msg}\n\n웹사이트나 공식 링크에서 직접 다운로드해주세요."
        )
