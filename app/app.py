"""
키 예측 웹 애플리케이션
Flask 기반 웹 인터페이스
"""

from flask import Flask, render_template, request, jsonify, make_response
from fnmatch import fnmatch
import os
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.modeling.enhanced_predictor import EnhancedHeightPredictor
from src.modeling.enhanced_growth_curve_predictor import EnhancedGrowthCurvePredictor
from src.utils.age_calculator import validate_birth_date, parse_date_input, calculate_age
from src.utils.growth_factors import get_available_countries
from src.utils.runtime_paths import get_model_dir
from version import __version__, __app_name__, __description__

app = Flask(__name__)

# 전역 예측기 인스턴스
enhanced_predictor = None
enhanced_growth_curve_predictor = None

DEFAULT_ALLOWED_ORIGIN_PATTERNS = (
    "http://localhost:*",
    "http://127.0.0.1:*",
    "https://localhost:*",
    "https://127.0.0.1:*",
    "https://*.github.io",
)


def _load_allowed_origin_patterns():
    raw_value = os.environ.get("HEIGHT_AI_ALLOWED_ORIGINS", "")
    if not raw_value.strip():
        return DEFAULT_ALLOWED_ORIGIN_PATTERNS
    return tuple(origin.strip() for origin in raw_value.split(",") if origin.strip())


ALLOWED_ORIGIN_PATTERNS = _load_allowed_origin_patterns()


def _is_origin_allowed(origin):
    if not origin:
        # 브라우저가 아닌 요청(curl, health check 등)은 허용
        return True
    return any(fnmatch(origin, pattern) for pattern in ALLOWED_ORIGIN_PATTERNS)


@app.before_request
def _handle_api_cors_preflight():
    """API 요청의 Origin 검증 + OPTIONS 사전요청 처리"""
    if not request.path.startswith("/api/"):
        return None

    origin = request.headers.get("Origin")
    if origin and not _is_origin_allowed(origin):
        return jsonify({"error": f"허용되지 않은 Origin입니다: {origin}"}), 403

    if request.method == "OPTIONS":
        return make_response("", 204)
    return None


