#!/usr/bin/env python3
"""
실제 데이터로 예측 모델 검증 스크립트
학습된 모델이 실제 데이터에서 얼마나 정확한지 측정
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.modeling.enhanced_predictor import EnhancedHeightPredictor
from src.modeling.growth_curve_predictor import GrowthCurvePredictor
import joblib
import json

def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def validate_galton_model():
    """Galton 모델 검증 (부모 키 → 성인 키)"""
    print_section("Galton 모델 검증 (부모 키 기반 성인 키 예측)")
    
    # 데이터 로드
    data_path = PROJECT_ROOT / "data" / "processed" / "galton_families_processed.csv"
    df = pd.read_csv(data_path)
    
    print(f"📊 데이터 로드: {len(df)}행")
    print(f"   남아: {len(df[df['gender'] == 'M'])}명")
    print(f"   여아: {len(df[df['gender'] == 'F'])}명")
    
    # 모델 로드
    model_dir = PROJECT_ROOT / "models" / "saved_models"
    model_file = list(model_dir.glob("galton_*_model.pkl"))[0]
    model = joblib.load(model_file)
    
    metadata_file = model_dir / model_file.stem.replace('_model', '_metadata.json')
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        print(f"\n📋 모델 정보:")
        print(f"   알고리즘: {metadata.get('algorithm', 'N/A')}")
        val_mae = metadata.get('val_mae')
        if val_mae is not None:
            print(f"   학습 시 검증 MAE: {val_mae:.2f}cm")
        else:
            print(f"   학습 시 검증 MAE: N/A")
    
    # 특성 준비
    X = df[['father_height_cm', 'mother_height_cm', 'midparent_height_cm']].copy()
    X['gender_M'] = (df['gender'] == 'M').astype(int)
    X['gender_F'] = (df['gender'] == 'F').astype(int)
    X = X[['father_height_cm', 'mother_height_cm', 'midparent_height_cm', 'gender_M', 'gender_F']].values
    
    y_true = df['adult_height_cm'].values
    
    # 예측
    y_pred = model.predict(X)
    
    # 평가
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    print(f"\n📈 검증 결과:")
    print(f"   MAE (평균 절대 오차): {mae:.2f}cm")
    print(f"   RMSE (평균 제곱근 오차): {rmse:.2f}cm")
    print(f"   R² (결정계수): {r2:.4f}")
    
    # 오차 분포
    errors = np.abs(y_true - y_pred)
    print(f"\n📊 오차 분포:")
    print(f"   평균 오차: {errors.mean():.2f}cm")
    print(f"   중앙값 오차: {np.median(errors):.2f}cm")
    print(f"   최대 오차: {errors.max():.2f}cm")
    print(f"   표준편차: {errors.std():.2f}cm")
    
    # 정확도 범위별 분포
    within_5cm = (errors <= 5).sum()
    within_10cm = (errors <= 10).sum()
    print(f"\n🎯 정확도:")
    print(f"   ±5cm 이내: {within_5cm}/{len(df)} ({within_5cm/len(df)*100:.1f}%)")
    print(f"   ±10cm 이내: {within_10cm}/{len(df)} ({within_10cm/len(df)*100:.1f}%)")
    
    # 성별별 성능
    print(f"\n👥 성별별 성능:")
    for gender in ['M', 'F']:
        mask = df['gender'] == gender
        if mask.sum() > 0:
            gender_mae = mean_absolute_error(y_true[mask], y_pred[mask])
            print(f"   {gender} ({mask.sum()}명): MAE {gender_mae:.2f}cm")
    
    return {
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'within_5cm': within_5cm / len(df),
        'within_10cm': within_10cm / len(df)
    }

def validate_growth_curve_model():
    """성장 곡선 모델 검증"""
    print_section("성장 곡선 모델 검증 (나이별 키 예측)")
    
    # 데이터 로드
    data_path = PROJECT_ROOT / "data" / "processed" / "stunting_balita_processed.csv"
    df = pd.read_csv(data_path)
    
    print(f"📊 데이터 로드: {len(df)}행")
    print(f"   나이 범위: {df['age_years'].min():.1f}세 ~ {df['age_years'].max():.1f}세")
    print(f"   키 범위: {df['height_cm'].min():.1f}cm ~ {df['height_cm'].max():.1f}cm")
    
    # 모델 로드
    predictor = GrowthCurvePredictor()
    available_ages = predictor.get_available_ages()
    print(f"\n📋 사용 가능한 모델: {available_ages}세")
    
    results = {}
    
    # 각 나이별 모델 검증
    for target_age in available_ages:
        print(f"\n🔍 {target_age}세 예측 모델 검증:")
        
        # 해당 나이의 데이터 필터링
        # 현재 나이가 target_age보다 작은 데이터만 사용
        # (예: 3세 데이터로 5세 예측 검증)
        if target_age == 5:
            # 5세 모델: 0-3세 데이터로 5세 예측 검증
            test_data = df[(df['age_years'] >= 0) & (df['age_years'] < 3)].copy()
        elif target_age == 10:
            # 10세 모델: 3-7세 데이터로 10세 예측 검증
            test_data = df[(df['age_years'] >= 3) & (df['age_years'] < 7)].copy()
        elif target_age == 15:
            # 15세 모델: 7-12세 데이터로 15세 예측 검증
            test_data = df[(df['age_years'] >= 7) & (df['age_years'] < 12)].copy()
        elif target_age == 18:
            # 18세 모델: 12-15세 데이터로 18세 예측 검증
            test_data = df[(df['age_years'] >= 12) & (df['age_years'] < 15)].copy()
        else:
            continue
        
        if len(test_data) == 0:
            print(f"   ⚠️  검증 데이터 없음")
            continue
        
        print(f"   검증 데이터: {len(test_data)}행")
        
        # 실제 target_age의 키 데이터가 필요하지만, 
        # Stunting 데이터는 0-5세만 있으므로 직접 검증 불가
        # 대신 모델이 정상 작동하는지만 확인
        try:
            # 샘플링하여 테스트
            sample_size = min(100, len(test_data))
            test_sample = test_data.sample(n=sample_size, random_state=42)
            
            predictions = []
            for _, row in test_sample.iterrows():
                try:
                    result = predictor.predict_at_age(
                        current_age_years=row['age_years'],
                        current_height_cm=row['height_cm'],
                        target_age_years=target_age,
                        gender=row['gender']
                    )
                    predictions.append(result['predicted_height_cm'])
                except:
                    pass
            
            if len(predictions) > 0:
                print(f"   ✅ 예측 성공: {len(predictions)}개")
                print(f"   예측 범위: {min(predictions):.1f}cm ~ {max(predictions):.1f}cm")
                print(f"   평균 예측: {np.mean(predictions):.1f}cm")
            else:
                print(f"   ⚠️  예측 실패")
                
        except Exception as e:
            print(f"   ❌ 검증 오류: {e}")
    
    return results

def validate_enhanced_predictor():
    """향상된 예측기 검증"""
    print_section("향상된 예측기 검증 (통합 모델)")
    
    predictor = EnhancedHeightPredictor()
    
    # Galton 데이터로 검증 (부모 키 + 성인 키가 있는 경우)
    data_path = PROJECT_ROOT / "data" / "processed" / "galton_families_processed.csv"
    df = pd.read_csv(data_path)
    
    print(f"📊 검증 데이터: {len(df)}행")
    
    predictions = []
    actuals = []
    errors_list = []
    
    # 샘플링하여 검증 (전체 데이터는 시간이 오래 걸림)
    sample_size = min(200, len(df))
    test_sample = df.sample(n=sample_size, random_state=42)
    
    print(f"   테스트 샘플: {sample_size}개")
    
    for idx, row in test_sample.iterrows():
        try:
            result = predictor.predict(
                gender=row['gender'],
                father_height_cm=row['father_height_cm'],
                mother_height_cm=row['mother_height_cm']
            )
            
            predictions.append(result['predicted_height'])
            actuals.append(row['adult_height_cm'])
            errors_list.append(abs(result['predicted_height'] - row['adult_height_cm']))
        except Exception as e:
            print(f"   ⚠️  예측 실패 (행 {idx}): {e}")
    
    if len(predictions) > 0:
        mae = mean_absolute_error(actuals, predictions)
        rmse = np.sqrt(mean_squared_error(actuals, predictions))
        r2 = r2_score(actuals, predictions)
        
        print(f"\n📈 검증 결과:")
        print(f"   테스트 샘플: {len(predictions)}개")
        print(f"   MAE: {mae:.2f}cm")
        print(f"   RMSE: {rmse:.2f}cm")
        print(f"   R²: {r2:.4f}")
        
        errors = np.array(errors_list)
        within_5cm = (errors <= 5).sum()
        within_10cm = (errors <= 10).sum()
        
        print(f"\n🎯 정확도:")
        print(f"   ±5cm 이내: {within_5cm}/{len(predictions)} ({within_5cm/len(predictions)*100:.1f}%)")
        print(f"   ±10cm 이내: {within_10cm}/{len(predictions)} ({within_10cm/len(predictions)*100:.1f}%)")
        
        print(f"\n📊 오차 분포:")
        print(f"   평균: {errors.mean():.2f}cm")
        print(f"   중앙값: {np.median(errors):.2f}cm")
        print(f"   최대: {errors.max():.2f}cm")
        
        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'within_5cm': within_5cm / len(predictions),
            'within_10cm': within_10cm / len(predictions)
        }
    else:
        print("   ❌ 검증 실패")
        return None

def main():
    """메인 함수"""
    print("="*70)
    print("  실제 데이터로 예측 모델 검증")
    print("="*70)
    
    results = {}
    
    # 각 모델 검증
    try:
        results['galton'] = validate_galton_model()
    except Exception as e:
        print(f"\n❌ Galton 모델 검증 실패: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        results['growth_curve'] = validate_growth_curve_model()
    except Exception as e:
        print(f"\n❌ 성장 곡선 모델 검증 실패: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        results['enhanced'] = validate_enhanced_predictor()
    except Exception as e:
        print(f"\n❌ 향상된 예측기 검증 실패: {e}")
        import traceback
        traceback.print_exc()
    
    # 결과 요약
    print_section("검증 결과 요약")
    
    if 'galton' in results and results['galton']:
        print("\n📊 Galton 모델:")
        print(f"   MAE: {results['galton']['mae']:.2f}cm")
        print(f"   R²: {results['galton']['r2']:.4f}")
        print(f"   ±5cm 정확도: {results['galton']['within_5cm']*100:.1f}%")
        print(f"   ±10cm 정확도: {results['galton']['within_10cm']*100:.1f}%")
    
    if 'enhanced' in results and results['enhanced']:
        print("\n📊 향상된 예측기:")
        print(f"   MAE: {results['enhanced']['mae']:.2f}cm")
        print(f"   R²: {results['enhanced']['r2']:.4f}")
        print(f"   ±5cm 정확도: {results['enhanced']['within_5cm']*100:.1f}%")
        print(f"   ±10cm 정확도: {results['enhanced']['within_10cm']*100:.1f}%")
    
    print("\n" + "="*70)
    print("✅ 검증 완료!")
    print("="*70)

if __name__ == "__main__":
    main()

