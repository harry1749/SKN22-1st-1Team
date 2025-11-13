import streamlit as st
import base64
import os

st.set_page_config(page_title="안전한 운전, 사고 없는 내일", layout="wide")

# 이미지 Base64 변환 함수
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 현재 파일 위치 기준 이미지 경로
current_dir = os.path.dirname(__file__)
img_path = os.path.join(current_dir, "safecar1.png")   # 배경 이미지 파일
img_base64 = get_base64_of_bin_file(img_path)

# CSS 정의
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-position: center;
    }}
    .main-box {{
        background: rgba(255,255,255,0.85);
        padding: 40px;
        border-radius: 20px;
        max-width: 950px;
        margin:auto;
        margin-top: 40px;
    }}
    .main-title {{
        font-size: 54px; 
        font-weight: 900; 
        color: #222; 
        line-height: 1.1; 
        margin-bottom: 0px;
    }}
    .sub-title {{
        font-size: 50px; 
        font-weight: 700; 
        color: #428AF7; 
        margin-bottom: 32px; 
        margin-top: -10px;
    }}
    .desc {{
        font-size: 22px; 
        color: #444; 
        margin-bottom: 40px;
    }}
    .btn-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    div.stButton > button:first-child {{
        background:#428AF7;
        color:white;
        border:none;
        border-radius:8px;
        padding:16px 28px;
        font-size:18px;
        font-weight:600;
        cursor:pointer;
    }}
    div.stButton.secondary > button:first-child {{
        background:white;
        color:#333;
        border:1px solid #ddd;
        border-radius:8px;
        padding:16px 28px;
        font-size:18px;
        font-weight:600;
        cursor:pointer;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# 메인 박스 + 타이틀 + 문구 + 버튼
st.markdown(
    """
    <div class="main-box">
        <div class="main-title">안전한 운전,</div>
        <div class="sub-title">사고 없는 내일</div>
        <div class="desc">
            전문적인 안전 운전 팁과 실시간 통계로<br>
            당신의 안전한 여행을 지켜드립니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 버튼 영역 (좌우 끝 정렬)
col_spacer1, col_left, col_right, col_spacer2 = st.columns([3, 3, 2, 2])

with col_left:
    st.markdown('<div class="stButton">', unsafe_allow_html=True)
    if st.button("안전 가이드 시작하기 →", key="guide_btn"):
        st.switch_page("pages/driver_input.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="stButton secondary">', unsafe_allow_html=True)
    if st.button("통계 확인하기", key="stats_btn"):
        st.switch_page("pages/stats.py")
    st.markdown('</div>', unsafe_allow_html=True)
