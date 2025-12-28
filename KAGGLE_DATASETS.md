# Kaggle에서 찾은 어린이 키 예측 관련 데이터셋

## 검색 결과 요약
- 검색어: "children height"
- 총 데이터셋 수: **86개**

---

## 🎯 가장 관련 있는 데이터셋 TOP 5

### 1. **Parents' Heights vs Adult Children's Heights** ⭐⭐⭐⭐⭐
- **URL**: https://www.kaggle.com/datasets/jacopoferretti/parents-heights-vs-children-heights-galton-data
- **설명**: 1886년 Galton의 관찰 데이터
- **데이터 크기**: 
  - 934명의 어린이
  - 205개 가족
  - 파일 크기: 34.72 kB
- **포함 컬럼**:
  - `family`: 가족 ID
  - `father`: 아버지 키 (인치)
  - `mother`: 어머니 키 (인치)
  - `midparentHeight`: 중간 부모 키 ((father + 1.08*mother)/2)
  - `children`: 가족 내 자녀 수
  - `childNum`: 가족 내 자녀 번호
  - `gender`: 성별 (male/female)
  - `childHeight`: 자녀 키 (인치) - **성인 키**
- **다운로드**: 2,167회
- **평점**: 75 votes, Usability 10.0
- **라이선스**: CC0: Public Domain (무료 사용 가능)
- **특징**: 
  - ✅ 실제 측정 데이터 (1886년 Galton 연구)
  - ✅ 부모 키 포함 (유전적 요인 분석 가능)
  - ✅ 성별 구분
  - ⚠️ 성인 키 데이터 (성장기 데이터 아님)
  - ⚠️ 인치 단위 (cm 변환 필요)

### 2. **Stunting Toddler (Balita) Detection** ⭐⭐⭐⭐
- **URL**: https://www.kaggle.com/datasets/rendiputra/stunting-balita-detection-121k-rows
- **설명**: 영아 성장 저하 감지 데이터
- **데이터 크기**: 
  - **121,000행** (매우 큰 데이터셋!)
  - 파일: CSV
- **포함 컬럼**:
  - `Height`: 키 (cm)
  - `Weight`: 체중
  - `Age`: 나이
  - 기타 성장 관련 지표
- **다운로드**: 9,644회
- **평점**: 121 votes
- **특징**:
  - ✅ 대규모 데이터셋
  - ✅ 키 데이터 포함 (cm 단위)
  - ✅ 연령 데이터 포함
  - ⚠️ 주로 유아기(0-5세) 데이터일 가능성

### 3. **Children Height Detection Data** ⭐⭐⭐
- **URL**: https://www.kaggle.com/datasets/drahulsingh/children-height-detection-data
- **설명**: 어린이 키 감지 데이터
- **데이터 크기**: 
  - 파일 크기: 4 kB
  - 파일: CSV
- **포함 컬럼**:
  - 키(height) 및 포즈(pose) 데이터
- **다운로드**: 122회
- **평점**: 24 votes, Usability 9.4
- **특징**:
  - ✅ 어린이 키 데이터
  - ⚠️ 데이터 크기가 작음
  - ⚠️ 정확한 컬럼 정보 확인 필요

### 4. **Lung Capacity of Kids** ⭐⭐⭐
- **URL**: https://www.kaggle.com/datasets/jacopoferretti/lung-capacity-of-kids
- **설명**: 어린이 폐용량 데이터
- **데이터 크기**: 
  - 파일 크기: 6 kB
  - 파일: CSV
- **포함 컬럼**:
  - `Gender`: 성별
  - `Height`: 키
  - `Smoking Habits`: 흡연 습관
  - 기타 건강 지표
- **다운로드**: 926회
- **평점**: 42 votes, Usability 10.0
- **특징**:
  - ✅ 키 데이터 포함
  - ✅ 성별 데이터 포함
  - ⚠️ 주제가 폐용량 (키 예측이 주 목적 아님)

### 5. **Malnutrition across the globe** ⭐⭐
- **URL**: https://www.kaggle.com/datasets/ruchi798/malnutrition-across-the-globe
- **설명**: 전 세계 영양실조 데이터
- **포함 컬럼**:
  - Weight-for-height 데이터
  - 0-59개월 어린이 데이터
- **다운로드**: 9,300회
- **평점**: 207 votes
- **특징**:
  - ✅ 어린이 성장 관련
  - ⚠️ 키 데이터가 주 목적 아님
  - ⚠️ 영양실조 관련 데이터

---

## 📊 데이터셋 비교표

| 데이터셋 | 데이터 크기 | 키 데이터 | 부모 키 | 성별 | 나이 | 다운로드 | 추천도 |
|---------|------------|----------|---------|------|------|----------|--------|
| Parents' Heights vs Children | 934행 | ✅ (성인) | ✅ | ✅ | ❌ | 2,167 | ⭐⭐⭐⭐⭐ |
| Stunting Toddler Detection | 121K행 | ✅ | ❌ | ❓ | ✅ | 9,644 | ⭐⭐⭐⭐ |
| Children Height Detection | 작음 | ✅ | ❌ | ❓ | ❓ | 122 | ⭐⭐⭐ |
| Lung Capacity of Kids | 작음 | ✅ | ❌ | ✅ | ❓ | 926 | ⭐⭐⭐ |
| Malnutrition across globe | 중간 | ✅ | ❌ | ❓ | ✅ | 9,300 | ⭐⭐ |

---

## 💡 권장사항

### 1순위: **Parents' Heights vs Adult Children's Heights**
- **이유**:
  - 실제 측정 데이터 (과학적 신뢰도 높음)
  - 부모 키 정보 포함 (유전적 요인 반영 가능)
  - 공개 도메인 (무료 사용)
  - 깨끗한 데이터 구조
- **단점**:
  - 성인 키 데이터 (성장기 예측에는 부적합할 수 있음)
  - 인치 단위 (cm 변환 필요)
  - 나이 정보 없음

### 2순위: **Stunting Toddler Detection**
- **이유**:
  - 대규모 데이터셋 (121K 행)
  - 키와 나이 정보 포함
- **단점**:
  - 세부 정보 확인 필요 (컬럼 구조 확인 필요)
  - 주로 유아기 데이터일 가능성

### 조합 사용 제안
- **Parents' Heights 데이터**: 부모 키와 성인 키 관계 학습용
- **Stunting Toddler 데이터**: 성장기 패턴 학습용
- 두 데이터셋을 결합하여 더 정확한 모델 구축 가능

---

## 🔗 데이터셋 직접 링크

1. [Parents' Heights vs Adult Children's Heights](https://www.kaggle.com/datasets/jacopoferretti/parents-heights-vs-children-heights-galton-data)
2. [Stunting Toddler Detection](https://www.kaggle.com/datasets/rendiputra/stunting-balita-detection-121k-rows)
3. [Children Height Detection Data](https://www.kaggle.com/datasets/drahulsingh/children-height-detection-data)
4. [Lung Capacity of Kids](https://www.kaggle.com/datasets/jacopoferretti/lung-capacity-of-kids)

---

## 📝 다음 단계

1. Kaggle 계정 로그인 필요 (데이터 다운로드 시)
2. 원하는 데이터셋 선택
3. 다운로드 후 프로젝트의 `data/raw/` 디렉토리에 저장
4. 데이터 전처리 및 분석 시작

---

**최종 업데이트**: 2024-12-28

