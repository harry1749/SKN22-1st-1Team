# **SKN22-1st-1Team**
Repository for SKN22-1st-1Team

# 🚘**교통사고 현황과 안전 팁을 제공하는 통합 정보 플랫폼**
<img src="image/safecar1.png" width="53%">

#### 사고/운전자/지역 유형별 데이터를 MySQL 기반으로 정규화하여.
#### 조회·분석·시각화에 활용하기 위한 데이터베이스 구축 프로젝트입니다.

## **💁‍♂️Dev Environment**
- Python 3.13.9

- Packages: pyyaml, requests, pandas, sqlalchemy, plotly, pymysql, os, sys

- Conda env: project_1_env

- Database : MySQL

- Schema: /repository/schema.sql

## **🔎주요 기능 요약**
1. **사고 데이터 조회**
    - 발생월·주야·사고내용·피해정도·사고유형·법규위반·기상/노면·도로형태 조건 필터링
    
    - 사고 유형 분포 및 심각도(사망/중상/경상) 분석
    
    - 클릭 기반 빠른 조회

2. **지역 기반 통계**
    - 지역별 사고 건수
   

3. **운전자 정보 분석**
    - 가해/피해 구분

    - 연령대·성별·차종별 사고 특성

    - 상해 정도 기반 사고 심각도 분류

### **🎯선택 가능 조건**

| 테이블   | 컬럼명               | 설명                    |
|----------|----------------------|-------------------------|
| REGION   | RegionCode           | 지역코드             |
| REGION   | RegionName           | 지역명                |
| ACCIDENT | OccurYearMonth       | 사고발생년월(YYYYMM)     |
| ACCIDENT | DayNight             | 주야(낮/밤)             |
| ACCIDENT | RegionCode           | 시군구 코드     |
| ACCIDENT | Description          | 사고내용                 |
| ACCIDENT | DeathCount           | 사망자수                |
| ACCIDENT | SevereInjuryCount    | 중상자수                |
| ACCIDENT | MinorInjuryCount     | 경상자수                |
| ACCIDENT | ReportedInjuryCount  | 부상신고자수             |
| ACCIDENT | AccidentType         | 사고유형                |
| ACCIDENT | LawViolationYn       | 법규위반 여부(Y/N)       |
| ACCIDENT | RoadSurfaceState     | 노면상태                |
| ACCIDENT | WeatherState         | 기상상태                |
| ACCIDENT | RoadForm             | 도로형태                |
| DRIVER   | Role                 | 운전자 구분(가해/피해)   |
| DRIVER   | VehicleType          | 차종                    |
| DRIVER   | Gender               | 성별(M/F)            |
| DRIVER   | AgeGroup             | 연령대                  |
| DRIVER   | InjuryLevel          | 상해정도                |


## **🏊‍♂️WorkFlow**
<img src="image/Web_flowchart.jpg" width="60%">

## **📖ERD**
<img src="image/ERD.png" width="60%">



## 👪 팀원

| 이신재 | 이준서 | 한승혁 | 황하령 |
| :---: | :---: | :---: | :---: |
| [![GitHub](https://img.shields.io/badge/GitHub-Codingcooker74-181717?style=flat&logo=github&logoColor=white)](https://github.com/Codingcooker74) | [![GitHub](https://img.shields.io/badge/GitHub-Leejunseo84-181717?style=flat&logo=github&logoColor=white)](https://github.com/Leejunseo84) | [![GitHub](https://img.shields.io/badge/GitHub-gksshing-181717?style=flat&logo=github&logoColor=white)](https://github.com/gksshing) | [![GitHub](https://img.shields.io/badge/GitHub-harry1749-181717?style=flat&logo=github&logoColor=white)](https://github.com/harry1749) |

