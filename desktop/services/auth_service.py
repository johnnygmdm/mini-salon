from typing import Optional, Dict, Any
from config import get_supabase_client, save_session, load_session, clear_session


class AuthService:
    """Supabase 인증 서비스"""

    @staticmethod
    def sign_in(email: str, password: str) -> Dict[str, Any]:
        """이메일/비밀번호 로그인"""
        client = get_supabase_client()
        try:
            res = client.auth.sign_in_with_password({
                "email": email.strip(),
                "password": password.strip()
            })
            if res.session:
                save_session(
                    access_token=res.session.access_token,
                    refresh_token=res.session.refresh_token,
                    user_email=res.user.email or email
                )
            return {"success": True, "user": res.user, "session": res.session}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def sign_up(email: str, password: str) -> Dict[str, Any]:
        """회원가입"""
        client = get_supabase_client()
        try:
            res = client.auth.sign_up({
                "email": email.strip(),
                "password": password.strip()
            })
            # 자동 로그인이 될 수도 있고, 이메일 확인이 필요할 수도 있음
            if res.session:
                save_session(
                    access_token=res.session.access_token,
                    refresh_token=res.session.refresh_token,
                    user_email=res.user.email or email
                )
            return {"success": True, "user": res.user, "session": res.session}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def sign_out() -> bool:
        """로그아웃"""
        client = get_supabase_client()
        try:
            client.auth.sign_out()
        except Exception:
            pass
        clear_session()
        return True

    @staticmethod
    def restore_session() -> Optional[Dict[str, Any]]:
        """로컬에 저장된 세션 복원 시도"""
        saved = load_session()
        if not saved:
            return None

        client = get_supabase_client()
        try:
            res = client.auth.set_session(saved["access_token"], saved["refresh_token"])
            if res.user:
                return {"user": res.user, "email": saved.get("user_email", res.user.email)}
        except Exception:
            # 토큰 만료 또는 유효하지 않은 경우 세션 삭제
            clear_session()
        return None

    @staticmethod
    def get_current_user() -> Optional[Any]:
        """현재 세션 유저 확인"""
        client = get_supabase_client()
        try:
            user_response = client.auth.get_user()
            return user_response.user if user_response else None
        except Exception:
            return None
