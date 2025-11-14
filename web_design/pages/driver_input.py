import streamlit as st
import sys
import os
from sqlalchemy import create_engine
import plotly.express as px

# --- 1. 모듈 Import 경로 설정 ---
# 이 파일이 'pages/' 폴더 안에 있다고 가정하고,
# 상위 폴더(프로젝트 루트)를 시스템 경로에 추가합니다.
# (예: /my_project/pages/driver_input.py -> /my_project/ 를 추가)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # 'web_design/' 폴더에 있는 'visualizer.py' 파일에서 클래스를 가져옵니다.
    from visualizer import AccidentVisualizer
except ImportError:
    st.error("치명적 오류: 'web_design/visualizer.py' 모듈을 찾을 수 없습니다. 파일 경로를 확인하세요.")
    st.stop() # 모듈이 없으면 앱 실행 중지


# --- 2. DB 연결 및 Visualizer 초기화 ---
# @st.cache_resource: Streamlit의 캐시 기능을 사용해 DB 연결(engine)과
# Visualizer 객체 생성을 앱 세션 동안 한 번만 수행합니다.
@st.cache_resource
def init_visualizer():
    """
    DB에 연결하고 AccidentVisualizer 객체를 초기화합니다.
    연결 실패 시 None을 반환합니다.
    """
    MYSQL_USER = 'skn22'
    MYSQL_PASSWORD = 'skn22'
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = '3306'
    MYSQL_DB_NAME = 'project_1'
    
    try:
        DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB_NAME}?charset=utf8mb4"
        engine = create_engine(DATABASE_URL)
        # 연결 테스트 (실패를 빨리 감지)
        with engine.connect() as conn:
            pass  # 연결 성공
        
        # Visualizer 객체 생성
        viz = AccidentVisualizer(engine)
        return viz
    
    except ImportError:
        # PyMySQL이 설치되지 않았을 경우
        st.error("DB 연결 오류: 'PyMySQL' 라이브러리가 필요합니다. (터미널에서: pip install pymysql)")
        return None  # st.stop() 대신 None 반환
    except Exception as e:
        # DB 연결 자체에 실패했을 경우 (서버 다운, 인증 실패 등)
        st.error(f"DB 연결 실패: {e}. (DB 서버 상태, 사용자/비밀번호, DB 이름 확인)")
        return None  # st.stop() 대신 None 반환

# --- 3. 페이지 설정 및 UI ---
st.set_page_config(page_title="2-Variable 분석", layout="wide")

# ===== 메인페이지 이동 버튼 (타이틀 상단) =====
if st.button("← 메인페이지로 이동", key="main_btn"):
    # 메인 앱 파일 이름이 'Safe_drive_app.py'인지 확인하세요.
    st.switch_page("Safe_drive_app.py") 

# ===== 타이틀 =====
st.title("교통사고 시각화 분석")
st.subheader("두 개의 변수를 선택해주세요")

# Visualizer 객체 로드 시도
viz = init_visualizer()
# viz 객체가 None인지 (초기화 실패) 확인합니다.
if viz is None:
    st.error("Visualizer 초기화에 실패했습니다. DB 연결 상태를 확인하고 페이지를 새로고침하세요.")
    st.stop() # 여기서 메인 스크립트 실행을 중지시킵니다.

try:
    korean_labels = viz.get_available_columns()
except Exception as e:
    st.error(f"컬럼 목록 로드 실패: {e}. 'visualizer.py' 또는 DB 스키마를 확인하세요.")
    korean_labels = [] # 비어있는 리스트로 설정하여 하위 코드 실행
    st.stop()




# ===== 입력 박스 (Visualizer와 연동) =====
# 컬럼 목록이 비어있지 않은 경우에만 selectbox를 표시
if korean_labels:
    st.markdown('<div class="box1">', unsafe_allow_html=True)
    # index=0 : 목록의 첫 번째 항목('사고건수')이 기본 선택되도록 설정
    label1 = st.selectbox("첫 번째 변수를 선택하세요:", korean_labels, index=0, key="var1")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="box2">', unsafe_allow_html=True)
    # index=1 : 목록의 두 번째 항목('사고유형')이 기본 선택되도록 설정
    label2 = st.selectbox("두 번째 변수를 선택하세요:", korean_labels, index=1, key="var2")
    st.markdown('</div>', unsafe_allow_html=True)

    # ===== 분석 버튼 =====
    if st.button("시각화 자료 생성하기", key="analyze_btn", use_container_width=True):
        if label1 == label2:
            st.warning("서로 다른 두 개의 변수를 선택하세요.")
        else:
            # visualizer 객체를 사용하여 차트 생성
            with st.spinner(f"'{label1}'와(과) '{label2}' 관계를 분석 중입니다..."):
                try:
                    fig, title = viz.generate_visualization(label1, label2)
                    
                    # 결과를 세션 상태에 저장 (페이지가 새로고침되어도 유지됨)
                    if fig:
                        st.session_state['last_fig'] = fig
                        st.session_state['last_title'] = title
                    else:
                        # fig가 None이면 오류 발생
                        st.session_state['last_fig'] = None
                        st.session_state['last_title'] = title # title에 오류 메시지가 담겨 있음
                
                except Exception as e:
                    st.error(f"시각화 생성 중 오류 발생: {e}")
                    st.session_state['last_fig'] = None
                    st.session_state['last_title'] = "시각화 생성 실패"

# ===== 차트 출력 =====
# 세션 상태에 저장된 차트가 있으면 화면에 표시
if 'last_fig' in st.session_state:
    if st.session_state['last_fig']:
        st.write(f"### {st.session_state['last_title']}")
        st.plotly_chart(st.session_state['last_fig'], use_container_width=True)
    else:
        # 차트 생성 실패 시 (fig is None 또는 오류 발생)
        st.error(f"차트 생성 실패: {st.session_state['last_title']}")