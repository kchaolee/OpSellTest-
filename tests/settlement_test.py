import pandas as pd
from datetime import datetime
from src.backtester.settlement import find_settlement_dates

def test_find_settlement_dates():
    dates = [datetime(2023, 1, day) for day in range(1, 32)]
    df = pd.DataFrame({"日期": dates})
    result = find_settlement_dates(df, 2023)
    assert len(result) == 12
    assert 1 in result  # January
    assert "2023-01-18" == result[1].strftime("%Y-%m-%d")  # 3rd Wednesday

def test_settlement_not_in_data():
    dates = [datetime(2023, 1, day) for day in range(1, 16)]  # No 3rd Wednesday
    df = pd.DataFrame({"日期": dates})
    result = find_settlement_dates(df, 2023)
    assert result[1] is None or result[1] > datetime(2023, 1, 15)
