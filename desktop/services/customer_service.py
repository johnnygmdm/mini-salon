from typing import List, Dict, Any, Optional
from config import get_supabase_client


class CustomerService:
    """고객 데이터 CRUD 및 검색 서비스"""

    @staticmethod
    def get_customers(search_query: str = "") -> List[Dict[str, Any]]:
        """고객 목록 조회 및 검색 (이름 또는 전화번호 부분 일치)"""
        client = get_supabase_client()
        query = client.table("customers").select("*")

        search = search_query.strip()
        if search:
            # 이름 또는 전화번호에 검색어가 포함된 경우
            query = query.or_(f"name.ilike.%{search}%,phone.ilike.%{search}%")

        response = query.order("created_at", desc=True).execute()
        return response.data or []

    @staticmethod
    def get_customer(customer_id: str) -> Optional[Dict[str, Any]]:
        """단일 고객 상세 조회"""
        client = get_supabase_client()
        response = client.table("customers").select("*").eq("id", customer_id).single().execute()
        return response.data

    @staticmethod
    def create_customer(name: str, phone: str, memo: str = "") -> Dict[str, Any]:
        """신규 고객 등록"""
        client = get_supabase_client()
        user = client.auth.get_user()
        if not user or not user.user:
            raise ValueError("로그인이 필요합니다.")

        payload = {
            "name": name.strip(),
            "phone": phone.strip(),
            "memo": memo.strip() if memo else "",
            "user_id": user.user.id
        }

        response = client.table("customers").insert(payload).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return {}

    @staticmethod
    def update_customer(customer_id: str, name: str, phone: str, memo: str = "") -> Dict[str, Any]:
        """고객 정보 수정"""
        client = get_supabase_client()
        payload = {
            "name": name.strip(),
            "phone": phone.strip(),
            "memo": memo.strip() if memo else ""
        }

        response = client.table("customers").update(payload).eq("id", customer_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return {}

    @staticmethod
    def delete_customer(customer_id: str) -> bool:
        """고객 삭제 (연관된 시술 내역도 CASCADE 설정에 의해 자동 삭제)"""
        client = get_supabase_client()
        client.table("customers").delete().eq("id", customer_id).execute()
        return True
