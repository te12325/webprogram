
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

# =============================================================================
# TAB 3: 독서 성향 MBTI - 완독 도서의 장르 비율 분석
# =============================================================================
with page_tab3:
    st.subheader("🧠 나의 독서 성향 MBTI")
    st.write("완독한 책의 장르 비율을 분석해 나만의 독서 유형을 알려드려요.")
    st.caption("진단은 재미를 위한 참고 정보예요. 장르가 등록된 완독 도서가 많을수록 결과가 더 정확해집니다.")

    completed_for_analysis = [
        b for b in st.session_state.my_books
        if b.get("status") == "읽기 완료"
    ]

    if not completed_for_analysis:
        st.info("아직 완독한 책이 없어요. 책을 완독으로 기록하면 독서 성향 분석이 시작됩니다!")
        st.write("💡 팁: 책을 등록할 때 장르를 선택하거나, 기존 책의 📝 기록 화면에서 장르를 지정해 주세요.")
    else:
        ratios, personality, message, personality_emoji = get_reading_personality(completed_for_analysis)
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #FFE4E6 0%, #F3E8FF 52%, #E0E7FF 100%);
                        border: 1px solid #F3D2DF; border-radius: 22px; padding: 26px;
                        text-align: center; margin: 10px 0 22px 0;">
                <div style="font-size: 3rem;">{personality_emoji}</div>
                <div style="font-size: 1.65rem; font-weight: 800; color: #4A3E3D;">{personality}</div>
                <div style="font-size: 1rem; color: #5D5050; margin-top: 10px;">{message}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        genre_col, stat_col = st.columns([3, 2])
        with genre_col:
            st.markdown("#### 📊 장르별 독서 비율")
            if ratios:
                ratio_df = pd.DataFrame({
                    "장르": list(ratios.keys()),
                    "비율(%)": [round(value, 1) for value in ratios.values()]
                }).set_index("장르")
                st.bar_chart(ratio_df, y="비율(%)")
                st.caption("비율은 완독한 도서의 권수를 기준으로 계산합니다.")
        with stat_col:
            st.markdown("#### 📚 분석 요약")
            st.metric("분석한 완독 도서", f"{len(completed_for_analysis)}권")
            if ratios:
                dominant = max(ratios, key=ratios.get)
                st.metric("가장 많이 읽은 장르", dominant)
                st.metric("해당 장르 비율", f"{ratios[dominant]:.1f}%")

        st.markdown("#### 🗂️ 장르별 기록")
        genre_rows = sorted(ratios.items(), key=lambda item: item[1], reverse=True)
        for genre_name, ratio_value in genre_rows:
            count = sum(1 for b in completed_for_analysis if (b.get("genre", "미분류") or "미분류") == genre_name)
            st.write(f"**{genre_name}** — {count}권 · {ratio_value:.1f}%")
            st.progress(min(ratio_value / 100, 1.0))
