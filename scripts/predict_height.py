#!/usr/bin/env python3
"""
키 예측 CLI 스크립트
하이브리드 모델을 사용하여 성인 키를 예측합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.modeling.hybrid_predictor import HybridHeightPredictor

def main():
    """메인 함수"""
    print("="*60)
    print("성인 키 예측 시스템")
    print("="*60)
    
    predictor = HybridHeightPredictor()
    
    print("\n📝 예측을 위한 정보를 입력해주세요:")
    print("   (정보가 많을수록 더 정확한 예측이 가능합니다)\n")
    
    # 필수 입력
    gender = input("성별 (M/F): ").strip().upper()
    if gender not in ['M', 'F']:
        print("❌ 성별은 M 또는 F여야 합니다.")
        return
    
    # 선택 입력
    age_years = None
    age_months = None
    height_cm = None
    father_height_cm = None
    mother_height_cm = None
    
    age_input = input("나이 (세, 예: 10) [선택사항]: ").strip()
    if age_input:
        try:
            age_years = float(age_input)
            age_months = age_years * 12
        except ValueError:
            print("⚠️  나이는 숫자로 입력해주세요.")
    
    height_input = input("현재 키 (cm, 예: 140) [선택사항]: ").strip()
    if height_input:
        try:
            height_cm = float(height_input)
        except ValueError:
            print("⚠️  키는 숫자로 입력해주세요.")
    
    father_input = input("아버지 키 (cm, 예: 175) [선택사항]: ").strip()
    if father_input:
        try:
            father_height_cm = float(father_input)
        except ValueError:
            print("⚠️  아버지 키는 숫자로 입력해주세요.")
    
    mother_input = input("어머니 키 (cm, 예: 162) [선택사항]: ").strip()
    if mother_input:
        try:
            mother_height_cm = float(mother_input)
        except ValueError:
            print("⚠️  어머니 키는 숫자로 입력해주세요.")
    
    # 예측 수행
    try:
        result = predictor.predict(
            age_years=age_years,
            age_months=age_months,
            height_cm=height_cm,
            gender=gender,
            father_height_cm=father_height_cm,
            mother_height_cm=mother_height_cm
        )
        
        print("\n" + "="*60)
        print("예측 결과")
        print("="*60)
        print(f"\n예상 성인 키: {result['predicted_height']:.1f}cm")
        print(f"사용된 모델: {', '.join(result['model_used'])}")
        print(f"신뢰도: {result['confidence']}")
        
        if 'galton_prediction' in result['details']:
            print(f"\n부모 키 기반 예측: {result['details']['galton_prediction']:.1f}cm")
        if 'stunting_prediction' in result['details']:
            print(f"성장 패턴 기반 예측: {result['details']['stunting_prediction']:.1f}cm")
        
        if 'weights' in result['details']:
            print(f"\n모델 가중치:")
            for model, weight in result['details']['weights'].items():
                print(f"  {model}: {weight:.1%}")
        
    except ValueError as e:
        print(f"\n❌ 오류: {e}")
        print("\n최소한 다음 정보가 필요합니다:")
        print("  - 성별 (필수)")
        print("  - 나이 + 현재 키 (성장 패턴 기반 예측)")
        print("  - 부모 키 (부모 키 기반 예측)")

if __name__ == "__main__":
    main()

