"""
생년월일 기반 나이 계산 유틸리티
한국 나이와 만 나이를 모두 지원
"""

from datetime import datetime
from typing import Tuple, Optional

def calculate_age(birth_date: str, reference_date: Optional[str] = None) -> Tuple[int, float]:
    """
    생년월일로부터 나이 계산
    
    Args:
        birth_date: 생년월일 (YYYY-MM-DD 형식)
        reference_date: 기준일 (YYYY-MM-DD 형식, None이면 오늘)
    
    Returns:
        (만 나이(세), 만 나이(세, 소수점 포함))
    """
    if reference_date is None:
        reference_date = datetime.now().strftime('%Y-%m-%d')
    
    birth = datetime.strptime(birth_date, '%Y-%m-%d')
    ref = datetime.strptime(reference_date, '%Y-%m-%d')
    
    # 만 나이 계산
    age_years = (ref - birth).days / 365.25
    age_years_int = int(age_years)
    
    return age_years_int, age_years

def calculate_age_months(birth_date: str, reference_date: Optional[str] = None) -> float:
    """
    생년월일로부터 나이(개월) 계산
    
    Args:
        birth_date: 생년월일 (YYYY-MM-DD 형식)
        reference_date: 기준일 (YYYY-MM-DD 형식, None이면 오늘)
    
    Returns:
        나이(개월, 소수점 포함)
    """
    if reference_date is None:
        reference_date = datetime.now().strftime('%Y-%m-%d')
    
    birth = datetime.strptime(birth_date, '%Y-%m-%d')
    ref = datetime.strptime(reference_date, '%Y-%m-%d')
    
    # 개월 수 계산
    months = (ref.year - birth.year) * 12 + (ref.month - birth.month)
    days = (ref.day - birth.day) / 30.0  # 대략적인 일수 변환
    
    return months + days

def parse_date_input(date_str: str) -> Optional[str]:
    """
    다양한 날짜 형식을 파싱하여 YYYY-MM-DD 형식으로 변환
    
    Args:
        date_str: 날짜 문자열 (YYYY-MM-DD, YYYY/MM/DD, YYYYMMDD 등)
    
    Returns:
        YYYY-MM-DD 형식의 날짜 문자열, 파싱 실패 시 None
    """
    if not date_str or date_str.strip() == '':
        return None
    
    date_str = date_str.strip().replace('/', '-')
    
    # YYYY-MM-DD 형식
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        pass
    
    # YYYYMMDD 형식
    try:
        if len(date_str) == 8 and date_str.isdigit():
            parsed = datetime.strptime(date_str, '%Y%m%d')
            return parsed.strftime('%Y-%m-%d')
    except ValueError:
        pass
    
    return None

def validate_birth_date(birth_date: str) -> Tuple[bool, Optional[str]]:
    """
    생년월일 유효성 검사
    
    Args:
        birth_date: 생년월일 문자열
    
    Returns:
        (유효 여부, 오류 메시지)
    """
    parsed = parse_date_input(birth_date)
    if parsed is None:
        return False, "올바른 날짜 형식이 아닙니다. (YYYY-MM-DD 형식)"
    
    try:
        birth = datetime.strptime(parsed, '%Y-%m-%d')
        today = datetime.now()
        
        if birth > today:
            return False, "생년월일이 미래일 수 없습니다."
        
        # 100세 이상 체크 (선택사항)
        if (today - birth).days > 36525:  # 약 100년
            return False, "생년월일이 너무 오래되었습니다."
        
        return True, None
    except Exception as e:
        return False, f"날짜 파싱 오류: {str(e)}"

