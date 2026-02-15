import pandas as pd
from src.backtester.backtester import run_monthly_backtest
from src.backtester.config import BacktestConfig

def test_run_monthly_backtest():
    config = BacktestConfig(n=3, max_order=2)
    df_data = {
        "日期": pd.date_range("2023-01-02", "2023-01-31"),
        "開盤": [30000 + i*10 for i in range(30)],
        "最高": [30200 + i*10 for i in range(30)],
        "最低": [29900 + i*10 for i in range(30)],
        "收盤": [30100 + i*10 for i in range(30)]
    }
    df = pd.DataFrame(df_data)

    result = run_monthly_backtest(df, config, 2023, 1)
    assert "positions" in result
    assert "settlement_date" in result
    assert "total_pnl" in result
    assert len(result["positions"]) > 0
