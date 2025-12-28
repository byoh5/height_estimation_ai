"""
다운로드된 Kaggle 데이터를 정리하는 스크립트
수동으로 다운로드한 데이터도 정리할 수 있습니다.
"""

import os
import shutil
import zipfile
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
KAGGLE_DATA_DIR = DATA_DIR / "kaggle"
DOWNLOADS_DIR = Path.home() / "Downloads"

def find_kaggle_zip_files():
    """Downloads 폴더에서 Kaggle 관련 ZIP 파일 찾기"""
    zip_files = []
    if DOWNLOADS_DIR.exists():
        for zip_file in DOWNLOADS_DIR.glob("*kaggle*.zip"):
            zip_files.append(zip_file)
        for zip_file in DOWNLOADS_DIR.glob("*galton*.zip"):
            zip_files.append(zip_file)
        for zip_file in DOWNLOADS_DIR.glob("*stunting*.zip"):
            zip_files.append(zip_file)
        for zip_file in DOWNLOADS_DIR.glob("*lung*.zip"):
            zip_files.append(zip_file)
    return zip_files

def extract_and_organize_dataset(zip_path, target_dir):
    """ZIP 파일을 압축 해제하고 정리"""
    try:
        print(f"  압축 해제 중: {zip_path.name}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        
        print(f"  ✅ 완료: {target_dir}")
        
        # CSV 파일 목록 확인
        csv_files = list(target_dir.glob("*.csv"))
        if csv_files:
            print(f"  발견된 CSV 파일 ({len(csv_files)}개):")
            for csv in csv_files:
                size = csv.stat().st_size / (1024 * 1024)  # MB
                print(f"    - {csv.name} ({size:.2f} MB)")
        
        return True
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        return False

def organize_existing_files():
    """이미 다운로드된 파일 정리"""
    KAGGLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Downloads에서 Kaggle ZIP 파일 찾기
    zip_files = find_kaggle_zip_files()
    
    if not zip_files:
        print("📁 Downloads 폴더에서 Kaggle 관련 ZIP 파일을 찾지 못했습니다.")
        print("   수동으로 다운로드한 파일이 있으면 data/raw/kaggle/ 디렉토리에 직접 복사해주세요.")
        return
    
    print(f"📦 {len(zip_files)}개의 ZIP 파일을 찾았습니다.")
    
    for zip_file in zip_files:
        # 파일명 기반으로 타겟 디렉토리 결정
        if "galton" in zip_file.name.lower() or "parents" in zip_file.name.lower():
            target_dir = KAGGLE_DATA_DIR / "parents-heights-vs-children-heights-galton-data"
        elif "stunting" in zip_file.name.lower() or "balita" in zip_file.name.lower():
            target_dir = KAGGLE_DATA_DIR / "stunting-balita-detection-121k-rows"
        elif "lung" in zip_file.name.lower():
            target_dir = KAGGLE_DATA_DIR / "lung-capacity-of-kids"
        else:
            target_dir = KAGGLE_DATA_DIR / zip_file.stem
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n처리 중: {zip_file.name}")
        if extract_and_organize_dataset(zip_file, target_dir):
            # 성공하면 원본 ZIP 파일은 그대로 두기 (나중에 삭제할 수도 있음)
            pass

def check_data_summary():
    """다운로드된 데이터 요약"""
    print("\n" + "="*60)
    print("다운로드된 데이터 요약")
    print("="*60)
    
    if not KAGGLE_DATA_DIR.exists():
        print("❌ Kaggle 데이터 디렉토리가 없습니다.")
        return
    
    datasets = []
    for dataset_dir in KAGGLE_DATA_DIR.iterdir():
        if dataset_dir.is_dir():
            csv_files = list(dataset_dir.glob("*.csv"))
            if csv_files:
                total_size = sum(f.stat().st_size for f in csv_files) / (1024 * 1024)
                datasets.append({
                    "name": dataset_dir.name,
                    "files": len(csv_files),
                    "size_mb": total_size
                })
    
    if not datasets:
        print("📂 Kaggle 데이터 디렉토리는 있지만 CSV 파일이 없습니다.")
        print(f"   경로: {KAGGLE_DATA_DIR}")
        return
    
    print(f"\n✅ {len(datasets)}개의 데이터셋 발견:\n")
    for ds in datasets:
        print(f"  📊 {ds['name']}")
        print(f"     파일: {ds['files']}개")
        print(f"     크기: {ds['size_mb']:.2f} MB")
        print()

def main():
    """메인 함수"""
    print("="*60)
    print("Kaggle 데이터 정리 스크립트")
    print("="*60)
    
    # Downloads 폴더의 ZIP 파일 정리
    organize_existing_files()
    
    # 데이터 요약
    check_data_summary()
    
    print("="*60)
    print("완료!")
    print("="*60)

if __name__ == "__main__":
    main()

