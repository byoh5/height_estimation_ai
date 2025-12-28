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
MODEL_DIR = PROJECT_ROOT / "models" / "saved_models"
sys.path.insert(0, str(PROJECT_ROOT))

from src.modeling.growth_curve_predictor import GrowthCurvePredictor
from src.utils.age_calculator import calculate_age, calculate_age_months, parse_date_input, validate_birth_date
from src.utils.growth_factors import HeightPredictionAdjuster, get_available_countries

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
    
    def predict(self,
                birth_date: Optional[str] = None,
                gender: Optional[str] = None,
                current_height_cm: Optional[float] = None,
                current_date: Optional[str] = None,
                father_height_cm: Optional[float] = None,
                mother_height_cm: Optional[float] = None,
                height_history: Optional[List[Dict]] = None,
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
        
        # 전략 1: 부모 키 기반 예측 (Galton 모델)
        if has_parents and self.galton_model is not None:
            try:
                X_galton = self._prepare_galton_features(father_height_cm, mother_height_cm, gender)
                pred_galton = self.galton_model.predict(X_galton)[0]
                predictions.append(pred_galton)
                # 성장 데이터가 있으면 가중치 0.8, 없으면 1.0
                if has_growth_data:
                    weights.append(0.8)
                else:
                    weights.append(1.0)
                results['model_used'].append('galton')
                results['details']['galton_prediction'] = float(pred_galton)
                results['confidence'] = 'high'
            except Exception as e:
                print(f"⚠️  Galton 모델 예측 오류: {e}")
        
        # 전략 2: 성장 곡선 기반 예측 (5세 초과일 때)
        if has_growth_data and age_years > 5:
            try:
                pred_growth_curve = self._estimate_adult_height_from_growth_curve(
                    current_age_years=age_years,
                    current_height_cm=current_height_cm,
                    gender=gender
                )
                if pred_growth_curve is not None:
                    if not has_parents:
                        # 부모 키가 없으면 성장 곡선 모델만 사용 (일관성 확보)
                        predictions = [pred_growth_curve]
                        weights = [1.0]
                        results['model_used'] = ['growth_curve']
                        results['details']['growth_curve_prediction'] = float(pred_growth_curve)
                        results['confidence'] = 'high'
                    else:
                        # 부모 키가 있으면 보조 모델로 사용 (가중치 0.2)
                        predictions.append(pred_growth_curve)
                        weights.append(0.2)
                        results['model_used'].append('growth_curve')
                        results['details']['growth_curve_prediction'] = float(pred_growth_curve)
            except Exception as e:
                print(f"⚠️  성장 곡선 모델 예측 오류: {e}")
        
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
        
        # 보정된 예측값으로 업데이트
        original_prediction = results['predicted_height']
        results['predicted_height'] = adjustment_result['final_prediction']
        results['details']['original_prediction'] = original_prediction
        results['details']['adjustments'] = adjustment_result['adjustments']
        results['details']['total_adjustment'] = adjustment_result['total_adjustment']
        results['details']['country_code'] = country_code
        
        return results
