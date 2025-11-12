import streamlit as st
import base64

# 페이지 설정
st.set_page_config(page_title="SAFE DRIVE 캠페인", page_icon="🚗", layout="wide")

# 배경 이미지 적용 함수
def set_background(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    css = f"""
    <style>
    html, body, .stApp {{
        height: 100%;
        margin: 0;
        overflow: hidden; /* 스크롤 제거 */
    }}
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }}
    /* 중앙 정렬 컨테이너 */
    .main-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh; /* 전체 화면 높이 기준 중앙 배치 */
        text-align: center;
    }}
    h1 {{
        font-size: 80px;
        color: #2C3E50;
        margin-bottom: 40px;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# safecar1.png 파일을 배경으로 적용
set_background("safecar1.png")

# 중앙 컨테이너 시작
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# 메인 타이틀
st.markdown("<h1>🚗 SAFE DRIVE 캠페인</h1>", unsafe_allow_html=True)

# 안전 가이드 메뉴 (타이틀 바로 밑 중앙)
st.subheader("🧾 안전 가이드")
st.write("전문적인 안전 운전 팁을 제공합니다.")
if st.button("안전 가이드 시작하기"):
    st.info("👉 안전 운전 가이드 페이지로 이동합니다.")

# 컨테이너 종료
st.markdown('</div>', unsafe_allow_html=True)

# 푸터 (하단 고정)
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>© 2025 Safe Drive Campaign</p>",
    unsafe_allow_html=True
)