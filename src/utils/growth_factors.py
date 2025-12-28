"""
성장 인자 및 오프셋 조절 유틸리티
- 국가/지역별 보정 계수
- 개인 성장 패턴 분석
- 다양한 유전 공식 적용
"""

from typing import Dict, Optional, List, Tuple
import numpy as np

# 국가/지역별 평균 키 및 보정 계수
# (출처: WHO, 세계보건기구 통계 기반)
COUNTRY_ADJUSTMENT_FACTORS = {
    # 아시아
    'KR': {'name': '대한민국', 'male_avg': 174.9, 'female_avg': 161.5, 'factor': 1.0},
    'JP': {'name': '일본', 'male_avg': 171.2, 'female_avg': 158.8, 'factor': 0.98},
    'CN': {'name': '중국', 'male_avg': 169.7, 'female_avg': 158.0, 'factor': 0.97},
    'VN': {'name': '베트남', 'male_avg': 165.7, 'female_avg': 154.9, 'factor': 0.95},
    
    # 유럽
    'US': {'name': '미국', 'male_avg': 175.3, 'female_avg': 162.1, 'factor': 1.0},
    'GB': {'name': '영국', 'male_avg': 175.3, 'female_avg': 161.6, 'factor': 1.0},
    'DE': {'name': '독일', 'male_avg': 178.0, 'female_avg': 165.9, 'factor': 1.02},
    'NL': {'name': '네덜란드', 'male_avg': 183.8, 'female_avg': 170.4, 'factor': 1.05},
    
    # 기타
    'DEFAULT': {'name': '기본', 'male_avg': 175.0, 'female_avg': 162.0, 'factor': 1.0},
}

def get_country_factor(country_code: str) -> Dict:
    """국가별 보정 계수 반환"""
    return COUNTRY_ADJUSTMENT_FACTORS.get(country_code.upper(), COUNTRY_ADJUSTMENT_FACTORS['DEFAULT'])

class GeneticFormulas:
    """다양한 유전 키 예측 공식"""
    
    @staticmethod
    def midparent_height_formula(father_cm: float, mother_cm: float, gender: str) -> float:
        """
        중간 부모 키 공식 (Mid-Parental Height)
        가장 기본적인 유전 공식
        
        남아: (아버지 키 + 어머니 키 + 13) / 2
        여아: (아버지 키 + 어머니 키 - 13) / 2
        """
        if gender.upper() == 'M':
            return (father_cm + mother_cm + 13) / 2
        else:
            return (father_cm + mother_cm - 13) / 2
    
    @staticmethod
    def tanner_formula(father_cm: float, mother_cm: float, gender: str) -> float:
        """
        Tanner 공식 (Tanner et al., 1970)
        더 정확한 유전 예측 공식
        
        남아: (아버지 키 + 어머니 키) / 2 + 6.5
        여아: (아버지 키 + 어머니 키) / 2 - 6.5
        """
        midparent = (father_cm + mother_cm) / 2
        if gender.upper() == 'M':
            return midparent + 6.5
        else:
            return midparent - 6.5
    
    @staticmethod
    def khamis_roche_formula(father_cm: float, mother_cm: float, 
                             gender: str, current_age: float, current_height: float) -> Optional[float]:
        """
        Khamis-Roche 공식
        현재 키와 나이를 고려한 예측 공식
        (간소화된 버전)
        """
        midparent = (father_cm + mother_cm) / 2
        if gender.upper() == 'M':
            target = midparent + 6.5
        else:
            target = midparent - 6.5
        
        # 성장 잠재력 추정 (나이에 따라)
        if current_age <= 2:
            potential = 0.85
        elif current_age <= 5:
            potential = 0.75
        elif current_age <= 10:
            potential = 0.60
        elif current_age <= 15:
            potential = 0.40
        else:
            potential = 0.20
        
        return current_height + (target - current_height) * potential

