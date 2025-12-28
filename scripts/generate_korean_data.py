"""
한국인 성장도표 기반 합성 데이터 생성 스크립트
질병관리청 한국인 성장도표 통계를 기반으로 한국 어린이 키 예측용 데이터를 생성합니다.
"""

import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"

# 질병관리청 한국인 성장도표 기반 평균 키 데이터 (cm)
# 출처: 질병관리청 한국인 성장도표 (2023년 기준)
KOREAN_GROWTH_CHART = {
    # 남아 (Male)
    'M': {
        # 연령(세): 평균 키 (cm)
        0: 50.5,      # 출생 시
        1: 76.5,
        2: 87.8,
        3: 96.1,
        4: 103.3,
        5: 109.4,
        6: 115.1,
        7: 120.5,
        8: 125.5,
        9: 130.3,
        10: 134.8,
        11: 139.5,
        12: 144.8,
        13: 151.2,
        14: 158.1,
        15: 163.8,
        16: 168.0,
        17: 170.8,
        18: 172.5,    # 성인 평균 키 (한국 남성)
    },
    # 여아 (Female)
    'F': {
        0: 49.9,      # 출생 시
        1: 75.0,
        2: 86.5,
        3: 94.9,
        4: 101.8,
        5: 108.1,
        6: 113.6,
        7: 118.8,
        8: 123.6,
        9: 128.1,
        10: 132.4,
        11: 137.2,
        12: 142.5,
        13: 148.5,
        14: 153.2,
        15: 156.5,
        16: 158.5,
        17: 159.5,
        18: 160.0,    # 성인 평균 키 (한국 여성)
    }
}

def interpolate_height(age_years, gender):
    """연령에 따른 키 보간 (한국인 성장도표 기반)"""
    chart = KOREAN_GROWTH_CHART[gender]
    ages = sorted(chart.keys())
    
    if age_years <= ages[0]:
        return chart[ages[0]]
    if age_years >= ages[-1]:
        return chart[ages[-1]]
    
    # 선형 보간
    for i in range(len(ages) - 1):
        if ages[i] <= age_years < ages[i + 1]:
            age1, height1 = ages[i], chart[ages[i]]
            age2, height2 = ages[i + 1], chart[ages[i + 1]]
            ratio = (age_years - age1) / (age2 - age1)
            return height1 + (height2 - height1) * ratio
    
    return chart[ages[-1]]

