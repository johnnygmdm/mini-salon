# Mini Salon CRM (미니 미용실 고객·시술 관리 시스템)

단일 Supabase 백엔드를 공유하는 **[웹 앱(React + Next.js)]**과 **[Python PC 앱(PySide6)]** 2가지 클라이언트를 병렬로 개발한 Monorepo 프로젝트입니다.

## 프로젝트 구조

```text
mini-salon/
├── supabase/
│   └── schema.sql        # DB 테이블 및 RLS 보안 정책 정의 SQL
├── desktop/              # Python PySide6 기반 Windows 데스크톱 앱
│   ├── run.bat           # 데스크톱 앱 원클릭 실행기
│   ├── main.py
│   └── requirements.txt
├── web/                  # React + Next.js 기반 모바일·반응형 웹 앱
│   ├── run_web.bat       # 웹 로컬 개발서버 원클릭 실행기
│   ├── package.json
│   └── src/
├── .gitignore
├── .env
└── README.md
```

## 빠른 시작

### 1. Supabase 데이터베이스 설정
1. [Supabase](https://supabase.com) 프로젝트 생성
2. 대시보드의 **SQL Editor**로 이동
3. `supabase/schema.sql` 내용을 복사하여 실행 (테이블 생성 및 RLS 정책 자동 설정)
4. **Project Settings -> API**에서 `Project URL` 및 `anon public` 키 확인

### 2. 환경 변수 설정
`desktop/.env` 및 `web/.env` 파일 생성 후 각각 발급받은 URL과 Anon Key를 입력합니다.
*(주의: `service_role` 키는 절대 클라이언트에 입력하지 마세요!)*
