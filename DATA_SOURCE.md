# 실제 키 데이터 출처

이 프로젝트에서 사용하는 실제 키 데이터의 출처와 상세 정보입니다.

---

## 📊 실제 데이터셋 목록

### 1. Galton Families 데이터 ⭐⭐⭐⭐⭐

**출처**: Kaggle - 1886년 Francis Galton의 실제 연구 데이터

**Kaggle 링크**: 
https://www.kaggle.com/datasets/jacopoferretti/parents-heights-vs-children-heights-galton-data

**원본 연구**:
- **연구자**: Francis Galton (1822-1911)
- **연구 시기**: 1886년
- **연구 내용**: 부모 키와 자녀 키의 유전적 관계 연구
- **역사적 의미**: 유전학과 통계학의 기초를 마련한 중요한 연구

**데이터 정보**:
- **행 수**: 934행
- **가족 수**: 205개 가족
- **자녀 수**: 평균 6.2명/가족
- **라이선스**: CC0: Public Domain (무료 사용 가능)
- **Kaggle 다운로드**: 2,167회
- **평점**: 75 votes, Usability 10.0

**데이터 구조**:
```
- family: 가족 ID
- father: 아버지 키 (인치)
- mother: 어머니 키 (인치)
- midparentHeight: 중간 부모 키 (인치)
- children: 가족 내 자녀 수
- childNum: 가족 내 자녀 번호
- gender: 성별 (male/female)
- childHeight: 자녀 키 (인치) - 성인 키
```

**통계 정보** (인치 → cm 변환 후):
- **아버지 키**: 평균 175.8cm (범위: 약 160-200cm)
- **어머니 키**: 평균 162.8cm (범위: 약 150-180cm)
- **자녀 키**: 평균 169.5cm (범위: 142.2-200.7cm)
- **성별 분포**: 남아 51.5%, 여아 48.5%

**특징**:
- ✅ **실제 측정 데이터** (1886년 실제 관찰)
- ✅ **부모 키 정보 포함** (유전적 요인 분석 가능)
- ✅ **가족 단위 데이터** (유전 패턴 분석 가능)
- ✅ **과학적 신뢰도 높음** (유명한 연구 데이터)
- ⚠️ 성인 키 데이터 (성장기 예측에는 부적합)
- ⚠️ 오래된 데이터 (1886년, 하지만 유전 패턴은 변하지 않음)

**프로젝트 내 위치**:
- 원본: `data/raw/kaggle/archive/GaltonFamilies.csv`
- 전처리: `data/processed/galton_families_processed.csv`

**사용 목적**:
- 부모 키 기반 성인 키 예측 모델 학습
- 유전적 요인 반영
- Galton 모델 학습

---

### 2. Stunting Balita Detection 데이터 ⭐⭐⭐⭐⭐

**출처**: Kaggle - 실제 영아 성장 데이터

**Kaggle 링크**: 
https://www.kaggle.com/datasets/rendiputra/stunting-balita-detection-121k-rows

**데이터 정보**:
- **행 수**: 120,999행 (대규모 데이터셋!)
- **파일 크기**: 3.15 MB
- **Kaggle 다운로드**: 9,644회
- **평점**: 121 votes

**데이터 구조** (인도네시아어):
```
- Umur (bulan): 나이 (개월) - 0~60개월
- Jenis Kelamin: 성별 (laki-laki/perempuan)
- Tinggi Badan (cm): 키 (cm)
- Status Gizi: 영양 상태 (normal/stunted/severely stunted/tinggi)
```

**통계 정보**:
- **나이**: 평균 30.2개월 (0~60개월), 표준편차 17.6개월
- **키**: 평균 88.7cm (40~128cm), 표준편차 17.3cm
- **성별 분포**:
  - 여아: 61,002명 (50.4%)
  - 남아: 59,997명 (49.6%)
- **영양 상태**:
  - Normal: 67,755명 (56.0%)
  - Severely stunted: 19,869명 (16.4%)
  - Tinggi (높음): 19,560명 (16.2%)
  - Stunted: 13,815명 (11.4%)

**특징**:
- ✅ **대규모 실제 데이터** (12만 행)
- ✅ **키 데이터 포함** (cm 단위)
- ✅ **연령 데이터 포함** (0-60개월)
- ✅ **성별 정보 포함**
- ✅ **영양 상태 정보 포함**
- ⚠️ 주로 유아기(0-5세) 데이터
- ⚠️ 부모 키 정보 없음
- ⚠️ 성인 키 데이터 없음 (예측 필요)

