import streamlit as st
import pandas as pd
import datetime
import calendar
import requests
from PIL import Image
from io import BytesIO, StringIO
import base64
from github import Github, GithubException

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 디자인 (감성 북카페 스타일 CSS) 적용
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="책 아지트",
    page_icon="📚",
    layout="wide"
)

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    html, body, [class*="css"], div, span, label, input, button, textarea {
        font-family: 'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
    }

    .stApp {
        background-color: #FAF7F2 !important;
    }

    .luxury-title {
        font-family: 'Pretendard Variable', Pretendard, sans-serif !important;
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        color: #5C4B43 !important;
        margin-bottom: 0px !important;
        letter-spacing: -0.5px;
    }

    [data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type > div {
        background: linear-gradient(135deg, #FDFBF7 0%, #F4ECE1 100%) !important;
        border-radius: 24px !important;
        border: 1px solid #E6DCD0 !important;
        padding: 22px !important;
        box-shadow: 0 6px 20px rgba(92, 75, 67, 0.06) !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF !important;
        border-radius: 20px !important;
        border: 1px solid #EFECE6 !important;
        padding: 16px !important;
        box-shadow: 0 4px 12px rgba(92, 75, 67, 0.04) !important;
        text-align: center !important;
    }

    div.stButton > button {
        background-color: #8C7A6B !important;
        color: #FFFFFF !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 3px 8px rgba(140, 122, 107, 0.2);
    }
    div.stButton > button:hover {
        background-color: #7A695B !important;
        transform: translateY(-2px);
    }

    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
        border-radius: 16px !important;
        border-color: #E6DCD0 !important;
    }
    input, textarea {
        border-radius: 16px !important;
        background-color: #FCFBF9 !important;
    }

    [data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border-radius: 24px !important;
        border: 1px solid #EFECE6 !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(92, 75, 67, 0.04) !important;
    }

    button[data-baseweb="tab"] {
        border-radius: 14px 14px 0 0 !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #7A695B !important;
        padding: 12px 24px !important;
    }

    img {
        border-radius: 4px !important;
    }

    /* 다이어리 날짜 칸 스타일 */
    .diary-cell {
        background-color: #FFFFFF;
        border: 1.5px solid #5C4B43;
        border-radius: 6px;
        padding: 4px;
        min-height: 75px;
        text-align: center;
        margin-bottom: 4px;
    }
    .diary-day-num {
        font-weight: 700;
        font-size: 0.75rem;
        color: #6D5C52;
        text-align: left;
        padding-left: 2px;
        margin-bottom: 2px;
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

if "show_login_pw" not in st.session_state:
    st.session_state.show_login_pw = False

if "show_reg_pw" not in st.session_state:
    st.session_state.show_reg_pw = False

if "cal_year" not in st.session_state:
    st.session_state.cal_year = datetime.date.today().year

if "cal_month" not in st.session_state:
    st.session_state.cal_month = datetime.date.today().month

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
# 3. 깃허브 파일 연동 함수 (회원 정보 및 도서 데이터 저장/불러오기)
# -----------------------------------------------------------------------------
USERS_FILE_PATH = "users.csv"
BOOKS_FILE_PATH = "user_books.csv"

def load_users_from_github():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return pd.DataFrame(columns=["username", "password"])
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        file_content = repo.get_contents(USERS_FILE_PATH)
        decoded_data = base64.b64decode(file_content.content).decode("utf-8")
        return pd.read_csv(StringIO(decoded_data))
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
            repo.update_file(USERS_FILE_PATH, f"Add user: {username}", csv_data, file.sha)
        except Exception:
            repo.create_file(USERS_FILE_PATH, f"Create {USERS_FILE_PATH}", csv_data)
        return True, "회원가입이 완료되었습니다!"
    except Exception as e:
        return False, f"오류 발생: {e}"

def load_books_for_user(username):
    if not GITHUB_TOKEN or not GITHUB_REPO or username == "게스트":
        return []
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        file_content = repo.get_contents(BOOKS_FILE_PATH)
        decoded_data = base64.b64decode(file_content.content).decode("utf-8")
        df = pd.read_csv(StringIO(decoded_data))
        
        user_df = df[df["username"] == username]
        books = []
        for _, row in user_df.iterrows():
            books.append({
                "id": int(row["id"]),
                "title": row["title"],
                "author": row["author"],
                "cover_url": row["cover_url"],
                "total_pages": int(row["total_pages"]),
                "current_page": int(row["current_page"]),
                "target_date": row["target_date"],
                "status": row["status"],
                "rating": float(row["rating"]),
                "notes": str(row["notes"]) if pd.notna(row["notes"]) else "",
                "completed_date": row["completed_date"] if pd.notna(row["completed_date"]) else None
            })
        return books
    except Exception:
        return []

def save_books_for_user(username, books):
    if not GITHUB_TOKEN or not GITHUB_REPO or username == "게스트":
        return
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        
        try:
            file_content = repo.get_contents(BOOKS_FILE_PATH)
            decoded_data = base64.b64decode(file_content.content).decode("utf-8")
            df = pd.read_csv(StringIO(decoded_data))
        except Exception:
            df = pd.DataFrame(columns=["username", "id", "title", "author", "cover_url", "total_pages", "current_page", "target_date", "status", "rating", "notes", "completed_date"])
        
        df = df[df["username"] != username]
        
        new_rows = []
        for b in books:
            new_rows.append({
                "username": username,
                "id": b["id"],
                "title": b["title"],
                "author": b["author"],
                "cover_url": b["cover_url"],
                "total_pages": b["total_pages"],
                "current_page": b["current_page"],
                "target_date": b["target_date"],
                "status": b["status"],
                "rating": b["rating"],
                "notes": b["notes"],
                "completed_date": b["completed_date"]
            })
        
        if new_rows:
            new_df = pd.DataFrame(new_rows)
            df = pd.concat([df, new_df], ignore_index=True)
            
        csv_data = df.to_csv(index=False)
        
        try:
            file = repo.get_contents(BOOKS_FILE_PATH)
            repo.update_file(BOOKS_FILE_PATH, f"Update books for {username}", csv_data, file.sha)
        except Exception:
            repo.create_file(BOOKS_FILE_PATH, f"Create {BOOKS_FILE_PATH}", csv_data)
    except Exception as e:
        st.error(f"데이터 저장 중 오류 발생: {e}")


# -----------------------------------------------------------------------------
# 4. 로그인 및 회원가입 화면
# -----------------------------------------------------------------------------
if not st.session_state.user_name:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        with st.container(border=True):
            st.markdown('<div class="luxury-title" style="text-align: center;">📖 책 아지트 ✨</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            auth_tab1, auth_tab2, auth_tab3 = st.tabs(["로그인", "회원가입", "게스트 입장"])
            
            with auth_tab1:
                st.write("🌱 아지트 계정으로 로그인하세요.")
                login_id = st.text_input("아이디", key="login_id")
                
                pw_col1, pw_col2 = st.columns([4, 1])
                with pw_col1:
                    login_pw = st.text_input(
                        "비밀번호", 
                        type="default" if st.session_state.show_login_pw else "password", 
                        key="login_pw"
                    )
                with pw_col2:
                    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                    text_eye = "[ 👀 ]" if st.session_state.show_login_pw else "[ 🙈 ]"
                    if st.button(text_eye, key="toggle_login_eye"):
                        st.session_state.show_login_pw = not st.session_state.show_login_pw
                        st.rerun()
                
                if st.button("로그인하기 ☕", use_container_width=True):
                    users_df = load_users_from_github()
                    if users_df.empty:
                        st.error("등록된 회원이 없거나 깃허브 연결을 확인해 주세요.")
                    else:
                        match = users_df[(users_df["username"] == login_id) & (users_df["password"] == login_pw)]
                        if not match.empty:
                            st.session_state.user_name = login_id
                            st.session_state.my_books = load_books_for_user(login_id)
                            st.success(f"환영합니다, {login_id}님! ✨")
                            st.rerun()
                        else:
                            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
            
            with auth_tab2:
                st.write("🌿 새로운 아지트 계정을 만드세요.")
                reg_id = st.text_input("사용할 아이디", key="reg_id")
                
                reg_pw_col1, reg_pw_col2 = st.columns([4, 1])
                with reg_pw_col1:
                    reg_pw = st.text_input(
                        "사용할 비밀번호", 
                        type="default" if st.session_state.show_reg_pw else "password", 
                        key="reg_pw"
                    )
                with reg_pw_col2:
                    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                    text_reg_eye = "[ 👀 ]" if st.session_state.show_reg_pw else "[ 🙈 ]"
                    if st.button(text_reg_eye, key="toggle_reg_eye"):
                        st.session_state.show_reg_pw = not st.session_state.show_reg_pw
                        st.rerun()
                
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
                st.write("☕ 로그인 없이 편안하게 체험해 보세요.")
                if st.button("🛋️ 게스트로 입장하기", use_container_width=True, type="secondary"):
                    st.session_state.user_name = "게스트"
                    st.session_state.my_books = []
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
        st.markdown(f'<h3 style="margin-top:0; color:#5C4B43; font-size:1.2rem;">🌱 프로필 설정</h3>', unsafe_allow_html=True)
        
        new_name = st.text_input("이름(닉네임) 수정", value=st.session_state.user_name)
        if new_name != st.session_state.user_name and new_name.strip():
            st.session_state.user_name = new_name.strip()
            st.rerun()

        new_profile = st.file_uploader("프로필 사진 등록/변경", type=["png", "jpg", "jpeg"], key="side_profile")
        if new_profile is not None:
            st.session_state.profile_image = new_profile.getvalue()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("로그아웃 🚪", use_container_width=True):
            st.session_state.user_name = ""
            st.session_state.my_books = []
            st.rerun()

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

                submit_button = st.form_submit_button("내 아지트에 추가 ✨")
                
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
                            "target_date": str(target_date),
                            "status": status,
                            "rating": initial_rating if status == "읽기 완료" else 0.0,
                            "notes": "",
                            "completed_date": comp_date_str
                        }
                        st.session_state.my_books.append(new_book)
                        save_books_for_user(st.session_state.user_name, st.session_state.my_books)
                        st.success(f"🌱 '{selected_book['title']}' 책이 아지트에 추가되었습니다!")
        else:
            st.warning("검색 결과가 없습니다.")


# -----------------------------------------------------------------------------
# 7. 도서 상세정보 및 삭제 팝업 모달
# -----------------------------------------------------------------------------
@st.dialog("☕ 도서 상세 및 기록 관리")
def show_book_details(book):
    st.image(book["cover_url"], width=150)
    st.subheader(book["title"])
    st.caption(f"저자: {book['author']} | 전체 {book['total_pages']}p")
    st.divider()

    RATING_OPTIONS = [i / 2 for i in range(1, 11)]

    if book["status"] == "읽는 중":
        progress = min(book["current_page"] / book["total_pages"], 1.0)
        st.progress(progress, text=f"진행률: {int(progress * 100)}%")
        
        new_page = st.number_input(
            "현재 읽은 페이지 입력", 
            min_value=0, 
            max_value=book["total_pages"], 
            value=book["current_page"],
            key=f"modal_page_{book['id']}"
        )
        
        completion_date = st.date_input("완독한 날짜", datetime.date.today(), key=f"modal_comp_date_{book['id']}")

        if st.button("페이지 저장 📝", key=f"modal_save_page_{book['id']}"):
            book["current_page"] = new_page
            if new_page >= book["total_pages"]:
                book["status"] = "읽기 완료"
                book["completed_date"] = completion_date.strftime("%Y-%m-%d")
                st.balloons()
                st.success("🎉 축하합니다! 완독하셨습니다!")
            save_books_for_user(st.session_state.user_name, st.session_state.my_books)
            st.rerun()

    elif book["status"] == "읽기 완료":
        st.success(f"🎉 완독한 책입니다! (완독일: {book.get('completed_date', '미기재')})")
        current_rating = book.get("rating", 5.0) or 5.0
        st.write(f"**내 평점:** {render_star_rating(current_rating)}")
        
        new_rating = st.select_slider(
            "평점 수정 (0.5 단위)",
            options=RATING_OPTIONS,
            value=current_rating,
            key=f"modal_rating_{book['id']}"
        )
        if new_rating != book.get("rating"):
            book["rating"] = new_rating
            save_books_for_user(st.session_state.user_name, st.session_state.my_books)
            st.rerun()

    elif book["status"] == "위시리스트":
        if st.button("지금 읽기 시작 🌿", key=f"modal_start_{book['id']}"):
            book["status"] = "읽는 중"
            save_books_for_user(st.session_state.user_name, st.session_state.my_books)
            st.rerun()

    st.divider()
    st.write("📝 **인용구 / 독서 메모**")
    note_text = st.text_area(
        label="인용구 입력",
        label_visibility="collapsed",
        value=book.get("notes", ""),
        height=120,
        key=f"modal_note_{book['id']}"
    )
    if st.button("인용구 저장 ✨", key=f"modal_save_note_{book['id']}"):
        book["notes"] = note_text
        save_books_for_user(st.session_state.user_name, st.session_state.my_books)
        st.success("메모가 저장되었습니다! 📝")
        st.rerun()

    # 삭제 버튼 문구 변경
    st.divider()
    if st.button("🗑️ 삭제하기", key=f"modal_delete_{book['id']}", use_container_width=True):
        st.session_state.my_books = [b for b in st.session_state.my_books if b["id"] != book["id"]]
        save_books_for_user(st.session_state.user_name, st.session_state.my_books)
        st.success("책이 삭제되었습니다.")
        st.rerun()


# -----------------------------------------------------------------------------
# 8. 메인 화면 탭 구역
# -----------------------------------------------------------------------------
page_tab1, page_tab2 = st.tabs([f"☕ {st.session_state.user_name}의 아지트", "📚 내 책장"])

with page_tab1:
    with st.container(border=True):
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.session_state.profile_image:
                image = Image.open(BytesIO(st.session_state.profile_image))
                st.image(image, width=130)
            else:
                st.markdown("""
                    <div style="font-size: 80px; text-align: center; background-color: #F4ECE1; border-radius: 50%; width: 120px; height: 120px; line-height: 120px;">
                        ☕
                    </div>
                """, unsafe_allow_html=True)
                
        with col2:
            st.markdown(f'<div class="luxury-title">☕ {st.session_state.user_name}의 아지트 ✨</div>', unsafe_allow_html=True)
            st.write("🌱 따뜻한 차 한 잔과 함께 독서 목표와 기록을 쌓아가는 아늑한 공간입니다.")
            
            total_b = len(st.session_state.my_books)
            reading_b = len([b for b in st.session_state.my_books if b['status'] == '읽는 중'])
            completed_b = len([b for b in st.session_state.my_books if b['status'] == '읽기 완료'])
            
            m1, m2, m3 = st.columns(3)
            m1.metric("총 등록 도서 📚", f"{total_b}권")
            m2.metric("현재 읽는 중 🌱", f"{reading_b}권")
            m3.metric("완독한 도서 ✨", f"{completed_b}권")

with page_tab2:
    shelf_tab1, shelf_tab2, shelf_tab3, shelf_tab4 = st.tabs(["📖 읽는 중", "📌 위시리스트", "📅 캘린더", "⭐ 평점"])
    
    # 1) 읽는 중
    with shelf_tab1:
        reading_books = [b for b in st.session_state.my_books if b["status"] == "읽는 중"]
        if not reading_books:
            st.info("🌱 현재 읽고 있는 책이 없습니다. 사이드바에서 책을 추가해 보세요!")
        else:
            cols = st.columns(6)
            for idx, book in enumerate(reading_books):
                with cols[idx % 6]:
                    with st.container(border=True):
                        st.image(book["cover_url"], width=95)
                        st.markdown(f"<div style='font-size: 0.8rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 6px; color: #5C4B43;'>{book['title']}</div>", unsafe_allow_html=True)
                        st.caption(f"<div style='font-size: 0.7rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 6px; color: #8C7A6B;'>{book['author']}</div>", unsafe_allow_html=True)
                        if st.button("📝 기록", key=f"btn_r_{book['id']}", use_container_width=True):
                            show_book_details(book)

    # 2) 위시리스트
    with shelf_tab2:
        wish_books = [b for b in st.session_state.my_books if b["status"] == "위시리스트"]
        if not wish_books:
            st.info("📌 위시리스트에 담긴 책이 없습니다.")
        else:
            cols = st.columns(6)
            for idx, book in enumerate(wish_books):
                with cols[idx % 6]:
                    with st.container(border=True):
                        st.image(book["cover_url"], width=95)
                        st.markdown(f"<div style='font-size: 0.8rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 6px; color: #5C4B43;'>{book['title']}</div>", unsafe_allow_html=True)
                        st.caption(f"<div style='font-size: 0.7rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 6px; color: #8C7A6B;'>{book['author']}</div>", unsafe_allow_html=True)
                        if st.button("📝 기록", key=f"btn_w_{book['id']}", use_container_width=True):
                            show_book_details(book)

    # 3) 스트림릿 컴포넌트 기반 완벽한 다이어리 캘린더
    with shelf_tab3:
        st.subheader("📅 완독 기록 다이어리 ✨")
        
        # 연도 및 월 선택 바
        c_col1, c_col2 = st.columns([1, 2])
        with c_col1:
            st.session_state.cal_year = st.selectbox(
                "연도 선택", 
                list(range(2026, 2036)), 
                index=list(range(2026, 2036)).index(st.session_state.cal_year) if st.session_state.cal_year in range(2026, 2036) else 0
            )
        with c_col2:
            months_full = ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"]
            months_short = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
            selected_m_name = st.selectbox(
                "월 선택",
                months_full,
                index=st.session_state.cal_month - 1
            )
            st.session_state.cal_month = months_full.index(selected_m_name) + 1

        st.markdown("<br>", unsafe_allow_html=True)

        # 다이어리 컨테이너 박스
        diary_box = st.container(border=True)
        with diary_box:
            st.markdown(f"<div style='text-align: center; font-size: 1.1rem; font-weight: 800; color: #5C4B43; margin-bottom: 8px;'>📓 {st.session_state.cal_year} . {months_short[st.session_state.cal_month - 1]} ({selected_m_name})</div>", unsafe_allow_html=True)
            
            month_calendar = calendar.monthcalendar(st.session_state.cal_year, st.session_state.cal_month)
            week_days = ["S", "M", "T", "W", "T", "F", "S"]

            completed_map = {}
            for b in st.session_state.my_books:
                if b.get("status") == "읽기 완료" and b.get("completed_date"):
                    completed_map[b["completed_date"]] = b

            # 요일 헤더 (S M T W T F S)
            d_cols = st.columns(7)
            for idx, d_name in enumerate(week_days):
                d_cols[idx].markdown(f"<div style='text-align: center; font-weight: 700; color: #5C4B43; font-size: 0.8rem; background-color: #F4ECE1; padding: 4px; border-radius: 4px;'>{d_name}</div>", unsafe_allow_html=True)

            st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)

            # 날짜 그리드 출력
            for week in month_calendar:
                w_cols = st.columns(7)
                for idx, day in enumerate(week):
                    with w_cols[idx]:
                        if day == 0:
                            st.markdown("<div class='diary-cell' style='background-color: #FCFBF9; border-color: #E6DCD0;'></div>", unsafe_allow_html=True)
                        else:
                            date_str = f"{st.session_state.cal_year}-{st.session_state.cal_month:02d}-{day:02d}"
                            if date_str in completed_map:
                                matched_book = completed_map[date_str]
                                cover = matched_book['cover_url']
                                st.markdown(f"""
                                    <div class='diary-cell'>
                                        <div class='diary-day-num'>{day} 🎉</div>
                                        <div style='text-align: center;'>
                                            <img src='{cover}' style='width: 24px; height: 32px; object-fit: cover; border-radius: 2px;'>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                    <div class='diary-cell'>
                                        <div class='diary-day-num'>{day}</div>
                                    </div>
                                """, unsafe_allow_html=True)

    # 4) 평점 모아보기
    with shelf_tab4:
        st.subheader("⭐ 완독 도서 평점 모아보기")
        completed_books = [b for b in st.session_state.my_books if b["status"] == "읽기 완료"]
        if not completed_books:
            st.info("✨ 아직 완독한 책이 없습니다.")
        else:
            completed_books.sort(key=lambda x: x.get("rating", 0), reverse=True)
            cols = st.columns(4)
            for idx, book in enumerate(completed_books):
                with cols[idx % 4]:
                    with st.container(border=True):
                        st.image(book["cover_url"], width=100)
                        st.markdown(f"<div style='font-size: 0.85rem; font-weight: 700; margin-top: 6px; color: #5C4B43;'>{book['title']}</div>", unsafe_allow_html=True)
                        st.caption(f"<div style='color: #8C7A6B;'>{render_star_rating(book.get('rating', 5.0))}</div>", unsafe_allow_html=True)
                        if st.button("📝 기록", key=f"btn_c_{book['id']}", use_container_width=True):
                            show_book_details(book)
