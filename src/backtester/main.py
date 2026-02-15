import pandas as pd
from .backtester import run_monthly_backtest

def run_yearly_backtest(df: pd.DataFrame, config, year: int) -> dict:
    results = {}

    for month in range(1, 13):
        result = run_monthly_backtest(df, config, year, month)
        results[month] = result

    return results
