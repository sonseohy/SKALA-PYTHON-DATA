import os

import joblib
import pandas as pd
import plotly.express as px
import polars as pl
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

os.makedirs('output', exist_ok=True)

# 0. 데이터 로드 및 개요
df = pl.read_csv('telco_churn.csv')
print(df.shape)
print(df.columns)
print(df.describe())
print(df.group_by('churn').len())  # 이탈 26% / 잔류 74% → 불균형이므로 지표는 ROC-AUC 사용

pdf = df.to_pandas()

# 1. t-검정 : churn(0/1) 두 그룹 간 월 요금 비교
churn_yes = pdf[pdf['churn'] == 1]['monthly_charges']
churn_no = pdf[pdf['churn'] == 0]['monthly_charges']
t, p = stats.ttest_ind(churn_yes, churn_no, equal_var=False)
print(f't-검정 p = {p:.2e}')

# 2. 박스플롯 : 이탈 여부별 월 요금 분포
fig = px.box(pdf, x='churn', y='monthly_charges', title='이탈 여부별 월 요금 분포')
fig.write_html('output/churn_charges.html')

# 3. 카이제곱 : 계약유형(contract) vs 이탈(churn)
table = pd.crosstab(pdf['contract'], pdf['churn'])
chi2, p, dof, expected = stats.chi2_contingency(table)
print(f'카이제곱 p = {p:.2e}')

# 4~5. 전처리 파이프라인 (실제 CSV 컬럼명 기준)
num_cols = ['tenure_months', 'monthly_charges', 'total_charges', 'num_services']
cat_cols = ['contract', 'payment_method']
preprocessor = ColumnTransformer([
    ('num', Pipeline([
        ('imp', SimpleImputer(strategy='median')),  # total_charges 결측 → 중앙값
        ('sc', StandardScaler()),
    ]), num_cols),
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols),
])

# 6. 학습/검증 분리 및 모델 학습
X = pdf.drop(columns=['churn', 'customer_id'])
y = pdf['churn'].astype(int)
X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.2, random_state=42,
    stratify=y,  # 이탈 비율을 train/test에 동일하게 유지
)
pipe = Pipeline([
    ('prep', preprocessor),
    ('model', RandomForestClassifier(n_estimators=200, random_state=42)),
])
pipe.fit(X_tr, y_tr)  # 전처리+모델이 한 번에 학습 (누수 없음)

# 7. 평가 및 모델 저장
proba = pipe.predict_proba(X_te)[:, 1]
auc = roc_auc_score(y_te, proba)
print(f'ROC-AUC = {auc:.3f}')
print(classification_report(y_te, pipe.predict(X_te)))
joblib.dump(pipe, 'output/churn_model.joblib')  # 전처리까지 통째로 저장
