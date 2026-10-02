
# -----------------------------------------------------------------------------
# 2. 최초 사용자 이름 입력 화면
# -----------------------------------------------------------------------------
if not st.session_state.user_name:
    # 화면 위쪽에 여백을 추가하여 입장 화면을 중앙에 배치
    st.markdown("<br><br><br>", unsafe_allow_html=True)

    # 화면 중앙에 입장 카드 배치
    _, center_col, _ = st.columns([1, 2, 1])

    with center_col:
        with st.container(border=True):
            # 책 아지트의 메인 타이틀
            st.markdown(
                '<div class="luxury-title" style="text-align: center;">'
                '📚 나만의 책 아지트</div>',
                unsafe_allow_html=True
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # 사용자 이름 입력 안내
            st.write("아지트에서 사용하실 이름을 입력해 주세요.")

            # 이름 또는 닉네임 입력창
            input_name = st.text_input(
                "이름 또는 닉네임 입력",
                placeholder="",
                label_visibility="collapsed"
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # 일반 입장 버튼
            if st.button(
                "책 아지트 입장하기 🚀",
                use_container_width=True
            ):
                # 이름을 입력했는지 확인
                if input_name.strip():
                    st.session_state.user_name = input_name.strip()
                    st.rerun()
                else:
                    st.warning("이름을 입력해 주세요!")

            # 게스트 입장 버튼
            # 이름을 입력하지 않아도 게스트라는 이름으로 입장 가능
            if st.button(
                "게스트로 입장하기",
                use_container_width=True
            ):
                st.session_state.user_name = "게스트"
                st.rerun()

    # 이름 입력 화면에서는 아래의 메인 화면을 표시하지 않음
    st.stop()
