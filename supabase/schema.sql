-- ==============================================================================
-- Mini Salon CRM (미니 미용실 고객·시술 관리 시스템)
-- Supabase PostgreSQL Schema & Row Level Security (RLS) Policies
-- ==============================================================================

-- 1. 확장 기능 활성화 (UUID 생성용)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. 고객 테이블 (customers)
CREATE TABLE IF NOT EXISTS public.customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE DEFAULT auth.uid(),
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    memo TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 고객 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_customers_user_id ON public.customers(user_id);
CREATE INDEX IF NOT EXISTS idx_customers_name ON public.customers(name);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON public.customers(phone);

-- 3. 시술 내역 테이블 (treatments)
CREATE TABLE IF NOT EXISTS public.treatments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE DEFAULT auth.uid(),
    customer_id UUID NOT NULL REFERENCES public.customers(id) ON DELETE CASCADE,
    service_name TEXT NOT NULL,
    price INTEGER NOT NULL DEFAULT 0,
    treated_at DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 시술 내역 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_treatments_user_id ON public.treatments(user_id);
CREATE INDEX IF NOT EXISTS idx_treatments_customer_id ON public.treatments(customer_id);
CREATE INDEX IF NOT EXISTS idx_treatments_treated_at ON public.treatments(treated_at DESC);

-- ==============================================================================
-- 4. RLS (Row Level Security) 설정 및 보안 정책
-- ==============================================================================

-- RLS 활성화
ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.treatments ENABLE ROW LEVEL SECURITY;

-- ------------------------------------------------------------------------------
-- customers RLS 정책: 본인(auth.uid() = user_id)의 데이터만 CRUD 허용
-- ------------------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view their own customers" ON public.customers;
CREATE POLICY "Users can view their own customers"
    ON public.customers
    FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert their own customers" ON public.customers;
CREATE POLICY "Users can insert their own customers"
    ON public.customers
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own customers" ON public.customers;
CREATE POLICY "Users can update their own customers"
    ON public.customers
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own customers" ON public.customers;
CREATE POLICY "Users can delete their own customers"
    ON public.customers
    FOR DELETE
    USING (auth.uid() = user_id);

-- ------------------------------------------------------------------------------
-- treatments RLS 정책: 본인(auth.uid() = user_id)의 데이터만 CRUD 허용
-- ------------------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view their own treatments" ON public.treatments;
CREATE POLICY "Users can view their own treatments"
    ON public.treatments
    FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert their own treatments" ON public.treatments;
CREATE POLICY "Users can insert their own treatments"
    ON public.treatments
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own treatments" ON public.treatments;
CREATE POLICY "Users can update their own treatments"
    ON public.treatments
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own treatments" ON public.treatments;
CREATE POLICY "Users can delete their own treatments"
    ON public.treatments
    FOR DELETE
    USING (auth.uid() = user_id);

-- ==============================================================================
-- 7. Supabase API (PostgREST) 권한 부여
-- ==============================================================================
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL ROUTINES IN SCHEMA public TO anon, authenticated, service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON ROUTINES TO anon, authenticated, service_role;

