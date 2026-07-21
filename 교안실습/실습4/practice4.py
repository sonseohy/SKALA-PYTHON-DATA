"""
작성자 : 광주_3반_손서현
작성목적 : 시각화 4종, 통계 검정, sklearn Pipeline, Plotly 시각화 실습 목적
작성일 : 2026-07-21

프로그램 설명 : sales_100k.csv를 4종 시각화·t-test/카이제곱 검정·sklearn Pipeline·Plotly 인터랙티브 차트로 분석하는 프로그램

변경사항 내역 (날짜, 변경목적, 변경내용 순으로 기입)
"""
import joblib
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
from scipy.stats import chi2_contingency, ttest_ind
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

plt.rcParams['font.family'] = 'AppleGothic'  # 한글 그래프 라벨 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('sales_100k.csv').dropna(subset=['region', 'category', 'amount'])
df['order_date'] = pd.to_datetime(df['order_date'])


# 1) EDA 시각화 4종 (2x2 서브플롯)
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# 1. 히스토그램 + KDE
sns.histplot(df['amount'], kde=True, ax=axes[0, 0])
# 2×2 서브플롯에서 좌상단(0행 0열) 위치의 박스플롯
axes[0, 0].set_title('매출액 분포')

# 2. 지역별 박스플롯
sns.boxplot(x='region', y='amount', data=df, ax=axes[0, 1])  
# 2×2 서브플롯에서 우상단(0행 1열) 위치의 박스플롯
axes[0, 1].set_title('지역별 매출액 박스플롯')

# 3. 월별 매출 합계
monthly = df.set_index('order_date')['amount'].resample('ME').sum()  
axes[1, 0].plot(monthly.index, monthly.values, marker='o')
# 2×2 서브플롯에서 좌하단(1행 0열) 위치의 박스플롯
axes[1, 0].set_title('월별 매출 추이')

# 4. 상관 히트맵
corr = df[['quantity', 'unit_price', 'customer_age', 'amount']].corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', ax=axes[1, 1])
# 2×2 서브플롯에서 우하단(1행 1열) 위치의 박스플롯
axes[1, 1].set_title('수치형 변수 상관관계')

fig.tight_layout()
fig.savefig('eda_4.png')
plt.show()


# 2) 통계 검정 — t-test + 카이제곱
seoul = df.loc[df['region'] == '서울', 'amount']
busan = df.loc[df['region'] == '부산', 'amount']
t_stat, t_p = ttest_ind(seoul, busan, equal_var=False)
t_result = "유의미한 차이 있음" if t_p < 0.05 else "유의미한 차이 없음"
print(f"[t-test] 서울 vs 부산 평균 매출 - t통계량: {t_stat:.4f}, p-value: {t_p:.4f} -> {t_result} (α=0.05)")

crosstab = pd.crosstab(df['region'], df['category'])
chi2, chi_p, dof, _ = chi2_contingency(crosstab)
chi_result = "종속 관계 있음" if chi_p < 0.05 else "독립적(연관성 없음)"
print(f"[카이제곱] 지역 x 카테고리 독립성 - 카이제곱: {chi2:.4f}, p-value: {chi_p:.4f}, 자유도: {dof} -> {chi_result} (α=0.05)")


# 3) sklearn Pipeline 구성 + 저장
numeric_features = ['quantity', 'unit_price', 'customer_age']
categorical_features = ['region', 'category', 'payment_method', 'customer_gender']

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numeric_features),
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
])

pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', LinearRegression()),
])

X = df[numeric_features + categorical_features]
y = df['amount']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
print(f"[Pipeline] 테스트 R2 스코어: {pipeline.score(X_test, y_test):.4f}")

joblib.dump(pipeline, 'sales_pipeline.pkl')  # 학습된 파이프라인 저장
loaded_pipeline = joblib.load('sales_pipeline.pkl')  # 저장한 파이프라인 재로딩
loaded_pred = loaded_pipeline.predict(X_test)
print(f"[Pipeline] 재로딩 후 R2 스코어: {loaded_pipeline.score(X_test, y_test):.4f}")


# 4) Plotly 인터랙티브 차트 저장
region_category_sum = df.groupby(['region', 'category'])['amount'].sum().reset_index()
bar_fig = px.bar(
    region_category_sum, x='region', y='amount', color='category',
    barmode='group', title='지역·카테고리별 총매출',
)
bar_fig.write_html('region_category_sales.html')
