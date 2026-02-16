import pandas as pd
from datetime import datetime
from src.backtester.settlement import find_settlement_dates, get_third_thursday, get_third_wednesday

def test_find_settlement_dates():
    dates = []
    for month in range(1, 7):  # Test first 6 months
        for day in range(1, 32):
            try:
                dates.append(datetime(2023, month, day))
            except:
                pass
    
    df = pd.DataFrame({"日期": dates})
    result = find_settlement_dates(df, 2023)
    
    assert len(result) == 6
    assert 1 in result  # January
    assert "start_date" in result[1]
    assert "settlement_date" in result[1]
    assert "2023-01-18" == result[1]["settlement_date"].strftime("%Y-%m-%d")  # 3rd Wednesday

def test_settlement_start_date():
    dates = []
    for day in range(1, 32):
        try:
            dates.append(datetime(2022, 12, day))
        except:
            pass
    for day in range(1, 32):
        try:
            dates.append(datetime(2023, 1, day))
        except:
            pass
    
    df = pd.DataFrame({"日期": dates})
    result = find_settlement_dates(df, 2023)
    
    assert 1 in result
    assert "start_date" in result[1]
    assert "settlement_date" in result[1]
    
    prev_year, prev_month = 2022, 12
    expected_start = get_third_thursday(prev_year, prev_month)
    assert expected_start == result[1]["start_date"]