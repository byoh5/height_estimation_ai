# 예측 모델 테스트 가이드

예측 모델이 잘 작동하는지 테스트하는 방법을 안내합니다.

---

## 🧪 테스트 방법

### 1. 종합 테스트 스크립트 (권장)

**파일**: `scripts/test_enhanced_predictor.py`

**실행 방법**:
```bash
python3 scripts/test_enhanced_predictor.py
```

**테스트 항목**:
- ✅ 기본 시나리오 테스트 (6개 케이스)
- ✅ 엣지 케이스 테스트 (5개 케이스)
- ✅ 일관성 테스트 (성별 차이, 초경 영향 등)
- ✅ 성장 곡선 예측 테스트
- ✅ 실제 사용 시나리오 테스트

**결과 해석**:
- 모든 테스트가 통과하면 모델이 정상 작동
- 일부 실패 시 문제 케이스 확인 필요

---

### 2. 빠른 테스트 스크립트

**파일**: `scripts/quick_test.py`

**실행 방법**:
```bash
python3 scripts/quick_test.py
```

**용도**:
- 빠르게 모델 동작 확인
- 주요 케이스만 테스트
- 개발 중 빠른 검증

---

### 3. 웹 API를 통한 테스트

**방법 1: curl 사용**
```bash
# 기본 테스트
curl -X POST http://localhost:5001/api/predict/adult \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "M",
    "birth_date": "2014-07-24",
    "current_height_cm": 163
  }'

# 여아 + 초경 테스트
curl -X POST http://localhost:5001/api/predict/adult \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "F",
    "birth_date": "2012-01-01",
    "current_height_cm": 150,
    "menarche_age": 12.5
  }'
```

**방법 2: Python 스크립트**
```python
import requests
import json

response = requests.post(
    'http://localhost:5001/api/predict/adult',
    json={
        'gender': 'M',
        'birth_date': '2014-07-24',
        'current_height_cm': 163
    }
)
result = response.json()
print(f"예측: {result['prediction']:.1f}cm")
print(f"모델: {result['models_used']}")
print(f"신뢰도: {result['confidence']}")
```

---

### 4. 웹 인터페이스를 통한 테스트

1. 브라우저에서 `http://localhost:5001` 접속
2. 다양한 입력값으로 테스트:
   - 남아/여아
   - 다양한 나이와 키
   - 부모 키 정보
   - 초경 정보 (여아)
   - 과거 키 기록

---

## 📊 테스트 케이스 예시

### 케이스 1: 기본 케이스
```
입력:
- 성별: 남아
- 생년월일: 2014-01-01
- 현재 키: 140cm

예상 결과:
- 예측값: 165-185cm 범위
- 모델: growth_curve 사용
- 신뢰도: low 또는 medium
```

### 케이스 2: 부모 키 포함
```
입력:
- 성별: 남아
- 생년월일: 2014-01-01
- 현재 키: 140cm
- 아버지 키: 175cm
- 어머니 키: 162cm

예상 결과:
- 예측값: 165-185cm 범위
- 모델: galton, growth_curve 사용
- 신뢰도: high 또는 very_high
```

### 케이스 3: 여아 + 초경
```
입력:
- 성별: 여아
- 생년월일: 2012-01-01
- 현재 키: 150cm
- 초경 시작 나이: 12.5세

예상 결과:
- 예측값: 155-170cm 범위
- 모델: menarche, growth_curve 사용
- 신뢰도: medium 이상
- 초경 정보 표시됨
```

### 케이스 4: 사용자 케이스 (11세 남아 163cm)
```
입력:
- 성별: 남아
- 생년월일: 2014-07-24
- 현재 키: 163cm

예상 결과:
- 예측값: 175-195cm 범위
- 현재 키보다 높아야 함
- 모델: growth_curve 사용
```

---

## ✅ 검증 기준

### 1. 합리성 검증
- ✅ 예측값이 현재 키보다 높아야 함
- ✅ 예측값이 합리적 범위 내 (남아: 150-200cm, 여아: 140-180cm)
- ✅ 나이가 증가할수록 예측값이 증가해야 함

### 2. 일관성 검증
- ✅ 남아가 여아보다 키가 크게 예측되어야 함 (약 10-15cm 차이)
- ✅ 부모 키 정보가 있으면 신뢰도가 향상되어야 함
- ✅ 초경 정보가 있으면 (여아) 신뢰도가 향상되어야 함

### 3. 모델 선택 검증
- ✅ 부모 키만 있으면: galton 모델 사용
- ✅ 현재 키만 있으면: growth_curve 모델 사용
- ✅ 부모 키 + 현재 키: 두 모델 모두 사용
- ✅ 여아 + 초경 정보: menarche 모델 사용

---

## 🔍 문제 발견 시 확인 사항

### 예측값이 현재 키보다 낮은 경우
- ❌ 문제: 최소 성장량 보장 로직 오류
- ✅ 확인: `src/modeling/enhanced_predictor.py`의 최소 성장량 로직

### 예측값이 비현실적으로 높은 경우
- ❌ 문제: 학습 데이터 범위를 벗어난 외삽
- ✅ 확인: 나이와 키가 학습 데이터 범위 내인지 확인

### 초경 정보가 반영되지 않는 경우
- ❌ 문제: 초경 예측 로직 오류
- ✅ 확인: `src/utils/growth_factors.py`의 `predict_female_height_with_menarche` 함수

### 신뢰도가 예상과 다른 경우
- ❌ 문제: 신뢰도 계산 로직 오류
- ✅ 확인: 예측기에 사용된 모델 수와 정보 완전도 확인

---

## 📈 성능 지표

### 모델별 검증 성능
- **성장 곡선 모델**: MAE 0.23cm, R² 0.9989 (매우 높은 정확도)
- **Galton 모델**: MAE 4.23cm, R² 0.6057 (보통 정확도)
- **Stunting 모델**: 5세 이하에서만 사용

### 예상 정확도
- **부모 키 + 현재 키**: ±3-5cm
- **현재 키만**: ±5-10cm (나이에 따라 다름)
- **초경 정보 포함 (여아)**: ±2-4cm (정확도 향상)

---

## 🚀 테스트 실행 예시

### 전체 테스트 실행
```bash
cd /Users/obyeong-yun/dev/height_estimation_ai
python3 scripts/test_enhanced_predictor.py
```

### 빠른 테스트 실행
```bash
python3 scripts/quick_test.py
```

### 특정 케이스만 테스트
```python
from src.modeling.enhanced_predictor import EnhancedHeightPredictor

predictor = EnhancedHeightPredictor()
result = predictor.predict(
    birth_date='2014-07-24',
    gender='M',
    current_height_cm=163
)
print(f"예측: {result['predicted_height']:.1f}cm")
```

---

**작성일**: 2024-12-29  
**버전**: 1.0.0

