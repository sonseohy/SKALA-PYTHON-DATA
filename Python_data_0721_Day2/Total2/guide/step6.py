from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import polars as pl
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

df = pl.read_csv('../telco_churn.csv')

pdf = df.to_pandas()

num_cols = ['tenure_months', 'monthly_charges', 'total_charges']
cat_cols = ['contract', 'payment_method', 'num_services']

# 수치형/범주형 컬럼을 각각 다르게 전처리하는 파이프라인
preprocessor = ColumnTransformer([
    ('num', Pipeline([
        ('imp', SimpleImputer(strategy='median')),  # 결측 → 중앙값
        ('sc', StandardScaler()),  # 스케일 통일
    ]), num_cols),
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols),
    # handle_unknown='ignore' : 실전에서 못 보던 범주가 와도 안 터짐
])

X = pdf.drop(columns=['churn'])
y = (pdf['churn'] == 'Yes').astype(int)
X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.2, random_state=42,
    stratify=y,  # ★ 이탈 비율을 train/test에 동일하게 유지
)
pipe = Pipeline([
    ('prep', preprocessor),
    ('model', RandomForestClassifier(n_estimators=200, random_state=42)),
])
pipe.fit(X_tr, y_tr) # ★ 전처리+모델이 한 번에 학습 (누수 없음)
