#!/usr/bin/env python3
"""
Mini Salon CRM - 외주 고객사 맞춤 1분 자동 설정 마법사 (configure_client.py)
새로운 외주 고객사가 들어왔을 때 상호명, 업종, 브랜드 컬러, Supabase 키를
단 몇 초 만에 일괄 갱신하고 배포 준비를 완료합니다.
"""

import os
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

# 업종별 기본 테마 및 메뉴 프리셋
PRESETS = {
    "1": {
        "name": "1인 헤어살롱 / 미용실",
        "clientName": "루나 헤어스튜디오",
        "clientSubtitle": "1인 프리미엄 헤어살롱",
        "category": "CRM",
        "logoIcon": "✂️",
        "theme": "indigo",
        "colors": {
            "primary": "#4f46e5",
            "primaryHover": "#4338ca",
            "primaryLight": "#eef2ff",
            "primaryBorder": "#c7d2fe",
            "textOnPrimary": "#ffffff"
        },
        "defaultMenuItems": [
            "남성 컷", "여성 컷", "디자인 펌", "열펌/세팅펌",
            "볼륨 매직", "전체 염색", "뿌리 염색", "모발 클리닉"
        ]
    },
    "2": {
        "name": "바버샵 / 맨즈헤어",
        "clientName": "클래식 바버샵",
        "clientSubtitle": "프리미엄 정통 바버샵",
        "category": "BARBER",
        "logoIcon": "💈",
        "theme": "slate",
        "colors": {
            "primary": "#0f172a",
            "primaryHover": "#1e293b",
            "primaryLight": "#f1f5f9",
            "primaryBorder": "#cbd5e1",
            "textOnPrimary": "#ffffff"
        },
        "defaultMenuItems": [
            "바버 컷", "사이드 파트", "포마드 쉐이빙", "풀 쉐이빙",
            "다운펌", "라인 정리", "두피 스케일링", "맨즈 펌"
        ]
    },
    "3": {
        "name": "네일샵 / 에스테틱 / 뷰티",
        "clientName": "블라썸 네일 & 뷰티",
        "clientSubtitle": "프리미엄 1:1 예약제 뷰티살롱",
        "category": "BEAUTY",
        "logoIcon": "💅",
        "theme": "rose",
        "colors": {
            "primary": "#e11d48",
            "primaryHover": "#be123c",
            "primaryLight": "#fff1f2",
            "primaryBorder": "#fecdd3",
            "textOnPrimary": "#ffffff"
        },
        "defaultMenuItems": [
            "기본 케어", "젤 네일 기본", "이달의 아트", "젤 패디큐어",
            "파츠/스톤 추가", "쏙오프/제거", "속눈썹 펌", "스킨 플래닝"
        ]
    },
    "4": {
        "name": "필라테스 / PT / 피트니스",
        "clientName": "바디핏 필라테스",
        "clientSubtitle": "1:1 개인 레슨 & 체형 교정",
        "category": "FITNESS",
        "logoIcon": "🏃",
        "theme": "emerald",
        "colors": {
            "primary": "#059669",
            "primaryHover": "#047857",
            "primaryLight": "#ecfdf5",
            "primaryBorder": "#a7f3d0",
            "textOnPrimary": "#ffffff"
        },
        "defaultMenuItems": [
            "1:1 개인레슨 1회", "1:1 개인레슨 10회권", "1:1 개인레슨 30회권",
            "2:1 듀엣레슨 10회권", "체형 분석 & 오리엔테이션", "원데이 클래스"
        ]
    },
    "5": {
        "name": "펫살롱 / 반려동물 미용",
        "clientName": "댕댕이 펫살롱",
        "clientSubtitle": "반려동물 안심 케어 & 스타일링",
        "category": "PET",
        "logoIcon": "🐾",
        "theme": "amber",
        "colors": {
            "primary": "#d97706",
            "primaryHover": "#b45309",
            "primaryLight": "#fffbeb",
            "primaryBorder": "#fde68a",
            "textOnPrimary": "#ffffff"
        },
        "defaultMenuItems": [
            "소형견 위생목욕", "소형견 전체미용", "가위컷 스타일링", "스포팅",
            "스파 & 탄산 입욕", "엉킨 털 관리", "중형견 기본미용"
        ]
    }
}


def prompt(label: str, default: str = "") -> str:
    """사용자 입력 프롬프트"""
    if default:
        val = input(f"{label} [{default}]: ").strip()
        return val if val else default
    return input(f"{label}: ").strip()


