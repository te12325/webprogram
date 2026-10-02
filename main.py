import streamlit as st
import pandas as pd
import datetime
import requests

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 세션 상태(데이터 저장소) 초기화
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="책 저장소 & 캘린더",
    page_icon="📚",
    layout="wide"
)

# 반듯하고 귀여운 글씨체 (Gowun Dodum / 고운돋움 폰트 적용)
st.markdown("""
    
""", unsafe_allow_html=True)

# 앱이 새로고침되어도 데이터가 유지되도록 st.session_state에 데이터베이스 생성
if "my_books" not in st.session_state:
    st.session_state.my_books = []

# Kakao 도서 검색 API 키 (필요시 발급받은 REST API 키 입력)
KAKAO_API_KEY = "" 

# -----------------------------------------------------------------------------
# 2. 유틸리티 함수 (책 검색 및 하루 독서량 계산)
# -----------------------------------------------------------------------------
def search_book_kakao(query):
    if not KAKAO_API_KEY:
        return [{
            "title": query,
            "authors": ["작자 미상"],
            "thumbnail": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=300&auto=format&fit=crop",
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
                    "thumbnail": item.get("thumbnail", "https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=300&auto=format&fit=crop"),
                    "total_pages": 300 
                })
            return books
    except Exception as e:
        st.error(f"도서 검색 중 오류가 발생했습니다: {e}")
    return []

def calculate_daily_pages(total_pages, read_pages, target_date):
    today = datetime.date.today()
    remaining_days = (target_date - today).days
    remaining_pages = total_pages - read_pages

    if remaining_pages <= 0:
        return 0, 0, "목표 달성!"
    
    if remaining_days <= 0:
        return remaining_pages, 0, "목표일이 지났거나 오늘이 목표일입니다."

    daily_pages = -(-remaining_pages // remaining_days)
    return remaining_pages, remaining_days, daily_pages


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
        
        with st.sidebar.form("add_book_form"):
            st.write(f"**선택한 책:** {selected_book['title']}")
            
            total_pages = st.number_input("전체 페이지 수", min_value=1, value=300, step=10)
            target_date = st.date_input("목표 완료일", datetime.date.today() + datetime.timedelta(days=14))
            status = st.selectbox("독서 상태", ["읽는 중", "읽기 완료", "읽고 싶음"])
            
            submit_button = st.form_submit_button("내 책장에 추가")
            
            if submit_button:
                new_book = {
                    "id": len(st.session_state.my_books) + 1,
                    "title": selected_book["title"],
                    "author": ", ".join(selected_book["authors"]),
                    "cover_url": selected_book["thumbnail"],
                    "total_pages": total_pages,
                    "current_page": 0,
                    "target_date": target_date,
                    "status": status
                }
                st.session_state.my_books.append(new_book)
                st.sidebar.success(f"'{selected_book['title']}' 책이 저장소에 추가되었습니다!")
    else:
        st.sidebar.warning("검색 결과가 없습니다.")


# -----------------------------------------------------------------------------
# 4. 메인 화면 - 책 저장소 및 상태별 섹션
# -----------------------------------------------------------------------------
st.title("📚 책 저장소 & 캘린더")
st.caption("목표일을 설정하면 오늘 읽어야 할 분량을 자동으로 맞춰드립니다.")

tab1, tab2, tab3 = st.tabs(["📖 읽는 중", "✅ 읽기 완료", "📌 읽고 싶음"])

def render_book_shelf(status_filter):
    filtered_books = [book for book in st.session_state.my_books if book["status"] == status_filter]
    
    if not filtered_books:
        st.info(f"'{status_filter}' 상태인 책이 없습니다. 사이드바에서 책을 추가해 보세요!")
        return

    cols = st.columns(3)
    
    for idx, book in enumerate(filtered_books):
        with cols[idx % 3]:
            with st.container(border=True):
                st.image(book["cover_url"], use_container_width=True)
                st.subheader(book["title"])
                st.caption(f"저자: {book['author']}")
                
                if status_filter == "읽는 중":
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
                        key=f"page_input_{book['id']}"
                    )
                    
                    if st.button("기록 업데이트", key=f"btn_{book['id']}"):
                        book["current_page"] = new_page
                        if new_page >= book["total_pages"]:
                            book["status"] = "읽기 완료"
                            st.balloons()
                            st.success("축하합니다! 완독하셨습니다!")
                        st.rerun()

                elif status_filter == "읽기 완료":
                    st.success("🎉 완독한 책입니다!")
                    st.write(f"총 {book['total_pages']} 페이지")

                elif status_filter == "읽고 싶음":
                    st.write(f"목표 페이지: {book['total_pages']}p")
                    if st.button("지금 읽기 시작", key=f"start_{book['id']}"):
                        book["status"] = "읽는 중"
                        st.rerun()

with tab1:
    render_book_shelf("읽는 중")

with tab2:
    render_book_shelf("읽기 완료")

with tab3:
    render_book_shelf("읽고 싶음")
