#!/usr/bin/env python3
"""
빠른 예측 모델 테스트 스크립트
간단한 케이스로 빠르게 모델 동작 확인
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.modeling.enhanced_predictor import EnhancedHeightPredictor

def quick_test():
    """빠른 테스트"""
    print("="*60)
    print("빠른 예측 모델 테스트")
    print("="*60)
    
    predictor = EnhancedHeightPredictor()
    print("✅ 예측기 초기화 완료\n")
    
    # 테스트 케이스 1: 사용자 케이스 (11세 남아 163cm)
    print("📋 테스트 케이스 1: 사용자 케이스")
    print("   입력: 생년월일 2014-07-24, 남아, 현재 키 163cm")
    result1 = predictor.predict(
        birth_date='2014-07-24',
        gender='M',
        current_height_cm=163
    )
    print(f"   ✅ 예상 성인 키: {result1['predicted_height']:.1f}cm")
    print(f"   모델: {', '.join(result1['model_used'])}")
    print(f"   신뢰도: {result1['confidence']}")
    
    # 테스트 케이스 2: 여아 + 초경
    print("\n📋 테스트 케이스 2: 여아 + 초경 정보")
    print("   입력: 생년월일 2012-01-01, 여아, 현재 키 150cm, 초경 12.5세")
    result2 = predictor.predict(
        birth_date='2012-01-01',
        gender='F',
        current_height_cm=150,
        menarche_age=12.5
    )
    print(f"   ✅ 예상 성인 키: {result2['predicted_height']:.1f}cm")
    print(f"   모델: {', '.join(result2['model_used'])}")
    print(f"   신뢰도: {result2['confidence']}")
    if 'menarche_info' in result2['details']:
        info = result2['details']['menarche_info']
        print(f"   초경 정보: {info.get('menarche_age')}세, 경과: {info.get('years_since_menarche', 0):.1f}년")
    
    # 테스트 케이스 3: 부모 키 포함
    print("\n📋 테스트 케이스 3: 부모 키 포함")
    print("   입력: 생년월일 2014-01-01, 남아, 현재 키 140cm, 부모 키(175cm, 162cm)")
    result3 = predictor.predict(
        birth_date='2014-01-01',
        gender='M',
        current_height_cm=140,
        father_height_cm=175,
        mother_height_cm=162
    )
    print(f"   ✅ 예상 성인 키: {result3['predicted_height']:.1f}cm")
    print(f"   모델: {', '.join(result3['model_used'])}")
    print(f"   신뢰도: {result3['confidence']}")
    
    print("\n" + "="*60)
    print("✅ 빠른 테스트 완료!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    quick_test()

