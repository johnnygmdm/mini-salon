from typing import List, Dict, Any
from config import get_supabase_client


class TreatmentService:
    """시술 내역 CRUD 서비스 (1:N 고객-시술 관계)"""

    @staticmethod
    def get_treatments_by_customer(customer_id: str) -> List[Dict[str, Any]]:
        """특정 고객의 시술 내역 목록 조회 (최신 시술일자 순)"""
        client = get_supabase_client()
        response = (
            client.table("treatments")
            .select("*")
            .eq("customer_id", customer_id)
            .order("treated_at", desc=True)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []

    @staticmethod
    def create_treatment(
        customer_id: str,
        service_name: str,
        price: int,
        treated_at: str
    ) -> Dict[str, Any]:
        """새 시술 내역 등록"""
        client = get_supabase_client()
        user = client.auth.get_user()
        if not user or not user.user:
            raise ValueError("로그인이 필요합니다.")

        payload = {
            "customer_id": customer_id,
            "service_name": service_name.strip(),
            "price": int(price),
            "treated_at": treated_at,
            "user_id": user.user.id
        }

        response = client.table("treatments").insert(payload).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return {}

    @staticmethod
    def delete_treatment(treatment_id: str) -> bool:
        """시술 내역 삭제"""
        client = get_supabase_client()
        client.table("treatments").delete().eq("id", treatment_id).execute()
        return True

    @staticmethod
    def get_customer_treatment_summary(customer_id: str) -> Dict[str, Any]:
        """고객의 시술 통계 요약 (총 방문 횟수, 총 이용 금액, 최근 방문일)"""
        treatments = TreatmentService.get_treatments_by_customer(customer_id)
        count = len(treatments)
        total_amount = sum(t.get("price", 0) for t in treatments)
        latest_date = treatments[0].get("treated_at") if count > 0 else "-"

        return {
            "count": count,
            "total_amount": total_amount,
            "latest_date": latest_date
        }
