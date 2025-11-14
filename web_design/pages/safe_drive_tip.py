import streamlit as st

st.set_page_config(page_title="핵심 안전 운전 팁", layout="wide")

# ===== 타이틀 상단 메인페이지 버튼 =====
if st.button("← 메인페이지로 이동", key="main_btn"):
    st.switch_page("Safe_drive_app.py")

# ===== 타이틀 =====
st.title("핵심 안전 운전 팁")

# ===== CSS 스타일 정의 (아이콘 강조) =====
st.markdown("""
<style>
.tip-box {
    background: #F9FAFB;
    border: 2px solid #428AF7;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    height: 200px; /* 정사각형 느낌 */
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin: 30px; /* 상하좌우 동일 간격 */
}
.tip-icon {
    font-size: 40px; /* 아이콘 크게 강조 */
    margin-bottom: 10px;
}
.tip-title {
    font-size: 18px;
    font-weight: 700;
    color: #1E4FBF;
    margin-bottom: 6px;
}
.tip-desc {
    font-size: 14px;
    color: #333;
}
</style>
""", unsafe_allow_html=True)

# ===== 안전 운전 팁 데이터 (아이콘 포함) =====
tips = [
    ("🏎️", "적정 속도 유지", "상황에 맞는 안전한 속도를 유지하세요."),
    ("👀", "전방 주시", "운전 중에는 스마트 기기 사용을 자제하세요."),
    ("😴", "충분한 휴식", "장거리 운전 시 2시간마다 휴식을 취하세요."),
    ("📏", "안전거리 확보", "앞차와 충분한 안전거리를 확보하세요."),
    ("☔", "날씨 대비", "출발 전 날씨를 확인하고 대비하세요."),
    ("⏰", "여유있는 출발", "시간 여유를 두고 출발하세요.")
]

# ===== 3열 × 2행 레이아웃 =====
for row in range(0, len(tips), 3):
    cols = st.columns(3)
    for i, col in enumerate(cols):
        if row + i < len(tips):
            icon, title, desc = tips[row + i]
            with col:
                st.markdown(f"""
                <div class="tip-box">
                    <div class="tip-icon">{icon}</div>
                    <div class="tip-title">{title}</div>
                    <div class="tip-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

# ===== 하단 버튼 영역 =====
col_left, col_mid, col_right = st.columns([1, 6, 1])

with col_left:
    if st.button("← 이전 페이지", key="prev_btn"):
        st.switch_page("pages/guide_all.py")