def generate_korean_growth_data(n_samples=3000):
    """
    한국인 성장도표 기반 합성 데이터 생성
    한국인 평균 성장 패턴을 반영한 데이터셋
    """
    print("="*60)
    print("한국인 성장도표 기반 데이터 생성")
    print("="*60)
    
    np.random.seed(42)
    data = []
    
    print(f"\n{n_samples}개의 샘플 생성 중...")
    
    for i in range(n_samples):
        gender = np.random.choice(['M', 'F'])
        
        # 부모 키 생성 (한국인 평균 반영)
        if gender == 'M':
            # 한국 남성 평균 키: 172.5cm, 표준편차: 5.5cm
            father_height = np.random.normal(172.5, 5.5)
            # 한국 여성 평균 키: 160.0cm, 표준편차: 5.0cm
            mother_height = np.random.normal(160.0, 5.0)
        else:
            father_height = np.random.normal(172.5, 5.5)
            mother_height = np.random.normal(160.0, 5.0)
        
        # 부모 평균 키
        mid_parental_height = (father_height + mother_height) / 2
        
        # 연령 생성 (0세 ~ 18세)
        age_years = np.random.uniform(0, 18)
        age_months = int(age_years * 12)
        
        # 한국인 성장도표 기반 현재 키
        base_height = interpolate_height(age_years, gender)
        
        # 유전적 요인 반영 (부모 키 영향)
        # 한국인 부모 키와 평균 키 차이를 일정 비율 반영
        genetic_factor = (mid_parental_height - (172.5 + 160.0) / 2) * 0.6
        
        # 개인차 반영 (표준편차 4cm)
        individual_variation = np.random.normal(0, 4)
        
        current_height = base_height + genetic_factor + individual_variation
        
        # 최종 성인 키 추정
        # 연령과 현재 키를 고려하여 추정
        if age_years < 10:
            # 성장 가능성이 높음
            adult_height = mid_parental_height + np.random.normal(0, 5)
            if gender == 'M':
                adult_height = max(155, min(adult_height, 195))
            else:
                adult_height = max(145, min(adult_height, 180))
            
            # 현재 키에서 성인 키까지의 성장 추정
            growth_remaining = (adult_height - current_height) * np.random.uniform(0.3, 0.7)
            adult_height = current_height + growth_remaining
            
        elif age_years < 14:
            # 성장 가능성 중간
            adult_height = mid_parental_height + np.random.normal(0, 4)
            if gender == 'M':
                adult_height = max(160, min(adult_height, 195))
            else:
                adult_height = max(150, min(adult_height, 180))
            
            growth_remaining = (adult_height - current_height) * np.random.uniform(0.2, 0.5)
            adult_height = current_height + growth_remaining
            
        else:
            # 성장 가능성 낮음 (거의 성인)
            adult_height = current_height + np.random.normal(0, 2)
            if gender == 'M':
                adult_height = max(160, min(adult_height, 195))
            else:
                adult_height = max(150, min(adult_height, 180))
        
        # 범위 제한
        current_height = max(45, min(current_height, 200))
        adult_height = max(140 if gender == 'F' else 150, 
                          min(adult_height, 220 if gender == 'M' else 190))
        
        # 체중 생성 (한국인 평균 BMI 기반)
        if age_years < 10:
            bmi = np.random.normal(16.5, 2.0)
        else:
            bmi = np.random.normal(19.0, 2.5)
        weight = (current_height / 100) ** 2 * bmi
        
        data.append({
            'age_years': round(age_years, 2),
            'age_months': age_months,
            'gender': gender,
            'height_cm': round(current_height, 1),
            'weight_kg': round(weight, 1),
            'father_height_cm': round(father_height, 1),
            'mother_height_cm': round(mother_height, 1),
            'adult_height_cm': round(adult_height, 1),
            'nationality': 'KR'  # 한국 데이터 표시
        })
    
    df = pd.DataFrame(data)
    
    # 저장
    output_path = DATA_DIR / "korean_growth_data.csv"
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ 한국인 성장 데이터 생성 완료!")
    print(f"   저장 위치: {output_path}")
    print(f"   데이터 크기: {len(df)} 행")
    print(f"\n📊 데이터 요약:")
    print(f"   남아: {len(df[df['gender'] == 'M'])}명")
    print(f"   여아: {len(df[df['gender'] == 'F'])}명")
    print(f"\n📏 평균 키:")
    print(f"   남아 평균 현재 키: {df[df['gender'] == 'M']['height_cm'].mean():.1f}cm")
    print(f"   여아 평균 현재 키: {df[df['gender'] == 'F']['height_cm'].mean():.1f}cm")
    print(f"   남아 평균 성인 키: {df[df['gender'] == 'M']['adult_height_cm'].mean():.1f}cm")
    print(f"   여아 평균 성인 키: {df[df['gender'] == 'F']['adult_height_cm'].mean():.1f}cm")
    
    print(f"\n📋 데이터 미리보기:")
    print(df.head(10).to_string())
    
    print(f"\n📈 기본 통계:")
    print(df[['age_years', 'height_cm', 'weight_kg', 'father_height_cm', 
              'mother_height_cm', 'adult_height_cm']].describe())
    
    return df

def main():
    """메인 함수"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 한국인 성장 데이터 생성
    df_korean = generate_korean_growth_data(n_samples=3000)
    
    print("\n" + "="*60)
    print("한국인 성장 데이터 생성 완료!")
    print("="*60)
    print("\n💡 참고:")
    print("  - 이 데이터는 질병관리청 한국인 성장도표 통계를 기반으로 생성되었습니다.")
    print("  - 한국인 평균 성장 패턴을 반영하고 있습니다.")
    print("  - 부모 키와 유전적 요인을 고려한 합성 데이터입니다.")
    print("\n📝 다음 단계:")
    print("  - 데이터 탐색 및 분석 (EDA)")
    print("  - 국제 데이터와 결합하여 모델 학습")

if __name__ == "__main__":
    main()

