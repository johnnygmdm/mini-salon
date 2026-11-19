# Mini Salon Web Client (React + Next.js)

미니 미용실 고객 및 1:N 시술 내역 통합 관리 모바일·반응형 웹 애플리케이션입니다.
Python PC 데스크톱 앱과 동일한 Supabase 백엔드를 실시간 공유합니다.

## 기술 스택
- **Framework**: Next.js 14 (App Router, React 18, Static HTML Export)
- **Styling**: Tailwind CSS (모바일/태블릿/PC 완벽 반응형)
- **Icons**: Lucide React
- **Hosting**: Cloudflare Pages (무료 무제한 CDN 호스팅)
- **Database / Auth**: Supabase JS Client (`@supabase/supabase-js`)

---

## 로컬 실행 방법

더블 클릭으로 `run_web.bat`을 실행하거나 터미널에서:
```bash
npm run dev
```
브라우저에서 `http://localhost:3000` 접속

---

## Cloudflare Pages 무료 배포 방법

### 방법 A: Cloudflare 대시보드에서 `out` 폴더 드래그 앤 드롭 (가장 쉽고 추천! 10초 완료)
1. 터미널에서 `npm run build`를 실행합니다. (이미 `web/out` 폴더 생성 완료)
2. [Cloudflare 대시보드](https://dash.cloudflare.com) 로그인
3. 좌측 메뉴 **Workers & Pages** -> **Create application** -> **Pages** 탭 클릭
4. **Upload assets (자산 업로드)** 선택
5. 프로젝트 이름: `mini-salon` 입력
6. 탐색기에서 `C:\project\mini-salon\web\out` 폴더를 화면에 **드래그 앤 드롭** 후 **Deploy site** 클릭!
7. 즉시 `https://mini-salon-xxx.pages.dev` 무료 주소 발급 완료!

### 방법 B: CLI 마법사 (`deploy_cloudflare.bat`) 실행
- `web/deploy_cloudflare.bat` 더블 클릭 ➡️ Cloudflare 로그인 승인 ➡️ 자동 배포 완료!
