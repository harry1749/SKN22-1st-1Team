import streamlit as st

st.set_page_config(page_title="운전 전 안전 체크리스트", page_icon="🚗", layout="wide")

# -----------------------------
# 상단: 메인페이지 버튼
# -----------------------------
top_cols = st.columns([1, 3])
with top_cols[0]:
    if st.button("🏠 메인페이지"):
        st.switch_page("safe_drive_app.py")   # 메인 페이지로 이동

with top_cols[1]:
    st.title("운전 전 안전 체크리스트")
    st.caption("출발 전 꼭 확인해야 할 항목들을 체크하세요.")

st.divider()

# -----------------------------
# 체크리스트 항목 정의
# -----------------------------
필수항목 = [
    "타이어의 마모 상태 확인",
    "엔진오일, 브레이크오일 점검",
    "냉각수 및 워셔액 점검",
    "조명 및 경고등 점등 여부 확인",
    "브레이크 작동 여부 확인",
]

권장추가항목 = [
    "타이어 공기압 확인",
    "배터리 상태 확인",
    "와이퍼 작동 여부 확인",
    "차량 외관 및 하부 상태 확인",
    "차량 내 비상용품 구비 여부 확인",
    "차량 내 소화기 구비 여부 확인",
    "차량 내 구급함 구비 여부 확인",
]

def make_keys(prefix, items):
    return [f"{prefix}_{item}" for item in items]

필수_keys = make_keys("필수", 필수항목)
권장_keys = make_keys("권장", 권장추가항목)
모든_keys = 필수_keys + 권장_keys

# -----------------------------
# 카드 스타일 + 중앙 알림 CSS
# -----------------------------
style = """
    <style>
    .card {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
        margin: 10px;
    }
    .card h3 {
        margin-top: 0;
        text-align: center;
        color: #333333;
    }
    .center-message {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0, 200, 0, 0.95);
        color: white;
        padding: 60px 100px;
        border-radius: 20px;
        font-size: 3em;
        text-align: center;
        z-index: 9999;
        animation: fadeout 5s forwards;
    }
    @keyframes fadeout {
        0% {opacity: 1;}
        80% {opacity: 1;}
        100% {opacity: 0;}
    }
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# -----------------------------
# 1행 2열 카드 UI
# -----------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="card"><h3>✅ 필수 항목</h3>', unsafe_allow_html=True)
    for item in 필수항목:
        st.checkbox(item, key=f"필수_{item}")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="card"><h3>📌 권장 추가 항목</h3>', unsafe_allow_html=True)
    for item in 권장추가항목:
        st.checkbox(item, key=f"권장_{item}")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# 진행률 표시
# -----------------------------
total_items = len(모든_keys)
checked_count = sum(1 for k in 모든_keys if st.session_state.get(k, False))
progress = checked_count / total_items if total_items else 0.0

st.divider()
st.markdown("### 진행률")
st.progress(progress)
st.write(f"체크 완료: {checked_count} / {total_items} 항목 ({int(progress * 100)}%)")

# 100%일 때 중앙 큰 메시지 출력
if progress >= 0.999:
    st.markdown('<div class="center-message">🎉 당신의 안전 운전 준비는 100점 입니다.</div>', unsafe_allow_html=True)

# -----------------------------
# 하단 좌/우 버튼
# -----------------------------
bottom_cols = st.columns([1, 1, 1, 1, 1])
with bottom_cols[0]:
    if st.button("⬅️ 이전페이지"):
        st.switch_page("pages/이전페이지.py")   # 로컬 pages 폴더 내 파일로 이동

with bottom_cols[-1]:
    if st.button("🚨 긴급 연락처"):
        st.switch_page("EC_details.py")   # 로컬 pages 폴더 내 파일로 이동

st.caption("체크리스트는 안전 운전을 돕기 위한 일반 가이드입니다. 차량 상태 이상이 있으면 즉시 전문가 점검을 받으세요.")