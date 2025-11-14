import pandas as pd
import plotly.express as px
from sqlalchemy.engine import Engine
from sqlalchemy import text
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

class AccidentVisualizer:
    """
    사고 데이터베이스(traffic_safety 스키마)를 기반으로
    2-variable 시각화를 생성하는 OOP 클래스.
    모든 입출력은 '한글 레이블'을 기준으로 하며,
    내부적으로 DB 컬럼명으로 변환하여 처리합니다.
    """
    
    # DB 스키마 기반의 컬럼 설정 (유형 + 한글 레이블)
    COLUMN_CONFIG = {
        # --- 범주형 (Categorical) ---
        'ACCIDENT.DayNight': {'type': '범주형', 'label': '주야'},
        'ACCIDENT.AccidentType': {'type': '범주형', 'label': '사고유형'},
        'ACCIDENT.LawViolationYn': {'type': '범주형', 'label': '법규위반 여부'},
        'ACCIDENT.RoadSurfaceState': {'type': '범주형', 'label': '노면상태'},
        'ACCIDENT.WeatherState': {'type': '범주형', 'label': '기상상태'},
        'ACCIDENT.RoadForm': {'type': '범주형', 'label': '도로형태'},
        'REGION.RegionName': {'type': '범주형', 'label': '지역명 (시군구)'},
        'DRIVER.Role': {'type': '범주형', 'label': '운전자 구분 (가해/피해)'},
        'DRIVER.VehicleType': {'type': '범주형', 'label': '운전자 차종'},
        'DRIVER.Gender': {'type': '범주형', 'label': '운전자 성별'},
        'DRIVER.AgeGroup': {'type': '범주형', 'label': '운전자 연령대'},
        'DRIVER.InjuryLevel': {'type': '범주형', 'label': '운전자 상해정도'},
        
        # --- 수치형 (Numerical) ---
        'ACCIDENT.DeathCount': {'type': '수치형', 'label': '사망자수'},
        'ACCIDENT.SevereInjuryCount': {'type': '수치형', 'label': '중상자수'},
        'ACCIDENT.MinorInjuryCount': {'type': '수치형', 'label': '경상자수'},
        'ACCIDENT.ReportedInjuryCount': {'type': '수치형', 'label': '부상신고자수'},
        'ACCIDENT.(사고건수)': {'type': '수치형', 'label': '사고건수'}, 
        
        # --- 시간형 (Temporal) ---
        'ACCIDENT.OccurYearMonth': {'type': '시간형', 'label': '발생년월'}
    }

    def __init__(self, engine: Engine):
        self.engine = engine
        # 한글 레이블 -> DB 컬럼명으로 변환하기 위한 역방향 맵 생성
        self.LABEL_TO_INTERNAL = {v['label']: k for k, v in self.COLUMN_CONFIG.items()}
        logging.info("AccidentVisualizer가 DB 엔진 및 한글 레이블 맵으로 초기화되었습니다.")

    def get_available_columns(self) -> list:
        """
        Streamlit의 selectbox에 사용할 '한글 레이블' 목록을 반환합니다.
        """
        return sorted(list(self.LABEL_TO_INTERNAL.keys()))

    def _get_internal_name(self, label: str) -> str:
        """
        한글 레이블을 받아 내부 DB 컬럼명을 반환합니다.
        """
        return self.LABEL_TO_INTERNAL.get(label)

    def _get_column_type(self, internal_name: str) -> str:
        """
        내부 DB 컬럼명을 기반으로 유형(범주형, 수치형, 시간형)을 반환합니다.
        """
        return self.COLUMN_CONFIG.get(internal_name, {}).get('type', '알 수 없음')

    def _build_query_components(self, var1: str, var2: str, agg_func: str = None):
        """
        [내부 함수] 두 '내부 컬럼명'을 기반으로 SQL 쿼리 구성요소를 생성합니다.
        (복잡한 쿼리는 각 차트 함수에서 직접 빌드합니다)
        """
        table1, col1 = var1.split('.')
        table2, col2 = var2.split('.')
        
        tables_needed = set(['ACCIDENT', table1, table2])
        
        from_clause = "FROM ACCIDENT"
        join_clause = ""
        if 'DRIVER' in tables_needed:
            join_clause += " JOIN DRIVER ON ACCIDENT.AccidentID = DRIVER.AccidentID"
        if 'REGION' in tables_needed:
            join_clause += " JOIN REGION ON ACCIDENT.RegionCode = REGION.RegionCode"
            
        if agg_func:
            if col2 == '(사고건수)':
                select_col2 = "COUNT(ACCIDENT.AccidentID)"
            else:
                # `col2`가 실제 컬럼명인지 확인 (예: 'DeathCount')
                safe_col2 = col2.replace("(", "").replace(")", "") # (사고건수) 방지
                select_col2 = f"{agg_func}({table2}.{safe_col2})"
                
            select_clause = f"SELECT {table1}.{col1}, {select_col2} AS Value"
            group_by_clause = f"GROUP BY {table1}.{col1}"
            order_by_clause = f"ORDER BY {table1}.{col1}"
        else:
            select_clause = f"SELECT {table1}.{col1}, {table2}.{col2}"
            group_by_clause = ""
            order_by_clause = ""
            
        return select_clause, from_clause, join_clause, group_by_clause, order_by_clause

    def generate_visualization(self, label1: str, label2: str):
        """
        [메인 함수] 두 개의 '한글 레이블'을 입력받아 적절한 시각화 차트를 생성합니다.
        """
        # 1. 한글 레이블 -> 내부 DB 컬럼명으로 변환
        var1 = self._get_internal_name(label1)
        var2 = self._get_internal_name(label2)

        if not var1 or not var2:
            return None, "선택된 변수명을 찾을 수 없습니다."

        # 2. 내부 컬럼명으로 유형 조회
        type1 = self._get_column_type(var1)
        type2 = self._get_column_type(var2)
        
        logging.info(f"시각화 생성 시작: {label1}({type1}) vs {label2}({type2})")

        try:
            # Case 1: 범주형 vs 수치형 -> 수직 막대 차트
            if (type1 == '범주형' and type2 == '수치형'):
                return self._create_bar_chart(var1, var2, label1, label2)
            if (type1 == '수치형' and type2 == '범주형'):
                return self._create_bar_chart(var2, var1, label2, label1) # 순서 변경

            # Case 2: 시간형 vs 수치형 -> 라인 차트
            if (type1 == '시간형' and type2 == '수치형'):
                return self._create_line_chart(var1, var2, label1, label2)
            if (type1 == '수치형' and type2 == '시간형'):
                return self._create_line_chart(var2, var1, label2, label1) # 순서 변경

            # Case 3: 범주형 vs 범주형 -> 그룹형 막대 차트
            if (type1 == '범주형' and type2 == '범주형'):
                num_label = '사고건수'
                num_var = self._get_internal_name(num_label)
                return self._create_grouped_bar_chart(var1, var2, num_var, label1, label2, num_label)

            # Case 4: 수치형 vs 수치형 -> 버블 차트 (수정됨)
            if (type1 == '수치형' and type2 == '수치형'):
                if '사고건수' in [label1, label2]:
                    return None, "이 시각화는 '사고건수'를 지원하지 않습니다."
                return self._create_bubble_chart(var1, var2, label1, label2)

            # Case 5: 시간형 vs 범주형 -> 다중 라인 차트
            if (type1 == '시간형' and type2 == '범주형'):
                num_label = '사고건수'
                num_var = self._get_internal_name(num_label)
                return self._create_multi_line_chart(var1, var2, num_var, label1, label2, num_label)
            if (type1 == '범주형' and type2 == '시간형'):
                num_label = '사고건수'
                num_var = self._get_internal_name(num_label)
                return self._create_multi_line_chart(var2, var1, num_var, label2, label1, num_label) # 순서 변경

            return None, "선택된 조합에 대한 시각화를 생성할 수 없습니다."

        except Exception as e:
            logging.error(f"시각화 생성 중 오류: {e}")
            return None, f"차트 생성 중 오류가 발생했습니다: {e}"

    def _fetch_data(self, query: str) -> pd.DataFrame:
        logging.info(f"Executing SQL: {query}")
        with self.engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
        logging.info(f"Data fetched: {len(df)} rows")
        return df

    # --- Case 1: 수직 막대 차트 (범주형 vs 수치형) ---
    def _create_bar_chart(self, cat_var: str, num_var: str, cat_label: str, num_label: str):
        title = f"'{cat_label}' 별 '{num_label}' (상위 20개)"
        agg_func = "COUNT" if '(사고건수)' in num_var else "SUM"
        
        sel, frm, jn, grp, _ = self._build_query_components(cat_var, num_var, agg_func)
        query = f"{sel} {frm} {jn} {grp} ORDER BY Value DESC LIMIT 20"
        
        df = self._fetch_data(query)
        col1_name = cat_var.split('.')[1]
        
        fig = px.bar(df, 
                     x=col1_name,
                     y='Value',
                     title=title,
                     labels={col1_name: cat_label, 'Value': num_label}) # 한글 레이블 적용
        fig.update_xaxes(type='category') # X축을 범주형으로 강제
        return fig, title

    # --- Case 2: 라인 차트 (시간형 vs 수치형) ---
    def _create_line_chart(self, time_var: str, num_var: str, time_label: str, num_label: str):
        title = f"'{time_label}' 별 '{num_label}' 추이"
        agg_func = "COUNT" if '(사고건수)' in num_var else "SUM"
        
        sel, frm, jn, grp, odr = self._build_query_components(time_var, num_var, agg_func)
        query = f"{sel} {frm} {jn} {grp} {odr}"

        df = self._fetch_data(query)
        col1_name = time_var.split('.')[1] # 'OccurYearMonth'
        
        # [시간축 버그 수정] '202201' 문자열을 datetime 객체로 변환
        try:
            df[col1_name] = pd.to_datetime(df[col1_name], format='%Y%m')
        except Exception as e:
            logging.warning(f"시간 변환 오류: {e}. 'OccurYearMonth' 형식이 'YYYYMM'이 아닐 수 있습니다.")
            pass # 변환 실패 시에도 일단 진행

        fig = px.line(df, 
                      x=col1_name,
                      y='Value', 
                      title=title,
                      labels={col1_name: time_label, 'Value': num_label}, # 한글 레이블 적용
                      markers=True)
        return fig, title

    # --- Case 3: 그룹형 막대 차트 (범주형 vs 범주형) ---
    def _create_grouped_bar_chart(self, var1: str, var2: str, num_var: str, 
                                  label1: str, label2: str, num_label: str):
        title = f"'{label1}'와 '{label2}' 별 '{num_label}' (그룹형 막대 차트)"
        
        table1, col1 = var1.split('.') # X축
        table2, col2 = var2.split('.') # Color (범례)
        table3, col3 = num_var.split('.') # Y축
        
        agg_val = "COUNT(ACCIDENT.AccidentID)" if col3 == '(사고건수)' else f"SUM({table3}.{col3})"
        
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
                     x=col1,
                     y='Value',
                     color=col2,
                     barmode='group',
                     title=title,
                     labels={col1: label1, col2: label2, 'Value': num_label}) # 한글 레이블 적용
        return fig, title

    # --- Case 4: 버블 차트 (수치형 vs 수치형) ---
    def _create_bubble_chart(self, var1: str, var2: str, label1: str, label2: str):
        title = f"'{label1}'와 '{label2}' 조합별 '사고건수' (버블 차트)"
        
        table1, col1 = var1.split('.') # X축
        table2, col2 = var2.split('.') # Y축
        
        # SQL 쿼리로 X, Y 조합별 건수(COUNT)를 미리 집계
        select_clause = f"SELECT {table1}.{col1}, {table2}.{col2}, COUNT(ACCIDENT.AccidentID) AS BubbleSize"
        tables_needed = set(['ACCIDENT', table1, table2])
        from_clause = "FROM ACCIDENT"
        join_clause = ""
        if 'DRIVER' in tables_needed:
            join_clause += " JOIN DRIVER ON ACCIDENT.AccidentID = DRIVER.AccidentID"
        if 'REGION' in tables_needed:
            join_clause += " JOIN REGION ON ACCIDENT.RegionCode = REGION.RegionCode"
        
        group_by_clause = f"GROUP BY {table1}.{col1}, {table2}.{col2}"
        query = f"{select_clause} {from_clause} {join_clause} {group_by_clause}"

        df = self._fetch_data(query)

        if df.empty:
            return None, "데이터가 없어 버블 차트를 생성할 수 없습니다."
        
        fig = px.scatter(df,
                         x=col1,
                         y=col2,
                         size='BubbleSize',  # 원의 크기를 '사고건수'로 매핑
                         color='BubbleSize', # 원의 색상도 '사고건수'로 매핑
                         hover_name=None,    # hover_name 기본값 제거
                         hover_data={       # 마우스 오버 시 표시될 정보
                             col1: True,
                             col2: True,
                             'BubbleSize': True
                         },
                         size_max=60,        # 최대 원 크기 (조정 가능)
                         title=title,
                         labels={col1: label1, col2: label2, 'BubbleSize': '사고건수'}) # 한글 레이블 적용
        
        # X, Y축이 정수형이므로, 틱(tick) 간격을 1로 설정하여 깔끔하게 표시
        fig.update_xaxes(dtick=1)
        fig.update_yaxes(dtick=1)
        
        return fig, title

    # --- Case 5: 다중 라인 차트 (시간형 vs 범주형) ---
    def _create_multi_line_chart(self, time_var: str, cat_var: str, num_var: str, 
                                 time_label: str, cat_label: str, num_label: str):
        title = f"'{time_label}'에 따른 '{cat_label}'별 '{num_label}' 추이"
        
        table1, col1 = time_var.split('.') # X축
        table2, col2 = cat_var.split('.') # Color
        table3, col3 = num_var.split('.') # Y축
        
        agg_val = "COUNT(ACCIDENT.AccidentID)" if col3 == '(사고건수)' else f"SUM({table3}.{col3})"
        
        select_clause = f"SELECT {table1}.{col1}, {table2}.{col2}, {agg_val} AS Value"
        tables_needed = set(['ACCIDENT', table1, table2, table3])
        from_clause = "FROM ACCIDENT"
        join_clause = ""
        if 'DRIVER' in tables_needed:
            join_clause += " JOIN DRIVER ON ACCIDENT.AccidentID = DRIVER.AccidentID"
        if 'REGION' in tables_needed:
            join_clause += " JOIN REGION ON ACCIDENT.RegionCode = REGION.RegionCode"
            
        group_by_clause = f"GROUP BY {table1}.{col1}, {table2}.{col2}"
        order_by_clause = f"ORDER BY {table1}.{col1}"
        
        query = f"{select_clause} {from_clause} {join_clause} {group_by_clause} {order_by_clause}"
        
        df = self._fetch_data(query)
        col1_name = time_var.split('.')[1] # 'OccurYearMonth'

        # [시간축 버그 수정] '202201' 문자열을 datetime 객체로 변환
        try:
            df[col1_name] = pd.to_datetime(df[col1_name], format='%Y%m')
        except Exception as e:
            logging.warning(f"시간 변환 오류: {e}. 'OccurYearMonth' 형식이 'YYYYMM'이 아닐 수 있습니다.")
            pass # 변환 실패 시에도 일단 진행

        fig = px.line(df, 
                      x=col1_name,
                      y='Value',
                      color=col2,
                      title=title,
                      labels={col1: time_label, 'Value': num_label, col2: cat_label}, # 한글 레이블 적용
                      markers=True)
        return fig, title