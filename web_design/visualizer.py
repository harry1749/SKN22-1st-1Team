import pandas as pd
import plotly.express as px
from sqlalchemy.engine import Engine
from sqlalchemy import text # SQLAlchemy 쿼리 실행을 위해 import
import logging

# 로깅 설정 (디버깅에 용이)
logging.basicConfig(level=logging.INFO)

class AccidentVisualizer:
    """
    사고 데이터베이스(traffic_safety 스키마)를 기반으로 
    2-variable 시각화를 생성하는 OOP 클래스.
    Streamlit 앱에서 이 클래스를 가져와 사용합니다.
    """
    
    # DB 스키마를 기반으로 각 컬럼의 "유형"을 미리 정의합니다.
    # 이 딕셔너리는 시각화 로직 분기의 핵심입니다.
    COLUMN_TYPES = {
        # --- 범주형 (Categorical) ---
        'ACCIDENT.DayNight': '범주형',
        'ACCIDENT.AccidentType': '범주형',
        'ACCIDENT.LawViolationYn': '범주형',
        'ACCIDENT.RoadSurfaceState': '범주형',
        'ACCIDENT.WeatherState': '범주형',
        'ACCIDENT.RoadForm': '범주형',
        'REGION.RegionName': '범주형',
        'DRIVER.Role': '범주형',
        'DRIVER.VehicleType': '범주형',
        'DRIVER.Gender': '범주형',
        'DRIVER.AgeGroup': '범주형',
        'DRIVER.InjuryLevel': '범주형',
        
        # --- 수치형 (Numerical) ---
        'ACCIDENT.DeathCount': '수치형',
        'ACCIDENT.SevereInjuryCount': '수치형',
        'ACCIDENT.MinorInjuryCount': '수치형',
        'ACCIDENT.ReportedInjuryCount': '수치형',
        # '(사고건수)'는 실제 컬럼이 아닌, UI에서 선택 가능한 가상 컬럼입니다.
        'ACCIDENT.(사고건수)': '수치형', 
        
        # --- 시간형 (Temporal) ---
        'ACCIDENT.OccurYearMonth': '시간형'
    }

    def __init__(self, engine: Engine):
        """
        Streamlit 앱 (app.py)에서 생성한 SQLAlchemy 엔진을 
        주입받아 클래스 인스턴스를 초기화합니다.
        """
        self.engine = engine
        logging.info("AccidentVisualizer가 DB 엔진으로 초기화되었습니다.")

    def get_available_columns(self) -> list:
        """
        Streamlit의 selectbox에 사용할 분석 가능한 컬럼 목록을 반환합니다.
        """
        return sorted(list(self.COLUMN_TYPES.keys()))

    def _get_column_type(self, column_name: str) -> str:
        """
        컬럼명을 기반으로 미리 정의된 유형(범주형, 수치형, 시간형)을 반환합니다.
        """
        return self.COLUMN_TYPES.get(column_name, '알 수 없음')

    def _build_query_components(self, var1: str, var2: str, agg_func: str = None):
        """
        두 변수를 기반으로 SQL 쿼리의 핵심 구성요소(SELECT, FROM, JOIN, GROUP BY)를 생성합니다.
        이 헬퍼 함수는 코드 중복을 줄여줍니다.
        """
        # 1. 테이블과 컬럼 분리 (예: 'ACCIDENT.DayNight' -> 'ACCIDENT', 'DayNight')
        table1, col1 = var1.split('.')
        table2, col2 = var2.split('.')
        
        # 2. 필요한 테이블 식별 (항상 ACCIDENT는 기본)
        tables_needed = set(['ACCIDENT', table1, table2])
        
        # 3. FROM 및 JOIN 절 구성
        from_clause = "FROM ACCIDENT"
        join_clause = ""
        # 필요한 테이블에 따라 JOIN을 동적으로 추가
        if 'DRIVER' in tables_needed:
            join_clause += " JOIN DRIVER ON ACCIDENT.AccidentID = DRIVER.AccidentID"
        if 'REGION' in tables_needed:
            join_clause += " JOIN REGION ON ACCIDENT.RegionCode = REGION.RegionCode"
            
        # 4. SELECT 및 GROUP BY 절 구성
        if agg_func: # 집계가 필요한 경우 (예: SUM, COUNT)
            # 가상 컬럼 '(사고건수)' 처리
            if col2 == '(사고건수)':
                select_col2 = "COUNT(ACCIDENT.AccidentID)"
            else:
                select_col2 = f"{agg_func}({table2}.{col2})"
                
            select_clause = f"SELECT {table1}.{col1}, {select_col2} AS Value"
            group_by_clause = f"GROUP BY {table1}.{col1}"
            order_by_clause = f"ORDER BY {table1}.{col1}" # 시간형일 경우를 대비
        else:
            # 집계가 없는 경우 (예: 2D 히트맵)
            select_clause = f"SELECT {table1}.{col1}, {table2}.{col2}"
            group_by_clause = ""
            order_by_clause = ""
            
        return select_clause, from_clause, join_clause, group_by_clause, order_by_clause

    def generate_visualization(self, var1: str, var2: str):
        """
        두 변수를 입력받아 적절한 시각화 차트(Plotly Figure)를 생성하는 메인 메서드.
        Streamlit 앱에서 이 메서드를 호출합니다.
        """
        type1 = self._get_column_type(var1)
        type2 = self._get_column_type(var2)
        
        logging.info(f"시각화 생성 시작: {var1}({type1}) vs {var2}({type2})")

        try:
            # Case 1: 범주형 vs 수치형 -> 수직 막대 차트 (수정됨)
            if (type1 == '범주형' and type2 == '수치형'):
                return self._create_bar_chart(var1, var2)
            if (type1 == '수치형' and type2 == '범주형'):
                # 변수 순서만 바꿔서 동일 함수 호출
                return self._create_bar_chart(var2, var1) 

            # Case 2: 시간형 vs 수치형 -> 라인 차트
            if (type1 == '시간형' and type2 == '수치형'):
                return self._create_line_chart(var1, var2)
            if (type1 == '수치형' and type2 == '시간형'):
                # 변수 순서만 바꿔서 동일 함수 호출
                return self._create_line_chart(var2, var1) 

            # Case 3: 범주형 vs 범주형 -> 그룹형 막대 차트
            if (type1 == '범주형' and type2 == '범주형'):
                # Y축 값은 '(사고건수)'로 고정
                return self._create_grouped_bar_chart(var1, var2, 'ACCIDENT.(사고건수)')

            # Case 4: 수치형 vs 수치형 -> 2D 밀도 히트맵 (논의 중)
            if (type1 == '수치형' and type2 == '수치형'):
                # (사고건수)는 집계 컬럼이므로 이 분석에서 제외
                if '(사고건수)' in var1 or '(사고건수)' in var2:
                    return None, "이 시각화는 '(사고건수)'를 지원하지 않습니다."
                return self._create_density_heatmap(var1, var2) 

            # Case 5: 시간형 vs 범주형 -> 다중 라인 차트
            if (type1 == '시간형' and type2 == '범주형'):
                # Y축 값은 '(사고건수)'로 고정
                return self._create_multi_line_chart(var1, var2, 'ACCIDENT.(사고건수)')
            if (type1 == '범주형' and type2 == '시간형'):
                # 변수 순서만 바꿔서 동일 함수 호출
                return self._create_multi_line_chart(var2, var1, 'ACCIDENT.(사고건수)')

            return None, "선택된 조합에 대한 시각화를 생성할 수 없습니다."

        except Exception as e:
            logging.error(f"시각화 생성 중 오류: {e}")
            return None, f"차트 생성 중 오류가 발생했습니다: {e}"

    def _fetch_data(self, query: str) -> pd.DataFrame:
        """
        SQL 쿼리를 실행하여 Pandas DataFrame으로 반환합니다.
        SQLAlchemy의 text() 함수를 사용하여 SQL Injection에 대비합니다.
        """
        logging.info(f"Executing SQL: {query}")
        with self.engine.connect() as conn:
            # text() 함수를 사용하여 쿼리 문자열을 안전하게 처리
            df = pd.read_sql(text(query), conn)
        logging.info(f"Data fetched: {len(df)} rows")
        return df

    # --- Case 1: 수직 막대 차트 (범주형 vs 수치형) ---
    def _create_bar_chart(self, cat_var: str, num_var: str):
        """
        수직 막대 차트 생성 (상위 20개).
        """
        title = f"'{cat_var}' 별 '{num_var}' (상위 20개)"
        agg_func = "COUNT" if '(사고건수)' in num_var else "SUM"
        
        # SQL 쿼리 빌드
        sel, frm, jn, grp, _ = self._build_query_components(cat_var, num_var, agg_func)
        
        # 값이 높은 상위 20개만 조회하도록 SQL 수정
        query = f"{sel} {frm} {jn} {grp} ORDER BY Value DESC LIMIT 20"
        
        df = self._fetch_data(query)
        
        # 수평 -> 수직으로 변경
        fig = px.bar(df, 
                     x=cat_var.split('.')[1],     # X축에 범주
                     y='Value',                   # Y축에 수치
                     title=title,
                     labels={cat_var.split('.')[1]: cat_var, 'Value': num_var})
        
        # X축 레이아웃을 'category'로 명시
        fig.update_xaxes(type='category') 
        
        return fig, title

    # --- Case 2: 라인 차트 (시간형 vs 수치형) ---
    def _create_line_chart(self, time_var: str, num_var: str):
        """
        시간 흐름에 따른 수치 변화를 보여주는 라인 차트 생성.
        """
        title = f"'{time_var}' 별 '{num_var}' 추이"
        agg_func = "COUNT" if '(사고건수)' in num_var else "SUM"
        
        sel, frm, jn, grp, odr = self._build_query_components(time_var, num_var, agg_func)
        query = f"{sel} {frm} {jn} {grp} {odr}" # 시간순 정렬 포함

        df = self._fetch_data(query)

        fig = px.line(df, 
                      x=time_var.split('.')[1], 
                      y='Value', 
                      title=title,
                      labels={time_var.split('.')[1]: time_var, 'Value': num_var}, 
                      markers=True) # 각 데이터 포인트를 점으로 표시
        return fig, title

    # --- Case 3: 그룹형 막대 차트 (범주형 vs 범주형) ---
    def _create_grouped_bar_chart(self, var1: str, var2: str, num_var: str):
        """
        두 범주형 변수를 교차 분석하는 그룹형 막대 차트 생성.
        Y축은 (사고건수)로 고정.
        """
        title = f"'{var1}'와 '{var2}' 별 '{num_var}' (그룹형 막대 차트)"
        
        table1, col1 = var1.split('.') # X축
        table2, col2 = var2.split('.') # Color (범례)
        table3, col3 = num_var.split('.') # Y축
        
        # Y축 값(num_var)에 대한 집계 로직
        agg_val = "COUNT(ACCIDENT.AccidentID)" if col3 == '(사고건수)' else f"SUM({table3}.{col3})"
        
        # 쿼리 빌드 (3개 변수 고려)
        select_clause = f"SELECT {table1}.{col1}, {table2}.{col2}, {agg_val} AS Value"
        tables_needed = set(['ACCIDENT', table1, table2, table3])
        from_clause = "FROM ACCIDENT"
        join_clause = ""
        if 'DRIVER' in tables_needed:
            join_clause += " JOIN DRIVER ON ACCIDENT.AccidentID = DRIVER.AccidentID"
        if 'REGION' in tables_needed:
            join_clause += " JOIN REGION ON ACCIDENT.RegionCode = REGION.RegionCode"
        group_by_clause = f"GROUP BY {table1}.{col1}, {table2}.{col2}"
        
        query = f"{select_clause} {from_clause} {join_clause} {group_by_clause}"
        
        df = self._fetch_data(query)
        
        fig = px.bar(df, 
                     x=col1,        # X축
                     y='Value',     # Y축
                     color=col2,    # 범례
                     barmode='group', # 'group' = 그룹형, 'stack' = 누적형
                     title=title,
                     labels={col1: var1, col2: var2, 'Value': num_var})
        return fig, title

    # --- Case 4: 2D 밀도 히트맵 (수치형 vs 수치형) ---
    def _create_density_heatmap(self, var1: str, var2: str):
        """
        (논의 중) 두 수치형 변수 간의 밀도를 보여주는 2D 히트맵 생성.
        겹치는 정수형 데이터(Overplotting) 문제 해결.
        """
        title = f"'{var1}'와 '{var2}' 간의 밀도 (2D 히트맵)"
        
        # 쿼리는 집계(GROUP BY) 없이 원본 데이터를 가져옴
        sel, frm, jn, _, _ = self._build_query_components(var1, var2)
        # 데이터가 많을수록 히트맵이 정확. (10,000건 샘플링)
        query = f"{sel} {frm} {jn} LIMIT 10000" 
        
        df = self._fetch_data(query)
        
        col1 = var1.split('.')[1]
        col2 = var2.split('.')[1]
        
        if df.empty:
            return None, "데이터가 없어 2D 히트맵을 생성할 수 없습니다."

        fig = px.density_heatmap(df, 
                                 x=col1, 
                                 y=col2, 
                                 title=title,
                                 labels={col1: var1, col2: var2},
                                 marginal_x="histogram", # X축 상단에 히스토그램 추가
                                 marginal_y="histogram"  # Y축 우측에 히스토그램 추가
                                 )
        return fig, title

    # --- Case 5: 다중 라인 차트 (시간형 vs 범주형) ---
    def _create_multi_line_chart(self, time_var: str, cat_var: str, num_var: str):
        """
        시간 흐름에 따른 범주별 수치 변화를 비교하는 다중 라인 차트 생성.
        Y축은 (사고건수)로 고정.
        """
        title = f"'{time_var}'에 따른 '{cat_var}'별 '{num_var}' 추이"
        
        table1, col1 = time_var.split('.') # X축 (시간)
        table2, col2 = cat_var.split('.') # Color (범례)
        table3, col3 = num_var.split('.') # Y축
        
        agg_val = "COUNT(ACCIDENT.AccidentID)" if col3 == '(사고건수)' else f"SUM({table3}.{col3})"
        
        # 쿼리 빌드 (3개 변수 고려)
        select_clause = f"SELECT {table1}.{col1}, {table2}.{col2}, {agg_val} AS Value"
        tables_needed = set(['ACCIDENT', table1, table2, table3])
        from_clause = "FROM ACCIDENT"
        join_clause = ""
        if 'DRIVER' in tables_needed:
            join_clause += " JOIN DRIVER ON ACCIDENT.AccidentID = DRIVER.AccidentID"
        if 'REGION' in tables_needed:
            join_clause += " JOIN REGION ON ACCIDENT.RegionCode = REGION.RegionCode"
            
        group_by_clause = f"GROUP BY {table1}.{col1}, {table2}.{col2}"
        order_by_clause = f"ORDER BY {table1}.{col1}" # 시간순 정렬
        
        query = f"{select_clause} {from_clause} {join_clause} {group_by_clause} {order_by_clause}"
        
        df = self._fetch_data(query)
        
        fig = px.line(df, 
                      x=col1,       # X축 (시간)
                      y='Value',    # Y축
                      color=col2,   # 범례
                      title=title,
                      labels={col1: time_var, 'Value': num_var, col2: cat_var}, 
                      markers=True) # 각 데이터 포인트를 점으로 표시
        return fig, title