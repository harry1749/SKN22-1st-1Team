import pandas as pd
from sqlalchemy import create_engine, text
import sys

# --- 1. 설정 (사용자 제공 값으로 하드코딩) ---
CSV_FILE = 'accident_df_preprocessed.csv'

MYSQL_USER = 'skn22'
MYSQL_PASSWORD = 'skn22'     # MySQL 비밀번호
MYSQL_HOST = 'localhost'     # 또는 127.0.0.1
MYSQL_PORT = '3306'
MYSQL_DB_NAME = 'project_1'  # 사용자가 생성한 DB 이름

# SQLAlchemy 연결 문자열 생성 (PyMySQL 드라이버 사용)
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB_NAME}?charset=utf8mb4"

# --- 2. DB 엔진 생성 및 연결 ---
try:
  engine = create_engine(DATABASE_URL)
  with engine.connect() as conn:
    print(f"MySQL '{MYSQL_DB_NAME}' 데이터베이스에 성공적으로 연결했습니다.")
except ImportError:
  print("오류: 'PyMySQL' 라이브러리를 찾을 수 없습니다.")
  print("터미널에서 'pip install pymysql'을 실행해주세요.")
  sys.exit()
except Exception as e:
  print(f"DB 연결 오류: {e}")
  print("DB 설정(사용자, 비밀번호, 호스트, DB 이름)을 확인하세요.")
  sys.exit()

# --- 3. CSV 데이터 읽기 ---
try:
  df = pd.read_csv(CSV_FILE)
  # 날짜 컬럼은 datetime으로 다시 변환 (Year, Month 추출을 위해)
  df['발생일시'] = pd.to_datetime(df['발생일시'])
  print(f"'{CSV_FILE}' 읽기 완료 (행: {len(df)})")
except FileNotFoundError:
  print(f"오류: '{CSV_FILE}'을 찾을 수 없습니다. 전처리 스크립트를 먼저 실행하세요.")
  engine.dispose()
  sys.exit()
except Exception as e:
  print(f"CSV 읽기 오류: {e}")
  engine.dispose()
  sys.exit()

# --- 4. ETL (Extract, Transform, Load) 시작 ---
print("ETL (Extract, Transform, Load)을 시작합니다...")

