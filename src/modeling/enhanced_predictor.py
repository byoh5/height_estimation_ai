"""
향상된 하이브리드 예측기
- 생년월일 기반 나이 계산
- 여러 시점의 키 입력 지원
- Stunting 모델 제한 및 성장 곡선 모델 활용
- 성장 곡선과 성인 키 예측 일관성 확보
"""

import numpy as np
import pandas as pd
from pathlib import Path
import joblib
import json
import sys
from typing import Dict, Optional, List, Tuple
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.modeling.growth_curve_predictor import GrowthCurvePredictor
from src.utils.age_calculator import calculate_age, calculate_age_months, parse_date_input, validate_birth_date
from src.utils.growth_factors import HeightPredictionAdjuster, get_available_countries
from src.utils.runtime_paths import get_model_dir

MODEL_DIR = get_model_dir()

class EnhancedHeightPredictor:
    """향상된 키 예측 모델 - 성장 곡선과 성인 키 예측 일관성 확보"""
    
    def __init__(self):
        self.galton_model = None
        self.stunting_model = None
        self.growth_curve_predictor = None
        self.galton_metadata = None
        self.stunting_metadata = None
        self._load_models()
    
    def _load_models(self):
        """학습된 모델 로드"""
        # Galton 모델 로드
        galton_files = list(MODEL_DIR.glob("galton_*_model.pkl"))
        if galton_files:
            self.galton_model = joblib.load(galton_files[0])
            metadata_file = MODEL_DIR / galton_files[0].stem.replace('_model', '_metadata.json')
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    self.galton_metadata = json.load(f)
            print(f"✅ Galton 모델 로드: {galton_files[0].name}")
        
        # Stunting 모델 로드 (5세 이하에서만 사용)
        stunting_files = list(MODEL_DIR.glob("stunting_*_model.pkl"))
        if stunting_files:
            self.stunting_model = joblib.load(stunting_files[0])
            metadata_file = MODEL_DIR / stunting_files[0].stem.replace('_model', '_metadata.json')
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    self.stunting_metadata = json.load(f)
            print(f"✅ Stunting 모델 로드: {stunting_files[0].name} (5세 이하에서만 사용)")
        
        # 성장 곡선 예측기 로드
        try:
            self.growth_curve_predictor = GrowthCurvePredictor()
            print(f"✅ 성장 곡선 예측기 로드 완료")
        except Exception as e:
            print(f"⚠️  성장 곡선 예측기 로드 실패: {e}")
    
    def _calculate_age_from_birthdate(self, birth_date: str, reference_date: Optional[str] = None) -> Tuple[float, float]:
        """생년월일로부터 나이 계산"""
        parsed_date = parse_date_input(birth_date)
        if parsed_date is None:
            raise ValueError(f"올바른 날짜 형식이 아닙니다: {birth_date}")
        
        age_years_int, age_years = calculate_age(parsed_date, reference_date)
        age_months = calculate_age_months(parsed_date, reference_date)
        
        return age_years, age_months
    
    def _prepare_galton_features(self, father_height_cm: float, mother_height_cm: float,
                                 gender: str) -> np.ndarray:
        """Galton 모델용 특성 준비"""
        midparent_height = (father_height_cm + mother_height_cm) / 2
        gender_M = 1 if gender.upper() == 'M' else 0
        gender_F = 1 if gender.upper() == 'F' else 0
        return np.array([[father_height_cm, mother_height_cm, midparent_height, gender_M, gender_F]])
    
    def _prepare_stunting_features(self, age_months: float, age_years: float,
                                   height_cm: float, gender: str) -> np.ndarray:
        """Stunting 모델용 특성 준비"""
        gender_M = 1 if gender.upper() == 'M' else 0
        gender_F = 1 if gender.upper() == 'F' else 0
        return np.array([[age_months, age_years, height_cm, gender_M, gender_F]])
    
    def _estimate_adult_height_from_growth_curve(self, current_age_years: float,
                                                  current_height_cm: float,
                                                  gender: str) -> Optional[float]:
        """성장 곡선 모델을 사용하여 성인 키 예측 (18세)"""
        try:
            if self.growth_curve_predictor is None:
                return None
            
            # 18세 키 예측
            result = self.growth_curve_predictor.predict_at_age(
                current_age_years=current_age_years,
                current_height_cm=current_height_cm,
                target_age_years=18,
                gender=gender
            )
            return result['predicted_height_cm']
        except Exception as e:
            print(f"⚠️  성장 곡선 모델 예측 오류: {e}")
            return None
    
    def _analyze_growth_pattern(self, height_records: List[Dict]) -> Dict:
        """
        여러 시점의 키 데이터를 분석하여 성장 패턴 파악
        
        Args:
            height_records: [{'age_years': float, 'height_cm': float, 'date': str}, ...]
        
        Returns:
            성장 패턴 분석 결과
        """
        if len(height_records) < 2:
            return {'growth_rate': None, 'trend': None}
        
        # 나이 순으로 정렬
        sorted_records = sorted(height_records, key=lambda x: x['age_years'])
        
        # 성장률 계산
        growth_rates = []
        for i in range(1, len(sorted_records)):
            age_diff = sorted_records[i]['age_years'] - sorted_records[i-1]['age_years']
            height_diff = sorted_records[i]['height_cm'] - sorted_records[i-1]['height_cm']
            if age_diff > 0:
                growth_rate = height_diff / age_diff  # cm/year
                growth_rates.append(growth_rate)
        
        avg_growth_rate = np.mean(growth_rates) if growth_rates else None
        
        return {
            'growth_rate': avg_growth_rate,
            'records_count': len(sorted_records),
            'age_range': (sorted_records[0]['age_years'], sorted_records[-1]['age_years'])
        }

    @staticmethod
    def _is_puberty_window(age_years: Optional[float], gender: str) -> bool:
        """사춘기 변동성이 큰 구간 판별"""
        if age_years is None:
            return False

        if gender.upper() == 'M':
            return 10.0 <= age_years <= 14.5
        if gender.upper() == 'F':
            return 9.0 <= age_years <= 13.5
        return False

    def _assess_confidence_and_uncertainty(self,
                                           gender: str,
                                           age_years: Optional[float],
                                           current_height_cm: Optional[float],
                                           has_parents: bool,
                                           has_menarche: bool,
                                           height_records: List[Dict],
                                           model_predictions: List[float],
                                           warning_text: Optional[str],
                                           final_prediction: float,
                                           weight_kg: Optional[float],
                                           bone_age_years: Optional[float],
                                           puberty_stage: Optional[str]) -> Dict:
        """
        보수적 신뢰도 산정 + 오차범위 추정.
        - 입력 완성도
        - 사춘기 변동성
        - 모델 간 불일치(충돌)
        를 함께 반영한다.
        """
        score = 70
        score_cap = 90
        strengths: List[str] = []
        limitations: List[str] = []

        history_count = len(height_records)
        model_spread_cm = 0.0
        if len(model_predictions) >= 2:
            model_spread_cm = float(max(model_predictions) - min(model_predictions))

        if has_parents:
            score += 8
            strengths.append("부모 키 정보가 포함되었습니다.")

        if history_count >= 3:
            score += 6
            strengths.append(f"연속 키 기록 {history_count}개가 반영되었습니다.")
        elif history_count >= 2:
            score += 3

        if history_count >= 5:
            score += 4

        if has_parents and history_count >= 3:
            score += 6
            strengths.append("부모 키 + 성장 이력이 함께 반영되었습니다.")

        if has_menarche:
            score += 4
            strengths.append("초경 정보가 예측에 반영되었습니다.")

        puberty_window = self._is_puberty_window(age_years, gender)
        adolescent_window = age_years is not None and 8.0 <= age_years <= 15.0

        if puberty_window:
            score -= 8
            limitations.append("사춘기 변동 구간으로 성장 속도 편차가 큽니다.")
            score_cap = min(score_cap, 82)

        if model_spread_cm >= 10:
            score -= 10
            limitations.append(f"모델 간 예측 차이가 큽니다 ({model_spread_cm:.1f}cm).")
            score_cap = min(score_cap, 68)
        elif model_spread_cm >= 6:
            score -= 6
            limitations.append(f"모델 간 예측 차이가 있습니다 ({model_spread_cm:.1f}cm).")
            score_cap = min(score_cap, 76)
        elif model_spread_cm >= 3:
            score -= 3

        if adolescent_window and bone_age_years is None:
            score -= 6
            limitations.append("골연령 정보가 없어 사춘기 보정 정확도가 제한됩니다.")
            score_cap = min(score_cap, 78)
        elif bone_age_years is not None:
            strengths.append("골연령 정보가 포함되었습니다.")

        if weight_kg is None:
            score -= 3
            limitations.append("체중 정보가 없어 일부 공식 보정이 제한됩니다.")
        else:
            strengths.append("체중 정보가 포함되었습니다.")

        if adolescent_window and (not puberty_stage or puberty_stage == 'unknown'):
            score -= 3
            limitations.append("사춘기 단계 정보가 없어 불확실성이 커질 수 있습니다.")
            score_cap = min(score_cap, 74)
        elif puberty_stage and puberty_stage != 'unknown':
            strengths.append("사춘기 진행 단계 정보가 포함되었습니다.")

        if warning_text:
            score -= 4
            limitations.append("학습 데이터 범위를 벗어난 입력이 일부 포함됩니다.")
            score_cap = min(score_cap, 72)

        score = max(25, min(score_cap, int(round(score))))

        if score >= 88:
            confidence = 'very_high'
        elif score >= 74:
            confidence = 'high'
        elif score >= 58:
            confidence = 'medium'
        else:
            confidence = 'low'

        uncertainty_cm = 2.8
        if puberty_window:
            uncertainty_cm += 1.0
        uncertainty_cm += min(model_spread_cm * 0.25, 2.0)
        if adolescent_window and bone_age_years is None:
            uncertainty_cm += 0.8
        if adolescent_window and (not puberty_stage or puberty_stage == 'unknown'):
            uncertainty_cm += 0.5
        if weight_kg is None:
            uncertainty_cm += 0.4
        if history_count >= 5:
            uncertainty_cm -= 0.5
        elif history_count >= 3:
            uncertainty_cm -= 0.3
        if has_parents:
            uncertainty_cm -= 0.4
        if warning_text:
            uncertainty_cm += 0.4

        uncertainty_cm = round(float(max(2.0, min(8.0, uncertainty_cm))), 1)

        lower = round(float(final_prediction - uncertainty_cm), 1)
        upper = round(float(final_prediction + uncertainty_cm), 1)
        if current_height_cm is not None:
            lower = round(float(max(lower, current_height_cm)), 1)

        return {
            'confidence': confidence,
            'confidence_score': score,
            'uncertainty_cm': uncertainty_cm,
            'prediction_range_cm': {
                'lower': lower,
                'upper': upper
            },
            'model_spread_cm': round(model_spread_cm, 1),
            'confidence_factors': {
                'strengths': strengths,
                'limitations': limitations
            }
        }
    
    def predict(self,
                birth_date: Optional[str] = None,
                gender: Optional[str] = None,
                current_height_cm: Optional[float] = None,
                current_date: Optional[str] = None,
                father_height_cm: Optional[float] = None,
                mother_height_cm: Optional[float] = None,
                height_history: Optional[List[Dict]] = None,
                menarche_age: Optional[float] = None,
                weight_kg: Optional[float] = None,
                bone_age_years: Optional[float] = None,
                puberty_stage: Optional[str] = None,
                country_code: str = 'DEFAULT',
                use_genetic_formulas: bool = True,
                use_growth_pattern: bool = True) -> Dict:
        """
        향상된 키 예측
        
        일관성 확보 전략:
        - 부모 키 없음 + 나이 > 5세: 성장 곡선 18세 예측만 사용 (일관성 확보)
        - 부모 키 있음 + 나이 > 5세: Galton (0.8) + 성장 곡선 (0.2) 가중 평균
        - 부모 키 없음 + 나이 <= 5세: Stunting 모델 사용
        - 부모 키 있음 + 나이 <= 5세: Galton (0.7) + Stunting (0.3) 가중 평균
        
        Args:
            birth_date: 생년월일 (YYYY-MM-DD)
            gender: 성별 ('M' or 'F')
            current_height_cm: 현재 키 (cm)
            current_date: 현재 날짜 (YYYY-MM-DD, None이면 오늘)
            father_height_cm: 아버지 키 (cm)
            mother_height_cm: 어머니 키 (cm)
            height_history: 과거 키 기록 [{'date': 'YYYY-MM-DD', 'height_cm': float}, ...]
            menarche_age: 초경 시작 나이 (여성만, 선택사항)
            weight_kg: 현재 체중 (kg, 선택사항)
            bone_age_years: 골연령 (세, 선택사항)
            puberty_stage: 사춘기 단계 (unknown/pre/early/mid/late/completed)
            country_code: 국가 코드
            use_genetic_formulas: 유전 공식 사용 여부
            use_growth_pattern: 성장 패턴 분석 사용 여부
        
        Returns:
            예측 결과 딕셔너리
        """
        results = {
            'predicted_height': None,
            'model_used': [],
            'confidence': 'low',
            'details': {}
        }
        
        # 필수 입력 검증
        if not gender:
            raise ValueError("성별(gender)은 필수 입력입니다.")
        
        # 성별 검증
        if gender.upper() not in ['M', 'F']:
            raise ValueError(f"성별은 'M' 또는 'F'만 허용됩니다. 입력값: {gender}")
        
        # 키 값 검증
        if current_height_cm is not None:
            if current_height_cm <= 0:
                raise ValueError(f"현재 키는 0보다 커야 합니다. 입력값: {current_height_cm}cm")
            if current_height_cm > 300:
                raise ValueError(f"현재 키는 300cm 이하여야 합니다. 입력값: {current_height_cm}cm")
        
        # 부모 키 검증
        if father_height_cm is not None:
            if father_height_cm <= 0:
                raise ValueError(f"아버지 키는 0보다 커야 합니다. 입력값: {father_height_cm}cm")
            if father_height_cm > 300:
                raise ValueError(f"아버지 키는 300cm 이하여야 합니다. 입력값: {father_height_cm}cm")
        
        if mother_height_cm is not None:
            if mother_height_cm <= 0:
                raise ValueError(f"어머니 키는 0보다 커야 합니다. 입력값: {mother_height_cm}cm")
            if mother_height_cm > 300:
                raise ValueError(f"어머니 키는 300cm 이하여야 합니다. 입력값: {mother_height_cm}cm")
        
        # 초경 나이 검증 (여성만)
        if menarche_age is not None:
            if gender.upper() != 'F':
                # 남성에게 초경 정보가 있으면 무시 (경고 없이)
                menarche_age = None
            else:
                if menarche_age < 0:
                    raise ValueError(f"초경 나이는 0 이상이어야 합니다. 입력값: {menarche_age}세")
                if menarche_age > 18:
                    raise ValueError(f"초경 나이는 18세 이하여야 합니다. 입력값: {menarche_age}세")
                
                # 현재 나이와 비교
                if birth_date:
                    age_years_temp, _ = self._calculate_age_from_birthdate(birth_date, current_date)
                    if menarche_age > age_years_temp:
                        raise ValueError(
                            f"초경 나이({menarche_age}세)는 현재 나이({age_years_temp:.1f}세)보다 클 수 없습니다."
                        )

        # 체중 검증
        if weight_kg is not None:
            try:
                weight_kg = float(weight_kg)
            except (TypeError, ValueError):
                raise ValueError(f"체중은 숫자여야 합니다. 입력값: {weight_kg}")

            if weight_kg <= 0:
                raise ValueError(f"체중은 0보다 커야 합니다. 입력값: {weight_kg}kg")
            if weight_kg > 200:
                raise ValueError(f"체중은 200kg 이하여야 합니다. 입력값: {weight_kg}kg")

        # 골연령 검증
        if bone_age_years is not None:
            try:
                bone_age_years = float(bone_age_years)
            except (TypeError, ValueError):
                raise ValueError(f"골연령은 숫자여야 합니다. 입력값: {bone_age_years}")

            if bone_age_years < 0:
                raise ValueError(f"골연령은 0세 이상이어야 합니다. 입력값: {bone_age_years}세")
            if bone_age_years > 20:
                raise ValueError(f"골연령은 20세 이하여야 합니다. 입력값: {bone_age_years}세")

        # 사춘기 단계 검증
        allowed_puberty_stages = {'unknown', 'pre', 'early', 'mid', 'late', 'completed', None}
        if puberty_stage not in allowed_puberty_stages:
            raise ValueError(
                f"사춘기 단계는 unknown/pre/early/mid/late/completed 중 하나여야 합니다. 입력값: {puberty_stage}"
            )
        
        # 나이 계산
        age_years = None
        age_months = None
        if birth_date:
            age_years, age_months = self._calculate_age_from_birthdate(birth_date, current_date)
        
        # 키 기록 처리
        height_records = []
        if current_height_cm is not None and age_years is not None:
            height_records.append({
                'age_years': age_years,
                'height_cm': current_height_cm,
                'date': current_date or datetime.now().strftime('%Y-%m-%d')
            })
        
        if height_history:
            for record in height_history:
                record_date = record.get('date')
                record_height = record.get('height_cm')
                if record_date and record_height:
                    try:
                        record_age_years, _ = self._calculate_age_from_birthdate(birth_date, record_date)
                        height_records.append({
                            'age_years': record_age_years,
                            'height_cm': record_height,
                            'date': record_date
                        })
                    except:
                        pass
        
        # 가장 최근 키 사용 (과거 기록이 있으면 더 정확한 예측 가능)
        if height_records:
            latest_record = max(height_records, key=lambda x: x['age_years'])
            current_height_cm = latest_record['height_cm']
            age_years = latest_record['age_years']
            age_months = age_years * 12
        
        predictions = []
        weights = []
        
        has_parents = father_height_cm is not None and mother_height_cm is not None
        has_growth_data = current_height_cm is not None and age_years is not None
        has_menarche = gender == 'F' and menarche_age is not None
        
        # 전략 0: 초경 기반 예측 (여성만, 초경 정보가 있을 때)
        if has_menarche and has_growth_data:
            try:
                from src.utils.growth_factors import predict_female_height_with_menarche
                
                menarche_prediction = predict_female_height_with_menarche(
                    age=age_years,
                    height=current_height_cm,
                    menarche_age=menarche_age
                )
                
                pred_menarche = menarche_prediction['predicted_height']
                
                # 초경 정보가 있으면 높은 가중치 부여
                if has_parents:
                    # 부모 키가 있으면 초경 예측과 부모 키 예측에 동일한 가중치
                    predictions.append(pred_menarche)
                    weights.append(0.4)  # 부모 키와 동일한 가중치
                else:
                    # 부모 키가 없으면 초경 예측에 더 높은 가중치
                    predictions.append(pred_menarche)
                    weights.append(0.6)
                
                results['model_used'].append('menarche')
                results['details']['menarche_prediction'] = float(pred_menarche)
                results['details']['menarche_info'] = {
                    'menarche_age': menarche_age,
                    'growth_before_menarche': menarche_prediction.get('growth_before_menarche'),
                    'growth_after_menarche': menarche_prediction.get('growth_after_menarche'),
                    'years_since_menarche': menarche_prediction.get('years_since_menarche'),
                    'years_until_menarche': menarche_prediction.get('years_until_menarche')
                }
                # 초경 정보가 있으면 신뢰도 향상
                if results['confidence'] == 'low':
                    results['confidence'] = 'medium'
                elif results['confidence'] == 'medium':
                    results['confidence'] = 'high'
                else:
                    results['confidence'] = 'very_high'
            except Exception as e:
                print(f"⚠️  초경 기반 예측 오류: {e}")
        
        # 전략 1: 부모 키 기반 예측 (Galton 모델)
        if has_parents and self.galton_model is not None:
            try:
                X_galton = self._prepare_galton_features(father_height_cm, mother_height_cm, gender)
                pred_galton = self.galton_model.predict(X_galton)[0]
                predictions.append(pred_galton)
                # 초경 정보가 있으면 가중치 조정
                if has_menarche:
                    weights.append(0.4)  # 초경 정보가 있으면 부모 키와 동일한 가중치
                elif has_growth_data:
                    weights.append(0.8)
                else:
                    weights.append(1.0)
                results['model_used'].append('galton')
                results['details']['galton_prediction'] = float(pred_galton)
                if not has_menarche:  # 초경 정보가 없을 때만 신뢰도 설정
                    results['confidence'] = 'high'
            except Exception as e:
                print(f"⚠️  Galton 모델 예측 오류: {e}")
        
        # 전략 2: 성장 곡선 기반 예측 (5세 초과일 때)
        # 주의: 학습 데이터는 0-5세만 포함하므로, 나이가 많거나 키가 큰 경우 신뢰도 낮음
        if has_growth_data and age_years > 5:
            # 학습 데이터 범위 확인: 나이 0-5세, 키 40-128cm
            # 나이가 많거나 키가 큰 경우 경고
            is_out_of_range = age_years > 10 or current_height_cm > 140
            
            try:
                pred_growth_curve = self._estimate_adult_height_from_growth_curve(
                    current_age_years=age_years,
                    current_height_cm=current_height_cm,
                    gender=gender
                )
                if pred_growth_curve is not None:
                    # 예측값이 현재 키보다 낮으면 보정
                    if pred_growth_curve < current_height_cm:
                        # 최소한 현재 키 + 나이에 따른 최소 성장량 보장
                        remaining_years = 18 - age_years
                        if remaining_years > 0:
                            # 나이에 따른 최소 성장량 (의료 연구 기반)
                            if age_years < 12:
                                min_growth = remaining_years * 2.0  # 사춘기 전: 연간 최소 2cm
                            elif age_years < 15:
                                min_growth = remaining_years * 1.5  # 사춘기 진행: 연간 최소 1.5cm
                            else:
                                min_growth = remaining_years * 1.0  # 성장 완료 직전: 연간 최소 1cm
                            pred_growth_curve = max(pred_growth_curve, current_height_cm + min_growth)
                    
                    # 나이가 많을수록 신뢰도 낮춤
                    if age_years > 10:
                        growth_curve_weight = 0.1  # 매우 낮은 가중치
                        growth_confidence = 'low'
                    elif age_years > 8:
                        growth_curve_weight = 0.3
                        growth_confidence = 'medium'
                    else:
                        growth_curve_weight = 0.2 if has_parents else 1.0
                        growth_confidence = 'high'
                    
                    # 초경 정보가 있으면 가중치 조정
                    if has_menarche:
                        growth_curve_weight = 0.2  # 초경 정보가 있으면 낮은 가중치
                    
                    if not has_parents and not has_menarche:
                        # 부모 키도 초경 정보도 없으면 성장 곡선 모델만 사용 (일관성 확보)
                        predictions = [pred_growth_curve]
                        weights = [1.0]
                        results['model_used'] = ['growth_curve']
                        results['details']['growth_curve_prediction'] = float(pred_growth_curve)
                        results['confidence'] = growth_confidence
                        if is_out_of_range:
                            results['confidence'] = 'low'
                            results['details']['warning'] = '학습 데이터 범위를 벗어난 예측입니다. 신뢰도가 낮을 수 있습니다.'
                    else:
                        # 부모 키나 초경 정보가 있으면 보조 모델로 사용 (가중치 조정)
                        predictions.append(pred_growth_curve)
                        weights.append(growth_curve_weight)
                        results['model_used'].append('growth_curve')
                        results['details']['growth_curve_prediction'] = float(pred_growth_curve)
                        if is_out_of_range:
                            results['details']['warning'] = '성장 곡선 모델이 학습 데이터 범위를 벗어난 예측입니다.'
            except Exception as e:
                print(f"⚠️  성장 곡선 모델 예측 오류: {e}")
                # 성장 곡선 모델 실패 시, 부모 키가 없으면 오류 발생
                if not has_parents and not predictions:
                    raise ValueError(
                        f"예측할 수 있는 충분한 정보가 없습니다. "
                        f"부모 키 정보를 제공하거나, 나이가 10세 이하일 때 사용해주세요."
                    )
        
        # 전략 3: Stunting 모델 (5세 이하에서만 사용)
        if has_growth_data and age_years is not None and age_years <= 5 and self.stunting_model is not None:
            try:
                X_stunting = self._prepare_stunting_features(age_months, age_years, current_height_cm, gender)
                pred_stunting = self.stunting_model.predict(X_stunting)[0]
                if not has_parents:
                    # 부모 키가 없으면 Stunting 모델만 사용
                    predictions = [pred_stunting]
                    weights = [1.0]
                    results['model_used'] = ['stunting']
                    results['details']['stunting_prediction'] = float(pred_stunting)
                    results['confidence'] = 'medium'
                else:
                    # 부모 키가 있으면 보조 모델로 사용
                    predictions.append(pred_stunting)
                    weights.append(0.3)
                    results['model_used'].append('stunting')
                    results['details']['stunting_prediction'] = float(pred_stunting)
            except Exception as e:
                print(f"⚠️  Stunting 모델 예측 오류: {e}")
        
        # 예측 결과 결합
        if predictions:
            weights = np.array(weights)
            weights = weights / weights.sum()  # 정규화
            final_prediction = np.average(predictions, weights=weights)
            
            results['predicted_height'] = float(final_prediction)
            results['details']['weighted_average'] = len(predictions) > 1
            if len(predictions) > 1:
                results['details']['weights'] = {model: float(w) for model, w in zip(results['model_used'], weights)}
        else:
            raise ValueError("예측할 수 있는 충분한 정보가 없습니다.")
        
        # 신뢰도 조정
        if len(height_records) > 1:
            # 과거 기록이 있으면 신뢰도 향상
            growth_pattern = self._analyze_growth_pattern(height_records)
            results['details']['growth_pattern'] = growth_pattern
            if results['confidence'] == 'high':
                results['confidence'] = 'very_high'
            elif results['confidence'] == 'medium':
                results['confidence'] = 'high'
        
        if len(predictions) == 2 and has_parents and has_growth_data:
            results['confidence'] = 'very_high'
        
        # 나이 정보 추가
        if age_years is not None:
            results['details']['age_years'] = age_years
            results['details']['age_months'] = age_months
        
        # 오프셋 조절 적용
        adjuster = HeightPredictionAdjuster(country_code=country_code)
        
        # 키 기록 형식 변환 (adjuster에 맞게)
        formatted_history = []
        if height_records:
            formatted_history = [
                {'age_years': r['age_years'], 'height_cm': r['height_cm']}
                for r in height_records
            ]
        
        # 오프셋 조절 적용 (단, 가중 평균 결과를 우선시)
        original_prediction = results['predicted_height']
        
        adjustment_result = adjuster.calculate_final_prediction(
            base_prediction=results['predicted_height'],
            father_cm=father_height_cm,
            mother_cm=mother_height_cm,
            gender=gender,
            current_age=age_years,
            current_height=current_height_cm,
            height_history=formatted_history,
            use_genetic_formulas=use_genetic_formulas,
            use_growth_pattern=use_growth_pattern
        )
        
        # 오프셋 조절 강도 제한: 가중 평균 결과를 크게 벗어나지 않도록
        total_adjustment = adjustment_result['total_adjustment']
        adjusted_prediction = adjustment_result['final_prediction']
        
        # 성장 곡선 예측이 가중 평균보다 훨씬 높으면, 오프셋 조절을 덜 적용
        if 'growth_curve_prediction' in results.get('details', {}):
            growth_curve_pred = results['details']['growth_curve_prediction']
            if growth_curve_pred > original_prediction + 10:
                # 성장 곡선이 높을 때는 오프셋 조절을 50%만 적용
                adjustment_limit = (adjusted_prediction - original_prediction) * 0.5
                adjusted_prediction = original_prediction + adjustment_limit
                total_adjustment = adjustment_limit
        
        # 최종 예측값이 현재 키보다 낮거나, 가중 평균보다 너무 낮으면 제한
        if current_height_cm is not None:
            remaining_years = 18 - age_years if age_years is not None and age_years < 18 else 1
            # 나이에 따른 최소 성장량 계산
            if age_years is not None:
                if age_years < 12:
                    min_growth = remaining_years * 2.0  # 사춘기 전: 연간 최소 2cm
                elif age_years < 15:
                    min_growth = remaining_years * 1.5  # 사춘기 진행: 연간 최소 1.5cm
                elif age_years < 18:
                    min_growth = remaining_years * 1.0  # 성장 완료 직전: 연간 최소 1cm
                else:
                    min_growth = 0.5  # 18세 이상: 최소 0.5cm
            else:
                min_growth = 1.0  # 나이 정보 없으면 최소 1cm
            
            min_acceptable_height = current_height_cm + min_growth
            
            if adjusted_prediction < min_acceptable_height:
                # 최소한 현재 키 + 최소 성장량보다는 높아야 함
                adjusted_prediction = max(min_acceptable_height, original_prediction * 0.95)
                total_adjustment = adjusted_prediction - original_prediction
            elif adjusted_prediction < original_prediction * 0.95:
                # 가중 평균보다 5% 이상 낮아지지 않도록 제한
                adjusted_prediction = original_prediction * 0.95
                total_adjustment = adjusted_prediction - original_prediction
        
        # 유전 공식 보정이 너무 강하게 적용되는 경우 제한
        if 'galton_prediction' in results.get('details', {}) and 'genetic_formulas' in adjustment_result.get('adjustments', {}):
            galton_pred = results['details']['galton_prediction']
            genetic_avg = adjustment_result['adjustments']['genetic_formulas'].get('average', 0)
            # 유전 공식 평균이 가중 평균보다 너무 낮으면 보정을 완화
            if genetic_avg > 0 and genetic_avg < original_prediction - 5:
                # 유전 공식 보정을 50%만 적용
                genetic_after = adjustment_result['adjustments']['genetic_formulas'].get('after', adjusted_prediction)
                genetic_adjustment = genetic_after - original_prediction
                if genetic_adjustment < 0:  # 음수 조정인 경우
                    adjusted_prediction = original_prediction + genetic_adjustment * 0.5
                    total_adjustment = adjusted_prediction - original_prediction
        
        results['predicted_height'] = adjusted_prediction
        results['details']['original_prediction'] = original_prediction
        results['details']['adjustments'] = adjustment_result['adjustments']
        results['details']['total_adjustment'] = total_adjustment
        results['details']['country_code'] = country_code

        # 입력 맥락(가독성/해석용)
        results['details']['input_context'] = {
            'weight_kg': weight_kg,
            'bone_age_years': bone_age_years,
            'puberty_stage': puberty_stage or 'unknown'
        }

        # 보수적 신뢰도/오차범위 재산정
        confidence_assessment = self._assess_confidence_and_uncertainty(
            gender=gender,
            age_years=age_years,
            current_height_cm=current_height_cm,
            has_parents=has_parents,
            has_menarche=has_menarche,
            height_records=height_records,
            model_predictions=[float(x) for x in predictions],
            warning_text=results['details'].get('warning'),
            final_prediction=adjusted_prediction,
            weight_kg=weight_kg,
            bone_age_years=bone_age_years,
            puberty_stage=puberty_stage
        )

        results['confidence'] = confidence_assessment['confidence']
        results['details'].update(confidence_assessment)
        if confidence_assessment['model_spread_cm'] >= 6:
            results['details']['model_conflict_warning'] = (
                f"모델 간 예측 차이 {confidence_assessment['model_spread_cm']:.1f}cm로 불확실성이 높습니다."
            )
        
        return results
