import pandas as pd
from sqlalchemy import create_engine, text # text 함수 import
import sys
import os

# --- 1. Visualizer 클래스 Import ---
# analyzer/visualizer.py 에 파일이 있다고 가정합니다.
try:
    from web_design.visualizer import AccidentVisualizer
    print("성공: 'analyzer.visualizer'를 찾았습니다.")
except ImportError:
    try:
        from visualizer import AccidentVisualizer
        print("성공: 'visualizer'를 찾았습니다. (같은 폴더)")
    except ImportError as e:
        print(f"오류: 'analyzer/visualizer.py' 또는 'visualizer.py'를 찾을 수 없습니다.")
        print(f"상세 오류: {e}")
        sys.exit()

# --- 2. DB 연결 설정 (app.py와 동일) ---
MYSQL_USER = 'skn22'
MYSQL_PASSWORD = 'skn22'         # MySQL 비밀번호
MYSQL_HOST = 'localhost'         # 또는 127.0.0.1
MYSQL_PORT = '3306'
MYSQL_DB_NAME = 'project_1'      # DB 이름

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB_NAME}?charset=utf8mb4"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1")) # 간단한 쿼리로 연결 테스트
    print(f"성공: MySQL '{MYSQL_DB_NAME}' 데이터베이스에 연결했습니다.")
except ImportError:
    print("오류: 'PyMySQL' 라이브러리를 찾을 수 없습니다.")
    print("터미널에서 'pip install pymysql'을 실행해주세요.")
    sys.exit()
except Exception as e:
    print(f"DB 연결 오류: {e}")
    print("DB 설정(사용자, 비밀번호, 호스트, DB 이름)을 확인하세요.")
    sys.exit()

# --- 3. Visualizer 인스턴스 생성 ---
viz = AccidentVisualizer(engine)
print("AccidentVisualizer 인스턴스가 성공적으로 생성되었습니다.")


# --- 4. 테스트 1: 사용 가능한 컬럼 목록 ---
print("\n" + "="*30)
print("테스트 1: get_available_columns()")
print("="*30)
# 이제 '한글 레이블' 목록이 반환됩니다.
columns = viz.get_available_columns()
print(f"사용 가능한 한글 레이블 ({len(columns)}개):")
print(columns)


# --- 5. 테스트 2: 막대 차트 (Case 1: 범주형 vs 수치형) ---
print("\n" + "="*30)
print("테스트 2: Bar Chart 생성 (수직, 상위 20개)")
print("변수: '지역명 (시군구)' vs '사고건수'")
print("="*30)
# 내부 DB 이름 대신 한글 레이블을 사용합니다.
label1 = '지역명 (시군구)'
label2 = '사고건수'

fig1, title1 = viz.generate_visualization(label1, label2)

if fig1:
    print(f"성공: '{title1}' 차트 생성 완료.")
    print("-> 브라우저에서 차트를 엽니다...")
    fig1.show()
else:
    print(f"실패: 차트 생성 중 오류: {title1}")


# --- 6. 테스트 3: 그룹형 막대 차트 (Case 3: 범주형 vs 범주형) ---
print("\n" + "="*30)
print("테스트 3: 그룹형 막대 차트 생성")
print("변수: '주야' vs '사고유형'")
print("="*30)
# 한글 레이블 사용
label3 = '주야'
label4 = '사고유형'

fig2, title2 = viz.generate_visualization(label3, label4)

if fig2:
    print(f"성공: '{title2}' 차트 생성 완료.")
    print("-> 브라우저에서 차트를 엽니다...")
    fig2.show()
else:
    print(f"실패: 차트 생성 중 오류: {title2}")


# --- 7. 테스트 4: 다중 라인 차트 (Case 5: 시간형 vs 범주형) ---
print("\n" + "="*30)
print("테스트 4: Multi-Line Chart 생성")
print("변수: '발생년월' vs '운전자 성별'")
print("="*30)
# 한글 레이블 사용
label5 = '발생년월'
label6 = '운전자 성별'

fig3, title3 = viz.generate_visualization(label5, label6)

if fig3:
    print(f"성공: '{title3}' 차트 생성 완료.")
    print("-> 브라우저에서 차트를 엽니다...")
    fig3.show()
else:
    print(f"실패: 차트 생성 중 오류: {title3}")


# --- 8. 테스트 5: 라인 차트 (Case 2: 시간형 vs 수치형) ---
print("\n" + "="*30)
print("테스트 5: 라인 차트 (Case 2)")
print("변수: '발생년월' vs '사망자수'")
print("="*30)
# 한글 레이블 사용
label7 = '발생년월'
label8 = '사망자수'

fig4, title4 = viz.generate_visualization(label7, label8)

if fig4:
    print(f"성공: '{title4}' 차트 생성 완료.")
    print("-> 브라우저에서 차트를 엽니다...")
    fig4.show()
else:
    print(f"실패: 차트 생성 중 오류: {title4}")


# --- 9. 테스트 6: 버블 차트 (Case 4: 수치형 vs 수치형) ---
print("\n" + "="*30)
print("테스트 6: 버블 차트 (Case 4)")
print("변수: '중상자수' vs '경상자수'")
print("="*30)
# 한글 레이블 사용
label9 = '중상자수'
label10 = '경상자수'

fig5, title5 = viz.generate_visualization(label9, label10)

if fig5:
    print(f"성공: '{title5}' 차트 생성 완료.")
    print("-> 브라우저에서 차트를 엽니다...")
    fig5.show()
else:
    print(f"실패: 차트 생성 중 오류: {title5}")


print("\n" + "="*30)
print("모든 테스트가 완료되었습니다.")
print("="*30)

# DB 엔진 리소스 해제
engine.dispose()