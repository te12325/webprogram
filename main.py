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
# 웹브라우저 탭의 제목, 아이콘, 레이아웃을 설정합니다.
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
# 2. 세션 상태(Session State) 초기화
# -----------------------------------------------------------------------------
# 앱이 새로고침되어도 데이터가 사라지지 않도록 메모리에 변수를 저장합니다.
if "my_books" not in st.session_state:
    st.session_state.my_books = []  # 등록된 책 목록 저장용 리스트

if "active_book_id" not in st.session_state:
    st.session_state.active_book_id = None  # 현재 선택된 책 ID

if "user_name" not in st.session_state:
    st.session_state.user_name = ""  # 사용자 이름/닉네임

if "profile_image" not in st.session_state:
    st.session_state.profile_image = None  # 사용자 프로필 이미지 바이너리 데이터

# 카카오 도서 검색 API 키 (필요 시 발급받은 REST API 키 문자열 입력)
KAKAO_API_KEY = "" 


# -----------------------------------------------------------------------------
# 3. 초기 화면: 사용자 이름 입력 또는 게스트 입장
# -----------------------------------------------------------------------------
# user_name 값이 비어있다면 대문 화면을 띄워 사용자 입력을 받습니다.
if not st.session_state.user_name:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 2, 1])  # 화면 중앙 정렬용 컬럼 분할
    
    with center_col:
        with st.container(border=True):
            st.markdown('<div class="luxury-title" style="text-align: center;">📚 나만의 책 아지트</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("아지트에서 사용하실 이름을 입력해 주세요.")
            
            # 사용자 이름 입력 칸
            input_name = st.text_input("이름 또는 닉네임 입력", placeholder="닉네임을 입력하세요", label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 1) 본인 이름으로 입장 버튼
            if st.button("책 아지트 입장하기 🚀", use_container_width=True):
                if input_name.strip():
                    st.session_state.user_name = input_name.strip()
                    st.rerun()  # 화면을 다시 불러와 메인 화면으로 전환
                else:
                    st.warning("이름을 입력해 주세요!")
            
            # 2) 게스트로 입장하기 버튼 (요청 기능 추가)
            if st.button("🙋‍♂️ 게스트로 입장하기", use_container_width=True, type="secondary"):
                st.session_state.user_name = "게스트"
                st.rerun()  # 화면을 다시 불러와 메인 화면으로 전환

    st.stop()  # 이름이 설정되기 전까지는 아래 코드를 실행하지 않고 여기서 멈춥니다.


# -----------------------------------------------------------------------------
# 4. 유틸리티 함수 정의
# -----------------------------------------------------------------------------

# 카카오 도서 검색 API 호출 함수
def search_book_kakao(query):
    """책 제목으로 검색하여 도서 목록 및 표지 이미지 URL을 가져옵니다."""
    if not KAKAO_API_KEY:
        # API 키가 설정되지 않은 경우 샘플 데이터를 반환합니다.
        return [{
            "title": query,
            "authors": ["작자 미상"],
            "thumbnail": "https://via.placeholder.com/150x200.png?text=No+Cover",
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
                    "total_pages": 300  # 기본 페이지 수 지정 (사용자가 수정 가능)
                })
            return books
    except Exception as e:
        st.error(f"도서 검색 중 오류가 발생했습니다: {e}")
    return []

# 하루 독서 권장 분량 계산 함수 (목표일 기준 자동 분량 조절)
def calculate_daily_pages(total_pages, read_pages, target_date):
    """현재 읽은 페이지, 목표일을 바탕으로 오늘 읽어야 할 하루 분량을 계산합니다."""
    today = datetime.date.today()
    remaining_days = (target_date - today).days
    remaining_pages = total_pages - read_pages

    if remaining_pages <= 0:
        return 0, 0, "목표 달성!"
    
    if remaining_days <= 0:
        return remaining_pages, 0, "목표일이 지났거나 오늘이 목표일입니다."

    # 남은 페이지 / 남은 일수 (올림 처리하여 하루 분량 산출)
    daily_pages = -(-remaining_pages // remaining_days)
    return remaining_pages, remaining_days, daily_pages

# 별점 시각화 함수
def render_star_rating(rating):
    """숫자 평점을 별 모양 문자열로 변환합니다."""
    full_stars = int(rating)
    has_half = (rating - full_stars) >= 0.5
    empty_stars = 5 - full_stars - (1 if has_half else 0)
    
    stars_str = "★" * full_stars + ("✨" if has_half else "") + "☆" * empty_stars
    return f"{stars_str} ({rating}/5.0)"


# -----------------------------------------------------------------------------
# 5. 사이드바 영역 (프로필 설정 및 책 등록)
# -----------------------------------------------------------------------------
with st.sidebar:
    # 1) 프로필 수정 영역
    with st.container(border=True):
        st.markdown('<h3 style="margin-top:0; color:#4A3E3D; font-size:1.2rem;">👤 프로필 설정</h3>', unsafe_allow_html=True)
        
        # 이름 수정 입력칸
        new_name = st.text_input("이름 수정", value=st.session_state.user_name)
        if new_name != st.session_state.user_name and new_name.strip():
            st.session_state.user_name = new_name.strip()
            st.rerun()

        # 프로필 이미지 업로드
        new_profile = st.file_uploader("프로필 사진 등록/변경", type=["png", "jpg", "jpeg"], key="side_profile")
        if new_profile is not None:
            st.session_state.profile_image = new_profile.getvalue()

    st.divider()

    # 2) 도서 검색 및 내 책장에 추가 영역
    st.header("📖 책 등록하기")
    search_term = st.text_input("책 제목을 검색하세요")

    if search_term:
        search_results = search_book_kakao(search_term)
        
        if search_results:
            # 검색된 결과를 드롭다운 메뉴로 선택
            selected_book = st.selectbox(
                "검색 결과에서 책을 선택하세요:",
                search_results,
                format_func=lambda x: f"{x['title']} ({', '.join(x['authors'])})"
            )
            
            # 선택한 책 등록 폼
            with st.form("add_book_form"):
                st.write(f"**선택한 책:** {selected_book['title']}")
                
                total_pages = st.number_input("전체 페이지 수", min_value=1, value=300, step=10)
                target_date = st.date_input("목표 완료일", datetime.date.today() + datetime.timedelta(days=14))
                status = st.selectbox("독서 상태", ["읽는 중", "읽기 완료", "위시리스트"])
                
                initial_rating = 5.0
                if status == "읽기 완료":
                    rating_options = [i / 2 for i in range(1, 11)]
                    initial_rating = st.select_slider("별점 평점 선택", options=rating_options, value=5.0)

                submit_button = st.form_submit_button("내 책장에 추가")
                
                if submit_button:
                    today_str = datetime.date.today().strftime("%Y-%m-%d")
                    new_book = {
                        "id": len(st.session_state.my_books) + 1,
                        "title": selected_book["title"],
                        "author": ", ".join(selected_book["authors"]),
                        "cover_url": selected_book["thumbnail"],
                        "total_pages": total_pages,
                        "current_page": total_pages if status == "읽기 완료" else 0,
                        "target_date": target_date,
                        "status": status,
                        "rating": initial_rating if status == "읽기 완료" else 0.0,
                        "notes": "",
                        "completed_date": today_str if status == "읽기 완료" else None
                    }
                    st.session_state.my_books.append(new_book)
                    st.success(f"'{selected_book['title']}' 책이 저장소에 추가되었습니다!")
        else:
            st.warning("검색 결과가 없습니다.")


# -----------------------------------------------------------------------------
# 6. 도서 상세정보 팝업 모달 (@st.dialog)
# -----------------------------------------------------------------------------
@st.dialog("📚 도서 상세 및 기록 관리")
def show_book_details(book):
    """책 표지 클릭 또는 기록 버튼 클릭 시 팝업으로 상세 정보를 띄웁니다."""
    st.image(book["cover_url"], width=150)
    st.subheader(book["title"])
    st.caption(f"저자: {book['author']} | 전체 {book['total_pages']}p")
    st.divider()

    RATING_OPTIONS = [i / 2 for i in range(1, 11)]

    # 1) '읽는 중' 상태일 때: 진행률 표시 및 페이지 기록
    if book["status"] == "읽는 중":
        rem_pages, rem_days, daily_target = calculate_daily_pages(
            book["total_pages"], book["current_page"], book["target_date"]
        )
        progress = min(book["current_page"] / book["total_pages"], 1.0)
        st.progress(progress, text=f"진행률: {int(progress * 100)}%")
        
        st.metric(
            label="Today 목표 (오늘 읽을 분량)", 
            value=f"{daily_target} 페이지/일",
            delta=f"남은 날: {rem_days}일"
        )
        
        new_page = st.number_input(
            "현재 읽은 페이지 입력", 
            min_value=0, 
            max_value=book["total_pages"], 
            value=book["current_page"],
            key=f"modal_page_{book['id']}"
        )
        
        if st.button("페이지 저장", key=f"modal_save_page_{book['id']}"):
            book["current_page"] = new_page
            # 만약 완독 페이지에 도달하면 자동으로 '읽기 완료' 상태로 변경
            if new_page >= book["total_pages"]:
                book["status"] = "읽기 완료"
                book["completed_date"] = datetime.date.today().strftime("%Y-%m-%d")
                st.balloons()  # 축하 풍선 효과
                st.success("축하합니다! 완독하셨습니다!")
            st.rerun()

    # 2) '읽기 완료' 상태일 때: 평점 수정 기능 제공
    elif book["status"] == "읽기 완료":
        st.success("🎉 완독한 책입니다!")
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
            st.rerun()

    # 3) '위시리스트' 상태일 때: 읽기 시작 버튼 제공
    elif book["status"] == "위시리스트":
        if st.button("지금 읽기 시작 📖", key=f"modal_start_{book['id']}"):
            book["status"] = "읽는 중"
            st.rerun()

    st.divider()
    # 인용구 및 독서 메모 저장
    st.write("💬 **인용구 / 독서 메모**")
    note_text = st.text_area(
        label="인용구 입력",
        label_visibility="collapsed",
        value=book.get("notes", ""),
        height=120,
        key=f"modal_note_{book['id']}"
    )
    if st.button("인용구 저장", key=f"modal_save_note_{book['id']}"):
        book["notes"] = note_text
        st.success("저장되었습니다!")
        st.rerun()


# -----------------------------------------------------------------------------
# 7. 메인 화면 메인 탭 구역 (1. 프로필 아지트 / 2. 내 책장)
# -----------------------------------------------------------------------------
page_tab1, page_tab2 = st.tabs([f"👤 {st.session_state.user_name}의 아지트", "📚 내 책장"])

# =============================================================================
# TAB 1: (사용자의 이름)의 아지트 메인 대시보드
# =============================================================================
with page_tab1:
    with st.container(border=True):
        col1, col2 = st.columns([1, 4])
        
        # 프로필 이미지 표시
        with col1:
            if st.session_state.profile_image:
                image = Image.open(BytesIO(st.session_state.profile_image))
                st.image(image, width=130)
            else:
                st.markdown("""
                    <div style="font-size: 80px; text-align: center; background-color: #F3E8FF; border-radius: 50%; width: 120px; height: 120px; line-height: 120px;">
                        👤
                    </div>
                """, unsafe_allow_html=True)
                
        # 환영 인사 및 전체 현황 지표(Metric) 표시
        with col2:
            st.markdown(f'<div class="luxury-title">📚 {st.session_state.user_name}의 아지트</div>', unsafe_allow_html=True)
            st.write("나만의 독서 목표와 기록을 차곡차곡 쌓아가는 공간입니다.")
            
            total_b = len(st.session_state.my_books)
            reading_b = len([b for b in st.session_state.my_books if b['status'] == '읽는 중'])
            completed_b = len([b for b in st.session_state.my_books if b['status'] == '읽기 완료'])
            
            m1, m2, m3 = st.columns(3)
            m1.metric("총 등록 도서", f"{total_b}권")
            m2.metric("현재 읽는 중", f"{reading_b}권")
            m3.metric("완독한 도서", f"{completed_b}권")

# =============================================================================
# TAB 2: 내 책장 (4개의 하위 서브 탭으로 구분)
# =============================================================================
with page_tab2:
    shelf_tab1, shelf_tab2, shelf_tab3, shelf_tab4 = st.tabs(["📖 읽는 중", "📌 위시리스트", "📅 캘린더", "⭐ 평점"])
    
    # 서브 탭 1) 읽는 중인 책 목록
    with shelf_tab1:
        reading_books = [b for b in st.session_state.my_books if b["status"] == "읽는 중"]
        if not reading_books:
            st.info("현재 읽고 있는 책이 없습니다. 사이드바에서 책을 추가해 보세요!")
        else:
            cols = st.columns(4)
            for idx, book in enumerate(reading_books):
                with cols[idx % 4]:
                    with st.container(border=True):
                        st.image(book["cover_url"], use_container_width=True)
                        st.markdown(f"**{book['title']}**")
                        st.caption(f"{book['author']}")
                        if st.button("📝 기록", key=f"btn_r_{book['id']}", use_container_width=True):
                            show_book_details(book)

    # 서브 탭 2) 위시리스트 목록
    with shelf_tab2:
        wish_books = [b for b in st.session_state.my_books if b["status"] == "위시리스트"]
        if not wish_books:
            st.info("위시리스트에 담긴 책이 없습니다.")
        else:
            cols = st.columns(4)
            for idx, book in enumerate(wish_books):
                with cols[idx % 4]:
                    with st.container(border=True):
                        st.image(book["cover_url"], use_container_width=True)
                        st.markdown(f"**{book['title']}**")
                        st.caption(f"{book['author']}")
                        if st.button("📝 기록", key=f"btn_w_{book['id']}", use_container_width=True):
                            show_book_details(book)

    # 서브 탭 3) 독서 캘린더 (완독 시 해당 날짜에 책 표지 출력)
    with shelf_tab3:
        st.subheader("📅 완독 기록 캘린더")
        
        # 연도 및 월 선택
        c_year_col, c_month_col = st.columns(2)
        with c_year_col:
            selected_year = st.selectbox("연도 선택", list(range(2026, 2036)), index=0)
        with c_month_col:
            selected_month = st.selectbox("월 선택", list(range(1, 13)), index=datetime.date.today().month - 1 if selected_year == 2026 else 0)

        # 선택된 월의 날짜 매트릭스 계산
        month_calendar = calendar.monthcalendar(selected_year, selected_month)
        week_days = ["일", "월", "화", "수", "목", "금", "토"]
        
        # 요일 헤더 표시
        day_cols = st.columns(7)
        for idx, day_name in enumerate(week_days):
            day_cols[idx].markdown(f"**{day_name}**")
            
        # 완독된 책 데이터 매핑 (날짜 -> 책 정보)
        completed_map = {}
        for b in st.session_state.my_books:
            if b.get("status") == "읽기 완료" and b.get("completed_date"):
                completed_map[b["completed_date"]] = b

        # 캘린더 화면 그리드 생성
        for week in month_calendar:
            w_cols = st.columns(7)
            for idx, day in enumerate(week):
                with w_cols[idx]:
                    if day == 0:
                        st.write("")
                    else:
                        date_str = f"{selected_year}-{selected_month:02d}-{day:02d}"
                        
                        # 해당 날짜에 완독한 책이 있으면 표지 이미지 출력
                        if date_str in completed_map:
                            matched_book = completed_map[date_str]
                            st.markdown(f"""
                                <div class="cal-day-box">
                                    <div class="cal-day-num">{day}일 🎉</div>
                                </div>
                            """, unsafe_allow_html=True)
                            st.image(matched_book["cover_url"], use_container_width=True)
                        else:
                            st.markdown(f"""
                                <div class="cal-day-box">
                                    <div class="cal-day-num">{day}</div>
                                </div>
                            """, unsafe_allow_html=True)

    # 서브 탭 4) 완독 도서 별점 모아보기
    with shelf_tab4:
        st.subheader("⭐ 완독 도서 평점 모아보기")
        completed_books = [b for b in st.session_state.my_books if b["status"] == "읽기 완료"]
        if not completed_books:
            st.info("아직 완독한 책이 없습니다.")
        else:
            # 평점이 높은 순으로 정렬하여 표시
            completed_books.sort(key=lambda x: x.get("rating", 0), reverse=True)
            cols = st.columns(4)
            for idx, book in enumerate(completed_books):
                with cols[idx % 4]:
                    with st.container(border=True):
                        st.image(book["cover_url"], use_container_width=True)
                        st.markdown(f"**{book['title']}**")
                        st.caption(render_star_rating(book.get("rating", 5.0)))
                        if st.button("📝 기록", key=f"btn_c_{book['id']}", use_container_width=True):
                            show_book_details(book)
