import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="교통사고 통계", layout="wide")

# ===== 메인페이지 이동 버튼 =====
if st.button("← 메인페이지로 이동"):
    st.switch_page("safe_drive_app.py")   # 루트에 있는 메인 파일 이름과 정확히 일치

# ===== 헤더 =====
st.title("교통사고 통계")
st.caption("출처: 도로교통공단 (샘플 데이터 포함). CSV 업로드 시 자동 반영됩니다.")

# ===== 데이터 입력 (업로드 또는 기본) =====
uploaded = st.file_uploader("CSV 업로드 (year, fatalities, accidents, seatbelt_effect_pct, speeding_fatal_pct)", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
else:
    df = pd.DataFrame({
        "year": [2020, 2021, 2022, 2023],
        "fatalities": [3300, 3200, 3376, 3081],
        "accidents": [205000, 202000, 200500, 196477],
        "seatbelt_effect_pct": [60, 61.5, 63.8, 67.0],
        "speeding_fatal_pct": [34, 35, 35, 35]
    })

# 최근 연도 데이터
latest = df.sort_values("year").iloc[-1]
prev = df.sort_values("year").iloc[-2] if len(df) >= 2 else latest

def pct_change(curr, prev):
    try:
        return (curr - prev) / prev * 100
    except Exception:
        return None

fatal_change = pct_change(latest["fatalities"], prev["fatalities"])
acc_change = pct_change(latest["accidents"], prev["accidents"])
seatbelt_change = pct_change(latest["seatbelt_effect_pct"], prev["seatbelt_effect_pct"]) if len(df) >= 2 else None

# KPI 카드
col1, col2, col3, col4 = st.columns(4)
col1.metric("사망자 수", f"{int(latest['fatalities']):,}명", f"{fatal_change:.1f}%" if fatal_change else "")
col2.metric("사고 건수", f"{int(latest['accidents']):,}건", f"{acc_change:.1f}%" if acc_change else "")
col3.metric("안전벨트 효과", f"{latest['seatbelt_effect_pct']:.1f}%", f"{seatbelt_change:.1f}%" if seatbelt_change else "")
col4.metric("과속 치명률", f"{latest['speeding_fatal_pct']:.0f}%")

st.markdown("---")

# 연도별 추이
st.subheader("연도별 추이")
line_base = alt.Chart(df).encode(x=alt.X('year:O', title='연도'))
fatal_line = line_base.mark_line(point=True, color='#e53935').encode(y=alt.Y('fatalities:Q', title='사망자 수'))
acc_line = line_base.mark_line(point=True, color='#428AF7').encode(y=alt.Y('accidents:Q', title='사고 건수'))
st.altair_chart((fatal_line | acc_line).resolve_scale(y='independent'), use_container_width=True)

# 인사이트
st.subheader("주요 인사이트")
st.info("교통사고 사망자는 전년 대비 감소 추세입니다.")
st.info("안전벨트 착용률 향상은 사망률 감소에 기여합니다.")
st.info("과속은 여전히 치명적 사고의 주요 원인입니다.")

# 데이터 테이블
st.subheader("데이터 테이블")
st.dataframe(df, use_container_width=True)