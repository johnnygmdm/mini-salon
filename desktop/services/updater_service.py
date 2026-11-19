"""
Mini Salon Desktop App - 자동 업데이트 서비스
exe 실행 파일 및 데스크톱 앱의 최신 버전 확인 및 자동 다운로드/교체
"""

import sys
import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
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


def check_update_sync(timeout: float = 3.0) -> Optional[Dict[str, Any]]:
    """앱 시작 시 즉시 최신 버전 여부를 확인 (새 버전 발견 시 정보 dict 반환)"""
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            res = client.get(
                VERSION_CHECK_URL,
                headers={"User-Agent": f"MiniSalonDesktop/{CURRENT_VERSION}"}
            )
            if res.status_code == 200:
                data = res.json()
                latest_ver_str = data.get("version", "1.0.0")
                if version.parse(latest_ver_str) > version.parse(CURRENT_VERSION):
                    return data
    except Exception:
        pass
    return None


class UpdateCheckWorker(QThread):
    """백그라운드에서 최신 버전 정보 확인"""
    update_available = Signal(dict)
    no_update = Signal()
    check_failed = Signal(str)

    def run(self):
        try:
            with httpx.Client(timeout=8.0, follow_redirects=True) as client:
                res = client.get(
                    VERSION_CHECK_URL,
                    headers={"User-Agent": f"MiniSalonDesktop/{CURRENT_VERSION}"}
                )
                if res.status_code == 200:
                    data = res.json()
                    latest_ver_str = data.get("version", "1.0.0")

                    if version.parse(latest_ver_str) > version.parse(CURRENT_VERSION):
                        self.update_available.emit(data)
                    else:
                        self.no_update.emit()
                else:
                    self.no_update.emit()
        except Exception as e:
            self.check_failed.emit(str(e))


class DownloadWorker(QThread):
    """새로운 버전의 실행 파일 스트리밍 다운로드 (진행률 표시)"""
    progress = Signal(int)
    download_finished = Signal(str)
    download_failed = Signal(str)

    def __init__(self, download_url: str):
        super().__init__()
        self.download_url = download_url

    def run(self):
        try:
            temp_dir = Path(tempfile.gettempdir())
            target_path = temp_dir / "MiniSalon_NewVersion.exe"

            # 기존 임시 파일 있으면 삭제
            if target_path.exists():
                try:
                    target_path.unlink()
                except Exception:
                    pass

            with httpx.Client(timeout=120.0, follow_redirects=True) as client:
                with client.stream("GET", self.download_url) as resp:
                    resp.raise_for_status()
                    total_bytes = int(resp.headers.get("content-length", 0))

                    downloaded = 0
                    with open(target_path, "wb") as f:
                        for chunk in resp.iter_bytes(chunk_size=131072): # 128KB chunks
                            if chunk:
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
    안전한 프로세스 완전 종료 대기, 파일 교체 및 새 버전 재시작 (PowerShell 기반)
    """
    current_exe = get_current_executable()
    current_pid = os.getpid()
    target_dir = current_exe.parent

    temp_dir = Path(tempfile.gettempdir())
    ps_path = temp_dir / "mini_salon_apply_update.ps1"

    # PowerShell 스크립트로 안전한 프로세스 종료 대기, 파일 교체 및 새 프로세스 구동
    # PyInstaller의 _MEIPASS2 환경변수를 비워주지 않으면 새 프로세스가
    # 종료된 이전 프로세스의 임시 폴더(_MEIxxxxx)를 참조하여 DLL 로드 에러(0x7e)가 발생하므로 완전히 제거
    ps_content = f"""
$ErrorActionPreference = 'SilentlyContinue'
$targetExe = '{str(current_exe).replace("'", "''")}'
$newExe = '{str(new_exe_path).replace("'", "''")}'
$targetPid = {current_pid}
$workDir = '{str(target_dir).replace("'", "''")}'

# 1. 이전 프로세스가 완전히 종료될 때까지 대기 (최대 15초)
for ($i = 0; $i -lt 30; $i++) {{
    if (-not (Get-Process -Id $targetPid -ErrorAction SilentlyContinue)) {{
        break
    }}
    Start-Sleep -Milliseconds 500
}}
Start-Sleep -Seconds 1

# 2. 실행 파일 교체 (최대 10회 재시도)
for ($i = 0; $i -lt 10; $i++) {{
    try {{
        Copy-Item -LiteralPath $newExe -Destination $targetExe -Force -ErrorAction Stop
        break
    }} catch {{
        Start-Sleep -Seconds 1
    }}
}}

# 3. 임시 다운로드 파일 삭제
Remove-Item -LiteralPath $newExe -Force -ErrorAction SilentlyContinue

# 4. PyInstaller 6+ 런타임 환경변수 완전 초기화 (새 프로세스가 삭제된 구 임시 폴더를 참조하지 않도록 보장)
$env:_PYI_APPLICATION_HOME_DIR = $null
$env:_PYI_ARCHIVE_FILE = $null
$env:_PYI_SPLASH_IPC = $null
$env:_PYI_PARENT_PROCESS_LEVEL = $null
$env:_MEIPASS2 = $null
$env:_MEIPASS = $null

# 5. 새 버전의 MiniSalon 실행
Start-Process -FilePath $targetExe -WorkingDirectory $workDir

# 6. 임시 스크립트 자신 삭제
Start-Sleep -Seconds 2
Remove-Item -LiteralPath $MyInvocation.MyCommand.Path -Force -ErrorAction SilentlyContinue
"""
    with open(ps_path, "w", encoding="utf-8") as f:
        f.write(ps_content)

    clean_env = {
        k: v for k, v in os.environ.items()
        if not k.startswith("_PYI_") and not k.startswith("PYI_") and not k.startswith("_MEI") and not k.startswith("MEI")
    }

    # PowerShell 비동기 실행 (백그라운드에서 동작)
    subprocess.Popen(
        [
            "powershell.exe",
            "-WindowStyle", "Hidden",
            "-ExecutionPolicy", "Bypass",
            "-File", str(ps_path)
        ],
        env=clean_env,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )

    # 현재 프로세스 즉시 및 확실한 종료
    os._exit(0)
