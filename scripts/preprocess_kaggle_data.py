"""
Kaggle 데이터 전처리 스크립트
다운로드한 데이터를 프로젝트에 맞게 정리하고 통합합니다.
"""

import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
KAGGLE_DIR = DATA_DIR / "kaggle"

def preprocess_balita_data():
    """Stunting Balita 데이터 전처리"""
    print("\n" + "="*60)
    print("Stunting Balita 데이터 전처리")
    print("="*60)
    
    input_path = KAGGLE_DIR / "stunting-balita-detection" / "data_balita.csv"
    
    if not input_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {input_path}")
        return None
    
    df = pd.read_csv(input_path)
    print(f"\n원본 데이터: {len(df):,}행, {len(df.columns)}컬럼")
    
    # 컬럼명 영어로 변경
    df = df.rename(columns={
        'Umur (bulan)': 'age_months',
        'Jenis Kelamin': 'gender',
        'Tinggi Badan (cm)': 'height_cm',
        'Status Gizi': 'nutrition_status'
    })
    
    # 성별 영어로 변경
    df['gender'] = df['gender'].map({
        'laki-laki': 'M',
        'perempuan': 'F'
    })
    
    # 나이를 연(세)로 변환
    df['age_years'] = df['age_months'] / 12
    
    # 성인 키 예측을 위한 컬럼 추가 (현재는 없으므로 추정 필요)
    # 단순 비율 기반 추정 (실제로는 더 복잡한 모델 필요)
    df['adult_height_cm'] = None  # 나중에 모델로 예측
    
    # 필요한 컬럼만 선택
    df_processed = df[[
        'age_years',
        'age_months',
        'gender',
        'height_cm',
        'nutrition_status'
    ]].copy()
    
    print(f"\n전처리 후 데이터: {len(df_processed):,}행")
    print(f"\n컬럼: {list(df_processed.columns)}")
    print(f"\n성별 분포:")
    print(df_processed['gender'].value_counts())
    print(f"\n샘플 데이터:")
    print(df_processed.head(10))
    
    return df_processed

def preprocess_galton_data():
    """Galton Families 데이터 전처리"""
    print("\n" + "="*60)
    print("Galton Families 데이터 전처리")
    print("="*60)
    
    input_path = KAGGLE_DIR / "archive" / "GaltonFamilies.csv"
    
    if not input_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {input_path}")
        return None
    
    df = pd.read_csv(input_path)
    print(f"\n원본 데이터: {len(df):,}행, {len(df.columns)}컬럼")
    
    # 인치를 cm로 변환 (1인치 = 2.54cm)
    df['father_height_cm'] = df['father'] * 2.54
    df['mother_height_cm'] = df['mother'] * 2.54
    df['child_height_cm'] = df['childHeight'] * 2.54
    df['midparent_height_cm'] = df['midparentHeight'] * 2.54
    
    # 성별 표준화
    df['gender'] = df['gender'].map({
        'male': 'M',
        'female': 'F'
    })
    
    # 나이 정보가 없으므로 성인 키 데이터로 표시
    df['age_years'] = None
    df['age_months'] = None
    df['adult_height_cm'] = df['child_height_cm']  # 이미 성인 키
    
    # 필요한 컬럼만 선택
    df_processed = df[[
        'family',
        'father_height_cm',
        'mother_height_cm',
        'midparent_height_cm',
        'gender',
        'child_height_cm',
        'adult_height_cm'
    ]].copy()
    
    # 컬럼명 표준화
    df_processed = df_processed.rename(columns={
        'child_height_cm': 'height_cm'
    })
    
    print(f"\n전처리 후 데이터: {len(df_processed):,}행")
    print(f"\n컬럼: {list(df_processed.columns)}")
    print(f"\n성별 분포:")
    print(df_processed['gender'].value_counts())
    print(f"\n키 통계 (cm):")
    print(df_processed[['father_height_cm', 'mother_height_cm', 'height_cm']].describe())
    print(f"\n샘플 데이터:")
    print(df_processed.head(10))
    
    return df_processed

def save_processed_data(df, filename):
    """전처리된 데이터 저장"""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / filename
    df.to_csv(output_path, index=False)
    print(f"\n✅ 저장 완료: {output_path}")
    return output_path

def main():
    """메인 함수"""
    print("="*60)
    print("Kaggle 데이터 전처리")
    print("="*60)
    
    # 1. Stunting Balita 데이터 전처리
    df_balita = preprocess_balita_data()
    if df_balita is not None:
        save_processed_data(df_balita, "stunting_balita_processed.csv")
    
    # 2. Galton Families 데이터 전처리
    df_galton = preprocess_galton_data()
    if df_galton is not None:
        save_processed_data(df_galton, "galton_families_processed.csv")
    
    print("\n" + "="*60)
    print("전처리 완료!")
    print("="*60)
    print(f"\n전처리된 데이터 위치: {PROCESSED_DIR}")
    
    # 요약
    if df_balita is not None:
        print(f"\n📊 Stunting Balita: {len(df_balita):,}행")
    if df_galton is not None:
        print(f"📊 Galton Families: {len(df_galton):,}행")

if __name__ == "__main__":
    main()

