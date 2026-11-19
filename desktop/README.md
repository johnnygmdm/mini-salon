# Mini Salon PC Desktop App (PySide6)

미니 미용실 고객 및 1:N 시술 내역 통합 관리 데스크톱 애플리케이션입니다.
단일 Supabase 백엔드와 연동되며, Row Level Security(RLS) 정책에 따라 인증된 미용사 본인의 데이터만 안전하게 관리합니다.

## 주요 기능

1. **사용자 인증 (Supabase Auth)**
   - 이메일/비밀번호 기반 로그인 및 회원가입
   - 로컬 세션 캐싱(`.session.json`)을 통한 자동 로그인 지원
   - 사용자 계정 정보 표시 및 로그아웃

2. **고객 관리 (Customers)**
   - 고객 목록 조회 및 실시간 검색 (고객명, 연락처 디바운스 검색)
   - 신규 고객 등록 (고객명, 연락처 자동 하이픈 포맷팅, 특이사항/메모)
   - 고객 정보 수정 (더블 클릭 또는 수정 버튼)
   - 고객 삭제 (연관된 모든 시술 내역 CASCADE 자동 삭제 및 안전 경고 다이얼로그)

3. **시술 내역 관리 (Treatments - 1:N)**
   - 마스터-디테일 분할 레이아웃 (QSplitter)
   - 고객 선택 시 실시간 통계 계산 (총 방문 횟수, 누적 시술 금액, 최근 시술 일자)
   - 신규 시술 등록 (자주 쓰는 시술 항목 추천 드롭다운, 시술 금액 천단위 구분, 달력 팝업)
   - 시술 내역 삭제 (개별 삭제 및 통계 즉시 갱신)

4. **모던 UI/UX**
   - 세련된 인디고/슬레이트 테마 (QSS 스타일시트)
   - 상태 바(QStatusBar) 실시간 작업 알림
   - 고해상도(Hi-DPI) 모니터 지원

---

## 실행 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`desktop/.env.example`을 복사하여 `desktop/.env`를 생성하고 Supabase 프로젝트 정보를 입력합니다:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 3. 애플리케이션 실행
```bash
python main.py
```
