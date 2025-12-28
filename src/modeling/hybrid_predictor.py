"""
하이브리드 예측 모델
입력 데이터의 완전도에 따라 최적의 모델을 선택하여 예측
"""

import numpy as np
import pandas as pd
from pathlib import Path
import joblib
import json
from typing import Dict, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent
MODEL_DIR = PROJECT_ROOT / "models" / "saved_models"

class HybridHeightPredictor:
    """하이브리드 키 예측 모델"""
    
    def __init__(self):
        self.stunting_model = None
        self.galton_model = None
        self.stunting_metadata = None
        self.galton_metadata = None
        self._load_models()
    
    def _load_models(self):
        """학습된 모델 로드"""
        # Stunting 모델 찾기
        stunting_files = list(MODEL_DIR.glob("stunting_*_model.pkl"))
        if stunting_files:
            self.stunting_model = joblib.load(stunting_files[0])
            metadata_file = MODEL_DIR / stunting_files[0].stem.replace('_model', '_metadata.json')
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    self.stunting_metadata = json.load(f)
            print(f"✅ Stunting 모델 로드: {stunting_files[0].name}")
        else:
            print("⚠️  Stunting 모델을 찾을 수 없습니다.")
        
        # Galton 모델 찾기
        galton_files = list(MODEL_DIR.glob("galton_*_model.pkl"))
        if galton_files:
            self.galton_model = joblib.load(galton_files[0])
            metadata_file = MODEL_DIR / galton_files[0].stem.replace('_model', '_metadata.json')
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    self.galton_metadata = json.load(f)
            print(f"✅ Galton 모델 로드: {galton_files[0].name}")
        else:
            print("⚠️  Galton 모델을 찾을 수 없습니다.")
    
    def _prepare_stunting_features(self, age_months: float, age_years: float, 
                                   height_cm: float, gender: str) -> np.ndarray:
        """Stunting 모델용 특성 준비"""
        gender_M = 1 if gender.upper() == 'M' else 0
        gender_F = 1 if gender.upper() == 'F' else 0
        return np.array([[age_months, age_years, height_cm, gender_M, gender_F]])
    
    def _prepare_galton_features(self, father_height_cm: float, mother_height_cm: float,
                                 gender: str) -> np.ndarray:
        """Galton 모델용 특성 준비"""
        midparent_height = (father_height_cm + mother_height_cm) / 2
        gender_M = 1 if gender.upper() == 'M' else 0
        gender_F = 1 if gender.upper() == 'F' else 0
        return np.array([[father_height_cm, mother_height_cm, midparent_height, gender_M, gender_F]])
    
    def predict(self, 
                age_months: Optional[float] = None,
                age_years: Optional[float] = None,
                height_cm: float = None,
                gender: str = None,
                father_height_cm: Optional[float] = None,
                mother_height_cm: Optional[float] = None) -> Dict:
        """
        하이브리드 예측 수행
        
        입력 데이터의 완전도에 따라:
        1. 부모 키 + 성별이 모두 있으면 → Galton 모델 (가장 정확)
        2. 나이 + 현재 키 + 성별이 있으면 → Stunting 모델
        3. 둘 다 있으면 → 가중 평균 (부모 키 모델에 더 높은 가중치)
        
        Args:
            age_months: 나이 (개월)
            age_years: 나이 (세)
            height_cm: 현재 키 (cm)
            gender: 성별 ('M' or 'F')
            father_height_cm: 아버지 키 (cm)
            mother_height_cm: 어머니 키 (cm)
        
        Returns:
            예측 결과 딕셔너리
        """
        results = {
            'predicted_height': None,
            'model_used': [],
            'confidence': 'low',
            'details': {}
        }
        
        # 입력 검증
        if gender is None:
            raise ValueError("성별(gender)은 필수 입력입니다.")
        
        has_parents = father_height_cm is not None and mother_height_cm is not None
        has_growth_data = height_cm is not None and (age_months is not None or age_years is not None)
        
        # 나이 통일 (age_years가 있으면 age_months 계산)
        if age_years is not None and age_months is None:
            age_months = age_years * 12
        elif age_months is None:
            age_months = None
        
        predictions = []
        weights = []
        
        # 1. 부모 키 기반 예측 (Galton 모델)
        if has_parents and self.galton_model is not None:
            try:
                X_galton = self._prepare_galton_features(father_height_cm, mother_height_cm, gender)
                pred_galton = self.galton_model.predict(X_galton)[0]
                predictions.append(pred_galton)
                weights.append(0.7)  # 부모 키 모델에 높은 가중치
                results['model_used'].append('galton')
                results['details']['galton_prediction'] = float(pred_galton)
                results['confidence'] = 'high'
            except Exception as e:
                print(f"⚠️  Galton 모델 예측 오류: {e}")
        
        # 2. 성장 패턴 기반 예측 (Stunting 모델)
        if has_growth_data and self.stunting_model is not None:
            try:
                if age_months is None:
                    raise ValueError("나이 정보가 필요합니다.")
                X_stunting = self._prepare_stunting_features(age_months, age_years or (age_months/12), 
                                                           height_cm, gender)
                pred_stunting = self.stunting_model.predict(X_stunting)[0]
                predictions.append(pred_stunting)
                weights.append(0.3 if has_parents else 1.0)  # 부모 키가 없으면 단독 사용
                results['model_used'].append('stunting')
                results['details']['stunting_prediction'] = float(pred_stunting)
                if results['confidence'] != 'high':
                    results['confidence'] = 'medium'
            except Exception as e:
                print(f"⚠️  Stunting 모델 예측 오류: {e}")
        
        # 예측 결과 결합
        if predictions:
            # 가중 평균
            weights = np.array(weights)
            weights = weights / weights.sum()  # 정규화
            final_prediction = np.average(predictions, weights=weights)
            
            results['predicted_height'] = float(final_prediction)
            results['details']['weighted_average'] = True
            results['details']['weights'] = {model: float(w) for model, w in zip(results['model_used'], weights)}
        else:
            raise ValueError("예측할 수 있는 충분한 정보가 없습니다.")
        
        # 신뢰도 조정
        if len(predictions) == 2 and has_parents and has_growth_data:
            results['confidence'] = 'very_high'  # 두 모델 모두 사용
        elif has_parents:
            results['confidence'] = 'high'
        elif has_growth_data:
            results['confidence'] = 'medium'
        
        return results
    
    def get_model_info(self) -> Dict:
        """모델 정보 반환"""
        info = {
            'stunting_model': None,
            'galton_model': None
        }
        
        if self.stunting_metadata:
            info['stunting_model'] = {
                'algorithm': self.stunting_metadata.get('algorithm'),
                'val_mae': self.stunting_metadata.get('metrics', {}).get('val_mae'),
                'features': self.stunting_metadata.get('features')
            }
        
        if self.galton_metadata:
            info['galton_model'] = {
                'algorithm': self.galton_metadata.get('algorithm'),
                'val_mae': self.galton_metadata.get('metrics', {}).get('val_mae'),
                'features': self.galton_metadata.get('features')
            }
        
        return info

