"""
데이터셋 다운로드 스크립트
공개 데이터셋을 다운로드하거나 합성 데이터를 생성합니다.
"""

import os
import sys
import requests
import pandas as pd
import numpy as np
from pathlib import Path

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"

def ensure_data_dir():
    """데이터 디렉토리 생성"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"데이터 디렉토리 확인: {DATA_DIR}")

def download_who_growth_data():
    """
    WHO 성장 표준 데이터를 기반으로 한 합성 데이터 생성
    WHO 표준은 통계표 형태로 제공되므로, 이를 기반으로 합성 데이터를 생성합니다.
    """
    print("\n=== WHO 성장 표준 기반 데이터 생성 ===")
    
    # WHO 성장 표준 (0-60개월 남아/여아 평균 키 데이터)
    # 출처: WHO Child Growth Standards
    # https://www.who.int/tools/child-growth-standards/standards
    
    who_data = []
    
    # 남아 데이터 (0-60개월)
    for month in range(0, 61):
        if month < 24:
            # 0-24개월: 더 빠른 성장
            height = 50.5 + (month * 1.5) + np.random.normal(0, 2)
        else:
            # 24-60개월: 성장 속도 감소
            base_height = 86.8 + ((month - 24) * 0.9)
            height = base_height + np.random.normal(0, 2.5)
        
        # 최종 성인 키 추정 (성별, 부모 키 등 고려하지 않은 간단한 추정)
        # 실제로는 더 복잡한 모델이 필요
        adult_height_estimate = height * (180 / 120)  # 단순 비율 추정 (실제로는 더 정교함)
        
        who_data.append({
            'age_months': month,
            'gender': 'M',
            'height_cm': max(45, min(height, 130)),  # 범위 제한
            'adult_height_cm': max(160, min(adult_height_estimate, 200))
        })
    
    # 여아 데이터 (0-60개월)
    for month in range(0, 61):
        if month < 24:
            height = 49.9 + (month * 1.4) + np.random.normal(0, 2)
        else:
            base_height = 85.7 + ((month - 24) * 0.85)
            height = base_height + np.random.normal(0, 2.5)
        
        adult_height_estimate = height * (165 / 115)  # 여아 평균 성인 키 고려
        
        who_data.append({
            'age_months': month,
            'gender': 'F',
            'height_cm': max(45, min(height, 130)),
            'adult_height_cm': max(150, min(adult_height_estimate, 185))
        })
    
    df_who = pd.DataFrame(who_data)
    
    # 여러 아이들을 시뮬레이션 (각 월령당 10명씩)
    expanded_data = []
    for _, row in df_who.iterrows():
        for i in range(10):
            noise = np.random.normal(0, 3)  # 개인차 반영
            expanded_data.append({
                'age_months': row['age_months'],
                'gender': row['gender'],
                'height_cm': max(45, row['height_cm'] + noise),
                'adult_height_cm': max(150 if row['gender'] == 'F' else 160, 
                                      row['adult_height_cm'] + np.random.normal(0, 5))
            })
    
    df_expanded = pd.DataFrame(expanded_data)
    output_path = DATA_DIR / "who_growth_synthetic.csv"
    df_expanded.to_csv(output_path, index=False)
    print(f"WHO 기반 합성 데이터 저장 완료: {output_path}")
    print(f"데이터 크기: {len(df_expanded)} 행")
    print(f"컬럼: {list(df_expanded.columns)}")
    
    return df_expanded

def generate_realistic_synthetic_data(n_samples=1000):
    """
    더 현실적인 합성 데이터 생성
    성별, 연령, 부모 키 등을 고려한 데이터셋
    """
    print("\n=== 현실적인 합성 데이터 생성 ===")
    
    np.random.seed(42)  # 재현 가능성을 위한 시드 설정
    
    data = []
    
    for i in range(n_samples):
        gender = np.random.choice(['M', 'F'])
        
        # 부모 키 생성 (정규 분포)
        if gender == 'M':
            father_height = np.random.normal(175, 6)  # 남성 평균 키
            mother_height = np.random.normal(162, 5)  # 여성 평균 키
        else:
            father_height = np.random.normal(175, 6)
            mother_height = np.random.normal(162, 5)
        
        # 부모 평균 키
        mid_parental_height = (father_height + mother_height) / 2
        
        # 연령 생성 (6개월 ~ 18세)
        age_years = np.random.uniform(0.5, 18)
        age_months = int(age_years * 12)
        
        # 현재 키 생성 (연령과 성별에 따른 성장 곡선 고려)
        if age_years < 2:
            # 0-2세: 빠른 성장
            base_height = 50 + (age_years * 24)
        elif age_years < 10:
            # 2-10세: 안정적 성장
            base_height = 85 + ((age_years - 2) * 6)
        elif age_years < 14:
            # 10-14세: 사춘기 전 성장
            base_height = 133 + ((age_years - 10) * 5)
        else:
            # 14-18세: 사춘기 및 성장 완료 단계
            if gender == 'M':
                base_height = 153 + ((age_years - 14) * 3)
            else:
                base_height = 153 + ((age_years - 14) * 1.5)
        
        # 성별 차이 반영
        if gender == 'F':
            base_height -= 5
        
        # 유전적 요인 반영 (부모 키 영향)
        genetic_factor = (mid_parental_height - 168) * 0.5
        current_height = base_height + genetic_factor + np.random.normal(0, 4)
        
        # 최종 성인 키 추정 (현재 키, 연령, 부모 키 기반)
        if age_years < 10:
            # 성장 가능성이 높음
            adult_height = mid_parental_height + np.random.normal(0, 5)
            if gender == 'M':
                adult_height += 5  # 남성은 여성보다 약 5cm 더 큼
            adult_height = current_height + (adult_height - current_height) * np.random.uniform(0.3, 0.7)
        elif age_years < 14:
            # 성장 가능성 중간
            adult_height = mid_parental_height + np.random.normal(0, 4)
            if gender == 'M':
                adult_height += 5
            adult_height = current_height + (adult_height - current_height) * np.random.uniform(0.2, 0.5)
        else:
            # 성장 가능성 낮음
            adult_height = current_height + np.random.normal(0, 3)
        
        # 범위 제한
        current_height = max(50, min(current_height, 200))
        adult_height = max(140 if gender == 'F' else 150, min(adult_height, 220))
        
        # 체중 생성 (BMI 기반 추정)
        bmi = np.random.normal(18, 2.5) if age_years < 10 else np.random.normal(20, 3)
        weight = (current_height / 100) ** 2 * bmi
        
        data.append({
            'age_years': round(age_years, 2),
            'age_months': age_months,
            'gender': gender,
            'height_cm': round(current_height, 1),
            'weight_kg': round(weight, 1),
            'father_height_cm': round(father_height, 1),
            'mother_height_cm': round(mother_height, 1),
            'adult_height_cm': round(adult_height, 1)
        })
    
    df = pd.DataFrame(data)
    output_path = DATA_DIR / "synthetic_growth_data.csv"
    df.to_csv(output_path, index=False)
    print(f"합성 데이터 저장 완료: {output_path}")
    print(f"데이터 크기: {len(df)} 행")
    print(f"\n데이터 미리보기:")
    print(df.head(10))
    print(f"\n기본 통계:")
    print(df.describe())
    
    return df

def main():
    """메인 함수"""
    print("=" * 50)
    print("성장기 어린이 키 예측 데이터셋 다운로드")
    print("=" * 50)
    
    ensure_data_dir()
    
    # 1. WHO 기반 합성 데이터 생성
    try:
        df_who = download_who_growth_data()
    except Exception as e:
        print(f"WHO 데이터 생성 중 오류: {e}")
    
    # 2. 더 현실적인 합성 데이터 생성 (더 큰 샘플)
    try:
        df_synthetic = generate_realistic_synthetic_data(n_samples=2000)
    except Exception as e:
        print(f"합성 데이터 생성 중 오류: {e}")
    
    print("\n" + "=" * 50)
    print("데이터 다운로드/생성 완료!")
    print(f"데이터 위치: {DATA_DIR}")
    print("=" * 50)

if __name__ == "__main__":
    main()


