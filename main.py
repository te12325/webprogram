import streamlit as st
import pandas as pd
import datetime
import requests
from PIL import Image
from io import BytesIO

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 세션 상태(데이터 저장소) 초기화
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="책 저장소",
    page_icon="📚",
    layout="wide"
)

# 반듯하면서 부드럽고 귀여운 '고운돋움' (Gowun Dodum) 폰트 적용 Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

    /* 전체 앱 글꼴 지정 (고운돋움) */
    html, body, [class*="css"], div, span, label, input, button, textarea {
        font-family: 'Gowun Dodum', sans-serif !important;
    }
    
    /* 제목 및 강조 텍스트 크기 조정 */
    h1 {
        font-size: 2.3rem !important;
        font-weight: 700 !important;
    }
    h2, h3 {
        font-size: 1.6rem !important;
        font-weight: 600 !important;
    }
    
    /* 탭 제목 폰트 크기 증대 */
    button[data-baseweb="tab"] {
        font-size: 1.1rem !important;
    }

    /* 카드 제목 및 줄바꿈 정리 */
    .book-title {
        font-weight: bold;
        font-size: 1.05rem;
        margin-top: 5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    </style>
""", unsafe_allow_html=True)

# 앱 데이터 및 팝업(모달) 상태 관리 세션 초기화
if "my_books" not in st.session_state:
    st.session_state.my_books = []

if "active_book_id" not in st.session_state:
    st.session_state.active_book_id = None

# Kakao 도서 검색 API 키 (필요시 발급받은 REST API 키 입력)
KAKAO_API_KEY = "" 

# -----------------------------------------------------------------------------
# 2. 유틸리티 함수 (책 검색, 하루 독서량 계산, 별점 시각화)
# -----------------------------------------------------------------------------
def search_book_kakao(query):
    """
    제목 검색을 통해 실제 책 표지 URL과 도서 정보를 가져오는 함수
    """
    if not KAKAO_API_KEY:
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
                    "total_pages": 300 
                })
            return books
    except Exception as e:
        st.error(f"도서 검색 중 오류가 발생했습니다: {e}")
    return []

def calculate_daily_pages(total_pages, read_pages, target_date):
    """
    남은 페이지 수와 남은 날짜를 계산하여 하루 권장 독서량을 자동 산출하는 함수
    """
    today = datetime.date.today()
    remaining_days = (target_date - today).days
    remaining_pages = total_pages - read_pages

    if remaining_pages <= 0:
        return 0, 0, "목표 달성!"
    
    if remaining_days <= 0:
        return remaining_pages, 0, "목표일이 지났거나 오늘이 목표일입니다."

    daily_pages = -(-remaining_pages // remaining_days)
    return remaining_pages, remaining_days, daily_pages

def render_star_rating(rating):
    """
    0.5 단위 숫자 평점을 별 모양 이모티콘 문자열로 변환해주는 함수
    """
    full_stars = int(rating)
    has_half = (rating - full_stars) >= 0.5
    empty_stars = 5 - full_stars - (1 if has_half else 0)
    
    stars_str = "★" * full_stars + ("✨" if has_half else "") + "☆" * empty_stars
    return f"{stars_str} ({rating}/5.0)"


# -----------------------------------------------------------------------------
# 3. 사이드바 - 책 등록하기
# -----------------------------------------------------------------------------
st.sidebar.header("📖 책 등록하기")

search_term = st.sidebar.text_input("책 제목을 검색하세요")

if search_term:
    search_results = search_book_kakao(search_term)
    
    if search_results:
        selected_book = st.sidebar.selectbox(
            "검색 결과에서 책을 선택하세요:",
            search_results,
            format_func=lambda x: f"{x['title']} ({', '.join(x['authors'])})"
        )
        
        with st.sidebar.form("add_book_form"):
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
                    "notes": ""
                }
                st.session_state.my_books.append(new_book)
                st.sidebar.success(f"'{selected_book['title']}' 책이 저장소에 추가되었습니다!")
    else:
        st.sidebar.warning("검색 결과가 없습니다.")


# -----------------------------------------------------------------------------
# 4. 상세 정보를 보여주는 팝업 모달 함수 (터치 시 실행)
# -----------------------------------------------------------------------------
@st.dialog("📚 도서 상세 및 기록 관리")
def show_book_details(book):
    st.image(book["cover_url"], width=150)
    st.subheader(book["title"])
    st.caption(f"저자: {book['author']} | 전체 {book['total_pages']}p")
    st.divider()

    RATING_OPTIONS = [i / 2 for i in range(1, 11)]

    # 1) 읽는 중 상태일 때 상세 정보
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
            if new_page >= book["total_pages"]:
                book["status"] = "읽기 완료"
                st.balloons()
                st.success("축하합니다! 완독하셨습니다!")
            st.rerun()

    # 2) 읽기 완료 상태일 때 상세 정보
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

    # 3) 위시리스트 상태일 때 상세 정보
    elif book["status"] == "위시리스트":
        if st.button("지금 읽기 시작 📖", key=f"modal_start_{book['id']}"):
            book["status"] = "읽는 중"
            st.rerun()

    st.divider()
    st.write("💬 **인용구**")
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
# 5. 메인 화면 - 콤팩트 카드형 책장 시각화
# -----------------------------------------------------------------------------
st.title("📚 책 저장소")
st.caption("책을 클릭하면 하루 분량, 평점, 인용구를 관리할 수 있습니다.")

tab1, tab2, tab3 = st.tabs(["📖 읽는 중", "✅ 읽기 완료", "📌 위시리스트"])

def render_compact_shelf(status_filter):
    filtered_books = [book for book in st.session_state.my_books if book["status"] == status_filter]
    
    if not filtered_books:
        st.info(f"'{status_filter}' 상태인 책이 없습니다. 사이드바에서 책을 추가해 보세요!")
        return

    # 한 줄에 4개씩 콤팩트하게 배치
    cols = st.columns(4)
    
    for idx, book in enumerate(filtered_books):
        with cols[idx % 4]:
            with st.container(border=True):
                # 1) 책 표지 이미지
                st.image(book["cover_url"], use_container_width=True)
                
                # 2) 제목 및 저자 표시 (간결화)
                st.markdown(f"**{book['title']}**")
                st.caption(f"{book['author']}")
                
                # 3) 클릭/터치 시 상세 모달을 띄우는 버튼
                if st.button("📝 기록", key=f"card_btn_{book['id']}", use_container_width=True):
                    st.session_state.active_book_id = book["id"]
                    show_book_details(book)

with tab1:
    render_compact_shelf("읽는 중")

with tab2:
    render_compact_shelf("읽기 완료")

with tab3:
    render_compact_shelf("위시리스트")
