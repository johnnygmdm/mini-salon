"""
Mini Salon Desktop App - QSS 현대적 스타일시트 (동적 브랜드 테마 지원)
"""

from config import BRAND_COLORS

PRIMARY = BRAND_COLORS.get("primary", "#4f46e5")
PRIMARY_HOVER = BRAND_COLORS.get("primaryHover", "#4338ca")
PRIMARY_LIGHT = BRAND_COLORS.get("primaryLight", "#eef2ff")
PRIMARY_BORDER = BRAND_COLORS.get("primaryBorder", "#c7d2fe")
TEXT_ON_PRIMARY = BRAND_COLORS.get("textOnPrimary", "#ffffff")

APP_STYLESHEET = f"""
/* 기본 위젯 스타일 */
QWidget {{
    font-family: 'Segoe UI', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
    font-size: 13px;
    color: #1e293b;
    background-color: #f8fafc;
}}

/* 메인 윈도우 배경 */
QMainWindow {{
    background-color: #f1f5f9;
}}

/* 카드 / 패널 프레임 */
QFrame#cardFrame {{
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px;
}}

QFrame#detailHeaderFrame {{
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 18px;
}}

/* 제목 레이블 */
QLabel#titleLabel {{
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.5px;
}}

QLabel#subtitleLabel {{
    font-size: 13px;
    color: #64748b;
}}

QLabel#cardTitle {{
    font-size: 16px;
    font-weight: 600;
    color: #1e293b;
}}

QLabel#statValue {{
    font-size: 22px;
    font-weight: 700;
    color: {PRIMARY};
}}

QLabel#statLabel {{
    font-size: 12px;
    font-weight: 500;
    color: #64748b;
}}

/* 입력 필드 */
QLineEdit, QTextEdit, QDateEdit, QSpinBox {{
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #0f172a;
    selection-background-color: {PRIMARY};
}}

QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QSpinBox:focus {{
    border: 1.5px solid {PRIMARY};
    background-color: #ffffff;
}}

QLineEdit:hover, QTextEdit:hover, QDateEdit:hover, QSpinBox:hover {{
    border-color: #94a3b8;
}}

/* 버튼 기본 스타일 */
QPushButton {{
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
    color: #334155;
}}

QPushButton:hover {{
    background-color: #f1f5f9;
    border-color: #94a3b8;
    color: #0f172a;
}}

QPushButton:pressed {{
    background-color: #e2e8f0;
}}

QPushButton:disabled {{
    background-color: #f8fafc;
    border-color: #e2e8f0;
    color: #94a3b8;
}}

/* 프라이머리 버튼 (주요 행동: 등록, 저장, 로그인 등) */
QPushButton#primaryBtn {{
    background-color: {PRIMARY};
    border: 1px solid {PRIMARY_HOVER};
    color: {TEXT_ON_PRIMARY};
}}

QPushButton#primaryBtn:hover {{
    background-color: {PRIMARY_HOVER};
}}

QPushButton#primaryBtn:pressed {{
    background-color: {PRIMARY_HOVER};
}}

/* 성공/보조 액션 버튼 */
QPushButton#successBtn {{
    background-color: #059669;
    border: 1px solid #047857;
    color: #ffffff;
}}

QPushButton#successBtn:hover {{
    background-color: #047857;
}}

/* 위험/삭제 버튼 */
QPushButton#dangerBtn {{
    background-color: #ffffff;
    border: 1px solid #fca5a5;
    color: #dc2626;
}}

QPushButton#dangerBtn:hover {{
    background-color: #fef2f2;
    border-color: #f87171;
    color: #b91c1c;
}}

QPushButton#dangerBtn:pressed {{
    background-color: #fee2e2;
}}

/* 테이블 위젯 */
QTableWidget {{
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #f1f5f9;
    selection-background-color: {PRIMARY_LIGHT};
    selection-color: #0f172a;
    outline: none;
}}

QTableWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid #f1f5f9;
}}

QTableWidget::item:selected {{
    background-color: {PRIMARY_LIGHT};
    color: #0f172a;
    font-weight: 600;
}}

QTableWidget::item:hover:!selected {{
    background-color: #f8fafc;
}}

/* 테이블 헤더 */
QHeaderView::section {{
    background-color: #f8fafc;
    color: #475569;
    padding: 10px 12px;
    font-size: 12px;
    font-weight: 700;
    border: none;
    border-bottom: 2px solid #e2e8f0;
}}

/* 스플리터 */
QSplitter::handle {{
    background-color: #cbd5e1;
    width: 2px;
}}

QSplitter::handle:hover {{
    background-color: {PRIMARY};
}}

/* 스크롤바 */
QScrollBar:vertical {{
    border: none;
    background: #f1f5f9;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: #cbd5e1;
    min-height: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: #94a3b8;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* 탭 위젯 */
QTabWidget::pane {{
    border: 1px solid #e2e8f0;
    background-color: #ffffff;
    border-radius: 8px;
}}

QTabBar::tab {{
    background-color: #f1f5f9;
    color: #64748b;
    padding: 10px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    background-color: #ffffff;
    color: {PRIMARY};
    border-bottom: 2px solid {PRIMARY};
}}

/* 상태 바 */
QStatusBar {{
    background-color: #ffffff;
    border-top: 1px solid #e2e8f0;
    color: #64748b;
    font-size: 12px;
    padding: 4px 12px;
}}

/* 툴바/헤더 */
QToolBar {{
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 6px 12px;
    spacing: 10px;
}}
"""
