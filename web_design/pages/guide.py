import streamlit as st

st.set_page_config(page_title="분석 결과", layout="wide")

# ===== 메인페이지 이동 버튼 =====
if st.button("← 메인페이지로 이동", key="main_btn"):
    st.switch_page("Safe_drive_app.py")

# ===== 타이틀 =====
st.title("교통사고 위험도 분석 결과")

if "risk_result" in st.session_state:
    result = st.session_state["risk_result"]

    st.write("🚗 입력 조건")
    st.write(f"- 1 선택: {result['select1']}")
    st.write(f"- 2 선택: {result['select2']}")

    st.write("📊 분석 결과")
    st.success(f"예상 교통사고 위험도 점수: {result['risk_score']}")
else:
    st.warning("분석 결과가 없습니다. 메인 페이지에서 먼저 입력해주세요.")