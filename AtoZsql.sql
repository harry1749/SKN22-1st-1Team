
-- Active: 1762504488515@@127.0.0.1@3306@project_1





---------------------------------------------------------------
-- 사고/운전자/지역 ERD 기반 MySQL 스키마 생성 스크립트
-- MySQL 8.0+ / InnoDB / utf8mb4
-- ------------------------------------------------------------

-- 0) 스키마 생성 (원하면 DB 이름 변경)
CREATE DATABASE IF NOT EXISTS project_1
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE project_1;

-- 1) REGION (시군구 마스터)
DROP TABLE IF EXISTS REGION;
CREATE TABLE REGION (
    RegionCode   VARCHAR(20)  NOT NULL COMMENT '시군구 코드',
    RegionName   VARCHAR(100) NOT NULL COMMENT '시군구명',
    PRIMARY KEY (RegionCode)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COMMENT='시군구 지역 정보';

-- 2) ACCIDENT (사고 기본 정보)
DROP TABLE IF EXISTS ACCIDENT;
CREATE TABLE ACCIDENT (
    AccidentID            BIGINT       NOT NULL AUTO_INCREMENT COMMENT '사고ID',
    OccurYearMonth        CHAR(6)      NOT NULL COMMENT '발생년월(YYYYMM)',
    DayNight              VARCHAR(10)  NOT NULL COMMENT '주야',
    RegionCode            VARCHAR(20)  NOT NULL COMMENT '시군구코드',
    Description           TEXT         NULL     COMMENT '사고내용',
    DeathCount            INT          NOT NULL DEFAULT 0 COMMENT '사망자수',
    SevereInjuryCount     INT          NOT NULL DEFAULT 0 COMMENT '중상자수',
    MinorInjuryCount      INT          NOT NULL DEFAULT 0 COMMENT '경상자수',
    ReportedInjuryCount   INT          NOT NULL DEFAULT 0 COMMENT '부상신고자수',
    AccidentType          VARCHAR(50)  NOT NULL COMMENT '사고유형',
    LawViolationYn        CHAR(1)      NOT NULL COMMENT '법규위반 여부(Y/N)',
    RoadSurfaceState      VARCHAR(50)  NOT NULL COMMENT '노면상태',
    WeatherState          VARCHAR(50)  NOT NULL COMMENT '기상상태',
    RoadForm              VARCHAR(50)  NOT NULL COMMENT '도로형태',
    PRIMARY KEY (AccidentID),
    KEY idx_accident_ym         (OccurYearMonth),
    KEY idx_accident_region     (RegionCode),
    KEY idx_accident_type       (AccidentType),
    CONSTRAINT fk_accident_region
        FOREIGN KEY (RegionCode)
        REFERENCES REGION (RegionCode)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    -- ▼ 체크 제약(8.0.16+에서 동작). 구버전이라면 무시될 수 있음
    CONSTRAINT chk_accident_ym
        CHECK (OccurYearMonth REGEXP '^[0-9]{6}$'),
    CONSTRAINT chk_law_violation_yn
        CHECK (LawViolationYn IN ('Y','N')),
    CONSTRAINT chk_nonnegative_counts
        CHECK (DeathCount >= 0 AND SevereInjuryCount >= 0 AND MinorInjuryCount >= 0 AND ReportedInjuryCount >= 0)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COMMENT='사고 정보';

-- 3) DRIVER (가해/피해 운전자)
DROP TABLE IF EXISTS DRIVER;
CREATE TABLE DRIVER (
    DriverID     BIGINT       NOT NULL AUTO_INCREMENT COMMENT '운전자ID',
    AccidentID   BIGINT       NOT NULL COMMENT '사고ID (외래키)',
    `Role`       VARCHAR(10)  NOT NULL COMMENT '구분(가해/피해)',
    VehicleType  VARCHAR(50)  NOT NULL COMMENT '차종',
    Gender       CHAR(1)      NOT NULL COMMENT '성별(M/F 등)',
    AgeGroup     VARCHAR(20)  NOT NULL COMMENT '연령대',
    InjuryLevel  VARCHAR(20)  NOT NULL COMMENT '상해정도',
    PRIMARY KEY (DriverID),
    KEY idx_driver_accident (AccidentID),
    KEY idx_driver_role     (`Role`),
    CONSTRAINT fk_driver_accident
        FOREIGN KEY (AccidentID)
        REFERENCES ACCIDENT (AccidentID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    -- 체크 제약(옵션)
    CONSTRAINT chk_driver_role
        CHECK (`Role` IN ('가해','피해')),
    CONSTRAINT chk_driver_gender
        CHECK (Gender REGEXP '^[A-Za-z]$')
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COMMENT='운전자 정보(가해/피해)';

-- 4) 조회 최적화를 위한 보조 인덱스(상황에 따라 추가)
-- 예: 날씨·노면·도로형태별 필터
CREATE INDEX idx_accident_weather  ON ACCIDENT (WeatherState);
CREATE INDEX idx_accident_surface  ON ACCIDENT (RoadSurfaceState);
CREATE INDEX idx_accident_roadform ON ACCIDENT (RoadForm);

