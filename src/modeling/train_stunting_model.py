"""
Stunting Balita 데이터 기반 성장 패턴 모델 학습
나이, 성별, 현재 키를 기반으로 성인 키 예측
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
    """Stunting Balita 데이터 로드"""
    data_path = DATA_DIR / "stunting_balita_processed.csv"
    df = pd.read_csv(data_path)
    print(f"✅ 데이터 로드 완료: {len(df):,}행")
    return df

def prepare_features(df):
    """특성 준비 및 타겟 생성"""
    print("\n📊 데이터 특성 준비 중...")
    
    # 현재 데이터는 성인 키가 없으므로, 성장 곡선을 기반으로 추정
    # 실제 성장 곡선 패턴을 학습하기 위해 가상의 타겟 생성
    # 이는 성장 패턴 학습을 위한 근사치입니다
    
    # 성별별 평균 성인 키 추정 (WHO 표준 기반)
    adult_height_male = 175.0  # 남성 평균
    adult_height_female = 162.0  # 여성 평균
    
    # 현재 나이에서 성인까지의 성장 잠재력 추정
    # 나이에 따라 성장 가능성 감소
    df['growth_potential'] = np.where(
        df['age_months'] <= 12, 0.85,  # 1세 이하: 높은 성장 잠재력
        np.where(
            df['age_months'] <= 24, 0.75,  # 2세 이하
            np.where(
                df['age_months'] <= 36, 0.65,  # 3세 이하
                np.where(
                    df['age_months'] <= 48, 0.55,  # 4세 이하
                    np.where(
                        df['age_months'] <= 60, 0.45,  # 5세 이하
                        0.35  # 그 이상
                    )
                )
            )
        )
    )
    
    # 타겟: 예상 성인 키 (근사치)
    df['target_adult_height'] = np.where(
        df['gender'] == 'M',
        df['height_cm'] + (adult_height_male - df['height_cm']) * df['growth_potential'],
        df['height_cm'] + (adult_height_female - df['height_cm']) * df['growth_potential']
    )
    
    # 특성 선택
    features = ['age_months', 'age_years', 'height_cm', 'gender']
    X = df[features].copy()
    
    # 성별 원핫 인코딩
    X['gender_M'] = (X['gender'] == 'M').astype(int)
    X['gender_F'] = (X['gender'] == 'F').astype(int)
    X = X.drop('gender', axis=1)
    
    # 컬럼 순서 명시적 지정 (feature name 경고 방지)
    X = X[['age_months', 'age_years', 'height_cm', 'gender_M', 'gender_F']]
    
    y = df['target_adult_height']
    
    print(f"   특성: {list(X.columns)}")
    print(f"   타겟 통계:")
    print(f"      평균: {y.mean():.2f}cm")
    print(f"      표준편차: {y.std():.2f}cm")
    print(f"      범위: {y.min():.2f}cm ~ {y.max():.2f}cm")
    
    return X, y, df

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
            max_depth=15,
            random_state=42,
            n_jobs=-1
        ),
        'gradient_boosting': GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
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
            'val_r2': val_r2
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
    model_path = MODEL_DIR / f"stunting_{model_name}_model.pkl"
    joblib.dump(model, model_path)
    print(f"\n💾 모델 저장 완료: {model_path}")
    
    # 모델 메타데이터 저장
    metadata = {
        'model_type': 'stunting_growth_pattern',
        'algorithm': model_name,
        'features': ['age_months', 'age_years', 'height_cm', 'gender_M', 'gender_F'],
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
            'training_samples': results[model_name].get('train_samples', 0),
            'validation_samples': results[model_name].get('val_samples', 0)
        }
    }
    
    metadata_path = MODEL_DIR / f"stunting_{model_name}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"💾 메타데이터 저장 완료: {metadata_path}")
    
    return model_path, metadata_path

def main():
    """메인 함수"""
    print("="*60)
    print("Stunting Balita 성장 패턴 모델 학습")
    print("="*60)
    
    # 데이터 로드
    df = load_data()
    
    # 특성 준비
    X, y, df_full = prepare_features(df)
    
    # 모델 학습
    best_model, model_name, results = train_models(X, y)
    
    # 모델 저장
    model_path, metadata_path = save_model(best_model, model_name, results)
    
    print("\n" + "="*60)
    print("학습 완료!")
    print("="*60)
    print(f"\n📌 사용 모델: {model_name}")
    print(f"📌 모델 저장 위치: {model_path}")
    print(f"\n💡 이 모델은 나이, 성별, 현재 키를 기반으로 성인 키를 예측합니다.")

if __name__ == "__main__":
    main()

