# 성장기 어린이 키 예측 AI 모델

성장기 어린이의 현재 키와 관련 정보를 입력받아, 성인 키 및 특정 나이의 키를 예측하는 인공지능 시스템입니다.

---

## 🎯 주요 기능

### 1. 성인 키 예측 (하이브리드 모델)
- **Stunting 성장 패턴 모델**: 나이, 현재 키, 성별 기반
- **Galton 부모 키 모델**: 부모 키, 성별 기반
- 입력 정보 완전도에 따라 최적 모델 자동 선택

### 2. 성장 곡선 예측 (나이별 키 예측)
- 5세, 10세, 15세, 18세 키 예측 가능
- 현재 나이와 키를 기반으로 미래 특정 나이의 키 예측
- 성장 곡선 시각화 가능

### 3. 신뢰도/불확실성 표시
- 결과를 단일 수치가 아닌 `중심값 + 오차범위(±cm)`로 제공
- `신뢰도 점수(0~100)`와 근거/제한사항을 함께 표시
- 모델 간 예측 차이가 크면 `모델 불일치 경고`를 자동 표기
- 사춘기 핵심 입력(골연령/체중/사춘기 단계) 누락 시 신뢰도 상한을 보수적으로 제한

---

## 📊 데이터셋

### 실제 데이터
- **Stunting Balita**: 120,999행 (성장 패턴 데이터)
- **Galton Families**: 934행 (부모-자녀 키 데이터)

---

## 🚀 빠른 시작

### 설치

```bash
# 1) 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 2) pip 업데이트
python -m pip install --upgrade pip

# 3) 프로젝트 의존성 설치
pip install -r requirements.txt
```

### 예측 사용

#### Python 코드
```python
# 성인 키 예측
from src.modeling.hybrid_predictor import HybridHeightPredictor

predictor = HybridHeightPredictor()
result = predictor.predict(
    age_years=10,
    height_cm=140,
    gender='M',
    father_height_cm=175,
    mother_height_cm=162
)
print(f"예상 성인 키: {result['predicted_height']:.1f}cm")

# 특정 나이 키 예측
from src.modeling.growth_curve_predictor import GrowthCurvePredictor

growth_predictor = GrowthCurvePredictor()
result = growth_predictor.predict_at_age(
    current_age_years=8,
    current_height_cm=130,
    target_age_years=15,
    gender='M'
)
print(f"15세 때 예상 키: {result['predicted_height_cm']:.1f}cm")
```

#### CLI 스크립트
```bash
# 성인 키 예측
python3 scripts/predict_height.py

# 성장 곡선 예측
python3 scripts/predict_growth_curve.py
```

---

## 🌐 GitHub Pages + 로컬 엔진 운영

이 프로젝트는 **정적 프론트(GitHub Pages)** + **사용자 PC 로컬 예측 엔진(Flask)** 구조를 지원합니다.

### 동작 방식
- GitHub Pages에 올라간 웹이 `http://127.0.0.1:58761` 로컬 API를 호출
- 실제 모델 추론은 사용자 PC에서 수행 (서버비 0원 운영 가능)

### 로컬 엔진 실행 (Python)
```bash
python scripts/run_local_engine.py --host 127.0.0.1 --port 58761
```

### 정적 페이지 내보내기
```bash
python scripts/export_pages_site.py
```
- 결과 파일: `docs/index.html`

### GitHub Actions
- Pages 배포: `.github/workflows/deploy-pages.yml`
- 로컬엔진 번들 빌드/Release 업로드: `.github/workflows/release-local-engine.yml`

자세한 설치 가이드는 [LOCAL_ENGINE_SETUP.md](LOCAL_ENGINE_SETUP.md) 참고.

---

## 📁 프로젝트 구조

```
height_estimation_ai/
├── data/
│   ├── raw/                  # 원본 데이터
│   └── processed/            # 전처리된 데이터
├── models/
│   └── saved_models/         # 학습된 모델
├── src/
│   └── modeling/             # 모델 코드
│       ├── train_stunting_model.py
│       ├── train_galton_model.py
│       ├── train_growth_curve_model.py
│       ├── hybrid_predictor.py
│       └── growth_curve_predictor.py
├── scripts/                  # 실행 스크립트
├── SPECIFICATION.md          # 기능 명세서
├── MODEL_SUMMARY.md          # 성인 키 예측 모델 요약
├── GROWTH_CURVE_MODEL.md     # 성장 곡선 모델 요약
└── README.md                 # 본 파일
```

---

## 📖 상세 문서

- [기능 명세서](SPECIFICATION.md)
- [성인 키 예측 모델 요약](MODEL_SUMMARY.md)
- [성장 곡선 모델 요약](GROWTH_CURVE_MODEL.md)
- [데이터셋 요약](FINAL_DATA_SUMMARY.md)

---

## 🔧 모델 학습

### 성인 키 예측 모델
```bash
# Stunting 모델 학습
python3 src/modeling/train_stunting_model.py

# Galton 모델 학습
python3 src/modeling/train_galton_model.py
```

### 성장 곡선 모델
```bash
# 나이별 모델 학습 (5세, 10세, 15세, 18세)
python3 src/modeling/train_growth_curve_model.py
```

---

## 💡 특징

1. **하이브리드 예측**: 두 개의 전문 모델을 결합
2. **적응형 예측**: 입력 정보가 많을수록 더 정확
3. **유연한 입력**: 부분 정보로도 예측 가능
4. **나이별 예측**: 성인 키뿐만 아니라 특정 나이의 키도 예측

---

## ⚠️ 주의사항

- 이 모델의 예측 결과는 참고용이며, 의료적 조언을 대체할 수 없습니다.
- 실제 성장 장애나 건강 문제가 의심될 경우 전문의 상담이 필요합니다.
- 모델은 학습 데이터에 기반하므로 개인차가 있을 수 있습니다.

---

## 📝 라이선스

프로젝트 내부 사용 목적

---

**최종 업데이트**: 2026-03-03
