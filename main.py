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
