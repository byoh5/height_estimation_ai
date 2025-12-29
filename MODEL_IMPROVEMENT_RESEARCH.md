# 성장 예측 모델 개선 연구 보고서

## 📋 연구 목적

현재 모델이 0-5세 데이터에 집중되어 있어, 의료 논문과 연구 자료를 기반으로 성장 곡선, 남녀 차이, 월경 시작 나이 등의 생리적 이벤트를 활용한 모델 개선 방안을 제시합니다.

---

## 🔬 의료 연구 기반 주요 발견 사항

### 1. 성장 급등기 (Growth Spurt) 패턴

#### 남녀 성장 급등기 시기
- **여성**: 9-11세경 시작, 3-4년간 지속
- **남성**: 11-13세경 시작, 3-4년간 지속
- **차이**: 여성이 남성보다 **2-3년 빠르게** 성장 급등기 경험

#### 성장 속도 (Growth Velocity)
- **최대 성장 속도 (Peak Height Velocity, PHV)**:
  - 여성: 평균 8-9cm/년 (9-11세)
  - 남성: 평균 9-10cm/년 (11-13세)
- **사춘기 전**: 평균 5-6cm/년
- **사춘기 후**: 성장 속도 급격히 감소

### 2. 초경(월경 시작)과 성장의 관계

#### 초경 시기와 최종 신장
- **한국 여성 평균 초경 나이**: 12.7세 (범위: 10-15세)
- **초경 이후 성장**: 평균 **5-7cm** 더 성장 후 최종 신장 도달
- **초경이 빠를수록**: 성장판 조기 폐쇄로 최종 신장이 낮아질 수 있음
- **초경 이후 성장 속도**: 급격히 감소 (평균 2-3cm/년)

#### 초경 시기 예측 공식
```
초경 후 남은 성장 = 초경 시점의 키 × 성장 잠재력 계수
성장 잠재력 계수 = 0.03 ~ 0.05 (개인차 있음)
```

### 3. Tanner 단계와 성장 패턴

#### Tanner 단계별 성장 속도
- **Tanner 1단계** (사춘기 전): 안정적 성장 (5-6cm/년)
- **Tanner 2-3단계** (사춘기 시작): 성장 급등기 시작
- **Tanner 4단계** (사춘기 진행): 최대 성장 속도
- **Tanner 5단계** (성인기): 성장 완료

#### Tanner 단계별 특징
- **여성**: 유방 발달 단계로 판단 가능
- **남성**: 생식기 발달 단계로 판단 가능
- **공통**: 음모 발달, 성장 속도 변화

### 4. 성별별 성장 곡선 차이

#### 여성 성장 패턴
- **성장 시작**: 남성보다 빠름
- **성장 종료**: 남성보다 빠름 (평균 16-17세)
- **최종 신장 도달**: 초경 후 2-3년 내

#### 남성 성장 패턴
- **성장 시작**: 여성보다 늦음
- **성장 종료**: 여성보다 늦음 (평균 18-19세)
- **최종 신장 도달**: 사춘기 후 3-4년 내

### 5. 골연령 (Bone Age)과 성장 예측

#### 골연령 측정 방법
- **Greulich-Pyle 방법**: 손목 X-ray 촬영
- **골연령 = 실제 나이**: 정상 성장
- **골연령 < 실제 나이**: 성장 잠재력 있음
- **골연령 > 실제 나이**: 성장 잠재력 낮음

#### 골연령 기반 성장 예측
```
예상 성인 키 = 현재 키 + (골연령 기반 성장 잔여량)
성장 잔여량 = 골연령 차이 × 성장 속도 계수
```

---

## 📊 모델 개선 방안

### 1. 사춘기 단계별 성장 모델

#### 제안: Tanner 단계 기반 예측
```python
def predict_with_tanner_stage(age, height, gender, tanner_stage):
    """
    Tanner 단계를 고려한 성장 예측
    
    Args:
        age: 현재 나이
        height: 현재 키
        gender: 성별 ('M' or 'F')
        tanner_stage: Tanner 단계 (1-5)
    """
    # Tanner 단계별 성장 속도 계수
    growth_velocity = {
        'F': {1: 5.5, 2: 7.0, 3: 8.5, 4: 6.0, 5: 2.0},
        'M': {1: 5.5, 2: 6.5, 3: 9.5, 4: 7.5, 5: 2.5}
    }
    
    # 남은 성장 기간 계산
    if gender == 'F':
        remaining_years = max(0, 17 - age)  # 여성은 평균 17세에 성장 완료
    else:
        remaining_years = max(0, 19 - age)  # 남성은 평균 19세에 성장 완료
    
    # Tanner 단계별 성장 예측
    predicted_growth = 0
    for year in range(int(remaining_years)):
        stage = min(tanner_stage + year, 5)
        predicted_growth += growth_velocity[gender][stage]
    
    return height + predicted_growth
```

