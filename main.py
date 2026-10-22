import streamlit as st
import pandas as pd
import datetime
import calendar
import html
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
