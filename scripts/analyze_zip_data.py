"""
ZIP 파일 압축 해제 및 분석 스크립트
"""

import zipfile
import pandas as pd
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
KAGGLE_DATA_DIR = DATA_DIR / "kaggle"

def extract_zip(zip_path, target_dir):
    """ZIP 파일 압축 해제"""
    try:
        print(f"\n📦 압축 해제 중: {zip_path.name}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        
        print(f"   ✅ 완료: {target_dir}")
        return True
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return False

def analyze_csv_files(directory):
    """디렉토리 내 CSV 파일 분석"""
    csv_files = list(directory.glob("*.csv"))
    
    if not csv_files:
        print(f"   ⚠️  CSV 파일을 찾을 수 없습니다.")
        return []
    
    results = []
    
    for csv_file in csv_files:
        try:
            print(f"\n📊 분석 중: {csv_file.name}")
            
            # 파일 크기
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            print(f"   파일 크기: {size_mb:.2f} MB")
            
            # 데이터 읽기 (큰 파일은 샘플만)
            try:
                df = pd.read_csv(csv_file, nrows=1000)
                print(f"   샘플 행 수: {len(df)} (처음 1000행)")
                
                # 전체 행 수 확인 (파일 크기로 추정 또는 실제 읽기)
                with open(csv_file, 'r', encoding='utf-8') as f:
                    total_rows = sum(1 for line in f) - 1  # 헤더 제외
                
                print(f"   전체 행 수: {total_rows:,} 행")
                print(f"   컬럼 수: {len(df.columns)}개")
                
                print(f"\n   📋 컬럼 목록:")
                for col in df.columns:
                    dtype = df[col].dtype
                    non_null = df[col].notna().sum()
                    print(f"      - {col} ({dtype}) - 비결측치: {non_null}/{len(df)}")
                
                print(f"\n   📈 데이터 미리보기 (처음 5행):")
                print(df.head().to_string())
                
                print(f"\n   📊 기본 통계:")
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    print(df[numeric_cols].describe().to_string())
                
                results.append({
                    'file': csv_file,
                    'rows': total_rows,
                    'columns': list(df.columns),
                    'size_mb': size_mb,
                    'sample_df': df
                })
                
            except Exception as e:
                print(f"   ❌ 데이터 읽기 오류: {e}")
                # 다른 인코딩 시도
                try:
                    df = pd.read_csv(csv_file, encoding='latin-1', nrows=1000)
                    print(f"   ✅ latin-1 인코딩으로 읽기 성공")
                    print(f"   샘플 행 수: {len(df)}")
                    print(f"   컬럼: {list(df.columns)}")
                except:
                    print(f"   ❌ 데이터를 읽을 수 없습니다.")
                    
        except Exception as e:
            print(f"   ❌ 분석 오류: {e}")
    
    return results

def main():
    """메인 함수"""
    print("="*60)
    print("ZIP 파일 압축 해제 및 분석")
    print("="*60)
    
    # ZIP 파일 찾기
    zip_files = list(DATA_DIR.glob("*.zip"))
    
    if not zip_files:
        print("❌ ZIP 파일을 찾을 수 없습니다.")
        return
    
    print(f"\n🔍 발견된 ZIP 파일: {len(zip_files)}개")
    for zip_file in zip_files:
        print(f"   - {zip_file.name}")
    
    # 각 ZIP 파일 처리
    for zip_file in zip_files:
        print(f"\n{'='*60}")
        print(f"처리 중: {zip_file.name}")
        print(f"{'='*60}")
        
        # 파일명 기반으로 타겟 디렉토리 결정
        if "balita" in zip_file.name.lower() or "stunting" in zip_file.name.lower():
            target_dir = KAGGLE_DATA_DIR / "stunting-balita-detection"
        elif "archive" in zip_file.name.lower():
            target_dir = KAGGLE_DATA_DIR / "archive"
        else:
            target_dir = KAGGLE_DATA_DIR / zip_file.stem
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 압축 해제
        if extract_zip(zip_file, target_dir):
            # CSV 파일 분석
            analyze_csv_files(target_dir)
    
    print("\n" + "="*60)
    print("완료!")
    print("="*60)
    print(f"\n📁 압축 해제된 데이터 위치: {KAGGLE_DATA_DIR}")

if __name__ == "__main__":
    main()

