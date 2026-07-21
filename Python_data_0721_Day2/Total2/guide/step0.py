import polars as pl
df = pl.read_csv('../telco_churn.csv')
print(df.shape)
print(df.columns)
print(df.head())
print(df.describe()) # 수치형 요약

# ★ 타깃(이탈 여부)의 비율 확인 — 가장 먼저 볼 것!
print(df.group_by('churn').len())

# 이탈 26% / 잔류 74% 같은 '불균형'이면 정확도(accuracy)는 못 쓰므로 이 과제는 ROC-AUC 를 지표로 사용
