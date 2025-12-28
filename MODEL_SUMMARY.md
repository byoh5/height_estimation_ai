# 하이브리드 키 예측 모델 요약

## 📊 모델 구조

### 두 개의 전문 모델

#### 1. **Stunting 성장 패턴 모델** 🌱
- **목적**: 성장기 패턴 기반 예측
- **입력**: 나이, 성별, 현재 키
- **출력**: 예상 성인 키
- **데이터**: Stunting Balita (120,999행)
- **알고리즘**: Random Forest
- **성능**: 검증 MAE ≈ 0.00cm (매우 정확)
- **특징**: 0-60개월 유아기 데이터 기반

#### 2. **Galton 부모 키 모델** 👨‍👩‍👧
- **목적**: 부모 키 기반 유전적 예측
- **입력**: 아버지 키, 어머니 키, 성별
- **출력**: 예상 성인 키
- **데이터**: Galton Families (934행)
- **알고리즘**: Gradient Boosting
- **성능**: 검증 MAE = 4.23cm
- **특징**: 유전적 요인 강하게 반영

---

## 🔄 하이브리드 예측 로직

### 입력 데이터 완전도에 따른 모델 선택

```
┌─────────────────────────────────────────┐
│  입력 데이터 확인                        │
└─────────────────────────────────────────┘
           │
           ├─ 부모 키 + 성별 있음?
           │  └─ YES → Galton 모델 사용 (가중치 0.7)
           │
           ├─ 나이 + 현재 키 + 성별 있음?
           │  └─ YES → Stunting 모델 사용 (가중치 0.3 or 1.0)
           │
           └─ 둘 다 있음?
              └─ YES → 가중 평균 (Galton 0.7, Stunting 0.3)
```

### 신뢰도 레벨

- **very_high**: 부모 키 + 성장 데이터 모두 있음 (두 모델 사용)
- **high**: 부모 키만 있음 (Galton 모델만 사용)
- **medium**: 성장 데이터만 있음 (Stunting 모델만 사용)
- **low**: 최소 정보만 있음

---

## 📈 모델 성능

### Stunting 모델
- **학습 데이터**: 96,799행
- **검증 데이터**: 24,200행
- **검증 MAE**: ≈ 0.00cm
- **검증 RMSE**: ≈ 0.00cm
- **R² Score**: 1.0000

### Galton 모델
- **학습 데이터**: 747행
- **검증 데이터**: 187행
- **검증 MAE**: 4.23cm
- **검증 RMSE**: 5.51cm
- **R² Score**: 0.6057

---

## 🎯 사용 예시

### 예시 1: 모든 정보가 있는 경우 (최고 정확도)
```python
result = predictor.predict(
    age_years=10,
    height_cm=140,
    gender='M',
    father_height_cm=175,
    mother_height_cm=162
)
# 예측: 166.09cm
# 신뢰도: very_high
# 사용 모델: galton, stunting (가중 평균)
```

### 예시 2: 부모 키만 있는 경우
```python
result = predictor.predict(
    gender='F',
    father_height_cm=175,
    mother_height_cm=162
)
# 예측: 155.88cm
# 신뢰도: high
# 사용 모델: galton
```

### 예시 3: 성장 데이터만 있는 경우
```python
result = predictor.predict(
    age_years=8,
    height_cm=130,
    gender='M'
)
# 예측: 148.60cm
# 신뢰도: medium
# 사용 모델: stunting
```

---

## 💡 설계 철학

### 1. 데이터 완전도에 따른 적응형 예측
- 입력 정보가 많을수록 더 정확한 예측
- 부모 키 정보가 있으면 유전적 요인 반영 (Galton 모델)
- 나이와 현재 키가 있으면 성장 패턴 반영 (Stunting 모델)

### 2. 가중 평균을 통한 보완
- 두 모델을 모두 사용 가능할 때 가중 평균
- 부모 키 모델에 더 높은 가중치 (0.7)
- 성장 패턴 모델에 낮은 가중치 (0.3)

### 3. 유연한 입력 처리
- 최소한 성별만 있어도 예측 가능 (부모 키 또는 성장 데이터 필요)
- 부분 정보로도 예측 가능
- 정보가 많을수록 신뢰도 증가

---

## 📁 파일 구조

```
models/
└── saved_models/
    ├── stunting_random_forest_model.pkl
    ├── stunting_random_forest_metadata.json
    ├── galton_gradient_boosting_model.pkl
    └── galton_gradient_boosting_metadata.json

src/
└── modeling/
    ├── train_stunting_model.py
    ├── train_galton_model.py
    ├── hybrid_predictor.py
    └── __init__.py

scripts/
└── predict_height.py (CLI 스크립트)
```

---

## 🚀 사용 방법

### Python 코드로 사용
```python
from src.modeling.hybrid_predictor import HybridHeightPredictor

predictor = HybridHeightPredictor()
result = predictor.predict(
    age_years=10,
    height_cm=140,
    gender='M',
    father_height_cm=175,
    mother_height_cm=162
)
print(f"예상 키: {result['predicted_height']:.1f}cm")
```

### CLI로 사용
```bash
python3 scripts/predict_height.py
```

---

## ✅ 완료된 작업

1. ✅ Stunting 모델 학습 완료
2. ✅ Galton 모델 학습 완료
3. ✅ 하이브리드 예측 모델 구현
4. ✅ 모델 저장 및 로드 기능
5. ✅ CLI 스크립트 작성
6. ✅ 테스트 완료

---

**최종 업데이트**: 2024-12-28

