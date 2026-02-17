import os
import pandas as pd
from src.backtester.excel_exporter import export_to_excel
from src.backtester.config import BacktestConfig

def test_export_to_excel():
    yearly_results = {
        1: {
            "positions": [
                {
                    "date": pd.Timestamp("2023-01-02"),
                    "sell_call_strike": 30900,
                    "sell_put_strike": 29100,
                    "closing_price": 31500,
                    "pos_pnl": -10000,
                    "call_pnl": -10000,
                    "put_pnl": 0,
                    "call_spread_pnl": -5000,
                    "put_spread_pnl": -10000,
                    "call_buy_strike": 31300,
                    "call_sell_strike": 32300,
                    "put_buy_strike": 28500,
                    "put_sell_strike": 27600,
                    "base_index": 30000
                }
            ],
            "settlement_date": pd.Timestamp("2023-01-18"),
            "closing_price": 31500,
            "total_pnl": -10000
        }
    }
    
    config = BacktestConfig()
    
    export_to_excel(yearly_results, "test_output.xlsx", config.__dict__)

    assert os.path.exists("test_output.xlsx")
    os.remove("test_output.xlsx")
