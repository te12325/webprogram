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
    </style>
""", unsafe_allow_html=True)

# 앱이 새로고침되어도 데이터가 유지되도록 st.session_state에 데이터베이스 생성
if "my_books" not in st.session_state:
    st.session_state.my_books = []

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
        # API 키가 없을 때 기본으로 반환할 샘플 표지 데이터
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

    # 하루 분량 계산 (소수점 올림 처리)
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
# 3. 사이드바 - 새로운 책 추가하기
# -----------------------------------------------------------------------------
st.sidebar.header("📖 새 책 등록하기")

search_term = st.sidebar.text_input("책 제목을 검색하세요")

if search_term:
    search_results = search_book_kakao(search_term)
    
    if search_results:
        selected_book = st.sidebar.selectbox(
            "검색 결과에서 책을 선택하세요:",
            search_results,
            format_func=lambda x: f"{x['title']} ({', '.join(x['authors'])})"
        )
        
        # 선택된 책의 정보 입력 폼
        with st.sidebar.form("add_book_form"):
            st.write(f"**선택한 책:** {selected_book['title']}")
            
            # 사용자 맞춤 정보 입력
            total_pages = st.number_input("전체 페이지 수", min_value=1, value=300, step=10)
            target_date = st.date_input("목표 완료일", datetime.date.today() + datetime.timedelta(days=14))
            status = st.selectbox("독서 상태", ["읽는 중", "읽기 완료", "위시리스트"])
            
            # 처음 추가할 때 '읽기 완료' 선택 시 별점 옵션 제공 (0.5 단위)
            initial_rating = 5.0
            if status == "읽기 완료":
                rating_options = [i / 2 for i in range(1, 11)]  # 0.5 ~ 5.0
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
                    "notes": ""  # 독후감 및 맘에 드는 구절 저장용
                }
                st.session_state.my_books.append(new_book)
                st.sidebar.success(f"'{selected_book['title']}' 책이 저장소에 추가되었습니다!")
    else:
        st.sidebar.warning("검색 결과가 없습니다.")


# -----------------------------------------------------------------------------
# 4. 메인 화면 - 책 저장소 및 상태별 섹션
# -----------------------------------------------------------------------------
st.title("📚 책 저장소")
st.caption("목표일을 설정하면 오늘 읽어야 할 분량을 자동으로 맞춰드립니다.")

# 3개의 상태 탭 생성
tab1, tab2, tab3 = st.tabs(["📖 읽는 중", "✅ 읽기 완료", "📌 위시리스트"])

# 0.5단위 별점 옵션 리스트 생성 (0.5, 1.0, 1.5 ... 5.0)
RATING_OPTIONS = [i / 2 for i in range(1, 11)]

# 세션에 저장된 책들을 상태별로 분류하는 함수
def render_book_shelf(status_filter):
    filtered_books = [book for book in st.session_state.my_books if book["status"] == status_filter]
    
    if not filtered_books:
        st.info(f"'{status_filter}' 상태인 책이 없습니다. 사이드바에서 책을 추가해 보세요!")
        return

    # 3열 grid로 책장 느낌 연출
    cols = st.columns(3)
    
    for idx, book in enumerate(filtered_books):
        with cols[idx % 3]:
            # 카드 형태의 컨테이너
            with st.container(border=True):
                # 책 표지 및 기본 정보
                st.image(book["cover_url"], use_container_width=True)
                st.subheader(book["title"])
                st.caption(f"저자: {book['author']}")
                
                # -------------------------------------------------------------
                # 1) '읽는 중' 섹션
                # -------------------------------------------------------------
                if status_filter == "읽는 중":
                    rem_pages, rem_days, daily_target = calculate_daily_pages(
                        book["total_pages"], book["current_page"], book["target_date"]
                    )
                    
                    # 진행률 표시
                    progress = min(book["current_page"] / book["total_pages"], 1.0)
                    st.progress(progress, text=f"진행률: {int(progress * 100)}%")
                    
                    # 하루 자동 분량 안내 메트릭
                    st.metric(
                        label="Today 목표 (오늘 읽을 분량)", 
                        value=f"{daily_target} 페이지/일",
                        delta=f"남은 날: {rem_days}일"
                    )
                    
                    # 페이지 업데이트 피드백 입력 폼
                    new_page = st.number_input(
                        "현재 읽은 페이지 입력", 
                        min_value=0, 
                        max_value=book["total_pages"], 
                        value=book["current_page"],
                        key=f"page_input_{book['id']}"
                    )
                    
                    if st.button("기록 업데이트", key=f"btn_{book['id']}"):
                        book["current_page"] = new_page
                        # 완독 처리 체크
                        if new_page >= book["total_pages"]:
                            book["status"] = "읽기 완료"
                            st.balloons()
                            st.success("축하합니다! 완독하셨습니다!")
                        st.rerun()

                # -------------------------------------------------------------
                # 2) '읽기 완료' 섹션 (0.5단위 별점)
                # -------------------------------------------------------------
                elif status_filter == "읽기 완료":
                    st.success("🎉 완독한 책입니다!")
                    
                    # 별점 표시 및 수정
                    current_rating = book.get("rating", 5.0)
                    if current_rating == 0.0:
                        current_rating = 5.0
                        
                    st.write(f"**내 평점:** {render_star_rating(current_rating)}")
                    
                    # 별점 수정 슬라이더
                    new_rating = st.select_slider(
                        "평점 수정 (0.5 단위)",
                        options=RATING_OPTIONS,
                        value=current_rating,
                        key=f"rating_slider_{book['id']}"
                    )
                    if new_rating != book.get("rating"):
                        book["rating"] = new_rating
                        st.rerun()

                # -------------------------------------------------------------
                # 3) '위시리스트' 섹션
                # -------------------------------------------------------------
                elif status_filter == "위시리스트":
                    st.write(f"전체 페이지: {book['total_pages']}p")
                    if st.button("지금 읽기 시작 📖", key=f"start_{book['id']}"):
                        book["status"] = "읽는 중"
                        st.rerun()

                # -------------------------------------------------------------
                # 공통: 💬 (따옴표/쉼표 이모티콘 - 독서 노트 입력창)
                # -------------------------------------------------------------
                st.divider()
                
                # expand_more 오류 방지 및 간단한 쉼표/따옴표 이모티콘 라벨 적용
                with st.expander("💬 맘에 드는 구절 / 메모 남기기"):
                    note_text = st.text_area(
                        "기록하고 싶은 대사나 생각한 점을 적어보세요:",
                        value=book.get("notes", ""),
                        height=120,
                        key=f"note_area_{book['id']}"
                    )
                    
                    if st.button("저장", key=f"save_note_{book['id']}"):
                        book["notes"] = note_text
                        st.success("저장되었습니다!")
                        st.rerun()

                # 저장된 노트가 있는 경우 미리보기 제공
                if book.get("notes"):
                    st.caption(f"💬 {book['notes']}")

# 각 탭에 데이터 연결
with tab1:
    render_book_shelf("읽는 중")

with tab2:
    render_book_shelf("읽기 완료")

with tab3:
    render_book_shelf("위시리스트")
