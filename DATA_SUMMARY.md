# 프로젝트 데이터셋 요약

## 📊 현재 보유 데이터

### ✅ 생성 완료된 데이터셋

#### 1. **한국인 성장 데이터** 🇰🇷 ⭐⭐⭐⭐⭐ (NEW!)
- **파일**: `data/raw/korean_growth_data.csv`
- **크기**: 3,000행
- **특징**:
  - ✅ 질병관리청 한국인 성장도표 기반
  - ✅ 한국인 평균 성장 패턴 반영
  - ✅ 남아/여아 성별 구분
  - ✅ 부모 키 정보 포함
  - ✅ 0-18세 연령대
- **컬럼**:
  - `age_years`, `age_months`: 나이
  - `gender`: 성별 (M/F)
  - `height_cm`: 현재 키 (cm)
  - `weight_kg`: 체중 (kg)
  - `father_height_cm`: 아버지 키 (cm)
  - `mother_height_cm`: 어머니 키 (cm)
  - `adult_height_cm`: 예상 성인 키 (cm)
  - `nationality`: KR (한국 표시)

#### 2. **일반 합성 데이터**
- **파일**: `data/raw/synthetic_growth_data.csv`
- **크기**: 2,000행
- **특징**: 국제적인 성장 패턴 기반

#### 3. **WHO 기반 합성 데이터**
- **파일**: `data/raw/who_growth_synthetic.csv`
- **크기**: 1,220행
- **특징**: WHO 성장 표준 기반 (0-60개월)

---

## 🌍 다운로드 가능한 실제 데이터셋 (Kaggle)

### 1. Parents' Heights vs Adult Children's Heights
- **상태**: 다운로드 필요
- **링크**: https://www.kaggle.com/datasets/jacopoferretti/parents-heights-vs-children-heights-galton-data
- **크기**: 934행
- **특징**: 부모 키와 성인 키 관계 학습용

### 2. Stunting Toddler Detection
- **상태**: 다운로드 필요
- **링크**: https://www.kaggle.com/datasets/rendiputra/stunting-balita-detection-121k-rows
- **크기**: 121,000행
- **특징**: 대규모 성장 데이터

### 3. Lung Capacity of Kids
- **상태**: 다운로드 필요
- **링크**: https://www.kaggle.com/datasets/jacopoferretti/lung-capacity-of-kids
- **크기**: 6 kB
- **특징**: 키, 성별 데이터 포함

---

## 📈 데이터셋 비교

| 데이터셋 | 국가 | 행 수 | 부모 키 | 성별 | 나이 | 상태 |
|---------|------|------|---------|------|------|------|
| 한국인 성장 데이터 | 🇰🇷 한국 | 3,000 | ✅ | ✅ | ✅ | ✅ 생성 완료 |
| 일반 합성 데이터 | 🌍 국제 | 2,000 | ✅ | ✅ | ✅ | ✅ 생성 완료 |
| WHO 기반 데이터 | 🌍 국제 | 1,220 | ❌ | ✅ | ✅ | ✅ 생성 완료 |
| Parents Heights | 🌍 국제 | 934 | ✅ | ✅ | ❌ | ⏳ 다운로드 필요 |
| Stunting Toddler | 🌍 국제 | 121K | ❌ | ❓ | ✅ | ⏳ 다운로드 필요 |

---

## 💡 권장 사용 전략

### 1단계: 현재 보유 데이터로 시작
- ✅ 한국인 성장 데이터 (3,000행) - 한국 특성 반영
- ✅ 일반 합성 데이터 (2,000행) - 일반 패턴 학습
- **총 5,000+ 행의 데이터로 모델 학습 가능**

### 2단계: Kaggle 데이터 추가 (선택)
- Kaggle API 설정 후 실제 데이터 다운로드
- 더 다양한 패턴 학습

### 3단계: 데이터 결합 및 정제
- 모든 데이터셋 결합
- 데이터 정제 및 전처리
- 모델 학습

---

## 🎯 한국 데이터의 장점

1. **한국인 특성 반영**
   - 한국인 평균 키 (남: 172.5cm, 여: 160.0cm)
   - 한국인 성장 패턴 반영

2. **실제 통계 기반**
   - 질병관리청 한국인 성장도표 기반
   - 신뢰성 있는 데이터 소스

3. **완전한 정보**
   - 부모 키 포함
   - 성별, 연령, 체중 등 모든 정보 포함

---

## 📝 다음 단계

1. ✅ 한국 데이터 생성 완료
2. ⏳ 데이터 탐색 및 분석 (EDA)
3. ⏳ 데이터 전처리
4. ⏳ 모델 학습 준비

---

**최종 업데이트**: 2024-12-28

