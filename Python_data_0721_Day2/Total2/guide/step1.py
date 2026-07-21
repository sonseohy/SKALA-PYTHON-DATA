import polars as pl
df = pl.read_csv('../telco_churn.csv')

# 이탈 여부별로 평균 요금 비교
print(df.group_by('churn').agg([
pl.col('monthly_charges').mean().alias('평균요금'),
pl.col('tenure_months').mean().alias('평균가입기간'),
pl.len().alias('인원'),
]))

