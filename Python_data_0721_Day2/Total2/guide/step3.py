from scipy import stats
import polars as pl
import pandas as pd

df = pl.read_csv('../telco_churn.csv')

pdf = df.to_pandas()
# 1. t-검정 : 숫자(요금)를 두 그룹 간 비교
# churn 컬럼은 'Yes'/'No' 문자열이 아니라 0/1 정수 코드이므로 이에 맞춰 비교
churn_yes = pdf[pdf['churn'] == 1]['monthly_charges']
churn_no = pdf[pdf['churn'] == 0]['monthly_charges']
t, p = stats.ttest_ind(churn_yes, churn_no, equal_var=False)
print(f't-검정 p = {p:.2e}') # ≈ 1.2e-20 → 유의!

# 3. 카이제곱 : 범주(계약유형) vs 범주(이탈)
table = pd.crosstab(pdf['contract'], pdf['churn'])
chi2, p, dof, expected = stats.chi2_contingency(table)
print(f'카이제곱 p = {p:.2e}') # ≈ 1.3e-70 → 유의!
# 해석: 요금과 계약 유형이 이탈과 '통계적으로 유의한 연관'이 있다
