# Kaggle 데이터 다운로드 가이드

## 현재 상황
Kaggle API 인증이 필요한 상태입니다. 두 가지 방법으로 데이터를 다운로드할 수 있습니다.

---

## 방법 1: Kaggle API 사용 (자동 다운로드) ⚡

### 1단계: Kaggle API 키 발급
1. https://www.kaggle.com/ 접속
2. 로그인 (계정이 없으면 회원가입)
3. 우측 상단 프로필 클릭 → **Settings** 선택
4. **API** 섹션으로 이동
5. **Create New Token** 버튼 클릭
6. `kaggle.json` 파일이 다운로드됨

### 2단계: API 키 파일 설정
```bash
# .kaggle 디렉토리 생성
mkdir -p ~/.kaggle

# 다운로드한 kaggle.json 파일을 ~/.kaggle/ 디렉토리로 이동
mv ~/Downloads/kaggle.json ~/.kaggle/

# 파일 권한 설정 (보안상 필수)
chmod 600 ~/.kaggle/kaggle.json
```

### 3단계: 다운로드 스크립트 실행
```bash
python3 scripts/download_kaggle_data.py
```

---

## 방법 2: 웹사이트에서 수동 다운로드 📥

Kaggle API 설정이 어려우시면 웹사이트에서 직접 다운로드할 수 있습니다.

### 다운로드할 데이터셋 링크

#### 1. Parents' Heights vs Adult Children's Heights ⭐⭐⭐⭐⭐
- **링크**: https://www.kaggle.com/datasets/jacopoferretti/parents-heights-vs-children-heights-galton-data
- **다운로드 방법**:
  1. 링크 접속
  2. 우측 상단 **Download** 버튼 클릭
  3. 다운로드한 ZIP 파일 압축 해제
  4. CSV 파일을 `data/raw/kaggle/parents-heights-vs-children-heights-galton-data/` 디렉토리에 복사

#### 2. Stunting Toddler Detection ⭐⭐⭐⭐
- **링크**: https://www.kaggle.com/datasets/rendiputra/stunting-balita-detection-121k-rows
- **다운로드 방법**: 위와 동일
- **저장 위치**: `data/raw/kaggle/stunting-balita-detection-121k-rows/`

#### 3. Lung Capacity of Kids ⭐⭐⭐
- **링크**: https://www.kaggle.com/datasets/jacopoferretti/lung-capacity-of-kids
- **다운로드 방법**: 위와 동일
- **저장 위치**: `data/raw/kaggle/lung-capacity-of-kids/`

### 수동 다운로드 후 디렉토리 구조
```
data/raw/kaggle/
├── parents-heights-vs-children-heights-galton-data/
│   └── GaltonFamilies.csv
├── stunting-balita-detection-121k-rows/
│   └── [CSV 파일들]
└── lung-capacity-of-kids/
    └── [CSV 파일들]
```

---

## 다음 단계

데이터 다운로드가 완료되면:
1. 데이터 검증 및 탐색
2. 데이터 전처리
3. 모델 학습 준비

---

**참고**: 일부 Kaggle 데이터셋은 라이선스 동의가 필요할 수 있습니다. 웹사이트에서 데이터셋 페이지를 열어 "I Understand and Accept" 버튼을 클릭해야 할 수 있습니다.

