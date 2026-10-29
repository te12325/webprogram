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
        df = pd.concat([df, new_row], ignore_index=True)
        csv_data = df.to_csv(index=False)
        
        try:
            file = repo.get_contents(USERS_FILE_PATH)
            repo.update_file(
                USERS_FILE_PATH, 
                f"Add new user: {username}", 
                csv_data, 
                file.sha
            )
        except Exception:
            repo.create_file(
                USERS_FILE_PATH, 
                f"Create {USERS_FILE_PATH}", 
                csv_data
            )
        return True, "회원가입이 완료되었습니다!"
    except Exception as e:
        return False, f"오류 발생: {e}"


# -----------------------------------------------------------------------------
# 4. 로그인 및 회원가입 화면
# -----------------------------------------------------------------------------
if not st.session_state.user_name:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        with st.container(border=True):
            st.markdown('<div class="luxury-title" style="text-align: center;">📚 책 아지트</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            auth_tab1, auth_tab2, auth_tab3 = st.tabs(["로그인", "회원가입", "게스트 입장"])
            
            with auth_tab1:
                st.write("계정으로 로그인하세요.")
                login_id = st.text_input("아이디", key="login_id")
                login_pw = st.text_input("비밀번호", type="password", key="login_pw")
                
                if st.button("로그인하기 🚀", use_container_width=True):
                    users_df = load_users_from_github()
                    if users_df.empty:
                        st.error("등록된 회원이 없거나 깃허브 연결을 확인해 주세요.")
                    else:
                        match = users_df[(users_df["username"] == login_id) & (users_df["password"] == login_pw)]
                        if not match.empty:
                            st.session_state.user_name = login_id
                            st.success(f"환영합니다, {login_id}님!")
                            st.rerun()
                        else:
                            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
            
            with auth_tab2:
                st.write("새로운 계정을 만드세요 (깃허브에 저장됩니다).")
                reg_id = st.text_input("사용할 아이디", key="reg_id")
                reg_pw = st.text_input("사용할 비밀번호", type="password", key="reg_pw")
                
                if st.button("회원가입 완료 ✨", use_container_width=True):
                    if reg_id.strip() and reg_pw.strip():
                        success, msg = save_user_to_github(reg_id.strip(), reg_pw.strip())
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.warning("아이디와 비밀번호를 모두 입력해 주세요!")
            
            with auth_tab3:
                st.write("로그인 없이 간편하게 체험해보세요.")
                if st.button("🙋‍♂️ 게스트로 입장하기", use_container_width=True, type="secondary"):
                    st.session_state.user_name = "게스트"
                    st.rerun()

    st.stop()


# -----------------------------------------------------------------------------
# 5. 유틸리티 함수 정의 (도서 검색 및 별점)
# -----------------------------------------------------------------------------
def search_book_kakao(query):
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
                books.append({
                    "title": item.get("title", "제목 없음"),
                    "authors": item.get("authors", ["저자 미상"]),
                    "thumbnail": item.get("thumbnail", "https://via.placeholder.com/150x200.png?text=No+Cover"),
                    "total_pages": 300
                })
            return books
    except Exception as e:
        st.error(f"도서 검색 중 오류가 발생했습니다: {e}")
    return []

def render_star_rating(rating):
    full_stars = int(rating)
    has_half = (rating - full_stars) >= 0.5
    empty_stars = 5 - full_stars - (1 if has_half else 0)
    
    stars_str = "★" * full_stars + ("✨" if has_half else "") + "☆" * empty_stars
    return f"{stars_str} ({rating}/5.0)"


# -----------------------------------------------------------------------------
# 6. 사이드바 영역 (프로필 설정 및 책 등록)
# -----------------------------------------------------------------------------
with st.sidebar:
    with st.container(border=True):
        st.markdown(f'<h3 style="margin-top:0; color:#4A3E3D; font-size:1.2rem;">👤 {st.session_state.user_name}</h3>', unsafe_allow_html=True)
        
        if st.button("로그아웃 🚪", use_container_width=True):
            st.session_state.user_name = ""
            st.rerun()

        new_profile = st.file_uploader("프로필 사진 등록/변경", type=["png", "jpg", "jpeg"], key="side_profile")
        if new_profile is not None:
            st.session_state.profile_image = new_profile.getvalue()

    st.divider()

    st.header("📖 책 등록하기")
    search_term = st.text_input("책 제목을 검색하세요")

    if search_term:
        search_results = search_book_kakao(search_term)
        
        if search_results:
            selected_book = st.selectbox(
                "검색 결과에서 책을 선택하세요:",
                search_results,
                format_func=lambda x: f"{x['title']} ({', '.join(x['authors'])})"
            )
            
            with st.form("add_book_form"):
                st.write(f"**선택한 책:** {selected_book['title']}")
                
                total_pages = st.number_input("전체 페이지 수", min_value=1, value=300, step=10)
                target_date = st.date_input("목표 완료일", datetime.date.today() + datetime.timedelta(days=14))
                status = st.selectbox("독서 상태", ["읽는 중", "읽기 완료", "위시리스트"])
                
                completed_date_input = datetime.date.today()
                if status == "읽기 완료":
                    completed_date_input = st.date_input("완독한 날짜 선택", datetime.date.today())
                
                initial_rating = 5.0
                if status == "읽기 완료":
                    rating_options = [i / 2 for i in range(1, 11)]
                    initial_rating = st.select_slider("별점 평점 선택", options=rating_options, value=5.0)

                submit_button = st.form_submit_button("내 책장에 추가")
                
                if submit_button:
                    is_duplicate = any(
                        b["title"] == selected_book["title"] and b["status"] == status
                        for b in st.session_state.my_books
                    )
                    
                    if is_duplicate:
                        st.warning(f"⚠️ 이미 [{status}]에 추가된 책입니다!")
                    else:
                        comp_date_str = completed_date_input.strftime("%Y-%m-%d") if status == "읽기 완료" else None
                        new_book = {
                            "id": len(st.session_state.my_books) + 1,
                            "title": selected_book["title"],
                            "author": ", ".join(selected_book["authors"]),
                            "cover_url": selected_book["thumbnail"],
                            "total_pages": total_pages,
                            "current_page": total_pages if status == "읽기 완료" else 0,
                            "target_date": target_date,
                            "status": status,
                            "rating": initial_rating if status == "읽기 완료" else 0.
