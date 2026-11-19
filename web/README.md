# Mini Salon Web Client (React + Next.js)

미니 미용실 고객 및 1:N 시술 내역 통합 관리 모바일·반응형 웹 애플리케이션입니다.
Python PC 데스크톱 앱과 동일한 Supabase 백엔드를 실시간 공유합니다.

## 기술 스택
- **Framework**: Next.js 14 (App Router, React 18)
- **Styling**: Tailwind CSS (모바일/태블릿/PC 완벽 반응형)
- **Icons**: Lucide React
- **Database / Auth**: Supabase JS Client (`@supabase/supabase-js`)

---

## 로컬 실행 방법

### 1. 패키지 설치 (이미 완료됨)
```bash
npm install
```

### 2. 개발 서버 실행
더블 클릭으로 `run_web.bat`을 실행하거나 터미널에서:
```bash
npm run dev
```
브라우저에서 `http://localhost:3000` 접속

---

## 클라우드 무료 배포 방법

### 방법 A: Vercel 배포 (가장 추천 & 1분 소요)
1. GitHub 저장소에 이 프로젝트를 푸시합니다.
2. [Vercel](https://vercel.com)에 로그인 후 **Add New Project**를 클릭합니다.
3. Root Directory를 `web`으로 설정합니다.
4. **Environment Variables**에 아래 2개를 등록하고 **Deploy**를 누릅니다:
   - `NEXT_PUBLIC_SUPABASE_URL`: `https://plfgpjvqctkynqpzvobz.supabase.co`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: `sb_publishable_FhOIW0yO-BfGg5BC1hbnqQ_q0NMVO1D`
5. 배포 완료 즉시 나만의 전용 웹 주소(`https://mini-salon-xxx.vercel.app`)가 생성되어 스마트폰에서 바로 사용하실 수 있습니다!

### 방법 B: Cloudflare Pages 배포
1. Cloudflare Dashboard -> **Compute (Workers & Pages)** -> **Create application** -> **Pages**
2. GitHub 저장소 연결
3. Build setting:
   - Framework preset: `Next.js`
   - Root directory: `web`
   - Environment variables 등록
