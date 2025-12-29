#!/usr/bin/env python3
"""
향상된 예측기 종합 테스트 스크립트
다양한 시나리오로 예측 모델의 정확도와 일관성 검증
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.modeling.enhanced_predictor import EnhancedHeightPredictor
from src.modeling.enhanced_growth_curve_predictor import EnhancedGrowthCurvePredictor

def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_test_case(name, input_data, result):
    """테스트 케이스 결과 출력"""
    print(f"\n📋 {name}")
    print(f"   입력: {json.dumps(input_data, indent=6, ensure_ascii=False)}")
    print(f"   예측: {result['predicted_height']:.1f}cm")
    print(f"   모델: {', '.join(result['model_used'])}")
    print(f"   신뢰도: {result['confidence']}")
    if 'details' in result:
        details = result['details']
        if 'age_years' in details:
            print(f"   현재 나이: {details['age_years']:.1f}세")
        if 'menarche_info' in details:
            info = details['menarche_info']
            print(f"   초경 정보: {info.get('menarche_age', 'N/A')}세")
            if info.get('years_since_menarche'):
                print(f"     초경 후 경과: {info['years_since_menarche']:.1f}년")

def test_basic_scenarios():
    """기본 시나리오 테스트"""
    print_section("기본 시나리오 테스트")
    
    predictor = EnhancedHeightPredictor()
    print("✅ 향상된 예측기 초기화 완료\n")
    
    test_cases = []
    
    # 케이스 1: 부모 키만 있는 경우
    test_cases.append({
        'name': '부모 키만 있는 경우',
        'input': {
            'gender': 'M',
            'father_height_cm': 175,
            'mother_height_cm': 162
        },
        'expected_range': (165, 185)
    })
    
    # 케이스 2: 현재 키와 나이만 있는 경우 (남아)
    test_cases.append({
        'name': '현재 키와 나이만 있는 경우 (남아)',
        'input': {
            'birth_date': '2014-01-01',
            'gender': 'M',
            'current_height_cm': 140
        },
        'expected_range': (165, 185)
    })
    
    # 케이스 3: 모든 정보가 있는 경우
    test_cases.append({
        'name': '모든 정보가 있는 경우',
        'input': {
            'birth_date': '2014-01-01',
            'gender': 'M',
            'current_height_cm': 140,
            'father_height_cm': 175,
            'mother_height_cm': 162
        },
        'expected_range': (165, 185)
    })
    
    # 케이스 4: 여아 + 초경 정보
    test_cases.append({
        'name': '여아 + 초경 정보',
        'input': {
            'birth_date': '2012-01-01',
            'gender': 'F',
            'current_height_cm': 150,
            'menarche_age': 12.5
        },
        'expected_range': (155, 170)
    })
    
    # 케이스 5: 여아 + 부모 키 + 초경 정보
    test_cases.append({
        'name': '여아 + 부모 키 + 초경 정보',
        'input': {
            'birth_date': '2012-01-01',
            'gender': 'F',
            'current_height_cm': 150,
            'father_height_cm': 170,
            'mother_height_cm': 160,
            'menarche_age': 12.5
        },
        'expected_range': (155, 170)
    })
    
    # 케이스 6: 과거 키 기록이 있는 경우
    test_cases.append({
        'name': '과거 키 기록이 있는 경우',
        'input': {
            'birth_date': '2014-01-01',
            'gender': 'M',
            'current_height_cm': 140,
            'height_history': [
                {'date': '2020-01-01', 'height_cm': 120},
                {'date': '2022-01-01', 'height_cm': 130}
            ],
            'father_height_cm': 175,
            'mother_height_cm': 162
        },
        'expected_range': (165, 185)
    })
    
    passed = 0
    failed = 0
    
    for case in test_cases:
        try:
            result = predictor.predict(**case['input'])
            print_test_case(case['name'], case['input'], result)
            
            # 범위 검증
            pred = result['predicted_height']
            min_val, max_val = case['expected_range']
            if min_val <= pred <= max_val:
                print(f"   ✅ 예측값이 합리적 범위 내 ({min_val}-{max_val}cm)")
                passed += 1
            else:
                print(f"   ⚠️  예측값이 범위를 벗어남: {pred:.1f}cm (예상: {min_val}-{max_val}cm)")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ 테스트 실패: {e}")
            failed += 1
    
    print(f"\n📊 결과: {passed}개 통과, {failed}개 실패")
    return failed == 0

def test_edge_cases():
    """엣지 케이스 테스트"""
    print_section("엣지 케이스 테스트")
    
    predictor = EnhancedHeightPredictor()
    
    test_cases = []
    
    # 케이스 1: 매우 어린 나이
    test_cases.append({
        'name': '매우 어린 나이 (3세)',
        'input': {
            'birth_date': '2021-01-01',
            'gender': 'M',
            'current_height_cm': 95
        },
        'expected_range': (150, 200)
    })
    
    # 케이스 2: 나이가 많은 경우 (15세)
    test_cases.append({
        'name': '나이가 많은 경우 (15세)',
        'input': {
            'birth_date': '2009-01-01',
            'gender': 'M',
            'current_height_cm': 170
        },
        'expected_range': (170, 195)
    })
    
    # 케이스 3: 초경이 빠른 경우
    test_cases.append({
        'name': '초경이 빠른 경우 (10세)',
        'input': {
            'birth_date': '2012-01-01',
            'gender': 'F',
            'current_height_cm': 145,
            'menarche_age': 10.0
        },
        'expected_range': (150, 165)
    })
    
    # 케이스 4: 초경이 늦은 경우
    test_cases.append({
        'name': '초경이 늦은 경우 (14세)',
        'input': {
            'birth_date': '2010-01-01',
            'gender': 'F',
            'current_height_cm': 160,
            'menarche_age': 14.0
        },
        'expected_range': (160, 175)
    })
    
    # 케이스 5: 키가 큰 경우
    test_cases.append({
        'name': '키가 큰 경우 (11세에 163cm)',
        'input': {
            'birth_date': '2014-07-24',
            'gender': 'M',
            'current_height_cm': 163
        },
        'expected_range': (175, 195)
    })
    
    passed = 0
    failed = 0
    
    for case in test_cases:
        try:
            result = predictor.predict(**case['input'])
            print_test_case(case['name'], case['input'], result)
            
            pred = result['predicted_height']
            min_val, max_val = case['expected_range']
            
            # 현재 키보다 높아야 함
            current_height = case['input'].get('current_height_cm')
            if current_height and pred < current_height:
                print(f"   ❌ 예측값이 현재 키보다 낮음: {pred:.1f}cm < {current_height}cm")
                failed += 1
            elif min_val <= pred <= max_val:
                print(f"   ✅ 예측값이 합리적 범위 내 ({min_val}-{max_val}cm)")
                passed += 1
            else:
                print(f"   ⚠️  예측값이 범위를 벗어남: {pred:.1f}cm (예상: {min_val}-{max_val}cm)")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ 테스트 실패: {e}")
            failed += 1
    
    print(f"\n📊 결과: {passed}개 통과, {failed}개 실패")
    return failed == 0

def test_consistency():
    """일관성 테스트"""
    print_section("일관성 테스트")
    
    predictor = EnhancedHeightPredictor()
    
    # 테스트 1: 성별 차이
    print("\n🔍 성별 차이 확인")
    result_m = predictor.predict(
        birth_date='2014-01-01',
        gender='M',
        current_height_cm=140,
        father_height_cm=175,
        mother_height_cm=162
    )
    result_f = predictor.predict(
        birth_date='2014-01-01',
        gender='F',
        current_height_cm=140,
        father_height_cm=175,
        mother_height_cm=162
    )
    
    print(f"   남아 예측: {result_m['predicted_height']:.1f}cm")
    print(f"   여아 예측: {result_f['predicted_height']:.1f}cm")
    diff = result_m['predicted_height'] - result_f['predicted_height']
    print(f"   차이: {diff:.1f}cm")
    
    if diff > 5:
        print("   ✅ 남아가 여아보다 키가 큰 것으로 예측됨 (정상)")
    else:
        print("   ⚠️  성별 차이가 예상보다 작음")
    
    # 테스트 2: 초경 정보의 영향
    print("\n🔍 초경 정보의 영향 확인")
    result_no_menarche = predictor.predict(
        birth_date='2012-01-01',
        gender='F',
        current_height_cm=150
    )
    result_with_menarche = predictor.predict(
        birth_date='2012-01-01',
        gender='F',
        current_height_cm=150,
        menarche_age=12.5
    )
    
    print(f"   초경 정보 없음: {result_no_menarche['predicted_height']:.1f}cm")
    print(f"   초경 정보 있음: {result_with_menarche['predicted_height']:.1f}cm")
    print(f"   신뢰도 변화: {result_no_menarche['confidence']} → {result_with_menarche['confidence']}")
    
    if result_with_menarche['confidence'] in ['high', 'very_high']:
        print("   ✅ 초경 정보로 신뢰도 향상")
    else:
        print("   ⚠️  초경 정보가 신뢰도에 영향을 주지 않음")
    
    # 테스트 3: 부모 키 정보의 영향
    print("\n🔍 부모 키 정보의 영향 확인")
    result_no_parents = predictor.predict(
        birth_date='2014-01-01',
        gender='M',
        current_height_cm=140
    )
    result_with_parents = predictor.predict(
        birth_date='2014-01-01',
        gender='M',
        current_height_cm=140,
        father_height_cm=175,
        mother_height_cm=162
    )
    
    print(f"   부모 키 없음: {result_no_parents['predicted_height']:.1f}cm (신뢰도: {result_no_parents['confidence']})")
    print(f"   부모 키 있음: {result_with_parents['predicted_height']:.1f}cm (신뢰도: {result_with_parents['confidence']})")
    
    if result_with_parents['confidence'] in ['high', 'very_high']:
        print("   ✅ 부모 키 정보로 신뢰도 향상")
    
    return True

def test_growth_curve():
    """성장 곡선 예측 테스트"""
    print_section("성장 곡선 예측 테스트")
    
    predictor = EnhancedGrowthCurvePredictor()
    
    try:
        result = predictor.predict_growth_curve(
            birth_date='2014-01-01',
            gender='M',
            current_height_cm=140,
            father_height_cm=175,
            mother_height_cm=162
        )
        
        print(f"\n📊 현재 정보:")
        print(f"   나이: {result['current']['age_years']:.1f}세")
        print(f"   키: {result['current']['height_cm']:.1f}cm")
        
        print(f"\n📈 예측 결과:")
        prev_height = result['current']['height_cm']
        for age in sorted(result['predictions'].keys()):
            pred = result['predictions'][age]
            height = pred['predicted_height_cm']
            growth = pred['growth_expected']
            print(f"   {age}세: {height:.1f}cm (성장: +{growth:.1f}cm)")
            
            # 나이가 증가할수록 키도 증가해야 함
            if height < prev_height:
                print(f"      ⚠️  {age}세 예측이 이전보다 작음")
            prev_height = height
        
        print("\n✅ 성장 곡선 예측 테스트 통과")
        return True
        
    except Exception as e:
        print(f"\n❌ 성장 곡선 예측 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_world_scenarios():
    """실제 사용 시나리오 테스트"""
    print_section("실제 사용 시나리오 테스트")
    
    predictor = EnhancedHeightPredictor()
    
    scenarios = [
        {
            'name': '사용자 케이스: 11세 남아 163cm',
            'input': {
                'birth_date': '2014-07-24',
                'gender': 'M',
                'current_height_cm': 163
            },
            'expected_range': (175, 195)
        },
        {
            'name': '사용자 케이스: 여아 + 초경',
            'input': {
                'birth_date': '2012-01-01',
                'gender': 'F',
                'current_height_cm': 155,
                'menarche_age': 12.3
            },
            'expected_range': (158, 168)
        }
    ]
    
    passed = 0
    for scenario in scenarios:
        try:
            result = predictor.predict(**scenario['input'])
            print_test_case(scenario['name'], scenario['input'], result)
            
            pred = result['predicted_height']
            min_val, max_val = scenario['expected_range']
            
            if min_val <= pred <= max_val:
                print(f"   ✅ 예측값이 합리적 범위 내")
                passed += 1
            else:
                print(f"   ⚠️  예측값: {pred:.1f}cm (예상 범위: {min_val}-{max_val}cm)")
                
        except Exception as e:
            print(f"   ❌ 테스트 실패: {e}")
    
    print(f"\n📊 결과: {passed}/{len(scenarios)}개 통과")
    return passed == len(scenarios)

def main():
    """메인 함수"""
    print("="*70)
    print("  향상된 예측기 종합 테스트")
    print("="*70)
    
    results = []
    
    # 각 테스트 실행
    results.append(("기본 시나리오", test_basic_scenarios()))
    results.append(("엣지 케이스", test_edge_cases()))
    results.append(("일관성", test_consistency()))
    results.append(("성장 곡선", test_growth_curve()))
    results.append(("실제 사용 시나리오", test_real_world_scenarios()))
    
    # 결과 요약
    print_section("테스트 결과 요약")
    
    all_passed = True
    for name, passed in results:
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"{name:20s}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ 모든 테스트 통과!")
        print("예측 모델이 정상적으로 작동하고 있습니다.")
    else:
        print("⚠️  일부 테스트 실패")
        print("문제를 확인해주세요.")
    print("="*70)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