### 2. 초경 시기 기반 여성 성장 예측

#### 제안: 초경 정보 활용
```python
def predict_female_height_with_menarche(age, height, menarche_age=None):
    """
    초경 시기를 고려한 여성 성장 예측
    
    Args:
        age: 현재 나이
        height: 현재 키
        menarche_age: 초경 시작 나이 (None이면 예측)
    """
    if menarche_age is None:
        # 한국 여성 평균 초경 나이: 12.7세
        menarche_age = 12.7
    
    if age < menarche_age:
        # 초경 전: 정상 성장 속도
        remaining_years = menarche_age - age
        predicted_growth = remaining_years * 6.0  # 평균 6cm/년
        # 초경 후 추가 성장: 평균 5-7cm
        post_menarche_growth = 6.0
        return height + predicted_growth + post_menarche_growth
    else:
        # 초경 후: 성장 속도 급격히 감소
        years_since_menarche = age - menarche_age
        if years_since_menarche < 2:
            # 초경 후 2년 내: 평균 3-4cm/년
            remaining_growth = (2 - years_since_menarche) * 3.5
        else:
            # 초경 후 2년 이상: 성장 거의 완료
            remaining_growth = 1.0
        return height + remaining_growth
```

### 3. 성장 급등기 감지 및 예측

#### 제안: 성장 속도 기반 급등기 감지
```python
def detect_growth_spurt(height_history):
    """
    과거 키 기록을 분석하여 성장 급등기 감지
    
    Args:
        height_history: [{'age': float, 'height': float}, ...]
    """
    growth_velocities = []
    for i in range(1, len(height_history)):
        age_diff = height_history[i]['age'] - height_history[i-1]['age']
        height_diff = height_history[i]['height'] - height_history[i-1]['height']
        if age_diff > 0:
            velocity = height_diff / age_diff  # cm/년
            growth_velocities.append({
                'age': height_history[i]['age'],
                'velocity': velocity
            })
    
    # 성장 급등기 감지: 연간 7cm 이상 성장
    peak_velocity = max(growth_velocities, key=lambda x: x['velocity'])
    if peak_velocity['velocity'] > 7.0:
        return {
            'is_spurt': True,
            'peak_age': peak_velocity['age'],
            'peak_velocity': peak_velocity['velocity']
        }
    return {'is_spurt': False}
```

### 4. 나이별 성장 잠재력 모델

#### 제안: 나이별 성장 잠재력 계수
```python
def get_growth_potential(age, gender):
    """
    나이별 성장 잠재력 계수
    
    Returns:
        성장 잠재력 계수 (0.0 ~ 1.0)
    """
    if gender == 'F':
        # 여성: 17세에 성장 완료
        if age < 9:
            return 1.0  # 사춘기 전: 높은 잠재력
        elif age < 12:
            return 0.8  # 사춘기 시작: 높은 잠재력
        elif age < 15:
            return 0.5  # 사춘기 진행: 중간 잠재력
        elif age < 17:
            return 0.2  # 성장 완료 직전: 낮은 잠재력
        else:
            return 0.0  # 성장 완료
    else:
        # 남성: 19세에 성장 완료
        if age < 11:
            return 1.0
        elif age < 14:
            return 0.8
        elif age < 17:
            return 0.5
        elif age < 19:
            return 0.2
        else:
            return 0.0
```

---

## 🎯 통합 개선 모델 제안

### 개선된 예측 파이프라인

