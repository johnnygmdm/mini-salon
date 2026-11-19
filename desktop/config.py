import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# 기본 내장 접속 정보 (exe 파일 단독 실행 시에도 정상 연결)
DEFAULT_SUPABASE_URL = "https://plfgpjvqctkynqpzvobz.supabase.co"
DEFAULT_SUPABASE_ANON_KEY = "sb_publishable_FhOIW0yO-BfGg5BC1hbnqQ_q0NMVO1D"

# 실행 경로 설정
if getattr(sys, "frozen", False):
    DESKTOP_DIR = Path(sys.executable).resolve().parent
else:
    DESKTOP_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = DESKTOP_DIR.parent
SESSION_FILE = DESKTOP_DIR / ".session.json"

# .env 파일 로드 (desktop/.env 우선, 없으면 프로젝트 루트 .env)
env_path = DESKTOP_DIR / ".env"
if not env_path.exists():
    env_path = PROJECT_ROOT / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip() or DEFAULT_SUPABASE_URL
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip() or DEFAULT_SUPABASE_ANON_KEY

_supabase_client: Client | None = None


def is_configured() -> bool:
    """Supabase URL과 Anon Key가 입력되어 있는지 검사"""
    return bool(
        SUPABASE_URL
        and SUPABASE_ANON_KEY
        and not SUPABASE_URL.startswith("https://your-project-id")
        and not SUPABASE_ANON_KEY.startswith("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your")
    )


def get_supabase_client() -> Client:
    """Supabase 클라이언트 싱글톤 반환"""
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            raise ValueError("SUPABASE_URL 또는 SUPABASE_ANON_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return _supabase_client


def save_session(access_token: str, refresh_token: str, user_email: str) -> None:
    """로컬 세션 저장"""
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_email": user_email
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"세션 저장 실패: {e}")


def load_session() -> dict | None:
    """저장된 세션 불러오기"""
    if not SESSION_FILE.exists():
        return None
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def clear_session() -> None:
    """저장된 세션 삭제"""
    if SESSION_FILE.exists():
        try:
            SESSION_FILE.unlink()
        except Exception as e:
            print(f"세션 파일 삭제 실패: {e}")
