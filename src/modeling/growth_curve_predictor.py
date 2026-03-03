"""
성장 곡선 예측기
특정 나이의 키를 예측하는 모델
"""

import numpy as np
import pandas as pd
from pathlib import Path
import joblib
import json
from typing import Dict, Optional, List
from src.utils.runtime_paths import get_model_dir

PROJECT_ROOT = Path(__file__).parent.parent.parent
MODEL_DIR = get_model_dir()

class GrowthCurvePredictor:
    """특정 나이의 키 예측 모델"""
    
    def __init__(self):
        self.models = {}
        self.metadata = {}
        self.available_ages = []
        self._load_models()
    
    def _load_models(self):
        """학습된 나이별 모델 로드"""
        growth_models = list(MODEL_DIR.glob("growth_curve_age_*_model.pkl"))
        
        for model_path in growth_models:
            # 나이 추출 (예: growth_curve_age_10_model.pkl → 10)
            age_str = model_path.stem.replace('growth_curve_age_', '').replace('_model', '')
            try:
                age = int(age_str)
                self.models[age] = joblib.load(model_path)
                self.available_ages.append(age)
                
                # 메타데이터 로드
                metadata_path = MODEL_DIR / model_path.stem.replace('_model', '_metadata.json')
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        self.metadata[age] = json.load(f)
                
                print(f"✅ {age}세 모델 로드: {model_path.name}")
            except ValueError:
                continue
        
        self.available_ages.sort()
        print(f"\n📊 사용 가능한 나이: {self.available_ages}세")
    
    def _prepare_features(self, current_age_years: float, current_height_cm: float,
                         target_age_years: float, gender: str) -> pd.DataFrame:
        """특성 준비 (DataFrame 형태로 반환하여 feature name 경고 방지)"""
        current_age_months = current_age_years * 12
        years_to_target = target_age_years - current_age_years
        months_to_target = years_to_target * 12
        
        gender_M = 1 if gender.upper() == 'M' else 0
        gender_F = 1 if gender.upper() == 'F' else 0
        
        return pd.DataFrame({
            'age_years': [current_age_years],
            'age_months': [current_age_months],
            'height_cm': [current_height_cm],
            'years_to_target': [years_to_target],
            'months_to_target': [months_to_target],
            'gender_M': [gender_M],
            'gender_F': [gender_F]
        })
    
    def predict_at_age(self, 
                      current_age_years: float,
                      current_height_cm: float,
                      target_age_years: float,
                      gender: str) -> Dict:
        """
        특정 나이의 키 예측
        
        Args:
            current_age_years: 현재 나이 (세)
            current_height_cm: 현재 키 (cm)
            target_age_years: 예측할 나이 (세)
            gender: 성별 ('M' or 'F')
        
        Returns:
            예측 결과 딕셔너리
        """
        # 입력 검증
        if target_age_years <= current_age_years:
            raise ValueError(f"목표 나이({target_age_years}세)는 현재 나이({current_age_years}세)보다 커야 합니다.")
        
        if current_age_years < 0 or current_age_years > 18:
            raise ValueError(f"현재 나이는 0-18세 사이여야 합니다.")
        
        if target_age_years > 18:
            print(f"⚠️  목표 나이({target_age_years}세)가 18세를 초과합니다. 18세 모델을 사용합니다.")
            target_age_years = 18
        
        # 가장 가까운 학습된 모델 찾기
        available_target = min(self.available_ages, key=lambda x: abs(x - target_age_years))
        
        if abs(available_target - target_age_years) > 3:
            print(f"⚠️  목표 나이({target_age_years}세)에 가장 가까운 모델({available_target}세)을 사용합니다.")
        
        model = self.models[available_target]
        
        # 특성 준비 (원래 목표 나이 사용)
        X = self._prepare_features(current_age_years, current_height_cm, target_age_years, gender)
        
        # 예측
        predicted_height = model.predict(X)[0]
        
        result = {
            'current_age_years': current_age_years,
            'current_height_cm': current_height_cm,
            'target_age_years': target_age_years,
            'predicted_height_cm': float(predicted_height),
            'model_used_age': available_target,
            'gender': gender,
            'growth_expected': float(predicted_height - current_height_cm),
            'years_until_target': float(target_age_years - current_age_years)
        }
        
        if available_target in self.metadata:
            result['model_metrics'] = {
                'val_mae': self.metadata[available_target].get('metrics', {}).get('val_mae')
            }
        
        return result
    
    def predict_growth_curve(self,
                            current_age_years: float,
                            current_height_cm: float,
                            gender: str,
                            target_ages: Optional[List[int]] = None) -> Dict:
        """
        여러 나이의 키를 한번에 예측 (성장 곡선)
        
        Args:
            current_age_years: 현재 나이 (세)
            current_height_cm: 현재 키 (cm)
            gender: 성별 ('M' or 'F')
            target_ages: 예측할 나이 목록 (기본값: 사용 가능한 모든 나이)
        
        Returns:
            각 나이별 예측 결과 딕셔너리
        """
        if target_ages is None:
            target_ages = [age for age in self.available_ages if age > current_age_years]
        
        if not target_ages:
            raise ValueError("예측할 수 있는 미래 나이가 없습니다.")
        
        results = {}
        for target_age in target_ages:
            try:
                result = self.predict_at_age(
                    current_age_years=current_age_years,
                    current_height_cm=current_height_cm,
                    target_age_years=target_age,
                    gender=gender
                )
                results[target_age] = result
            except Exception as e:
                print(f"⚠️  {target_age}세 예측 실패: {e}")
        
        return {
            'current_info': {
                'age_years': current_age_years,
                'height_cm': current_height_cm,
                'gender': gender
            },
            'predictions': results,
            'growth_curve': {
                'ages': list(results.keys()),
                'heights': [results[age]['predicted_height_cm'] for age in results.keys()]
            }
        }
    
    def get_available_ages(self) -> List[int]:
        """사용 가능한 예측 나이 목록 반환"""
        return self.available_ages.copy()

def main():
    """테스트용 메인 함수"""
    print("="*60)
    print("성장 곡선 예측 모델 테스트")
    print("="*60)
    
    predictor = GrowthCurvePredictor()
    
    if not predictor.models:
        print("❌ 모델이 없습니다. 먼저 모델을 학습시켜주세요.")
        return
    
    print(f"\n📊 사용 가능한 나이: {predictor.get_available_ages()}세")
    
    # 예제 예측
    print("\n🔮 예측 예제:")
    
    print("\n1. 5세 아이의 10세 때 키 예측:")
    result1 = predictor.predict_at_age(
        current_age_years=5,
        current_height_cm=110,
        target_age_years=10,
        gender='M'
    )
    print(f"   현재: {result1['current_age_years']}세, {result1['current_height_cm']}cm")
    print(f"   예측: {result1['target_age_years']}세에 {result1['predicted_height_cm']:.1f}cm")
    print(f"   예상 성장: {result1['growth_expected']:.1f}cm")
    
    print("\n2. 성장 곡선 예측 (여러 나이):")
    result2 = predictor.predict_growth_curve(
        current_age_years=8,
        current_height_cm=130,
        gender='F'
    )
    print(f"   현재: {result2['current_info']['age_years']}세, {result2['current_info']['height_cm']}cm")
    print(f"   예측 결과:")
    for age, pred in result2['predictions'].items():
        print(f"      {age}세: {pred['predicted_height_cm']:.1f}cm")

if __name__ == "__main__":
    main()
