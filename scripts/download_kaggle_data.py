"""
Kaggle 데이터셋 다운로드 스크립트
프로젝트에 가장 적합한 데이터셋들을 다운로드합니다.
"""

import os
import sys
import subprocess
from pathlib import Path
import zipfile
import shutil

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
KAGGLE_DATA_DIR = DATA_DIR / "kaggle"

# 다운로드할 데이터셋 목록
DATASETS = [
    {
        "name": "Parents Heights vs Children Heights",
        "dataset": "jacopoferretti/parents-heights-vs-children-heights-galton-data",
        "description": "1886년 Galton 데이터 - 부모 키와 자녀 성인 키 (934명, 부모 키 포함)"
    },
    {
        "name": "Stunting Toddler Detection",
        "dataset": "rendiputra/stunting-balita-detection-121k-rows",
        "description": "대규모 영아 성장 데이터 (121K 행, 키/나이 포함)"
    },
    {
        "name": "Lung Capacity of Kids",
        "dataset": "jacopoferretti/lung-capacity-of-kids",
        "description": "어린이 폐용량 데이터 (키, 성별 포함)"
    }
]

def check_kaggle_installed():
    """Kaggle 패키지 설치 확인"""
    try:
        # kaggle 모듈 import만 확인 (인증은 나중에)
        import importlib.util
        spec = importlib.util.find_spec("kaggle")
        if spec is None:
            raise ImportError("Kaggle module not found")
        print("✅ Kaggle 패키지가 설치되어 있습니다.")
        return True
    except ImportError:
        print("❌ Kaggle 패키지가 설치되지 않았습니다.")
        print("설치 중...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle", "--quiet"])
            print("✅ Kaggle 패키지 설치 완료")
            return True
        except Exception as e:
            print(f"❌ Kaggle 패키지 설치 실패: {e}")
            return False

def check_kaggle_auth():
    """Kaggle 인증 확인"""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if kaggle_json.exists():
        print("✅ Kaggle 인증 파일이 발견되었습니다.")
        # 권한 설정 (Kaggle 요구사항)
        os.chmod(kaggle_json, 0o600)
        return True
    else:
        print("❌ Kaggle 인증 파일이 없습니다.")
        print("\n📝 Kaggle API 키 설정 방법:")
        print("1. https://www.kaggle.com/ 접속")
        print("2. 계정 설정 > API > Create New Token 클릭")
        print("3. 다운로드된 kaggle.json 파일을 ~/.kaggle/ 디렉토리에 저장")
        print(f"   저장 경로: {kaggle_json}")
        return False

def download_dataset(dataset_info):
    """개별 데이터셋 다운로드"""
    dataset_name = dataset_info["name"]
    dataset_id = dataset_info["dataset"]
    
    print(f"\n{'='*60}")
    print(f"다운로드 중: {dataset_name}")
    print(f"데이터셋 ID: {dataset_id}")
    print(f"설명: {dataset_info['description']}")
    print(f"{'='*60}")
    
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        
        # 데이터셋 저장 디렉토리 생성
        dataset_dir = KAGGLE_DATA_DIR / dataset_id.split('/')[1]
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        # 데이터셋 다운로드
        print(f"다운로드 시작...")
        api.dataset_download_files(
            dataset_id, 
            path=str(dataset_dir),
            unzip=True,
            quiet=False
        )
        
        # 압축 파일이 있으면 삭제
        for zip_file in dataset_dir.glob("*.zip"):
            zip_file.unlink()
        
        print(f"✅ {dataset_name} 다운로드 완료!")
        print(f"   저장 위치: {dataset_dir}")
        
        # 다운로드된 파일 목록 출력
        files = list(dataset_dir.glob("*"))
        if files:
            print(f"   다운로드된 파일 ({len(files)}개):")
            for f in files:
                if f.is_file():
                    size = f.stat().st_size
                    size_mb = size / (1024 * 1024)
                    print(f"     - {f.name} ({size_mb:.2f} MB)")
        
        return True, dataset_dir
        
    except Exception as e:
        print(f"❌ 다운로드 실패: {e}")
        print(f"   가능한 원인:")
        print(f"   1. Kaggle 계정 인증 필요")
        print(f"   2. 데이터셋 접근 권한 필요 (일부 데이터셋은 라이선스 동의 필요)")
        print(f"   3. 네트워크 연결 문제")
        return False, None

def main():
    """메인 함수"""
    print("="*60)
    print("Kaggle 데이터셋 다운로드")
    print("="*60)
    
    # 디렉토리 생성
    KAGGLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Kaggle 패키지 확인
    if not check_kaggle_installed():
        print("\n⚠️  Kaggle 패키지 설치 후 다시 시도해주세요.")
        return
    
    # Kaggle 인증 확인
    if not check_kaggle_auth():
        print("\n⚠️  Kaggle API 키 설정 후 다시 시도해주세요.")
        print("\n대안: Kaggle 웹사이트에서 수동으로 다운로드하세요:")
        for ds in DATASETS:
            print(f"  - {ds['name']}: https://www.kaggle.com/datasets/{ds['dataset']}")
        return
    
    print("\n" + "="*60)
    print("다운로드 시작")
    print("="*60)
    
    # 데이터셋 다운로드
    success_count = 0
    failed_datasets = []
    
    for dataset_info in DATASETS:
        success, download_dir = download_dataset(dataset_info)
        if success:
            success_count += 1
        else:
            failed_datasets.append(dataset_info["name"])
    
    # 결과 요약
    print("\n" + "="*60)
    print("다운로드 결과 요약")
    print("="*60)
    print(f"성공: {success_count}/{len(DATASETS)}")
    if failed_datasets:
        print(f"실패: {len(failed_datasets)}개")
        for name in failed_datasets:
            print(f"  - {name}")
    
    if success_count > 0:
        print(f"\n✅ 다운로드된 데이터 위치: {KAGGLE_DATA_DIR}")
        print("\n다음 단계:")
        print("1. 다운로드된 데이터 확인")
        print("2. 데이터 전처리 스크립트 실행")
        print("3. 모델 학습 준비")

if __name__ == "__main__":
    main()

