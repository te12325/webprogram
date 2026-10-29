import streamlit as st
import pandas as pd
import datetime
import calendar
import requests
from PIL import Image
from io import BytesIO
import base64
from github import Github, GithubException

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 디자인 (CSS) 적용
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="책 아지트",
    page_icon="📚",
    layout="wide"
)

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRound.woff');

    html, body, [class*="css"], div, span, label, input, button, textarea {
        font-family: 'NanumSquareRound', sans-serif !important;
    }

    .luxury-title {
        font-family: 'NanumSquareRound', sans-serif !important;
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        color: #4A3E3D !important;
        margin-bottom: 0px !important;
    }

    [data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type > div {
        background: linear-gradient(135deg, #FFE4E6 0%, #F3E8FF 50%, #E0E7FF 100%) !important;
        border-radius: 20px !important;
        border: 1px solid #F3D2DF !important;
        padding: 18px !important;
        box-shadow: 0 4px 15px rgba(243, 210, 223, 0.4) !important;
    }

    div.stButton > button {
        border-radius: 14px !important;
        font-weight: bold !important;
        border: none !important;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
    }

    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
        border-radius: 14px !important;
    }
    input, textarea {
        border-radius: 14px !important;
    }

    [data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border-radius: 20px !important;
    }

    button[data-baseweb="tab"] {
        border-radius: 16px 16px 0 0 !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        padding: 12px 24px !important;
    }

    img {
        border-radius: 14px !important;
    }

    .cal-day-box {
        background-color: #F8F9FA;
        border-radius: 12px;
        padding: 6px;
        min-height: 120px;
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
# 2. 세션 상태 초기화 및 Secrets 불러오기
# -----------------------------------------------------------------------------
if "my_books" not in st.session_state:
    st.session_state.my_books = []

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "profile_image" not in st.session_state:
    st.session_state.profile_image = None

try:
    KAKAO_API_KEY = st.secrets["KAKAO_API_KEY"]
except (KeyError, FileNotFoundError):
    KAKAO_API_KEY = ""

try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    GITHUB_REPO = st.secrets["GITHUB_REPO"]
except (KeyError, FileNotFoundError):
    GITHUB_TOKEN = ""
    GITHUB_REPO = ""


# -----------------------------------------------------------------------------
# 3. 깃허브 파일 연동 함수 (회원가입 정보 저장/불러오기)
# -----------------------------------------------------------------------------
USERS_FILE_PATH = "users.csv"

def load_users_from_github():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return pd.DataFrame(columns=["username", "password"])
    
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        file_content = repo.get_contents(USERS_FILE_PATH)
        decoded_data = base64.b64decode(file_content.content).decode("utf-8")
        from io import StringIO
        df = pd.read_csv(StringIO(decoded_data))
        return df
    except Exception:
        return pd.DataFrame(columns=["username", "password"])

def save_user_to_github(username, password):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return False, "깃허브 설정이 되어있지 않습니다."
    
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        
        df = load_users_from_github()
        
        if not df.empty and username in df["username"].values:
            return False, "이미 존재하는 아이디입니다."
        
        new_row = pd.DataFrame([[username, password]], columns=["username", "password"])
        df = pd