@app.after_request
def _set_api_cors_headers(response):
    """허용된 Origin에 대해서만 CORS 헤더 추가"""
    if not request.path.startswith("/api/"):
        return response

    origin = request.headers.get("Origin")
    if origin and _is_origin_allowed(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"

    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,X-Local-Engine-Token"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response


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
    return render_template('index.html', version=__version__, app_name=__app_name__)


@app.route('/api/health', methods=['GET'])
def health_check():
    """로컬 엔진 상태 확인"""
    return jsonify({
        'success': True,
        'service': 'height-prediction-local-engine',
        'predictors_ready': enhanced_predictor is not None and enhanced_growth_curve_predictor is not None,
        'model_dir': str(get_model_dir()),
        'version': __version__
    })

@app.route('/api/predict/adult', methods=['POST'])
def predict_adult_height():
    """성인 키 예측 API (향상된 버전)"""
    try:
        # JSON 파싱 검증
        if not request.is_json:
            return jsonify({'error': 'Content-Type이 application/json이어야 합니다.'}), 400
        
        try:
            data = request.json
            if data is None:
                return jsonify({'error': 'JSON 데이터가 비어있습니다.'}), 400
        except Exception as e:
            return jsonify({'error': f'JSON 파싱 오류: {str(e)}'}), 400
        
        # 입력 데이터 추출
        gender = data.get('gender')
        birth_date = data.get('birth_date')
        current_height_cm = data.get('current_height_cm')
        current_date = data.get('current_date')
        father_height_cm = data.get('father_height_cm')
        mother_height_cm = data.get('mother_height_cm')
        height_history = data.get('height_history', [])  # [{'date': 'YYYY-MM-DD', 'height_cm': float}, ...]
        weight_kg = data.get('weight_kg')
        bone_age_years = data.get('bone_age_years')
        puberty_stage = data.get('puberty_stage')
        
        # 필수 입력 검증
        if not gender:
            return jsonify({'error': '성별은 필수 입력입니다.'}), 400
        
        # 성별 검증
        if gender.upper() not in ['M', 'F']:
            return jsonify({'error': f"성별은 'M' 또는 'F'만 허용됩니다. 입력값: {gender}"}), 400
        gender = gender.upper()
        
        if not birth_date and not current_height_cm:
            return jsonify({'error': '생년월일 또는 현재 키 중 하나는 필수입니다.'}), 400
        
        # 생년월일 검증
        if birth_date:
            is_valid, error_msg = validate_birth_date(birth_date)
            if not is_valid:
                return jsonify({'error': error_msg}), 400
        
        # 키 값 검증
        if current_height_cm is not None:
            try:
                current_height_cm = float(current_height_cm)
                if current_height_cm <= 0:
                    return jsonify({'error': f'현재 키는 0보다 커야 합니다. 입력값: {current_height_cm}cm'}), 400
                if current_height_cm > 300:
                    return jsonify({'error': f'현재 키는 300cm 이하여야 합니다. 입력값: {current_height_cm}cm'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': f'현재 키는 숫자여야 합니다. 입력값: {current_height_cm}'}), 400
        
        # 부모 키 검증
        if father_height_cm is not None:
            try:
                father_height_cm = float(father_height_cm)
                if father_height_cm <= 0:
                    return jsonify({'error': f'아버지 키는 0보다 커야 합니다. 입력값: {father_height_cm}cm'}), 400
                if father_height_cm > 300:
                    return jsonify({'error': f'아버지 키는 300cm 이하여야 합니다. 입력값: {father_height_cm}cm'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': f'아버지 키는 숫자여야 합니다. 입력값: {father_height_cm}'}), 400
        
        if mother_height_cm is not None:
            try:
                mother_height_cm = float(mother_height_cm)
                if mother_height_cm <= 0:
                    return jsonify({'error': f'어머니 키는 0보다 커야 합니다. 입력값: {mother_height_cm}cm'}), 400
                if mother_height_cm > 300:
                    return jsonify({'error': f'어머니 키는 300cm 이하여야 합니다. 입력값: {mother_height_cm}cm'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': f'어머니 키는 숫자여야 합니다. 입력값: {mother_height_cm}'}), 400
        
        # 초경 정보 추출 및 검증 (여성만)
        menarche_age = None
        if gender == 'F':
            menarche_age = data.get('menarche_age')
            if menarche_age is not None:
                try:
                    menarche_age = float(menarche_age)
                except (ValueError, TypeError):
                    return jsonify({'error': f'초경 시작 나이는 숫자여야 합니다. 입력값: {menarche_age}'}), 400

                # 초경 나이 검증
                if menarche_age < 8 or menarche_age > 18:
                    return jsonify({'error': '초경 시작 나이는 8-18세 사이여야 합니다.'}), 400
                
                # 현재 나이와 비교 검증
                if birth_date:
                    age_years, _ = calculate_age(parse_date_input(birth_date), current_date)
                    if menarche_age > age_years:
                        return jsonify({'error': '초경 시작 나이는 현재 나이보다 클 수 없습니다.'}), 400
        
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
            menarche_age=menarche_age,
            weight_kg=weight_kg,
            bone_age_years=bone_age_years,
            puberty_stage=puberty_stage,
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
            'growth_curve': growth_curve_result,
            'version': __version__
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'예측 중 오류 발생: {str(e)}'}), 500


@app.route('/api/predict/age', methods=['POST'])
def predict_age_height():
    """특정 나이 키 예측 API"""
    try:
        if enhanced_growth_curve_predictor is None:
            return jsonify({'error': '예측기가 초기화되지 않았습니다.'}), 503

        data = request.json
        if data is None:
            return jsonify({'error': 'JSON 데이터가 비어있습니다.'}), 400
        
        # 입력 데이터 추출
        gender = data.get('gender')
        current_age_years = data.get('current_age_years')
        current_height_cm = data.get('current_height_cm')
        target_age_years = data.get('target_age_years')
        
        # 필수 입력 검증
        if (
            gender is None
            or current_age_years is None
            or current_height_cm is None
            or target_age_years is None
        ):
            return jsonify({'error': '모든 필수 입력을 제공해주세요.'}), 400
        
        # 예측 수행
        result = enhanced_growth_curve_predictor.growth_curve_predictor.predict_at_age(
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

@app.route('/api/version', methods=['GET'])
def get_version():
    """버전 정보 반환"""
    return jsonify({
        'success': True,
        'version': __version__,
        'app_name': __app_name__,
        'description': __description__
    })

if __name__ == '__main__':
    host = os.environ.get("HEIGHT_AI_HOST", "127.0.0.1")
    port = int(os.environ.get("HEIGHT_AI_PORT", "5001"))

    print("="*60)
    print(f"{__app_name__} v{__version__}")
    print("="*60)
    
    # 예측기 초기화
    init_predictors()
    
    if enhanced_predictor is None or enhanced_growth_curve_predictor is None:
        print("❌ 예측기 초기화 실패. 애플리케이션을 시작할 수 없습니다.")
        sys.exit(1)
    
    print("\n🌐 웹 서버 시작 중...")
    print(f"   http://{host}:{port} 에서 접속 가능합니다.")
    print(f"   허용 Origin 패턴: {', '.join(ALLOWED_ORIGIN_PATTERNS)}")
    print("\n종료하려면 Ctrl+C를 누르세요.")
    
    app.run(debug=False, host=host, port=port)