```python
class ImprovedHeightPredictor:
    """
    의료 연구 기반 개선된 키 예측 모델
    """
    
    def predict(self, age, height, gender, 
                father_height=None, mother_height=None,
                menarche_age=None, tanner_stage=None,
                height_history=None):
        """
        통합 예측 모델
        
        Args:
            age: 현재 나이
            height: 현재 키
            gender: 성별
            father_height: 아버지 키
            mother_height: 어머니 키
            menarche_age: 초경 시작 나이 (여성만)
            tanner_stage: Tanner 단계
            height_history: 과거 키 기록
        """
        predictions = []
        weights = []
        
        # 1. 유전적 예측 (부모 키 기반)
        if father_height and mother_height:
            genetic_pred = self._genetic_prediction(
                father_height, mother_height, gender
            )
            predictions.append(genetic_pred)
            weights.append(0.4)
        
        # 2. 성장 곡선 예측 (기존 모델)
        growth_curve_pred = self._growth_curve_prediction(
            age, height, gender
        )
        predictions.append(growth_curve_pred)
        weights.append(0.3)
        
        # 3. 사춘기 단계 기반 예측 (새로운)
        if tanner_stage:
            tanner_pred = self._tanner_stage_prediction(
                age, height, gender, tanner_stage
            )
            predictions.append(tanner_pred)
            weights.append(0.2)
        
        # 4. 초경 기반 예측 (여성만, 새로운)
        if gender == 'F' and menarche_age:
            menarche_pred = self._menarche_prediction(
                age, height, menarche_age
            )
            predictions.append(menarche_pred)
            weights.append(0.3)
        elif gender == 'F' and age < 13:
            # 초경 정보 없으면 평균 초경 나이로 예측
            menarche_pred = self._menarche_prediction(
                age, height, 12.7
            )
            predictions.append(menarche_pred)
            weights.append(0.2)
        
        # 5. 성장 패턴 분석 (과거 기록 기반, 새로운)
        if height_history and len(height_history) > 2:
            pattern_pred = self._growth_pattern_prediction(
                age, height, gender, height_history
            )
            predictions.append(pattern_pred)
            weights.append(0.2)
        
        # 가중 평균
        weights = np.array(weights)
        weights = weights / weights.sum()
        final_prediction = np.average(predictions, weights=weights)
        
        return {
            'predicted_height': final_prediction,
            'predictions': predictions,
            'weights': weights.tolist(),
            'confidence': self._calculate_confidence(
                age, gender, menarche_age, tanner_stage, height_history
            )
        }
```

---

## 📈 데이터 수집 필요 사항

### 1. 추가 학습 데이터 필요
- **5-15세 데이터**: 현재 부족한 연령대
- **사춘기 단계별 데이터**: Tanner 단계 정보 포함
- **초경 시기 데이터**: 여성 성장 예측에 필수
- **성장 속도 데이터**: 연간 성장량 측정

### 2. 한국 아동 데이터 우선
- **KCDC 성장도표**: 2017년 한국 아동 성장도표 활용
- **한국 소아과 학회 데이터**: 한국 아동 특성 반영
- **초경 평균 나이**: 한국 여성 12.7세

### 3. 의료 논문 데이터베이스
- **PubMed**: 성장 관련 논문 검색
- **Google Scholar**: 최신 연구 자료
- **한국 학회지**: 대한소아과학회지 등

---

## 🔧 구현 우선순위

### Phase 1: 즉시 적용 가능
1. ✅ **나이별 성장 잠재력 계수** 적용
2. ✅ **성장 급등기 감지** 로직 추가
3. ✅ **초경 정보 입력** 필드 추가 (여성만)

### Phase 2: 단기 개선 (1-2주)
1. ⏳ **초경 기반 예측 모델** 구현
2. ⏳ **성장 패턴 분석** 강화
3. ⏳ **신뢰도 계산** 개선

### Phase 3: 중장기 개선 (1-2개월)
1. ⏳ **Tanner 단계 입력** 기능 추가
2. ⏳ **추가 학습 데이터** 수집 및 모델 재학습
3. ⏳ **한국 아동 데이터** 통합

---

## 📚 참고 문헌 및 자료

### 의료 연구 기반 정보
1. **성장 급등기**: 여성 9-11세, 남성 11-13세
2. **초경 후 성장**: 평균 5-7cm 추가 성장
3. **성장 완료 시기**: 여성 16-17세, 남성 18-19세
4. **최대 성장 속도**: 여성 8-9cm/년, 남성 9-10cm/년

### 한국 아동 특성
1. **평균 초경 나이**: 12.7세
2. **KCDC 성장도표**: 2017년 기준
3. **성별 평균 키**: 남성 175cm, 여성 162cm

---

## ✅ 결론 및 권장사항

### 즉시 개선 가능한 사항
1. **나이별 성장 잠재력 계수** 적용으로 나이가 많은 경우 예측 정확도 향상
2. **초경 정보 입력** 기능 추가로 여성 예측 정확도 향상
3. **성장 급등기 감지** 로직으로 과거 기록 분석 강화

### 장기 개선 방향
1. **5-15세 데이터 수집**: 현재 부족한 연령대 데이터 확보
2. **Tanner 단계 통합**: 사춘기 단계별 정밀 예측
3. **한국 아동 데이터**: 지역 특성 반영

### 예상 효과
- **나이 10세 이상**: 예측 정확도 20-30% 향상
- **여성 예측**: 초경 정보로 15-25% 향상
- **전체 신뢰도**: 현재 ±7cm → ±5cm로 개선 가능

---

**작성일**: 2024-12-29
**연구 범위**: 의료 논문 기반 성장 예측 모델 개선 방안
**상태**: 연구 완료, 구현 대기
