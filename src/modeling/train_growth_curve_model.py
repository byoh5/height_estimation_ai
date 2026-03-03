"""
성장 곡선 예측 모델 학습
특정 나이의 키를 예측할 수 있는 모델
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models" / "saved_models"

def load_data():
    """Stunting Balita 데이터 로드"""
    data_path = DATA_DIR / "stunting_balita_processed.csv"
    df = pd.read_csv(data_path)
    print(f"✅ 데이터 로드 완료: {len(df):,}행")
    return df

def prepare_features_for_age_prediction(df, target_age_years):
    """
    특정 나이의 키 예측을 위한 특성 준비
    
    Args:
        df: 데이터프레임
        target_age_years: 예측할 목표 나이 (세)
    """
    print(f"\n📊 {target_age_years}세 키 예측 모델 특성 준비 중...")
    
    # 현재 나이가 목표 나이보다 작은 데이터만 사용 (미래 예측)
    df_valid = df[df['age_years'] < target_age_years].copy()
    
    if len(df_valid) == 0:
        print(f"⚠️  {target_age_years}세보다 어린 데이터가 없습니다.")
        return None, None, None
    
    print(f"   사용 가능한 데이터: {len(df_valid):,}행")
    
    # 특성: 현재 나이, 현재 키, 성별, 목표 나이까지의 남은 시간
    df_valid['years_to_target'] = target_age_years - df_valid['age_years']
    df_valid['months_to_target'] = df_valid['years_to_target'] * 12
    
    # 성별별 평균 성장률을 기반으로 목표 키 추정 (간단한 근사)
    # 실제로는 이 값을 모델이 학습해야 함
    # 여기서는 타겟 생성용 근사치만 사용
    gender_mean_growth = df.groupby('gender')['height_cm'].mean()
    
    # 나이에 따른 성장 잠재력 (간단한 추정)
    growth_rate = 6.0  # 연간 평균 성장률 (cm/year)
    df_valid['estimated_target_height'] = (
        df_valid['height_cm'] + 
        df_valid['years_to_target'] * growth_rate * 
        (1.0 - df_valid['age_years'] / 18.0)  # 나이가 많을수록 성장률 감소
    )
    
    # 특성 선택
    X = df_valid[['age_years', 'age_months', 'height_cm', 'gender', 'years_to_target', 'months_to_target']].copy()
    
    # 성별 원핫 인코딩
    X['gender_M'] = (X['gender'] == 'M').astype(int)
    X['gender_F'] = (X['gender'] == 'F').astype(int)
    X = X.drop('gender', axis=1)
    
    # 컬럼 순서 명시적 지정 및 DataFrame으로 변환 (feature name 경고 방지)
    X = X[['age_years', 'age_months', 'height_cm', 'years_to_target', 'months_to_target', 'gender_M', 'gender_F']]
    X.columns = ['age_years', 'age_months', 'height_cm', 'years_to_target', 'months_to_target', 'gender_M', 'gender_F']
    
    y = df_valid['estimated_target_height']
    
    print(f"   특성: {list(X.columns)}")
    print(f"   타겟 통계:")
    print(f"      평균: {y.mean():.2f}cm")
    print(f"      표준편차: {y.std():.2f}cm")
    
    return X, y, df_valid

def train_multiple_age_models(df):
    """
    여러 나이별 모델 학습 (5세, 10세, 15세, 18세)
    """
    target_ages = [5, 10, 15, 18]
    models_dict = {}
    
    for target_age in target_ages:
        print(f"\n{'='*60}")
        print(f"{target_age}세 키 예측 모델 학습")
        print(f"{'='*60}")
        
        X, y, df_valid = prepare_features_for_age_prediction(df, target_age)
        
        if X is None:
            continue
        
        # 학습/검증 데이터 분리
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"\n   학습 데이터: {len(X_train):,}행")
        print(f"   검증 데이터: {len(X_val):,}행")
        
        # 모델 학습
        model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42,
            learning_rate=0.1
        )
        
        model.fit(X_train, y_train)
        
        # 예측 및 평가
        y_pred_train = model.predict(X_train)
        y_pred_val = model.predict(X_val)
        
        train_mae = mean_absolute_error(y_train, y_pred_train)
        val_mae = mean_absolute_error(y_val, y_pred_val)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        val_rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))
        train_r2 = r2_score(y_train, y_pred_train)
        val_r2 = r2_score(y_val, y_pred_val)
        
        print(f"\n   Train MAE: {train_mae:.2f}cm, RMSE: {train_rmse:.2f}cm, R²: {train_r2:.4f}")
        print(f"   Val MAE: {val_mae:.2f}cm, RMSE: {val_rmse:.2f}cm, R²: {val_r2:.4f}")
        
        models_dict[target_age] = {
            'model': model,
            'metrics': {
                'train_mae': train_mae,
                'val_mae': val_mae,
                'train_rmse': train_rmse,
                'val_rmse': val_rmse,
                'train_r2': train_r2,
                'val_r2': val_r2
            },
            'train_samples': len(X_train),
            'val_samples': len(X_val)
        }
        
        # 모델 저장
        model_path = MODEL_DIR / f"growth_curve_age_{target_age}_model.pkl"
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)
        
        # 메타데이터 저장
        metadata = {
            'model_type': 'growth_curve_age_prediction',
            'target_age_years': target_age,
            'algorithm': 'gradient_boosting',
            'features': list(X.columns),
            'target': f'height_at_{target_age}_years',
            'metrics': {
                'train_mae': float(train_mae),
                'val_mae': float(val_mae),
                'train_rmse': float(train_rmse),
                'val_rmse': float(val_rmse),
                'train_r2': float(train_r2),
                'val_r2': float(val_r2)
            },
            'data_info': {
                'training_samples': len(X_train),
                'validation_samples': len(X_val)
            }
        }
        
        metadata_path = MODEL_DIR / f"growth_curve_age_{target_age}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"   💾 모델 저장: {model_path}")
    
    return models_dict

def main():
    """메인 함수"""
    print("="*60)
    print("성장 곡선 예측 모델 학습")
    print("="*60)
    
    # 데이터 로드
    df = load_data()
    
    # 여러 나이별 모델 학습
    models_dict = train_multiple_age_models(df)
    
    print("\n" + "="*60)
    print("학습 완료!")
    print("="*60)
    print(f"\n✅ 학습된 나이별 모델: {list(models_dict.keys())}세")
    print("\n💡 이 모델들은 현재 나이와 키를 기반으로 특정 나이의 키를 예측합니다.")

if __name__ == "__main__":
    main()
