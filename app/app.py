"""
키 예측 웹 애플리케이션
Flask 기반 웹 인터페이스
"""

from flask import Flask, render_template, request, jsonify
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.modeling.enhanced_predictor import EnhancedHeightPredictor
from src.modeling.enhanced_growth_curve_predictor import EnhancedGrowthCurvePredictor
from src.utils.age_calculator import validate_birth_date, parse_date_input
from src.utils.growth_factors import get_available_countries

app = Flask(__name__)

# 전역 예측기 인스턴스
enhanced_predictor = None
enhanced_growth_curve_predictor = None

def init_predictors():
    """예측기 초기화"""
    global enhanced_predictor, enhanced_growth_curve_predictor
    try:
        enhanced_predictor = EnhancedHeightPredictor()
        enhanced_growth_curve_predictor = EnhancedGrowthCurvePredictor()
        print("✅ 예측기 초기화 완료")
    except Exception as e:
        print(f"❌ 예측기 초기화 오류: {e}")

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/predict/adult', methods=['POST'])
def predict_adult_height():
    """성인 키 예측 API (향상된 버전)"""
    try:
        data = request.json
        
        # 입력 데이터 추출
        gender = data.get('gender')
        birth_date = data.get('birth_date')
        current_height_cm = data.get('current_height_cm')
        current_date = data.get('current_date')
        father_height_cm = data.get('father_height_cm')
        mother_height_cm = data.get('mother_height_cm')
        height_history = data.get('height_history', [])  # [{'date': 'YYYY-MM-DD', 'height_cm': float}, ...]
        
        # 필수 입력 검증
        if not gender:
            return jsonify({'error': '성별은 필수 입력입니다.'}), 400
        
        if not birth_date and not current_height_cm:
            return jsonify({'error': '생년월일 또는 현재 키 중 하나는 필수입니다.'}), 400
        
        # 생년월일 검증
        if birth_date:
            is_valid, error_msg = validate_birth_date(birth_date)
            if not is_valid:
                return jsonify({'error': error_msg}), 400
        
        # 추가 옵션
        country_code = data.get('country_code', 'DEFAULT')
        use_genetic_formulas = data.get('use_genetic_formulas', True)
        use_growth_pattern = data.get('use_growth_pattern', True)
        
        # 예측 수행
        result = enhanced_predictor.predict(
            birth_date=birth_date,
            gender=gender,
            current_height_cm=current_height_cm,
            current_date=current_date,
            father_height_cm=father_height_cm,
            mother_height_cm=mother_height_cm,
            height_history=height_history,
            country_code=country_code,
            use_genetic_formulas=use_genetic_formulas,
            use_growth_pattern=use_growth_pattern
        )
        
        # 성장 곡선도 함께 예측 (동일한 설정 사용)
        try:
            growth_curve_result = enhanced_growth_curve_predictor.predict_growth_curve(
                birth_date=birth_date,
                gender=gender,
                current_height_cm=current_height_cm,
                current_date=current_date,
                father_height_cm=father_height_cm,
                mother_height_cm=mother_height_cm,
                height_history=height_history,
                country_code=country_code,
                use_genetic_formulas=use_genetic_formulas,
                use_growth_pattern=use_growth_pattern
            )
            
            # enhanced_growth_curve_predictor가 이미 성인 키 예측과 일치시키므로 여기서는 할 필요 없음
            # (성장 곡선 예측기 내부에서 처리됨)
        except Exception as e:
            print(f"⚠️  성장 곡선 예측 오류: {e}")
            growth_curve_result = None
        
        return jsonify({
            'success': True,
            'prediction': result['predicted_height'],
            'confidence': result['confidence'],
            'models_used': result['model_used'],
            'details': result.get('details', {}),
            'growth_curve': growth_curve_result
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'예측 중 오류 발생: {str(e)}'}), 500


@app.route('/api/predict/age', methods=['POST'])
def predict_age_height():
    """특정 나이 키 예측 API"""
    try:
        data = request.json
        
        # 입력 데이터 추출
        gender = data.get('gender')
        current_age_years = data.get('current_age_years')
        current_height_cm = data.get('current_height_cm')
        target_age_years = data.get('target_age_years')
        
        # 필수 입력 검증
        if not all([gender, current_age_years, current_height_cm, target_age_years]):
            return jsonify({'error': '모든 필수 입력을 제공해주세요.'}), 400
        
        # 예측 수행
        result = growth_curve_predictor.predict_at_age(
            current_age_years=float(current_age_years),
            current_height_cm=float(current_height_cm),
            target_age_years=float(target_age_years),
            gender=gender
        )
        
        return jsonify({
            'success': True,
            'prediction': result
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'예측 중 오류 발생: {str(e)}'}), 500


@app.route('/api/countries', methods=['GET'])
def get_countries():
    """사용 가능한 국가 목록 반환"""
    try:
        countries = get_available_countries()
        return jsonify({
            'success': True,
            'countries': countries
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("키 예측 웹 애플리케이션 시작")
    print("="*60)
    
    # 예측기 초기화
    init_predictors()
    
    if enhanced_predictor is None or enhanced_growth_curve_predictor is None:
        print("❌ 예측기 초기화 실패. 애플리케이션을 시작할 수 없습니다.")
        sys.exit(1)
    
    print("\n🌐 웹 서버 시작 중...")
    print("   http://localhost:5001 에서 접속 가능합니다.")
    print("\n종료하려면 Ctrl+C를 누르세요.")
    
    app.run(debug=True, host='0.0.0.0', port=5001)

