# 로컬 예측 엔진 설치/실행 가이드

GitHub Pages는 정적 웹만 제공하므로, 실제 예측은 로컬 엔진(Flask API)으로 처리합니다.

## 1) 실행 파일 배포 방식

- GitHub `Releases`에서 OS별 번들(zip)을 다운로드합니다.
- 압축 해제 후 `height-prediction-local-engine` 실행 파일을 실행합니다.
  - Windows: `height-prediction-local-engine.exe`
  - macOS/Linux: `height-prediction-local-engine`

## 2) 기본 API 주소

- 로컬 엔진 기본 주소: `http://127.0.0.1:58761`
- GitHub Pages 웹은 이 주소를 자동으로 감지해 호출합니다.

## 3) 직접 Python으로 실행(개발/테스트용)

권장 Python 버전: `3.11` (모델 학습/릴리즈 환경과 동일)

```bash
python -m venv .venv  # 가능하면 python3.11 사용 권장
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python scripts/run_local_engine.py --host 127.0.0.1 --port 58761
```

## 4) CORS 허용 Origin 지정(권장)

기본값은 `https://*.github.io` 및 localhost 계열입니다.

특정 페이지 도메인만 허용하려면:

```bash
HEIGHT_AI_ALLOWED_ORIGINS="https://<your-id>.github.io" \
python scripts/run_local_engine.py
```

Windows PowerShell:

```powershell
$env:HEIGHT_AI_ALLOWED_ORIGINS="https://<your-id>.github.io"
python scripts/run_local_engine.py
```

## 5) API 주소를 강제로 바꾸고 싶다면

페이지 URL에 `apiBase`를 붙입니다:

`https://<your-id>.github.io/<repo>/?apiBase=http://127.0.0.1:58761`
