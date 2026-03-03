#!/usr/bin/env python3
"""
모델 동작 검증 스크립트
모든 모델이 제대로 작동하는지 종합 테스트
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.modeling.hybrid_predictor import HybridHeightPredictor
from src.modeling.growth_curve_predictor import GrowthCurvePredictor


def assert_plausible_adult_height(predicted_height, min_height=130, max_height=230):
    """성인 키 예측값이 의학적으로 불가능한 범위를 벗어나지 않는지 검증"""
    assert min_height <= predicted_height <= max_height, (
        f"예측 값이 비현실적 범위를 벗어남: {predicted_height:.1f}cm "
        f"(허용 범위: {min_height}~{max_height}cm)"
    )


def assert_not_below_current_height(predicted_height, current_height, tolerance_cm=0.5):
    """성인 예측 키가 현재 키보다 지나치게 낮지 않은지 검증"""
    assert predicted_height >= (current_height - tolerance_cm), (
        f"성인 예측 키({predicted_height:.1f}cm)가 현재 키({current_height:.1f}cm)보다 낮음"
    )


def test_hybrid_predictor():
    """하이브리드 예측기 테스트"""
    print("\n" + "="*60)
    print("하이브리드 예측기 테스트")
    print("="*60)
    
    try:
        predictor = HybridHeightPredictor()
        print("✅ 하이브리드 예측기 초기화 성공")
        
        # 모델 정보 확인
        info = predictor.get_model_info()
        print(f"\n📊 모델 정보:")
        if info['stunting_model']:
            print(f"   Stunting 모델: {info['stunting_model']['algorithm']}")
            print(f"     검증 MAE: {info['stunting_model']['val_mae']:.2f}cm")
        if info['galton_model']:
            print(f"   Galton 모델: {info['galton_model']['algorithm']}")
            print(f"     검증 MAE: {info['galton_model']['val_mae']:.2f}cm")
        
        # 테스트 케이스 1: 부모 키만
        print("\n🔍 테스트 케이스 1: 부모 키만 있는 경우")
        result1 = predictor.predict(
            gender='M',
            father_height_cm=175,
            mother_height_cm=162
        )
        print(f"   입력: 남아, 부모 키(175cm, 162cm)")
        print(f"   예측: {result1['predicted_height']:.1f}cm")
        print(f"   모델: {result1['model_used']}")
        print(f"   신뢰도: {result1['confidence']}")
        assert_plausible_adult_height(result1['predicted_height'])
        
        # 테스트 케이스 2: 성장 데이터만
        print("\n🔍 테스트 케이스 2: 성장 데이터만 있는 경우")
        result2 = predictor.predict(
            age_years=10,
            height_cm=140,
            gender='M'
        )
        print(f"   입력: 남아, 10세, 140cm")
        print(f"   예측: {result2['predicted_height']:.1f}cm")
        print(f"   모델: {result2['model_used']}")
        print(f"   신뢰도: {result2['confidence']}")
        assert_plausible_adult_height(result2['predicted_height'])
        assert_not_below_current_height(result2['predicted_height'], current_height=140.0)
        
        # 테스트 케이스 3: 모든 정보
        print("\n🔍 테스트 케이스 3: 모든 정보가 있는 경우")
        result3 = predictor.predict(
            age_years=10,
            height_cm=140,
            gender='M',
            father_height_cm=175,
            mother_height_cm=162
        )
        print(f"   입력: 남아, 10세, 140cm, 부모 키(175cm, 162cm)")
        print(f"   예측: {result3['predicted_height']:.1f}cm")
        print(f"   모델: {result3['model_used']}")
        print(f"   신뢰도: {result3['confidence']}")
        assert_plausible_adult_height(result3['predicted_height'])
        assert_not_below_current_height(result3['predicted_height'], current_height=140.0)
        
        # 테스트 케이스 4: 여아
        print("\n🔍 테스트 케이스 4: 여아 예측")
        result4 = predictor.predict(
            age_years=8,
            height_cm=130,
            gender='F',
            father_height_cm=170,
            mother_height_cm=160
        )
        print(f"   입력: 여아, 8세, 130cm, 부모 키(170cm, 160cm)")
        print(f"   예측: {result4['predicted_height']:.1f}cm")
        print(f"   모델: {result4['model_used']}")
        print(f"   신뢰도: {result4['confidence']}")
        assert_plausible_adult_height(result4['predicted_height'])
        assert_not_below_current_height(result4['predicted_height'], current_height=130.0)
        
        print("\n✅ 하이브리드 예측기 테스트 모두 통과!")
        return True
        
    except Exception as e:
        print(f"\n❌ 하이브리드 예측기 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_growth_curve_predictor():
    """성장 곡선 예측기 테스트"""
    print("\n" + "="*60)
    print("성장 곡선 예측기 테스트")
    print("="*60)
    
    try:
        predictor = GrowthCurvePredictor()
        print("✅ 성장 곡선 예측기 초기화 성공")
        
        available_ages = predictor.get_available_ages()
        print(f"📊 사용 가능한 나이: {available_ages}세")
        
        if not available_ages:
            print("❌ 사용 가능한 모델이 없습니다!")
            return False
        
        # 테스트 케이스 1: 특정 나이 예측
        print("\n🔍 테스트 케이스 1: 특정 나이 예측 (8세 → 15세)")
        result1 = predictor.predict_at_age(
            current_age_years=8,
            current_height_cm=130,
            target_age_years=15,
            gender='M'
        )
        print(f"   현재: {result1['current_age_years']}세, {result1['current_height_cm']}cm")
        print(f"   예측: {result1['target_age_years']}세에 {result1['predicted_height_cm']:.1f}cm")
        print(f"   예상 성장: {result1['growth_expected']:.1f}cm")
        assert result1['predicted_height_cm'] > result1['current_height_cm'], "예측 키가 현재 키보다 작음"
        
        # 테스트 케이스 2: 성장 곡선 예측
        print("\n🔍 테스트 케이스 2: 성장 곡선 예측")
        result2 = predictor.predict_growth_curve(
            current_age_years=8,
            current_height_cm=130,
            gender='M'
        )
        print(f"   현재: {result2['current_info']['age_years']}세, {result2['current_info']['height_cm']}cm")
        print(f"   예측 결과:")
        prev_height = result2['current_info']['height_cm']
        for age in sorted(result2['predictions'].keys()):
            pred = result2['predictions'][age]
            print(f"     {age}세: {pred['predicted_height_cm']:.1f}cm (성장: +{pred['growth_expected']:.1f}cm)")
            assert pred['predicted_height_cm'] >= prev_height, f"{age}세 예측이 이전 값보다 작음"
            prev_height = pred['predicted_height_cm']
        
        # 테스트 케이스 3: 여아
        print("\n🔍 테스트 케이스 3: 여아 성장 곡선")
        result3 = predictor.predict_growth_curve(
            current_age_years=5,
            current_height_cm=110,
            gender='F'
        )
        print(f"   현재: {result3['current_info']['age_years']}세, {result3['current_info']['height_cm']}cm")
        for age in sorted(result3['predictions'].keys()):
            pred = result3['predictions'][age]
            print(f"     {age}세: {pred['predicted_height_cm']:.1f}cm")
            assert 100 <= pred['predicted_height_cm'] <= 180, "예측 값이 합리적 범위를 벗어남"
        
        print("\n✅ 성장 곡선 예측기 테스트 모두 통과!")
        return True
        
    except Exception as e:
        print(f"\n❌ 성장 곡선 예측기 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_consistency():
    """데이터 일관성 테스트"""
    print("\n" + "="*60)
    print("데이터 일관성 테스트")
    print("="*60)
    
    # 남아와 여아의 키 차이 확인
    predictor = HybridHeightPredictor()
    
    print("\n🔍 성별별 예측 차이 확인")
    result_m = predictor.predict(
        age_years=10,
        height_cm=140,
        gender='M',
        father_height_cm=175,
        mother_height_cm=162
    )
    result_f = predictor.predict(
        age_years=10,
        height_cm=140,
        gender='F',
        father_height_cm=175,
        mother_height_cm=162
    )
    
    print(f"   남아 예측: {result_m['predicted_height']:.1f}cm")
    print(f"   여아 예측: {result_f['predicted_height']:.1f}cm")
    print(f"   차이: {result_m['predicted_height'] - result_f['predicted_height']:.1f}cm")
    
    # 남아가 여아보다 키가 큰지 확인
    if result_m['predicted_height'] > result_f['predicted_height']:
        print("   ✅ 남아가 여아보다 키가 큰 것으로 예측됨 (정상)")
    else:
        print("   ⚠️  성별 차이가 예상과 다름")
    
    return True

def main():
    """메인 함수"""
    print("="*60)
    print("모델 동작 종합 검증")
    print("="*60)
    
    results = []
    
    # 각 모델 테스트
    results.append(("하이브리드 예측기", test_hybrid_predictor()))
    results.append(("성장 곡선 예측기", test_growth_curve_predictor()))
    results.append(("데이터 일관성", test_data_consistency()))
    
    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ 모든 테스트 통과!")
        print("모델이 정상적으로 작동하고 있습니다.")
    else:
        print("❌ 일부 테스트 실패")
        print("문제를 확인해주세요.")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
