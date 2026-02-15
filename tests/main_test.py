import pandas as pd
from src.backtester.main import run_yearly_backtest
from src.backtester.config import BacktestConfig

def test_run_yearly_backtest():
    config = BacktestConfig(n=3, max_order=2)
    df_data = {
        "日期": pd.date_range("2023-01-01", "2023-12-31"),
        "開盤": [30000 + i*50 for i in range(365)],
        "最高": [30200 + i*50 for i in range(365)],
        "最低": [29900 + i*50 for i in range(365)],
        "收盤": [30100 + i*50 for i in range(365)]
    }
    df = pd.DataFrame(df_data)

    result = run_yearly_backtest(df, config, 2023)
    assert len(result) == 12
    assert all("total_pnl" in month for month in result.values())
