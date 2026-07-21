import pandas as pd
def aggregate(df: pd.DataFrame, top_n: int = 10) -> dict:
    """데이터 → 리포트에 넣을 값들. 파일은 안 건드림(순수 함수)"""
    return {
        'kpi': {
            '총매출': int(df['amount'].sum()),
            '주문수': len(df),
            '평균주문액': round(df['amount'].mean(), 1),
        },
        'by_category': (df.groupby('category', observed=True)['amount']
                         .sum().sort_values(ascending=False)
                         .head(top_n).reset_index()
                         .to_dict('records')),
    }
