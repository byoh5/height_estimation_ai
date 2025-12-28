"""
향상된 성장 곡선 예측기
오프셋 조절 기능을 포함한 성장 곡선 예측
"""

import numpy as np
import pandas as pd
from pathlib import Path
import joblib
import json
from typing import Dict, Optional, List
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
MODEL_DIR = PROJECT_ROOT / "models" / "saved_models"
import sys
sys.path.insert(0, str(PROJECT_ROOT))

from src.modeling.growth_curve_predictor import GrowthCurvePredictor
from src.utils.growth_factors import HeightPredictionAdjuster

class EnhancedGrowthCurvePredictor:
    """오프셋 조절이 적용된 성장 곡선 예측기"""
    
    def __init__(self):
        self.growth_curve_predictor = GrowthCurvePredictor()
        self.available_ages = self.growth_curve_predictor.get_available_ages()
    
    def predict_growth_curve(self,
                            birth_date: str,
                            gender: str,
                            current_height_cm: float,
                            current_date: Optional[str] = None,
                            father_height_cm: Optional[float] = None,
                            mother_height_cm: Optional[float] = None,
                            height_history: Optional[List[Dict]] = None,
                            country_code: str = 'DEFAULT',
                            use_genetic_formulas: bool = True,
                            use_growth_pattern: bool = True,
                            target_ages: Optional[List[int]] = None) -> Dict:
        """
        오프셋 조절이 적용된 성장 곡선 예측
        
        Args:
            birth_date: 생년월일 (YYYY-MM-DD)
            gender: 성별 ('M' or 'F')
            current_height_cm: 현재 키 (cm)
            current_date: 현재 날짜 (YYYY-MM-DD, None이면 오늘)
            father_height_cm: 아버지 키 (cm)
            mother_height_cm: 어머니 키 (cm)
            height_history: 과거 키 기록
            country_code: 국가 코드
            use_genetic_formulas: 유전 공식 사용 여부
            use_growth_pattern: 성장 패턴 분석 사용 여부
            target_ages: 예측할 나이 목록 (None이면 사용 가능한 모든 나이)
        
        Returns:
            성장 곡선 예측 결과
        """
        from src.utils.age_calculator import calculate_age
        
        # 현재 나이 계산
        if current_date is None:
            current_date = datetime.now().strftime('%Y-%m-%d')
        
        _, current_age_years = calculate_age(birth_date, current_date)
        
        # 키 기록 처리 (가장 최근 키 사용)
        height_records = []
        if height_history:
            for record in height_history:
                record_date = record.get('date')
                record_height = record.get('height_cm')
                if record_date and record_height:
                    try:
                        _, record_age = calculate_age(birth_date, record_date)
                        height_records.append({
                            'age_years': record_age,
                            'height_cm': record_height
                        })
                    except:
                        pass
        
        # 현재 키 추가
        height_records.append({
            'age_years': current_age_years,
            'height_cm': current_height_cm
        })
        
        # 가장 최근 키 사용
        latest_record = max(height_records, key=lambda x: x['age_years'])
        base_age = latest_record['age_years']
        base_height = latest_record['height_cm']
        
        # 예측할 나이 목록
        if target_ages is None:
            target_ages = [age for age in self.available_ages if age > base_age]
        
        if not target_ages:
            # 현재 나이가 18세 이상이면 18세만 예측
            target_ages = [18] if base_age < 18 else []
        
        # 기본 성장 곡선 예측
        base_predictions = {}
        for target_age in target_ages:
            try:
                result = self.growth_curve_predictor.predict_at_age(
                    current_age_years=base_age,
                    current_height_cm=base_height,
                    target_age_years=target_age,
                    gender=gender
                )
                base_predictions[target_age] = result['predicted_height_cm']
            except Exception as e:
                print(f"⚠️  {target_age}세 예측 오류: {e}")
        
        # 각 나이별로 오프셋 조절 적용
        adjuster = HeightPredictionAdjuster(country_code=country_code)
        
        # 키 기록 형식 변환
        formatted_history = [
            {'age_years': r['age_years'], 'height_cm': r['height_cm']}
            for r in height_records
        ]
        
        adjusted_predictions = {}
        adjustments_detail = {}
        
        for target_age, base_pred in base_predictions.items():
            # 각 나이별로 오프셋 조절 적용
            # 18세는 전체 보정 적용, 그 이하는 나이에 따라 보정 강도 조절
            if target_age == 18:
                # 18세는 성인 키 예측과 동일하게 전체 보정 적용
                age_factor = 1.0
            else:
                # 나이가 적을수록 보정 영향이 작아짐 (성장 가능성이 크므로)
                age_factor = (target_age - base_age) / (18 - base_age) if base_age < 18 else 1.0
                age_factor = max(0.3, min(1.0, age_factor))  # 최소 30% 최대 100%
            
            adjustment_result = adjuster.calculate_final_prediction(
                base_prediction=base_pred,
                father_cm=father_height_cm,
                mother_cm=mother_height_cm,
                gender=gender,
                current_age=base_age,
                current_height=base_height,
                height_history=formatted_history,
                use_genetic_formulas=use_genetic_formulas,
                use_growth_pattern=use_growth_pattern
            )
            
            # 나이에 따라 보정 강도 조절
            adjusted_pred = base_pred + (adjustment_result['total_adjustment'] * age_factor)
            adjusted_predictions[target_age] = adjusted_pred
            
            adjustments_detail[target_age] = {
                'base': base_pred,
                'adjusted': adjusted_pred,
                'adjustment': adjustment_result['total_adjustment'] * age_factor
            }
        
        # 18세가 있으면 성인 키 예측과 일치시키고, 다른 나이들을 비례적으로 조정
        # 이렇게 하면 성장 곡선의 일관성이 유지됨
        if 18 in adjusted_predictions:
            # 성인 키 예측을 구하기 위해 enhanced predictor 사용
            from src.modeling.enhanced_predictor import EnhancedHeightPredictor
            adult_predictor = EnhancedHeightPredictor()
            try:
                adult_result = adult_predictor.predict(
                    birth_date=birth_date,
                    gender=gender,
                    current_height_cm=base_height,
                    current_date=current_date,
                    father_height_cm=father_height_cm,
                    mother_height_cm=mother_height_cm,
                    height_history=height_history,
                    country_code=country_code,
                    use_genetic_formulas=use_genetic_formulas,
                    use_growth_pattern=use_growth_pattern
                )
                adult_prediction = adult_result['predicted_height']
                
                # 18세 기본 예측값
                base_18 = base_predictions[18]
                
                # 비례 계수 계산 (18세 기본 대비 성인 키 예측의 비율)
                if base_18 > 0:
                    scale_factor = adult_prediction / base_18
                    
                    # 모든 예측값을 비례적으로 조정 (18세는 정확히 성인 키로)
                    for age in adjusted_predictions.keys():
                        if age == 18:
                            adjusted_predictions[age] = adult_prediction
                        else:
                            # 현재 나이부터 18세까지의 비율을 유지하면서 조정
                            base_age_pred = base_predictions[age]
                            base_18_pred = base_predictions[18]
                            
                            if base_18_pred > base_age_pred:
                                # 선형 보간: 현재 나이 예측과 18세 예측 사이의 비율 유지
                                ratio = (base_age_pred - base_height) / (base_18_pred - base_height) if (base_18_pred - base_height) > 0 else 0
                                adjusted_predictions[age] = base_height + (adult_prediction - base_height) * ratio
                            else:
                                # 기본 예측이 이상한 경우 (15세가 18세보다 크면) 비례 적용
                                adjusted_predictions[age] = base_age_pred * scale_factor
            except Exception as e:
                print(f"⚠️  성인 키 예측 통합 오류: {e}")
        
        # 성장 곡선 데이터 준비 (현재 + 예측)
        curve_data = []
        
        # 과거 기록 (있는 경우)
        for record in sorted(height_records, key=lambda x: x['age_years']):
            curve_data.append({
                'age': record['age_years'],
                'height': record['height_cm'],
                'type': 'actual'
            })
        
        # 예측 데이터
        for age in sorted(adjusted_predictions.keys()):
            curve_data.append({
                'age': age,
                'height': adjusted_predictions[age],
                'type': 'predicted'
            })
        
        return {
            'current': {
                'age_years': base_age,
                'height_cm': base_height
            },
            'predictions': {
                age: {
                    'predicted_height_cm': adjusted_predictions[age],
                    'base_prediction': adjustments_detail[age]['base'],
                    'adjustment': adjustments_detail[age]['adjustment'],
                    'growth_expected': adjusted_predictions[age] - base_height,
                    'years_until_target': age - base_age
                }
                for age in sorted(adjusted_predictions.keys())
            },
            'curve': {
                'ages': [d['age'] for d in curve_data],
                'heights': [d['height'] for d in curve_data],
                'types': [d['type'] for d in curve_data]
            },
            'adjustments': adjustments_detail,
            'settings': {
                'country_code': country_code,
                'use_genetic_formulas': use_genetic_formulas,
                'use_growth_pattern': use_growth_pattern
            }
        }

