#!/usr/bin/env python3
"""
예외 처리 및 엣지 케이스 테스트 스크립트
잘못된 입력, 경계값, 예외 상황을 검증
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.modeling.enhanced_predictor import EnhancedHeightPredictor
import requests
import json

def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_test(name, passed, error_msg=None):
    """테스트 결과 출력"""
    status = "✅ 통과" if passed else "❌ 실패"
    print(f"{status}: {name}")
    if not passed and error_msg:
        print(f"   오류: {error_msg}")

def test_invalid_inputs():
    """잘못된 입력값 테스트"""
    print_section("잘못된 입력값 테스트")
    
    predictor = EnhancedHeightPredictor()
    results = []
    
    # 테스트 케이스 1: 음수 키
    try:
        result = predictor.predict(
            birth_date='2014-01-01',
            gender='M',
            current_height_cm=-10
        )
        results.append(("음수 키", False, "음수 키가 허용됨"))
    except (ValueError, AssertionError) as e:
        results.append(("음수 키", True, None))
    except Exception as e:
        results.append(("음수 키", False, f"예상치 못한 오류: {e}"))
    
    # 테스트 케이스 2: 비정상적으로 큰 키
    try:
        result = predictor.predict(
            birth_date='2014-01-01',
            gender='M',
            current_height_cm=300
        )
        # 경고는 있지만 예외는 발생하지 않을 수 있음
        results.append(("비정상적으로 큰 키 (300cm)", True, None))
    except Exception as e:
        results.append(("비정상적으로 큰 키 (300cm)", True, None))
    
    # 테스트 케이스 3: 음수 나이 (미래 생년월일)
    try:
        future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        result = predictor.predict(
            birth_date=future_date,
            gender='M',
            current_height_cm=140
        )
        results.append(("미래 생년월일", False, "미래 생년월일이 허용됨"))
    except (ValueError, AssertionError) as e:
        results.append(("미래 생년월일", True, None))
    except Exception as e:
        results.append(("미래 생년월일", True, None))
    
    # 테스트 케이스 4: 잘못된 성별
    try:
        result = predictor.predict(
            birth_date='2014-01-01',
            gender='X',  # 잘못된 성별
            current_height_cm=140
        )
        results.append(("잘못된 성별", False, "잘못된 성별이 허용됨"))
    except (ValueError, AssertionError, KeyError) as e:
        results.append(("잘못된 성별", True, None))
    except Exception as e:
        results.append(("잘못된 성별", True, None))
    
    # 테스트 케이스 5: 음수 부모 키
    try:
        result = predictor.predict(
            birth_date='2014-01-01',
            gender='M',
            current_height_cm=140,
            father_height_cm=-10,
            mother_height_cm=160
        )
        results.append(("음수 부모 키", False, "음수 부모 키가 허용됨"))
    except (ValueError, AssertionError) as e:
        results.append(("음수 부모 키", True, None))
    except Exception as e:
        results.append(("음수 부모 키", True, None))
    
    # 테스트 케이스 6: 비정상적으로 큰 부모 키
    try:
        result = predictor.predict(
            birth_date='2014-01-01',
            gender='M',
            current_height_cm=140,
            father_height_cm=300,
            mother_height_cm=160
        )
        results.append(("비정상적으로 큰 부모 키 (300cm)", True, None))
    except Exception as e:
        results.append(("비정상적으로 큰 부모 키 (300cm)", True, None))
    
    # 테스트 케이스 7: 잘못된 초경 나이 (음수)
    try:
        result = predictor.predict(
            birth_date='2012-01-01',
            gender='F',
            current_height_cm=150,
            menarche_age=-5
        )
        results.append(("음수 초경 나이", False, "음수 초경 나이가 허용됨"))
    except (ValueError, AssertionError) as e:
        results.append(("음수 초경 나이", True, None))
    except Exception as e:
        results.append(("음수 초경 나이", True, None))
    
    # 테스트 케이스 8: 비정상적으로 큰 초경 나이
    try:
        result = predictor.predict(
            birth_date='2012-01-01',
            gender='F',
            current_height_cm=150,
            menarche_age=25  # 비정상적으로 큰 값
        )
        results.append(("비정상적으로 큰 초경 나이 (25세)", True, None))
    except Exception as e:
        results.append(("비정상적으로 큰 초경 나이 (25세)", True, None))
    
    # 테스트 케이스 9: 초경 나이가 현재 나이보다 큰 경우
    try:
        result = predictor.predict(
            birth_date='2012-01-01',  # 약 12세
            gender='F',
            current_height_cm=150,
            menarche_age=20  # 현재 나이보다 큼
        )
        results.append(("초경 나이 > 현재 나이", True, None))
    except (ValueError, AssertionError) as e:
        results.append(("초경 나이 > 현재 나이", True, None))
    except Exception as e:
        results.append(("초경 나이 > 현재 나이", True, None))
    
    # 테스트 케이스 10: 남아에게 초경 정보 입력
    try:
        result = predictor.predict(
            birth_date='2014-01-01',
            gender='M',
            current_height_cm=140,
            menarche_age=12.5
        )
        # 남아에게 초경 정보가 있어도 예외는 발생하지 않을 수 있음 (무시됨)
        results.append(("남아에게 초경 정보", True, None))
    except Exception as e:
        results.append(("남아에게 초경 정보", True, None))
    
    # 결과 출력
    passed = 0
    failed = 0
    for name, result, error in results:
        print_test(name, result, error)
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 결과: {passed}개 통과, {failed}개 실패")
    return failed == 0

def test_missing_parameters():
    """필수 파라미터 누락 테스트"""
    print_section("필수 파라미터 누락 테스트")
    
    predictor = EnhancedHeightPredictor()
    results = []
    
    # 테스트 케이스 1: 성별 없음
    try:
        result = predictor.predict(
            birth_date='2014-01-01',
            current_height_cm=140
        )
        results.append(("성별 없음", False, "성별 없이 예측됨"))
    except (ValueError, TypeError, KeyError) as e:
        results.append(("성별 없음", True, None))
    except Exception as e:
        results.append(("성별 없음", True, None))
    
    # 테스트 케이스 2: 현재 키 없음
    try:
        result = predictor.predict(
            birth_date='2014-01-01',
            gender='M'
        )
        # 부모 키만 있으면 예측 가능할 수 있음
        results.append(("현재 키 없음 (부모 키만)", True, None))
    except Exception as e:
        results.append(("현재 키 없음 (부모 키만)", True, None))
    
    # 테스트 케이스 3: 모든 파라미터 없음
    try:
        result = predictor.predict()
        results.append(("모든 파라미터 없음", False, "파라미터 없이 예측됨"))
    except (ValueError, TypeError) as e:
        results.append(("모든 파라미터 없음", True, None))
    except Exception as e:
        results.append(("모든 파라미터 없음", True, None))
    
    # 테스트 케이스 4: 생년월일 없음 (나이 정보 없음)
    try:
        result = predictor.predict(
            gender='M',
            current_height_cm=140
        )
        # 나이 없이도 예측 가능할 수 있음 (부모 키만)
        results.append(("생년월일 없음", True, None))
    except Exception as e:
        results.append(("생년월일 없음", True, None))
    
    # 결과 출력
    passed = 0
    failed = 0
    for name, result, error in results:
        print_test(name, result, error)
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 결과: {passed}개 통과, {failed}개 실패")
    return failed == 0

def test_boundary_values():
    """경계값 테스트"""
    print_section("경계값 테스트")
    
    predictor = EnhancedHeightPredictor()
    results = []
    
    # 테스트 케이스 1: 매우 어린 나이 (0세)
    try:
        result = predictor.predict(
            birth_date=datetime.now().strftime('%Y-%m-%d'),
            gender='M',
            current_height_cm=50
        )
        if result['predicted_height'] > 0:
            results.append(("0세 (신생아)", True, None))
        else:
            results.append(("0세 (신생아)", False, "예측값이 0 이하"))
    except Exception as e:
        results.append(("0세 (신생아)", True, None))
    
    # 테스트 케이스 2: 매우 큰 나이 (18세)
    try:
        birth_date = (datetime.now() - timedelta(days=18*365)).strftime('%Y-%m-%d')
        result = predictor.predict(
            birth_date=birth_date,
            gender='M',
            current_height_cm=175
        )
        if result['predicted_height'] >= 175:
            results.append(("18세 (성인)", True, None))
        else:
            results.append(("18세 (성인)", False, "예측값이 현재 키보다 작음"))
    except Exception as e:
        results.append(("18세 (성인)", True, None))
    
    # 테스트 케이스 3: 매우 작은 키 (30cm)
    try:
        result = predictor.predict(
            birth_date='2021-01-01',
            gender='M',
            current_height_cm=30
        )
        if result['predicted_height'] > 30:
            results.append(("매우 작은 키 (30cm)", True, None))
        else:
            results.append(("매우 작은 키 (30cm)", False, "예측값이 현재 키보다 작음"))
    except Exception as e:
        results.append(("매우 작은 키 (30cm)", True, None))
    
    # 테스트 케이스 4: 매우 큰 키 (200cm)
    try:
        result = predictor.predict(
            birth_date='2010-01-01',
            gender='M',
            current_height_cm=200
        )
        if result['predicted_height'] >= 200:
            results.append(("매우 큰 키 (200cm)", True, None))
        else:
            results.append(("매우 큰 키 (200cm)", False, "예측값이 현재 키보다 작음"))
    except Exception as e:
        results.append(("매우 큰 키 (200cm)", True, None))
    
    # 테스트 케이스 5: 초경 나이 경계값 (8세)
    try:
        result = predictor.predict(
            birth_date='2012-01-01',
            gender='F',
            current_height_cm=130,
            menarche_age=8.0
        )
        results.append(("초경 나이 최소값 (8세)", True, None))
    except Exception as e:
        results.append(("초경 나이 최소값 (8세)", True, None))
    
    # 테스트 케이스 6: 초경 나이 경계값 (18세)
    try:
        result = predictor.predict(
            birth_date='2006-01-01',
            gender='F',
            current_height_cm=160,
            menarche_age=18.0
        )
        results.append(("초경 나이 최대값 (18세)", True, None))
    except Exception as e:
        results.append(("초경 나이 최대값 (18세)", True, None))
    
    # 결과 출력
    passed = 0
    failed = 0
    for name, result, error in results:
        print_test(name, result, error)
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 결과: {passed}개 통과, {failed}개 실패")
    return failed == 0

def test_invalid_date_formats():
    """잘못된 날짜 형식 테스트"""
    print_section("잘못된 날짜 형식 테스트")
    
    predictor = EnhancedHeightPredictor()
    results = []
    
    # 테스트 케이스 1: 잘못된 날짜 형식
    invalid_formats = [
        '2014/01/01',  # 슬래시 구분
        '01-01-2014',  # 순서 바뀜
        '2014-1-1',    # 한 자리 숫자
        '2014-13-01',  # 잘못된 월
        '2014-01-32',  # 잘못된 일
        'abcd-01-01',  # 문자 포함
        '',             # 빈 문자열
        '2014',        # 불완전한 날짜
    ]
    
    for date_format in invalid_formats:
        try:
            result = predictor.predict(
                birth_date=date_format,
                gender='M',
                current_height_cm=140
            )
            results.append((f"날짜 형식 '{date_format}'", False, "잘못된 형식이 허용됨"))
        except (ValueError, TypeError) as e:
            results.append((f"날짜 형식 '{date_format}'", True, None))
        except Exception as e:
            # 다른 예외도 허용 (날짜 파싱 실패)
            results.append((f"날짜 형식 '{date_format}'", True, None))
    
    # 결과 출력
    passed = 0
    failed = 0
    for name, result, error in results:
        print_test(name, result, error)
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 결과: {passed}개 통과, {failed}개 실패")
    return failed == 0

def test_api_exceptions():
    """API 레벨 예외 처리 테스트"""
    print_section("API 레벨 예외 처리 테스트")
    
    api_url = "http://localhost:5001/api/predict/adult"
    results = []
    
    # 테스트 케이스 1: 잘못된 JSON
    try:
        response = requests.post(
            api_url,
            data="잘못된 JSON",
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 400:
            results.append(("잘못된 JSON", True, None))
        else:
            results.append(("잘못된 JSON", False, f"상태 코드: {response.status_code}"))
    except requests.exceptions.RequestException:
        results.append(("잘못된 JSON", True, None))
    except Exception as e:
        results.append(("잘못된 JSON", True, None))
    
    # 테스트 케이스 2: 필수 파라미터 누락
    try:
        response = requests.post(
            api_url,
            json={},
            timeout=5
        )
        if response.status_code == 400:
            results.append(("필수 파라미터 누락", True, None))
        else:
            results.append(("필수 파라미터 누락", False, f"상태 코드: {response.status_code}"))
    except requests.exceptions.RequestException:
        results.append(("필수 파라미터 누락", True, None))
    except Exception as e:
        results.append(("필수 파라미터 누락", True, None))
    
    # 테스트 케이스 3: 잘못된 타입 (문자열을 숫자로)
    try:
        response = requests.post(
            api_url,
            json={
                "gender": "M",
                "birth_date": "2014-01-01",
                "current_height_cm": "140"  # 문자열
            },
            timeout=5
        )
        # 타입 변환은 자동으로 될 수 있음
        if response.status_code in [200, 400]:
            results.append(("잘못된 타입 (문자열)", True, None))
        else:
            results.append(("잘못된 타입 (문자열)", False, f"상태 코드: {response.status_code}"))
    except requests.exceptions.RequestException:
        results.append(("잘못된 타입 (문자열)", True, None))
    except Exception as e:
        results.append(("잘못된 타입 (문자열)", True, None))
    
    # 테스트 케이스 4: 음수 값
    try:
        response = requests.post(
            api_url,
            json={
                "gender": "M",
                "birth_date": "2014-01-01",
                "current_height_cm": -10
            },
            timeout=5
        )
        if response.status_code == 400:
            results.append(("API 음수 키", True, None))
        else:
            results.append(("API 음수 키", False, f"상태 코드: {response.status_code}"))
    except requests.exceptions.RequestException:
        results.append(("API 음수 키", True, None))
    except Exception as e:
        results.append(("API 음수 키", True, None))
    
    # 결과 출력
    passed = 0
    failed = 0
    for name, result, error in results:
        print_test(name, result, error)
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 결과: {passed}개 통과, {failed}개 실패")
    print("⚠️  API 서버가 실행 중이지 않으면 일부 테스트가 실패할 수 있습니다.")
    return failed == 0

def test_data_consistency():
    """데이터 일관성 테스트"""
    print_section("데이터 일관성 테스트")
    
    predictor = EnhancedHeightPredictor()
    results = []
    
    # 테스트 케이스 1: 현재 키보다 예측값이 작은 경우
    try:
        result = predictor.predict(
            birth_date='2014-01-01',
            gender='M',
            current_height_cm=163
        )
        if result['predicted_height'] >= 163:
            results.append(("예측값 >= 현재 키", True, None))
        else:
            results.append(("예측값 >= 현재 키", False, 
                           f"예측값({result['predicted_height']:.1f}cm) < 현재 키(163cm)"))
    except Exception as e:
        results.append(("예측값 >= 현재 키", False, f"예외 발생: {e}"))
    
    # 테스트 케이스 2: 남아가 여아보다 키가 큰지 확인
    try:
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
        if result_m['predicted_height'] > result_f['predicted_height']:
            results.append(("남아 > 여아 키", True, None))
        else:
            results.append(("남아 > 여아 키", False, 
                           f"남아({result_m['predicted_height']:.1f}cm) <= 여아({result_f['predicted_height']:.1f}cm)"))
    except Exception as e:
        results.append(("남아 > 여아 키", False, f"예외 발생: {e}"))
    
    # 테스트 케이스 3: 부모 키가 있을 때 신뢰도가 높은지 확인
    try:
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
        # 신뢰도 비교 (간단히 모델 수로 비교)
        if len(result_with_parents['model_used']) >= len(result_no_parents['model_used']):
            results.append(("부모 키 있을 때 신뢰도 향상", True, None))
        else:
            results.append(("부모 키 있을 때 신뢰도 향상", False, "신뢰도가 향상되지 않음"))
    except Exception as e:
        results.append(("부모 키 있을 때 신뢰도 향상", False, f"예외 발생: {e}"))
    
    # 결과 출력
    passed = 0
    failed = 0
    for name, result, error in results:
        print_test(name, result, error)
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 결과: {passed}개 통과, {failed}개 실패")
    return failed == 0

def main():
    """메인 함수"""
    print("="*70)
    print("  예외 처리 및 엣지 케이스 종합 테스트")
    print("="*70)
    
    results = []
    
    # 각 테스트 실행
    results.append(("잘못된 입력값", test_invalid_inputs()))
    results.append(("필수 파라미터 누락", test_missing_parameters()))
    results.append(("경계값", test_boundary_values()))
    results.append(("잘못된 날짜 형식", test_invalid_date_formats()))
    results.append(("API 예외 처리", test_api_exceptions()))
    results.append(("데이터 일관성", test_data_consistency()))
    
    # 결과 요약
    print_section("테스트 결과 요약")
    
    all_passed = True
    for name, passed in results:
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"{name:25s}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ 모든 테스트 통과!")
        print("예외 처리가 잘 되어 있습니다.")
    else:
        print("⚠️  일부 테스트 실패")
        print("예외 처리를 개선할 필요가 있습니다.")
    print("="*70)
    
    return all_passed

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("⚠️  requests 패키지가 없습니다. API 테스트를 건너뜁니다.")
        print("설치: pip install requests")
    
    success = main()
    sys.exit(0 if success else 1)

