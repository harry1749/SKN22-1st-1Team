import streamlit as st
import mysql.connector

st.set_page_config(page_title="안전운전 분석 시스템", layout="wide")

# ===== 메인페이지 이동 버튼 (타이틀 상단) =====
if st.button("← 메인페이지로 이동", key="main_btn"):
    st.switch_page("Safe_drive_app.py")

# ===== 타이틀 =====
st.title("안전운전 분석 시스템")
st.subheader("운전 정보 입력")

# ===== CSS 스타일 정의 =====
st.markdown(
    """
    <style>
    .box1 {
        background: #E3F2FD;   /* 연한 파란색 */
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .box2 {
        background: #FFF3E0;   /* 연한 주황색 */
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===== 입력 박스 (각각 개별 박스) =====
st.markdown('<div class="box1">', unsafe_allow_html=True)
select1 = st.selectbox("1 선택", ["옵션 A", "옵션 B", "옵션 C"])
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="box2">', unsafe_allow_html=True)
select2 = st.selectbox("2 선택", ["옵션 X", "옵션 Y", "옵션 Z"])
st.markdown('</div>', unsafe_allow_html=True)

# ===== 분석 버튼 =====
if st.button("교통사고 위험도 분석하기", key="analyze_btn"):
    try:
        # MySQL 연결 (예시, 실제 접속정보 수정 필요)
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="traffic_db"
        )
        cursor = conn.cursor()

        # 예시 쿼리 (실제 분석 로직은 추후 작성)
        query = """
        SELECT risk_score
        FROM accident_risk
        WHERE option1=%s AND option2=%s
        """
        cursor.execute(query, (select1, select2))
        result = cursor.fetchone()

        if result:
            risk_score = result[0]
        else:
            risk_score = "데이터 없음"

        # 결과를 세션 상태에 저장
        st.session_state["risk_result"] = {
            "select1": select1,
            "select2": select2,
            "risk_score": risk_score
        }

        # guide 페이지로 이동
        st.switch_page("pages/guide.py")

    except Exception as e:
        st.error(f"MySQL 연결 오류: {e}")