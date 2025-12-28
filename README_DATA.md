# 데이터 다운로드 및 정리 가이드

## 📊 프로젝트에 필요한 데이터셋

이 프로젝트에서는 다음 데이터셋들을 사용하는 것을 권장합니다:

### 1. Parents' Heights vs Adult Children's Heights ⭐⭐⭐⭐⭐
- **가장 추천**: 부모 키와 성인 키 관계 학습
- **링크**: https://www.kaggle.com/datasets/jacopoferretti/parents-heights-vs-children-heights-galton-data
- **크기**: 934행, 34.72 kB

### 2. Stunting Toddler Detection ⭐⭐⭐⭐
- **대규모 데이터**: 성장 패턴 학습
- **링크**: https://www.kaggle.com/datasets/rendiputra/stunting-balita-detection-121k-rows
- **크기**: 121,000행

### 3. Lung Capacity of Kids ⭐⭐⭐
- **보조 데이터**: 키, 성별 데이터 포함
- **링크**: https://www.kaggle.com/datasets/jacopoferretti/lung-capacity-of-kids
- **크기**: 6 kB

---

## 🚀 빠른 시작

### 방법 1: Kaggle API 사용 (권장)

#### 1단계: Kaggle API 키 발급
1. https://www.kaggle.com/ 접속 후 로그인
2. 프로필 → Settings → API
3. "Create New Token" 클릭
4. 다운로드된 `kaggle.json` 파일을 `~/.kaggle/` 디렉토리에 저장
5. 권한 설정: `chmod 600 ~/.kaggle/kaggle.json`

#### 2단계: 자동 다운로드
```bash
python3 scripts/download_kaggle_data.py
```

### 방법 2: 웹에서 수동 다운로드

#### 1단계: 데이터셋 다운로드
각 링크에서 "Download" 버튼을 클릭하여 ZIP 파일 다운로드

#### 2단계: 데이터 정리
다운로드한 ZIP 파일을 `~/Downloads/` 폴더에 두고:
```bash
python3 scripts/organize_downloaded_data.py
```

또는 수동으로:
```bash
# 디렉토리 생성
mkdir -p data/raw/kaggle/parents-heights-vs-children-heights-galton-data
mkdir -p data/raw/kaggle/stunting-balita-detection-121k-rows
mkdir -p data/raw/kaggle/lung-capacity-of-kids

# ZIP 파일 압축 해제 후 CSV 파일을 해당 디렉토리에 복사
```

---

## 📁 데이터 디렉토리 구조

```
data/
├── raw/
│   ├── kaggle/
│   │   ├── parents-heights-vs-children-heights-galton-data/
│   │   │   └── GaltonFamilies.csv
│   │   ├── stunting-balita-detection-121k-rows/
│   │   │   └── [CSV 파일들]
│   │   └── lung-capacity-of-kids/
│   │       └── [CSV 파일들]
│   ├── synthetic_growth_data.csv          # 합성 데이터 (이미 생성됨)
│   └── who_growth_synthetic.csv           # WHO 기반 합성 데이터 (이미 생성됨)
└── processed/                              # 전처리된 데이터 (추후 생성)
```

---

## ✅ 현재 상태

- ✅ 합성 데이터: 생성 완료 (2,000행 + 1,220행)
- ⏳ Kaggle 실제 데이터: 다운로드 필요
- ✅ 데이터 정리 스크립트: 준비 완료
- ✅ 디렉토리 구조: 생성 완료

---

## 🔍 데이터 확인

다운로드 완료 후 데이터 확인:
```bash
python3 scripts/organize_downloaded_data.py
```

이 스크립트는:
- Downloads 폴더의 Kaggle ZIP 파일 자동 탐지 및 압축 해제
- 데이터셋별 디렉토리 정리
- 다운로드된 데이터 요약 출력

---

## 📝 다음 단계

데이터 다운로드 완료 후:
1. ✅ 데이터 탐색 및 분석 (EDA)
2. ✅ 데이터 전처리
3. ✅ 모델 학습
4. ✅ 모델 평가 및 개선

---

**참고**: 일부 Kaggle 데이터셋은 웹사이트에서 라이선스 동의가 필요할 수 있습니다. 
데이터셋 페이지에서 "I Understand and Accept" 버튼을 클릭해주세요.

