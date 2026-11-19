"""
Mini Salon Desktop App - 자동 업데이트 서비스
exe 실행 파일 및 데스크톱 앱의 최신 버전 확인 및 자동 다운로드/교체
"""

import sys
import os
import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional, Dict, Any
from packaging import version
from PySide6.QtCore import QThread, Signal

CURRENT_VERSION = "1.0.0"
VERSION_CHECK_URL = "https://mini-salon.pages.dev/version.json"


def get_current_executable() -> Path:
    """현재 실행 파일 경로 반환 (PyInstaller frozen exe 또는 python main.py)"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve()
    return Path(__file__).resolve().parent.parent / "main.py"


def is_running_as_exe() -> bool:
    """PyInstaller 등으로 패키징된 .exe로 실행 중인지 확인"""
    return getattr(sys, "frozen", False)


class UpdateCheckWorker(QThread):
    """백그라운드에서 최신 버전 정보 확인"""
    update_available = Signal(dict)  # 새 버전 정보 딕셔너리
    no_update = Signal()            # 최신 버전임
    check_failed = Signal(str)      # 검사 실패

    def run(self):
        try:
            req = urllib.request.Request(
                VERSION_CHECK_URL,
                headers={"User-Agent": f"MiniSalonDesktop/{CURRENT_VERSION}"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    latest_ver_str = data.get("version", "1.0.0")

                    # semver 비교
                    if version.parse(latest_ver_str) > version.parse(CURRENT_VERSION):
                        self.update_available.emit(data)
                    else:
                        self.no_update.emit()
                else:
                    self.no_update.emit()
        except Exception as e:
            self.check_failed.emit(str(e))


class DownloadWorker(QThread):
    """새로운 버전의 실행 파일 다운로드"""
    progress = Signal(int)          # 다운로드 퍼센트 (0~100)
    download_finished = Signal(str) # 다운로드된 임시 파일 경로
    download_failed = Signal(str)   # 실패 메시지

    def __init__(self, download_url: str):
        super().__init__()
        self.download_url = download_url

    def run(self):
        try:
            temp_dir = Path(tempfile.gettempdir())
            target_path = temp_dir / "MiniSalon_NewVersion.exe"

            req = urllib.request.Request(
                self.download_url,
                headers={"User-Agent": "MiniSalonDesktopUpdater"}
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                total_size = resp.headers.get("Content-Length")
                total_bytes = int(total_size) if total_size else 0

                downloaded = 0
                block_size = 65536  # 64KB

                with open(target_path, "wb") as f:
                    while True:
                        chunk = resp.read(block_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_bytes > 0:
                            percent = int((downloaded / total_bytes) * 100)
                            self.progress.emit(min(percent, 100))

            self.progress.emit(100)
            self.download_finished.emit(str(target_path))
        except Exception as e:
            self.download_failed.emit(str(e))


def apply_update_and_restart(new_exe_path: str):
    """
    다운로드된 새 exe를 기존 실행 파일 위치에 덮어쓰고 앱 재실행
    배치 스크립트를 독립 프로세스로 띄운 뒤 현재 프로세스 종료
    """
    current_exe = get_current_executable()
    temp_dir = Path(tempfile.gettempdir())
    bat_path = temp_dir / "mini_salon_apply_update.bat"

    # 배치 파일 작성:
    # 1초 대기(현재 프로세스 완전 종료 보장) -> 덮어쓰기 -> 임시파일 삭제 -> 새 exe 시작 -> 배치파일 자체 삭제
    bat_script = f"""@echo off
chcp 65001 > nul
echo Mini Salon 업데이트를 적용하는 중입니다...
timeout /t 2 /nobreak > nul
copy /y "{new_exe_path}" "{current_exe}" > nul
del /f /q "{new_exe_path}" > nul
start "" "{current_exe}"
del "%~f0"
"""
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_script)

    # 비동기로 배치 파일 실행
    subprocess.Popen(
        ["cmd.exe", "/c", str(bat_path)],
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    # 현재 앱 즉시 종료
    sys.exit(0)
