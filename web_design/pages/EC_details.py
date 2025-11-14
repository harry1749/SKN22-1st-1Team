import streamlit as st

st.set_page_config(page_title="긴급 연락처", page_icon="📞", layout="wide")

# -----------------------------
# 상단: 메인페이지 버튼
# -----------------------------
top_cols = st.columns([1, 3])
with top_cols[0]:
    if st.button("🏠 메인페이지"):
        st.switch_page("Home.py")   # 메인페이지로 이동

with top_cols[1]:
    st.title("긴급 연락처")
    st.caption("사고 발생 시 즉시 연락할 수 있도록 저장해주세요.")

st.divider()

# -----------------------------
# 카드 스타일 CSS + 행동요령 박스 CSS
# -----------------------------
style = """
    <style>
    .card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
        margin: 10px;
        text-align: center;
    }
    .card h3 {
        margin-top: 0;
        color: #333333;
    }
    .red-box {
        background-color: rgba(200, 0, 0, 0.8);
        color: white;
        padding: 25px;
        border-radius: 12px;
        margin-top: 20px;
        font-size: 1.1em;
    }
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# -----------------------------
# 긴급 연락처 1행 3열 카드
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card"><h3>🚨 긴급신고</h3>', unsafe_allow_html=True)
    st.write("📞 112 - 범죄 신고 및 긴급 상황")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><h3>🚑 응급의료</h3>', unsafe_allow_html=True)
    st.write("📞 119 - 구조 및 응급 의료")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card"><h3>🚗 교통사고</h3>', unsafe_allow_html=True)
    st.write("📞 112 - 교통사고 신고 및 처리")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# 긴급출동 (아래 따로 배치)
# -----------------------------
st.markdown('<div class="card"><h3>🔧 긴급출동</h3>', unsafe_allow_html=True)
st.write("📞 1588-2119 - 차량 고장 및 긴급 서비스")
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# -----------------------------
# 사고 발생 시 행동요령 (붉은색 박스)
# -----------------------------
st.markdown("""
<div class="red-box">
<h3>⚠️ 사고 발생 시 행동 요령</h3>
1. **첫 확인**: 차량을 안전한 곳으로 이동하고 비상등을 켭니다.<br>
2. **두 번째**: 사고 상황을 파악하고 필요한 경우 긴급 연락처로 연락합니다.<br>
3. **세 번째**: 부상자가 있을 경우 즉시 119에 연락하여 응급조치를 요청합니다.<br>
4. **네 번째**: 교통사고 발생 시 112에 신고하여 경찰의 도움을 받습니다.<br>
5. **다섯 번째**: 사고 경위를 기록하고 증거를 확보합니다.
</div>
""", unsafe_allow_html=True)

# -----------------------------
# 하단 좌측: 이전페이지 버튼
# -----------------------------
bottom_cols = st.columns([1, 1, 1, 1, 1])
with bottom_cols[0]:
    if st.button("⬅️ 이전페이지"):
        st.switch_page("driver_checklist.py")   # 로컬 이전페이지로 이동