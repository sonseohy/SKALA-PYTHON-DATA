from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
cat_cols = ['Contract', 'PaymentMethod', 'InternetService']
preprocessor = ColumnTransformer([
    ('num', Pipeline([
    ('imp', SimpleImputer(strategy='median')), # 결측 → 중앙값
    ('sc', StandardScaler()), # 스케일 통일
    ]), num_cols),
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols),
    # handle_unknown='ignore' : 실전에서 못 보던 범주가 와도 안 터짐
])
