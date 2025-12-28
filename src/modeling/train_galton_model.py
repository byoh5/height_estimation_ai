"""
Galton Families 데이터 기반 부모 키 모델 학습
부모 키, 성별을 기반으로 성인 키 예측
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models" / "saved_models"

def load_data():
    """Galton Families 데이터 로드"""
    data_path = DATA_DIR / "galton_families_processed.csv"
    df = pd.read_csv(data_path)
    print(f"✅ 데이터 로드 완료: {len(df):,}행")
    return df

def prepare_features(df):
    """특성 준비"""
    print("\n📊 데이터 특성 준비 중...")
    
    # 특성 선택: 부모 키 정보와 성별
    X = df[['father_height_cm', 'mother_height_cm', 'midparent_height_cm', 'gender']].copy()
    
    # 성별 원핫 인코딩
    X['gender_M'] = (X['gender'] == 'M').astype(int)
    X['gender_F'] = (X['gender'] == 'F').astype(int)
    X = X.drop('gender', axis=1)
    
    # 컬럼 순서 명시적 지정 (feature name 경고 방지)
    X = X[['father_height_cm', 'mother_height_cm', 'midparent_height_cm', 'gender_M', 'gender_F']]
    
    # 타겟: 성인 키
    y = df['adult_height_cm']
    
    print(f"   특성: {list(X.columns)}")
    print(f"   타겟 통계:")
    print(f"      평균: {y.mean():.2f}cm")
    print(f"      표준편차: {y.std():.2f}cm")
    print(f"      범위: {y.min():.2f}cm ~ {y.max():.2f}cm")
    
    return X, y

def train_models(X, y):
    """여러 모델 학습 및 비교"""
    print("\n🤖 모델 학습 중...")
    
    # 학습/검증 데이터 분리
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"   학습 데이터: {len(X_train):,}행")
    print(f"   검증 데이터: {len(X_val):,}행")
    
    models = {
        'random_forest': RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        ),
        'gradient_boosting': GradientBoostingRegressor(
            n_estimators=100,
            max_depth=4,
            random_state=42
        ),
        'linear_regression': LinearRegression()
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n   학습 중: {name}...")
        model.fit(X_train, y_train)
        
        # 예측
        y_pred_train = model.predict(X_train)
        y_pred_val = model.predict(X_val)
        
        # 평가
        train_mae = mean_absolute_error(y_train, y_pred_train)
        val_mae = mean_absolute_error(y_val, y_pred_val)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        val_rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))
        train_r2 = r2_score(y_train, y_pred_train)
        val_r2 = r2_score(y_val, y_pred_val)
        
        results[name] = {
            'model': model,
            'train_mae': train_mae,
            'val_mae': val_mae,
            'train_rmse': train_rmse,
            'val_rmse': val_rmse,
            'train_r2': train_r2,
            'val_r2': val_r2,
            'train_samples': len(X_train),
            'val_samples': len(X_val)
        }
        
        print(f"      Train MAE: {train_mae:.2f}cm, RMSE: {train_rmse:.2f}cm, R²: {train_r2:.4f}")
        print(f"      Val MAE: {val_mae:.2f}cm, RMSE: {val_rmse:.2f}cm, R²: {val_r2:.4f}")
    
    # 최고 성능 모델 선택
    best_model_name = min(results.keys(), key=lambda x: results[x]['val_mae'])
    best_model = results[best_model_name]['model']
    
    print(f"\n✅ 최고 성능 모델: {best_model_name}")
    print(f"   검증 MAE: {results[best_model_name]['val_mae']:.2f}cm")
    
    return best_model, best_model_name, results

def save_model(model, model_name, results):
    """모델 저장"""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    # 모델 저장
    model_path = MODEL_DIR / f"galton_{model_name}_model.pkl"
    joblib.dump(model, model_path)
    print(f"\n💾 모델 저장 완료: {model_path}")
    
    # 모델 메타데이터 저장
    metadata = {
        'model_type': 'galton_parental_height',
        'algorithm': model_name,
        'features': ['father_height_cm', 'mother_height_cm', 'midparent_height_cm', 'gender_M', 'gender_F'],
        'target': 'adult_height_cm',
        'metrics': {
            'train_mae': float(results[model_name]['train_mae']),
            'val_mae': float(results[model_name]['val_mae']),
            'train_rmse': float(results[model_name]['train_rmse']),
            'val_rmse': float(results[model_name]['val_rmse']),
            'train_r2': float(results[model_name]['train_r2']),
            'val_r2': float(results[model_name]['val_r2'])
        },
        'data_info': {
            'training_samples': results[model_name]['train_samples'],
            'validation_samples': results[model_name]['val_samples']
        }
    }
    
    metadata_path = MODEL_DIR / f"galton_{model_name}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"💾 메타데이터 저장 완료: {metadata_path}")
    
    return model_path, metadata_path

def main():
    """메인 함수"""
    print("="*60)
    print("Galton Families 부모 키 기반 모델 학습")
    print("="*60)
    
    # 데이터 로드
    df = load_data()
    
    # 특성 준비
    X, y = prepare_features(df)
    
    # 모델 학습
    best_model, model_name, results = train_models(X, y)
    
    # 모델 저장
    model_path, metadata_path = save_model(best_model, model_name, results)
    
    print("\n" + "="*60)
    print("학습 완료!")
    print("="*60)
    print(f"\n📌 사용 모델: {model_name}")
    print(f"📌 모델 저장 위치: {model_path}")
    print(f"\n💡 이 모델은 부모 키와 성별을 기반으로 성인 키를 예측합니다.")

if __name__ == "__main__":
    main()

