#!/usr/bin/env python3
"""
성장 곡선 예측 CLI 스크립트
특정 나이의 키를 예측합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.modeling.growth_curve_predictor import GrowthCurvePredictor

def main():
    """메인 함수"""
    print("="*60)
    print("성장 곡선 예측 시스템")
    print("="*60)
    
    predictor = GrowthCurvePredictor()
    
    if not predictor.models:
        print("❌ 모델이 없습니다. 먼저 모델을 학습시켜주세요.")
        return
    
    print(f"\n📊 사용 가능한 예측 나이: {predictor.get_available_ages()}세")
    
    print("\n📝 현재 정보를 입력해주세요:\n")
    
    # 필수 입력
    gender = input("성별 (M/F): ").strip().upper()
    if gender not in ['M', 'F']:
        print("❌ 성별은 M 또는 F여야 합니다.")
        return
    
    current_age_input = input("현재 나이 (세, 예: 8): ").strip()
    try:
        current_age_years = float(current_age_input)
    except ValueError:
        print("❌ 나이는 숫자로 입력해주세요.")
        return
    
    current_height_input = input("현재 키 (cm, 예: 130): ").strip()
    try:
        current_height_cm = float(current_height_input)
    except ValueError:
        print("❌ 키는 숫자로 입력해주세요.")
        return
    
    # 예측할 나이 선택
    print("\n예측할 나이를 선택하세요:")
    print("1. 특정 나이 예측")
    print("2. 여러 나이 예측 (성장 곡선)")
    
    choice = input("선택 (1 또는 2): ").strip()
    
    if choice == "1":
        target_age_input = input("\n예측할 나이 (세, 예: 15): ").strip()
        try:
            target_age_years = float(target_age_input)
            
            result = predictor.predict_at_age(
                current_age_years=current_age_years,
                current_height_cm=current_height_cm,
                target_age_years=target_age_years,
                gender=gender
            )
            
            print("\n" + "="*60)
            print("예측 결과")
            print("="*60)
            print(f"\n현재: {result['current_age_years']}세, {result['current_height_cm']}cm")
            print(f"예측: {result['target_age_years']}세에 {result['predicted_height_cm']:.1f}cm")
            print(f"\n예상 성장: {result['growth_expected']:.1f}cm")
            print(f"남은 시간: {result['years_until_target']:.1f}년")
            if 'model_metrics' in result:
                print(f"모델 정확도 (검증 MAE): {result['model_metrics']['val_mae']:.2f}cm")
        
        except ValueError as e:
            print(f"\n❌ 오류: {e}")
    
    elif choice == "2":
        result = predictor.predict_growth_curve(
            current_age_years=current_age_years,
            current_height_cm=current_height_cm,
            gender=gender
        )
        
        print("\n" + "="*60)
        print("성장 곡선 예측 결과")
        print("="*60)
        print(f"\n현재: {result['current_info']['age_years']}세, {result['current_info']['height_cm']}cm")
        print(f"\n예측 결과:")
        print(f"{'나이':<6} {'예상 키':<10} {'예상 성장':<12} {'남은 시간':<12}")
        print("-" * 45)
        
        for age in sorted(result['predictions'].keys()):
            pred = result['predictions'][age]
            print(f"{age}세     {pred['predicted_height_cm']:>6.1f}cm   {pred['growth_expected']:>+8.1f}cm      {pred['years_until_target']:>6.1f}년")
    
    else:
        print("❌ 1 또는 2를 선택해주세요.")

if __name__ == "__main__":
    main()

