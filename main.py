import streamlit as st
import pandas as pd
import datetime
import calendar
import requests
from PIL import Image
from io import BytesIO

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 디자인 (CSS) 적용
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="책 아지트",
    page_icon="📚",
    layout="wide"
)

# 나눔스퀘어라운드 폰트 적용 및 파스텔톤 스타일 정의
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRound.woff');

    /* 전체 앱 기본 글꼴 설정 */
    html, body, [class*="css"], div, span, label, input, button, textarea {
        font-family: 'NanumSquareRound', sans-serif !important;
    }

    /* 메인 타이틀 스타일 */
    .luxury-title {
        font-family: 'NanumSquareRound', sans-serif !important;
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        color: #4A3E3D !important;
        margin-bottom: 0px !important;
    }

    /* 사이드바 프로필 상자 그라데이션 및 디자인 */
    [data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type > div {
        background: linear-gradient(135deg, #FFE4E6 0%, #F3E8FF 50%, #E0E7FF 100%) !important;
        border-radius: 20px !important;
        border: 1px solid #F3D2DF !important;
        padding: 18px !important;
        box-shadow: 0 4px 15px rgba(243, 210, 223, 0.4) !important;
    }

    /* 모든 버튼의 모서리를 둥글게 설정 */
    div.stButton > button {
        border-radius: 14px !important;
        font-weight: bold !important;
        border: none !important;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
    }

    /* 입력창 모서리 둥글게 설정 */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
        border-radius: 14px !important;
    }
    input, textarea {
        border-radius: 14px !important;
    }

    /* 카드형 컨테이너 모서리 둥글게 설정 */
    [data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border-radius: 20px !important;
    }

    /* 상단 페이지 전환 탭 스타일 */
    button[data-baseweb="tab"] {
        border-radius: 16px 16px 0 0 !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        padding: 12px 24px !important;
    }

    /* 이미지 모서리 둥글게 설정 */
    img {
        border-radius: 14px !important;
    }

    /* 캘린더 날짜 상자 스타일 */
    .cal-day-box {
        background-color: #F8F9FA;
        border-radius: 12px;
        padding: 6px;
        min-height: 110px;
        border: 1px solid #E9ECEF;
    }
    .cal-day-num {
        font-weight: bold;
        font-size: 0.9rem;
        color: #495057;
        margin-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. 세션 상태(Session State) 초기화 및 API 키 불러오기
# -----------------------------------------------------------------------------
if "my_books" not in st.session_state:
    st.session_state.my_books = []

if "active_book_id" not in st.session_state:
    st.session_state.active_book_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "profile_image" not in st.session_state:
    st.session_state.profile_image = None

# Streamlit Secrets에서 카카오 API 키 안전하게 가져오기
try:
    KAKAO_API_KEY = st.secrets["KAKAO_API_KEY"]
except (KeyError, FileNotFoundError):
    KAKAO_API_KEY = ""


# -----------------------------------------------------------------------------
# 3. 초기 화면: 사용자 이름 입력 또는 게스트 입장
# -----------------------------------------------------------------------------
if not st.session_state.user_name:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        with st.container(border=True):
            st.markdown('<div class="luxury-title" style="text-align: center;">📚 나만의 책 아지트</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("아지트에서 사용하실 이름을 입력해 주세요.")
            
            input_name = st.text_input("이름 또는 닉네임 입력", placeholder="닉네임을 입력하세요", label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("책 아지트 입장하기 🚀", use_container_width=True):
                if input_name.strip():
                    st.session_state.user_name = input_name.strip()
                    st.rerun()
                else:
                    st.warning("이름을 입력해 주세요!")
            
            if st.button("🙋‍♂️ 게스트로 입장하기", use_container_width=True, type="secondary"):
                st.session_state.user_name = "게스트"
                st.rerun()

    st.stop()


# -----------------------------------------------------------------------------
# 4. 유틸리티 함수 정의
# -----------------------------------------------------------------------------

def search_book_kakao(query):
    """카카오 API를 통해 책 제목으로 검색하고 실제 표지 이미지와 데이터를 가져옵니다."""
    if not KAKAO_API_KEY:
        return [{
            "title": f"[API키 미설정] {query}",
            "authors": ["설정 확인 필요"],
            "thumbnail": "https://via.placeholder.com/150x200.png?text=No+API+Key",
            "total_pages": 300
        }]
    
    url = f"https://dapi.kakao.com/v3/search/book?query={query}"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            results = response.json().get("documents", [])
            books = []
            for item in results:
                books.