class GrowthPatternAnalyzer:
    """개인 성장 패턴 분석"""
    
    @staticmethod
    def analyze_growth_velocity(height_records: List[Dict]) -> Dict:
        """
        성장 속도 분석
        
        Args:
            height_records: [{'age_years': float, 'height_cm': float}, ...]
        
        Returns:
            성장 패턴 분석 결과
        """
        if len(height_records) < 2:
            return {'velocity': None, 'percentile': None, 'pattern': 'insufficient_data'}
        
        # 나이 순으로 정렬
        sorted_records = sorted(height_records, key=lambda x: x['age_years'])
        
        # 연간 성장률 계산 (cm/year)
        velocities = []
        for i in range(1, len(sorted_records)):
            age_diff = sorted_records[i]['age_years'] - sorted_records[i-1]['age_years']
            height_diff = sorted_records[i]['height_cm'] - sorted_records[i-1]['height_cm']
            if age_diff > 0:
                velocity = height_diff / age_diff
                velocities.append({
                    'age_range': (sorted_records[i-1]['age_years'], sorted_records[i]['age_years']),
                    'velocity': velocity
                })
        
        avg_velocity = np.mean([v['velocity'] for v in velocities]) if velocities else None
        
        # 성장 패턴 분류
        pattern = 'normal'
        if avg_velocity:
            # 연간 성장률 기준 (나이별 상이하지만 간단히)
            if avg_velocity < 3.0:
                pattern = 'slow'
            elif avg_velocity > 8.0:
                pattern = 'rapid'
            else:
                pattern = 'normal'
        
        return {
            'average_velocity': avg_velocity,
            'velocities': velocities,
            'pattern': pattern,
            'records_count': len(sorted_records)
        }
    
    @staticmethod
    def calculate_percentile(height_cm: float, age_years: float, gender: str, 
                            country_code: str = 'DEFAULT') -> Optional[float]:
        """
        백분위수 계산 (간단한 근사)
        실제로는 성장 도표 데이터가 필요하지만, 평균과 표준편차로 근사
        """
        country_info = get_country_factor(country_code)
        if gender.upper() == 'M':
            avg_height = country_info['male_avg']
            std_height = 7.0  # 대략적인 표준편차
        else:
            avg_height = country_info['female_avg']
            std_height = 6.0
        
        # Z-score 계산
        z_score = (height_cm - avg_height) / std_height
        
        # Z-score를 백분위수로 변환 (근사)
        # 정규분포 가정
        percentile = 50 + (z_score * 16)  # 간단한 근사
        percentile = max(0, min(100, percentile))  # 0-100 범위로 제한
        
        return percentile