def main():
    """테스트용 메인 함수"""
    print("="*60)
    print("하이브리드 예측 모델 테스트")
    print("="*60)
    
    predictor = HybridHeightPredictor()
    
    # 모델 정보 출력
    info = predictor.get_model_info()
    print("\n📊 모델 정보:")
    print(f"   Stunting 모델: {info['stunting_model']}")
    print(f"   Galton 모델: {info['galton_model']}")
    
    # 예제 예측
    print("\n🔮 예측 예제:")
    
    # 예제 1: 모든 정보가 있는 경우
    print("\n1. 모든 정보가 있는 경우 (부모 키 + 성장 데이터):")
    result1 = predictor.predict(
        age_years=10,
        age_months=120,
        height_cm=140,
        gender='M',
        father_height_cm=175,
        mother_height_cm=162
    )
    print(f"   예측 키: {result1['predicted_height']:.2f}cm")
    print(f"   사용 모델: {', '.join(result1['model_used'])}")
    print(f"   신뢰도: {result1['confidence']}")
    
    # 예제 2: 부모 키만 있는 경우
    print("\n2. 부모 키만 있는 경우:")
    result2 = predictor.predict(
        gender='F',
        father_height_cm=175,
        mother_height_cm=162
    )
    print(f"   예측 키: {result2['predicted_height']:.2f}cm")
    print(f"   사용 모델: {', '.join(result2['model_used'])}")
    print(f"   신뢰도: {result2['confidence']}")
    
    # 예제 3: 성장 데이터만 있는 경우
    print("\n3. 성장 데이터만 있는 경우:")
    result3 = predictor.predict(
        age_years=8,
        height_cm=130,
        gender='M'
    )
    print(f"   예측 키: {result3['predicted_height']:.2f}cm")
    print(f"   사용 모델: {', '.join(result3['model_used'])}")
    print(f"   신뢰도: {result3['confidence']}")

if __name__ == "__main__":
    main()