try:
  # --- 4a. REGION 차원 테이블 준비 ---
  print("REGION 테이블 확인 및 동기화 중...")
  
  # 1. DB에서 현재 REGION 맵 읽기
  try:
    db_regions_df = pd.read_sql("SELECT RegionCode, RegionName FROM REGION", engine)
    print(f"기존 REGION 테이블에서 {len(db_regions_df)}건 로드됨.")
  except Exception as e:
    print(f"REGION 테이블 읽기 오류: {e}. 스키마가 DDL과 일치하는지 확인하세요.")
    raise e

  # 2. CSV에서 고유 시군구 목록(RegionName) 추출
  csv_regions_set = set(df['시군구'].unique())
  
  # 3. DB에 없는 새로운 시군구(RegionName) 찾기
  existing_region_names = set(db_regions_df['RegionName'])
  new_region_names = csv_regions_set - existing_region_names
  
  if new_region_names:
    print(f"새로운 REGION {len(new_region_names)}건 발견. DB에 추가합니다...")
    
    # 4. 새 RegionCode 생성 (예: R001, R002...)
    # 마지막 RegionCode에서 숫자 부분 추출
    last_code_num = 0
    if not db_regions_df.empty:
      last_code_num = db_regions_df['RegionCode'].str.replace('R', '').astype(int).max()
      
    new_regions_list = []
    for i, name in enumerate(new_region_names, 1):
      new_code = f"R{last_code_num + i:03d}" # R001, R002...
      new_regions_list.append({'RegionCode': new_code, 'RegionName': name})
      
    # 5. 새 REGION 데이터를 DB에 적재
    new_regions_df = pd.DataFrame(new_regions_list)
    new_regions_df.to_sql('REGION', engine, if_exists='append', index=False)
    print(f"{len(new_regions_df)}건 REGION 테이블에 추가 완료.")
    
    # 6. 전체 REGION 맵 다시 로드
    all_regions_map = pd.read_sql("SELECT RegionCode, RegionName FROM REGION", engine)
  else:
    print("CSV의 모든 REGION이 DB에 이미 존재합니다.")
    all_regions_map = db_regions_df.copy()

  # --- 4b. 메인 DF에 REGION FK(RegionCode) 매핑 ---
  df = pd.merge(df, all_regions_map, left_on='시군구', right_on='RegionName', how='left')
  
  # 누락된 RegionCode가 있는지 확인 (있으면 안 됨)
  if df['RegionCode'].isnull().any():
    print("오류: 일부 행의 RegionCode를 매핑할 수 없습니다.")
    missing = df[df['RegionCode'].isnull()]['시군구'].unique()
    print(f"매핑 실패한 시군구: {missing}")
    raise ValueError("RegionCode 매핑 실패")

  # --- 4c. 메인 DF에 스키마 맞게 데이터 변환 ---
  print("데이터프레임 전처리 중 (스키마 매핑)...")
  
  # OccurYearMonth (YYYYMM)
  df['OccurYearMonth'] = df['Year'].astype(str) + df['Month'].astype(str).str.zfill(2)
  
  # LawViolationYn (Y/N)
  # '법규위반' 컬럼에 값이 있으므로 'Y'로 간주 (스키마 제약조건)
  df['LawViolationYn'] = 'Y'
  
  # Gender (M/F/O/N)
  gender_map = {'남': 'M', '여': 'F', '기타불명': 'O', '해당없음': 'N'}
  df['g_gender_mapped'] = df['가해운전자 성별'].map(gender_map).fillna('O') # 기본값 'Other'
  df['p_gender_mapped'] = df['피해운전자 성별'].map(gender_map).fillna('N') # 기본값 'N/A'
  
  # --- 4d. ACCIDENT / DRIVER 테이블 적재 (Row-by-Row 트랜잭션) ---
  print(f"ACCIDENT 및 DRIVER 테이블 적재 시작 (총 {len(df)}건)...")
  
  # SQL 쿼리 정의 (text() 사용)
  # 컬럼 이름은 DDL과 정확히 일치해야 함
  sql_insert_accident = text("""
    INSERT INTO ACCIDENT (
      OccurYearMonth, DayNight, RegionCode, Description, 
      DeathCount, SevereInjuryCount, MinorInjuryCount, ReportedInjuryCount, 
      AccidentType, LawViolationYn, RoadSurfaceState, WeatherState, RoadForm
    ) VALUES (
      :OccurYearMonth, :DayNight, :RegionCode, :Description, 
      :DeathCount, :SevereInjuryCount, :MinorInjuryCount, :ReportedInjuryCount, 
      :AccidentType, :LawViolationYn, :RoadSurfaceState, :WeatherState, :RoadForm
    )
  """)
  
  # DRIVER 테이블의 `Role` 컬럼은 백틱(`)으로 감싸야 함 (예약어)
  sql_insert_driver = text("""
    INSERT INTO DRIVER (
      AccidentID, `Role`, VehicleType, Gender, AgeGroup, InjuryLevel
    ) VALUES (
      :AccidentID, :Role, :VehicleType, :Gender, :AgeGroup, :InjuryLevel
    )
  """)

  # --- [수정됨] 기존 데이터 삭제 쿼리 정의 ---
  sql_delete_drivers = text("DELETE FROM DRIVER")
  sql_delete_accidents = text("DELETE FROM ACCIDENT")
  # --- [수정 완료] ---

  inserted_count = 0
  # .begin()을 사용하여 트랜잭션 시작
  with engine.begin() as conn:
    
    # --- [수정됨] 트랜잭션 내부에서 기존 데이터 삭제 ---
    # 외래 키 제약조건(DRIVER.AccidentID -> ACCIDENT.AccidentID) 때문에
    # 반드시 DRIVER 테이블부터 삭제해야 합니다.
    print("기존 DRIVER 테이블 데이터 삭제 중...")
    conn.execute(sql_delete_drivers)
    
    print("기존 ACCIDENT 테이블 데이터 삭제 중...")
    conn.execute(sql_delete_accidents)
    print("기존 데이터 삭제 완료. 새 데이터 삽입을 시작합니다.")
    # --- [수정 완료] ---
    
    for index, row in df.iterrows():
      try:
        # 1. ACCIDENT 행 INSERT
        acc_params = {
          "OccurYearMonth": row['OccurYearMonth'],
          "DayNight": row['주야'],
          "RegionCode": row['RegionCode'], # 4b에서 매핑됨
          "Description": row['사고내용'],
          "DeathCount": row['사망자수'],
          "SevereInjuryCount": row['중상자수'],
          "MinorInjuryCount": row['경상자수'],
          "ReportedInjuryCount": row['부상신고자수'],
          "AccidentType": row['사고유형'],
          "LawViolationYn": row['LawViolationYn'], # 4c에서 매핑됨
          "RoadSurfaceState": row['노면상태'],
          "WeatherState": row['기상상태'],
          "RoadForm": row['도로형태']
        }
        result = conn.execute(sql_insert_accident, acc_params)
        
        # 2. 방금 생성된 AccidentID (AUTO_INCREMENT 값) 가져오기
        new_accident_id = result.lastrowid
        
        # 3. DRIVER (가해) 행 INSERT
        driver_g_params = {
          "AccidentID": new_accident_id,
          "Role": "가해",
          "VehicleType": row['가해운전자 차종'],
          "Gender": row['g_gender_mapped'], # 4c에서 매핑됨
          "AgeGroup": row['가해운전자 연령대'],
          "InjuryLevel": row['가해운전자 상해정도']
        }
        conn.execute(sql_insert_driver, driver_g_params)
        
        # 4. DRIVER (피해) 행 INSERT (존재하는 경우)
        if row['피해운전자 차종'] != '해당없음':
          driver_p_params = {
            "AccidentID": new_accident_id,
            "Role": "피해",
            "VehicleType": row['피해운전자 차종'],
            "Gender": row['p_gender_mapped'], # 4c에서 매핑됨
            "AgeGroup": row['피해운전자 연령대'],
            "InjuryLevel": row['피해운전자 상해정도']
          }
          conn.execute(sql_insert_driver, driver_p_params)
        
        inserted_count += 1
        
        # 진행 상황 출력
        if (inserted_count % 1000) == 0:
          print(f"  ... {inserted_count} / {len(df)} 건 처리 완료 ...")
          
      except Exception as e:
        print(f"오류: {index}번 행 데이터 적재 중 문제 발생: {e}")
        print(f"데이터: {row}")
        raise e # 오류 발생 시 트랜잭션 롤백

  print(f"\n--- 모든 데이터 적재 완료! (총 {inserted_count}건의 사고 및 관련 운전자 정보) ---")

except Exception as e:
  print(f"ETL 프로세스 중 심각한 오류 발생: {e}")
finally:
  # 엔진 리소스 해제
  engine.dispose()
  print("데이터베이스 엔진 연결을 종료했습니다.")