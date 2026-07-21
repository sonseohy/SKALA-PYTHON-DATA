# ❌ 위험한 인코딩: Month-to-month=0, One year=1, Two year=2
# → 모델이 '2년 계약은 1년 계약의 2배다' 라고 오해합니다!
# ✅ One-Hot 인코딩: 각 범주를 독립된 0/1 컬럼으로
# Contract_Month Contract_One Contract_Two
# 1 0 0
# 0 1 0
# → 순서/크기 관계가 생기지 않습니다
