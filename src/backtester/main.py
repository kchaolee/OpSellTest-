import pandas as pd
try:
    from .backtester import run_monthly_backtest
except ImportError:
    from backtester.backtester import run_monthly_backtest

def run_yearly_backtest(df: pd.DataFrame, config, year: int) -> dict:
    results = {}

    for month in range(1, 13):
        result = run_monthly_backtest(df, config, year, month)
        results[month] = result

    return results

def run_monthly_range_backtest(df: pd.DataFrame, config, start_year: int, start_month: int, end_year: int, end_month: int) -> dict:
    results = {}
    
    if start_year == end_year:
        for month in range(start_month, end_month + 1):
            result = run_monthly_backtest(df, config, start_year, month)
            results[(start_year, month)] = result
    else:
        for month in range(start_month, 13):
            result = run_monthly_backtest(df, config, start_year, month)
            results[(start_year, month)] = result
        
        for year in range(start_year + 1, end_year):
            for month in range(1, 13):
                result = run_monthly_backtest(df, config, year, month)
                results[(year, month)] = result
        
        for month in range(1, end_month + 1):
            result = run_monthly_backtest(df, config, end_year, month)
            results[(end_year, month)] = result
    
    return results
