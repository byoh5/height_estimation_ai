"""
실제 공개 데이터셋 다운로드를 시도하는 스크립트
"""

import requests
import pandas as pd
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"

def try_download_nhanes():
    """
    NHANES 데이터 다운로드 시도
    참고: NHANES는 복잡한 구조이며 일반적으로 직접 CSV 다운로드가 어렵습니다.
    """
    print("=== NHANES 데이터 다운로드 시도 ===")
    print("NHANES 데이터는 일반적으로 공식 웹사이트에서 복잡한 구조로 제공됩니다.")
    print("직접 다운로드보다는 nhanes 패키지를 사용하는 것이 권장됩니다.")
    print("URL: https://www.cdc.gov/nchs/nhanes/index.htm")
    return False

def check_kaggle_datasets():
    """Kaggle에서 관련 데이터셋 검색 (kaggle API 필요)"""
    print("\n=== Kaggle 데이터셋 검색 ===")
    print("Kaggle API를 사용하려면 kaggle 패키지 설치 및 인증이 필요합니다.")
    print("수동으로 검색할 수 있는 키워드:")
    print("- 'children height'")
    print("- 'pediatric growth'")
    print("- 'child growth chart'")
    print("URL: https://www.kaggle.com/datasets")
    return False

def main():
    """실제 데이터셋 다운로드 시도"""
    print("=" * 60)
    print("실제 공개 데이터셋 다운로드 시도")
    print("=" * 60)
    
    print("\n⚠️  주의사항:")
    print("성장기 어린이의 키 데이터는 개인정보 보호 문제로")
    print("공개 데이터셋이 매우 제한적입니다.")
    print("\n가능한 옵션:")
    print("1. 합성 데이터 사용 (현재 생성됨)")
    print("2. 공공기관 데이터 신청 (한국 질병관리청 등)")
    print("3. 연구 기관 협업")
    print("4. Kaggle에서 수동 검색 및 다운로드")
    
    try_download_nhanes()
    check_kaggle_datasets()
    
    print("\n" + "=" * 60)
    print("현재 상황:")
    print("✓ 합성 데이터셋 생성 완료 (synthetic_growth_data.csv)")
    print("  - 2,000개의 합성 샘플")
    print("  - 성별, 연령, 부모 키 등 포함")
    print("\n실제 데이터셋을 찾으려면:")
    print("1. Kaggle에서 직접 검색 및 다운로드")
    print("2. 질병관리청 한국인 성장도표 데이터 활용")
    print("3. 연구 논문 부록 데이터 활용")
    print("=" * 60)

if __name__ == "__main__":
    main()