class HeightPredictionAdjuster:
    """키 예측 오프셋 조절"""
    
    def __init__(self, country_code: str = 'DEFAULT'):
        self.country_code = country_code
        self.country_info = get_country_factor(country_code)
    
    def apply_country_adjustment(self, predicted_height: float, gender: str) -> float:
        """
        국가별 평균 키 차이를 반영한 보정
        
        Args:
            predicted_height: 원래 예측 키
            gender: 성별
        
        Returns:
            보정된 예측 키
        """
        if gender.upper() == 'M':
            country_avg = self.country_info['male_avg']
            default_avg = COUNTRY_ADJUSTMENT_FACTORS['DEFAULT']['male_avg']
        else:
            country_avg = self.country_info['female_avg']
            default_avg = COUNTRY_ADJUSTMENT_FACTORS['DEFAULT']['female_avg']
        
        # 평균 차이를 보정 계수로 적용
        adjustment_ratio = country_avg / default_avg
        
        return predicted_height * adjustment_ratio
    
    def apply_genetic_formula_adjustment(self, father_cm: float, mother_cm: float,
                                        gender: str, current_age: Optional[float] = None,
                                        current_height: Optional[float] = None) -> Dict[str, float]:
        """
        다양한 유전 공식으로 예측하고 가중 평균
        
        Returns:
            각 공식별 예측값
        """
        predictions = {}
        
        # Mid-parental 공식
        predictions['midparent'] = GeneticFormulas.midparent_height_formula(
            father_cm, mother_cm, gender
        )
        
        # Tanner 공식
        predictions['tanner'] = GeneticFormulas.tanner_formula(
            father_cm, mother_cm, gender
        )
        
        # Khamis-Roche 공식 (현재 키와 나이가 있을 때)
        if current_age is not None and current_height is not None:
            khamis_roche = GeneticFormulas.khamis_roche_formula(
                father_cm, mother_cm, gender, current_age, current_height
            )
            if khamis_roche:
                predictions['khamis_roche'] = khamis_roche
        
        return predictions
    
    def apply_growth_pattern_adjustment(self, base_prediction: float,
                                       growth_pattern: Dict,
                                       height_records: List[Dict]) -> float:
        """
        개인 성장 패턴에 따른 조정
        
        Args:
            base_prediction: 기본 예측값
            growth_pattern: 성장 패턴 분석 결과
            height_records: 키 기록
        
        Returns:
            조정된 예측값
        """
        if growth_pattern.get('pattern') == 'insufficient_data':
            return base_prediction
        
        adjusted = base_prediction
        
        # 성장 속도에 따른 조정
        pattern = growth_pattern.get('pattern', 'normal')
        if pattern == 'slow':
            # 성장이 느리면 약간 감소
            adjusted = base_prediction * 0.97
        elif pattern == 'rapid':
            # 성장이 빠르면 약간 증가
            adjusted = base_prediction * 1.03
        
        return adjusted
    
    def calculate_final_prediction(self, 
                                   base_prediction: float,
                                   father_cm: Optional[float] = None,
                                   mother_cm: Optional[float] = None,
                                   gender: str = 'M',
                                   current_age: Optional[float] = None,
                                   current_height: Optional[float] = None,
                                   height_history: Optional[List[Dict]] = None,
                                   use_genetic_formulas: bool = True,
                                   use_growth_pattern: bool = True) -> Dict:
        """
        모든 보정을 적용한 최종 예측
        
        Returns:
            최종 예측 결과 및 상세 정보
        """
        result = {
            'base_prediction': base_prediction,
            'adjustments': {},
            'final_prediction': base_prediction
        }
        
        adjusted = base_prediction
        
        # 1. 국가별 보정
        country_adjusted = self.apply_country_adjustment(adjusted, gender)
        country_diff = country_adjusted - adjusted
        adjusted = country_adjusted
        result['adjustments']['country'] = {
            'factor': self.country_info['factor'],
            'adjustment': country_diff,
            'after': adjusted
        }
        
        # 2. 유전 공식 보정 (부모 키가 있을 때)
        if use_genetic_formulas and father_cm and mother_cm:
            genetic_predictions = self.apply_genetic_formula_adjustment(
                father_cm, mother_cm, gender, current_age, current_height
            )
            
            # 유전 공식들의 평균
            genetic_avg = np.mean(list(genetic_predictions.values()))
            
            # 유전 공식 예측과 기본 예측의 가중 평균 (유전 공식 30%)
            adjusted = adjusted * 0.7 + genetic_avg * 0.3
            
            result['adjustments']['genetic_formulas'] = {
                'predictions': genetic_predictions,
                'average': genetic_avg,
                'after': adjusted
            }
        
        # 3. 성장 패턴 보정
        if use_growth_pattern and height_history and len(height_history) >= 2:
            growth_pattern = GrowthPatternAnalyzer.analyze_growth_velocity(height_history)
            pattern_adjusted = self.apply_growth_pattern_adjustment(
                adjusted, growth_pattern, height_history
            )
            pattern_diff = pattern_adjusted - adjusted
            adjusted = pattern_adjusted
            
            result['adjustments']['growth_pattern'] = {
                'pattern': growth_pattern.get('pattern'),
                'velocity': growth_pattern.get('average_velocity'),
                'adjustment': pattern_diff,
                'after': adjusted
            }
        
        result['final_prediction'] = adjusted
        result['total_adjustment'] = adjusted - base_prediction
        
        return result

def get_available_countries() -> Dict[str, str]:
    """사용 가능한 국가 목록 반환"""
    return {code: info['name'] for code, info in COUNTRY_ADJUSTMENT_FACTORS.items() 
            if code != 'DEFAULT'}

