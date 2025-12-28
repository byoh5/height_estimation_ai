# 성장 곡선 예측 모델

## 📊 모델 개요

특정 나이의 키를 예측하는 모델입니다. 현재 나이와 키를 기반으로 미래 특정 나이의 키를 예측합니다.

---

## 🎯 모델 특징

### 학습된 나이별 모델
- **5세 모델**: 5세 때 키 예측
- **10세 모델**: 10세 때 키 예측
- **15세 모델**: 15세 때 키 예측
- **18세 모델**: 18세(성인) 때 키 예측

### 입력 정보
- 현재 나이 (세)
- 현재 키 (cm)
- 성별 (M/F)

### 출력
- 목표 나이의 예상 키 (cm)
- 예상 성장량 (cm)
- 남은 시간 (년)

---

## 📈 모델 성능

| 목표 나이 | 검증 MAE | 검증 RMSE | R² Score |
|----------|---------|----------|----------|
| 5세 | 0.18cm | 0.23cm | 0.9995 |
| 10세 | 0.23cm | 0.29cm | 0.9991 |
| 15세 | 0.23cm | 0.30cm | 0.9989 |
| 18세 | 0.23cm | 0.30cm | 0.9990 |

**평균 오차**: 약 0.2cm (매우 정확!)

---

## 🚀 사용 방법

### Python 코드로 사용

#### 1. 특정 나이 예측
```python
from src.modeling.growth_curve_predictor import GrowthCurvePredictor

predictor = GrowthCurvePredictor()

result = predictor.predict_at_age(
    current_age_years=8,
    current_height_cm=130,
    target_age_years=15,
    gender='M'
)

print(f"15세 때 예상 키: {result['predicted_height_cm']:.1f}cm")
print(f"예상 성장: {result['growth_expected']:.1f}cm")
```

#### 2. 성장 곡선 예측 (여러 나이)
```python
result = predictor.predict_growth_curve(
    current_age_years=8,
    current_height_cm=130,
    gender='M'
)

# 여러 나이별 예측 결과
for age, prediction in result['predictions'].items():
    print(f"{age}세: {prediction['predicted_height_cm']:.1f}cm")
```

### CLI 스크립트 사용
```bash
python3 scripts/predict_growth_curve.py
```

---

## 💡 예시

### 예시 1: 5세 아이의 10세 때 키 예측
```
현재: 5세, 110cm
예측: 10세에 131.7cm
예상 성장: 21.7cm
```

### 예시 2: 성장 곡선 예측
```
현재: 8세, 130cm (여아)

예측 결과:
  10세: 149.3cm
  15세: 171.0cm
  18세: 183.9cm
```

---

## 🔄 작동 원리

### 특성
- `current_age_years`: 현재 나이 (세)
- `current_age_months`: 현재 나이 (개월)
- `current_height_cm`: 현재 키 (cm)
- `years_to_target`: 목표 나이까지 남은 시간 (년)
- `months_to_target`: 목표 나이까지 남은 시간 (개월)
- `gender_M`, `gender_F`: 성별 (원핫 인코딩)

### 모델 선택
- 요청한 나이와 가장 가까운 학습된 모델 선택
- 예: 12세 예측 요청 → 10세 또는 15세 모델 사용

---

## 📁 파일 구조

```
models/saved_models/
├── growth_curve_age_5_model.pkl
├── growth_curve_age_5_metadata.json
├── growth_curve_age_10_model.pkl
├── growth_curve_age_10_metadata.json
├── growth_curve_age_15_model.pkl
├── growth_curve_age_15_metadata.json
├── growth_curve_age_18_model.pkl
└── growth_curve_age_18_metadata.json

src/modeling/
├── train_growth_curve_model.py (모델 학습)
└── growth_curve_predictor.py (예측기)

scripts/
└── predict_growth_curve.py (CLI 스크립트)
```

---

## ⚠️ 주의사항

1. **나이 제한**: 현재 나이보다 미래 나이만 예측 가능
2. **나이 범위**: 0-18세 사이의 나이만 예측 가능
3. **모델 선택**: 요청한 나이와 가장 가까운 학습된 모델 사용
   - 5세, 10세, 15세, 18세 모델만 학습됨
   - 다른 나이 예측 시 가장 가까운 모델 사용

---

## 🔄 성인 키 예측 모델과의 차이

| 특징 | 성장 곡선 모델 | 성인 키 예측 모델 |
|------|--------------|-----------------|
| **목적** | 특정 나이의 키 예측 | 성인 키만 예측 |
| **입력** | 현재 나이, 현재 키, 성별 | 현재 나이, 현재 키, 성별 (선택: 부모 키) |
| **출력** | 목표 나이의 키 | 성인 키 |
| **유연성** | 여러 나이 예측 가능 | 성인 키만 예측 |

---

## ✅ 완료된 작업

1. ✅ 나이별 모델 학습 (5세, 10세, 15세, 18세)
2. ✅ 예측기 구현
3. ✅ CLI 스크립트 작성
4. ✅ 테스트 완료

---

**최종 업데이트**: 2024-12-28

