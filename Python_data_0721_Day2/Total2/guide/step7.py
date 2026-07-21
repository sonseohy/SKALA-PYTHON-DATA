import joblib
import polars as pl
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

df = pl.read_csv('../telco_churn.csv')
pdf = df.to_pandas()

num_cols = ['tenure_months', 'monthly_charges', 'total_charges']
cat_cols = ['contract', 'payment_method', 'num_services']

preprocessor = ColumnTransformer([
    ('num', Pipeline([
        ('imp', SimpleImputer(strategy='median')),  # 결측 → 중앙값
        ('sc', StandardScaler()),  # 스케일 통일
    ]), num_cols),
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols),
])

X = pdf.drop(columns=['churn'])
y = pdf['churn'].astype(int)
X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.2, random_state=42,
    stratify=y,  # ★ 이탈 비율을 train/test에 동일하게 유지
)
pipe = Pipeline([
    ('prep', preprocessor),
    ('model', RandomForestClassifier(n_estimators=200, random_state=42)),
])
pipe.fit(X_tr, y_tr)

proba = pipe.predict_proba(X_te)[:, 1] # ★ 확률을 씁니다 (0/1 아님)
auc = roc_auc_score(y_te, proba)
print(f'ROC-AUC = {auc:.3f}') # ≈ 0.66
print(classification_report(y_te, pipe.predict(X_te)))
joblib.dump(pipe, 'output/churn_model.joblib') # ★ 전처리까지 통째로 저장
# 나중에: pipe = joblib.load('output/churn_model.joblib')
# pipe.predict(새데이터) ← 전처리가 같이 딸려오므로 바로 예측 가능
