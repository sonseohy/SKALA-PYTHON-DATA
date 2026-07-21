import plotly.express as px
import polars as pl

df = pl.read_csv('../telco_churn.csv')

pdf = df.to_pandas() # Plotly 는 pandas 를 받습니다
fig = px.box(pdf, x='churn', y='monthly_charges', title='이탈 여부별 월 요금 분포')
fig.write_html('output/churn_charges.html') # HTML 로 저장
# 박스플롯을 쓰는 이유: 평균만 보면 놓치는 '분포의 모양'과 이상치를 한눈에 볼 수 있습니다.