**프로젝트 내 위치**:
- 원본: `data/raw/kaggle/stunting-balita-detection/data_balita.csv`
- 전처리: `data/processed/stunting_balita_processed.csv`

**사용 목적**:
- 성장기 패턴 학습 모델 (Stunting 모델)
- 성장 곡선 모델 학습
- 나이별 성장 패턴 분석

---

## 📈 데이터 활용 현황

### 현재 사용 중인 데이터

| 데이터셋 | 행 수 | 사용 모델 | 용도 |
|---------|------|----------|------|
| **Galton Families** | 934 | Galton 모델 | 부모 키 기반 성인 키 예측 |
| **Stunting Balita** | 120,999 | Stunting 모델, 성장 곡선 모델 | 성장기 패턴 학습, 나이별 키 예측 |

**총 실제 데이터**: 121,933행

---

## 🔍 데이터 출처 상세 정보

### Galton Families 데이터

**원본 연구**:
- **연구 제목**: "Regression towards mediocrity in hereditary stature"
- **연구자**: Francis Galton
- **발표 연도**: 1886년
- **연구 내용**: 
  - 부모 키와 자녀 키의 관계를 통계적으로 분석
  - "회귀(Regression)" 개념을 처음 도입한 연구
  - 유전학과 통계학의 기초를 마련

**데이터 수집 방법**:
- 실제 가족들의 키를 측정
- 부모와 자녀의 키를 기록
- 총 205개 가족, 934명의 자녀 데이터

**과학적 가치**:
- 유전적 요인이 키에 미치는 영향 연구
- 통계학의 회귀 분석 기법 개발
- 현대 유전학의 기초가 된 중요한 데이터

### Stunting Balita 데이터

**데이터 출처**:
- 인도네시아 영아 성장 데이터
- 실제 측정 데이터
- 영양 상태와 성장 관계 연구용 데이터

**데이터 특징**:
- 대규모 샘플 (12만 행)
- 다양한 영양 상태 포함
- 실제 임상/조사 데이터

---

## 📚 참고 자료

### Galton 데이터 관련
- **원본 논문**: Galton, F. (1886). "Regression towards mediocrity in hereditary stature"
- **Kaggle**: https://www.kaggle.com/datasets/jacopoferretti/parents-heights-vs-children-heights-galton-data
- **위키피디아**: Francis Galton 관련 문서

### Stunting Balita 데이터 관련
- **Kaggle**: https://www.kaggle.com/datasets/rendiputra/stunting-balita-detection-121k-rows
- **용어 설명**:
  - Balita: 인도네시아어로 "영아" (0-5세)
  - Stunting: 성장 저하

---

## ✅ 데이터 사용 권한

### Galton Families
- **라이선스**: CC0: Public Domain
- **사용 제한**: 없음 (무료 사용 가능)
- **출처 표기**: 권장 (학술적 정확성)

### Stunting Balita
- **라이선스**: Kaggle 데이터셋 (일반적으로 연구/교육 목적 사용 가능)
- **사용 제한**: Kaggle 이용약관 준수
- **출처 표기**: 권장

---

## 🎯 데이터의 한계와 보완

### 한계점

1. **Galton 데이터**:
   - 오래된 데이터 (1886년)
   - 나이 정보 없음 (성인 키만)
   - 인치 단위 (cm 변환 필요)

2. **Stunting Balita 데이터**:
   - 유아기만 포함 (0-5세)
   - 부모 키 정보 없음
   - 성인 키 데이터 없음

### 보완 방법

1. **의학적 지식 활용**:
   - 성장 곡선 연구 결과 반영
   - 초경 정보 활용 (여성)
   - 성장 잠재력 계수 적용

2. **통계적 보정**:
   - 국가별 평균 키 보정
   - 성별별 성장 패턴 보정
   - 나이별 성장 속도 보정

---

## 📊 데이터 품질 평가

### Galton 데이터: ⭐⭐⭐⭐⭐
- **신뢰도**: 매우 높음 (실제 측정 데이터)
- **완전성**: 높음 (부모 키, 성별, 성인 키 포함)
- **규모**: 작음 (934행)
- **최신성**: 낮음 (1886년, 하지만 유전 패턴은 변하지 않음)

### Stunting Balita 데이터: ⭐⭐⭐⭐
- **신뢰도**: 높음 (실제 측정 데이터)
- **완전성**: 중간 (나이, 키, 성별 포함, 부모 키 없음)
- **규모**: 매우 큼 (120,999행)
- **최신성**: 높음 (최근 데이터)

---

**작성일**: 2024-12-29  
**버전**: 1.0.0  
**데이터 상태**: 실제 데이터만 사용 (121,933행)