def run_wizard():
    print("=" * 65)
    print(" 🚀 Mini Salon CRM - 외주 고객사 맞춤 설정 마법사")
    print("=" * 65)
    print("새로운 외주 프로젝트를 위한 브랜드, 업종, DB 접속 정보를 설정합니다.\n")

    # 기존 설정 읽기 (있을 경우 기본값 활용)
    current_cfg_path = ROOT_DIR / "client_config.json"
    current_cfg = {}
    if current_cfg_path.exists():
        try:
            with open(current_cfg_path, "r", encoding="utf-8") as f:
                current_cfg = json.load(f)
        except Exception:
            pass

    # 1. 업종 프리셋 선택
    print("📋 [1단계] 업종 템플릿 프리셋을 선택하세요:")
    for k, v in PRESETS.items():
        print(f"  {k}. {v['logoIcon']} {v['name']} (대표컬러: {v['theme']})")
    print("  6. ⚙️ 직접 커스텀 입력 (수동 설정)")

    preset_choice = prompt("선택 (1~6)", "1")
    selected_preset = PRESETS.get(preset_choice, PRESETS["1"])

    print("\n" + "-" * 50)
    print("🏢 [2단계] 고객사 브랜드 정보 입력")
    print("-" * 50)

    def_name = current_cfg.get("clientName") or selected_preset["clientName"]
    def_subtitle = current_cfg.get("clientSubtitle") or selected_preset["clientSubtitle"]
    def_category = current_cfg.get("category") or selected_preset["category"]
    def_icon = current_cfg.get("logoIcon") or selected_preset["logoIcon"]
    def_primary = current_cfg.get("colors", {}).get("primary") or selected_preset["colors"]["primary"]

    client_name = prompt("1. 상호명 (고객사명)", def_name)
    client_subtitle = prompt("2. 부제목 / 슬로건", def_subtitle)
    category = prompt("3. 카테고리 태그 (예: CRM, BARBER, STUDIO)", def_category)
    logo_icon = prompt("4. 대표 이모지 아이콘", def_icon)
    primary_color = prompt("5. 대표 브랜드 색상 HEX코드", def_primary)

    # 3. 기본 서비스 메뉴 구성
    print("\n" + "-" * 50)
    print("💈 [3단계] 기본 제공 시술/이용권 항목 (쉼표로 구분)")
    print("-" * 50)
    def_menu_str = ", ".join(selected_preset["defaultMenuItems"])
    menu_input = prompt("서비스 항목들", def_menu_str)
    menu_items = [m.strip() for m in menu_input.split(",") if m.strip()]

    # 4. 관리자 계정 & Supabase DB 정보
    print("\n" + "-" * 50)
    print("🔑 [4단계] Supabase 데이터베이스 및 관리자 계정")
    print("-" * 50)
    def_email = current_cfg.get("adminEmail", "owner@salon.com")
    def_url = current_cfg.get("supabase", {}).get("url", "https://plfgpjvqctkynqpzvobz.supabase.co")
    def_key = current_cfg.get("supabase", {}).get("anonKey", "sb_publishable_FhOIW0yO-BfGg5BC1hbnqQ_q0NMVO1D")

    admin_email = prompt("1. 원장님(관리자) 로그인 이메일", def_email)
    supabase_url = prompt("2. Supabase Project URL", def_url)
    supabase_anon_key = prompt("3. Supabase Anon Key", def_key)

    # 설정 딕셔너리 조립
    new_config = {
        "clientName": client_name,
        "clientSubtitle": client_subtitle,
        "category": category,
        "logoIcon": logo_icon,
        "theme": selected_preset.get("theme", "custom"),
        "colors": {
            "primary": primary_color,
            "primaryHover": primary_color, # 추후 필요 시 자동 음영 계산 가능
            "primaryLight": "#f8fafc",
            "primaryBorder": "#cbd5e1",
            "textOnPrimary": "#ffffff"
        },
        "defaultMenuItems": menu_items,
        "adminEmail": admin_email,
        "supabase": {
            "url": supabase_url,
            "anonKey": supabase_anon_key
        },
        "version": current_cfg.get("version", "1.0.1"),
        "updateCheckUrl": current_cfg.get("updateCheckUrl", "https://mini-salon.pages.dev/version.json")
    }

    # 파일 동기화 작업
    print("\n⚙️ 설정을 프로젝트 전체에 일괄 동기화하는 중...")

    # 1. 루트 client_config.json
    with open(ROOT_DIR / "client_config.json", "w", encoding="utf-8") as f:
        json.dump(new_config, f, indent=2, ensure_ascii=False)

    # 2. desktop/client_config.json
    with open(ROOT_DIR / "desktop" / "client_config.json", "w", encoding="utf-8") as f:
        json.dump(new_config, f, indent=2, ensure_ascii=False)

    # 3. web/client_config.json
    with open(ROOT_DIR / "web" / "client_config.json", "w", encoding="utf-8") as f:
        json.dump(new_config, f, indent=2, ensure_ascii=False)

    # 4. desktop/.env
    desktop_env = f"""# {client_name} - 데스크톱 환경설정
SUPABASE_URL={supabase_url}
SUPABASE_ANON_KEY={supabase_anon_key}
"""
    with open(ROOT_DIR / "desktop" / ".env", "w", encoding="utf-8") as f:
        f.write(desktop_env)

    # 5. web/.env.local
    web_env = f"""# {client_name} - 웹 클라이언트 환경설정
NEXT_PUBLIC_SUPABASE_URL={supabase_url}
NEXT_PUBLIC_SUPABASE_ANON_KEY={supabase_anon_key}
"""
    with open(ROOT_DIR / "web" / ".env.local", "w", encoding="utf-8") as f:
        f.write(web_env)

    # 6. supabase/setup_new_client.sql 생성
    sql_content = f"""-- =========================================================
-- {client_name} ({category}) 신규 고객사 원클릭 DB 셋업 스크립트
-- 관리자 계정: {admin_email}
-- =========================================================

-- 1. 고객 테이블 (customers)
CREATE TABLE IF NOT EXISTS public.customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    gender VARCHAR(10) DEFAULT '여성',
    memo TEXT,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- 2. 시술/이용 내역 테이블 (treatments)
CREATE TABLE IF NOT EXISTS public.treatments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES public.customers(id) ON DELETE CASCADE,
    treatment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    menu VARCHAR(100) NOT NULL,
    price INTEGER NOT NULL DEFAULT 0,
    memo TEXT,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- 3. 빠른 검색을 위한 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_customers_phone ON public.customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_name ON public.customers(name);
CREATE INDEX IF NOT EXISTS idx_treatments_customer_id ON public.treatments(customer_id);

-- 4. RLS 활성화 및 권한 부여
ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.treatments ENABLE ROW LEVEL SECURITY;

GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;

DROP POLICY IF EXISTS "Allow authenticated full access to customers" ON public.customers;
CREATE POLICY "Allow authenticated full access to customers"
ON public.customers FOR ALL TO authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow authenticated full access to treatments" ON public.treatments;
CREATE POLICY "Allow authenticated full access to treatments"
ON public.treatments FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- 5. 관리자({admin_email}) 전용 회원가입 차단 트리거
CREATE OR REPLACE FUNCTION public.block_new_user_signup()
RETURNS TRIGGER AS $$
BEGIN
    -- 허용된 관리자 이메일만 가입 가능 (최초 가입 후 자동 차단)
    IF NEW.email = '{admin_email}' THEN
        RETURN NEW;
    END IF;
    RAISE EXCEPTION '신규 회원가입이 비활성화된 관리자 전용 시스템입니다.';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_signup_block ON auth.users;
CREATE TRIGGER on_auth_user_signup_block
BEFORE INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION public.block_new_user_signup();
"""
    sql_path = ROOT_DIR / "supabase" / "setup_new_client.sql"
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write(sql_content)

    print("\n" + "=" * 65)
    print(" 🎉 [설정 완료] 고객사 맞춤 템플릿 세팅이 완료되었습니다!")
    print("=" * 65)
    print(f" • 상호명: {logo_icon} {client_name} ({category})")
    print(f" • 대표색상: {primary_color}")
    print(f" • 관리자 이메일: {admin_email}")
    print(f" • SQL 스크립트: {sql_path.name} 생성 완료")
    print("\n🚀 [다음 납품 단계 가이드]")
    print(" 1. Supabase SQL 에디터에 'supabase/setup_new_client.sql' 실행 (1분)")
    print(" 2. PC 앱 빌드: 'cd desktop && build_exe.bat' 실행 (3분)")
    print(" 3. 웹 배포: 'cd web && npm run build && npx wrangler pages deploy out' (2분)")
    print("=" * 65)


if __name__ == "__main__":
    run_wizard()
