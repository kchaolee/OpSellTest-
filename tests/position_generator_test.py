from src.backtester.position_generator import generate_positions
from src.backtester.config import BacktestConfig

def test_generate_single_position():
    config = BacktestConfig(n=3, max_order=1)
    df_data = {
        "日期": ["2023-01-02", "2023-01-18"],
        "開盤": [30000, 30500],
        "最高": [30200, 30800],
        "最低": [29900, 30400],
        "收盤": [30100, 30700]
    }
    import pandas as pd
    df = pd.DataFrame(df_data)
    df["日期"] = pd.to_datetime(df["日期"])

    positions = generate_positions(df, config, 2023, 1)
    assert len(positions) == 1
    assert positions[0]["sell_call_strike"] == 30900
    assert positions[0]["sell_put_strike"] == 29100

def test_chain_based_monitoring():
    config = BacktestConfig(n=3, max_order=3)
    df_data = {
        "日期": ["2023-01-02", "2023-01-05", "2023-01-10", "2023-01-18"],
        "開盤": [30000, 30500, 31000, 31500],
        "最高": [30200, 30800, 31500, 31800],
        "最低": [29900, 30400, 30900, 31400],
        "收盤": [30100, 30700, 31300, 31600]
    }
    import pandas as pd
    df = pd.DataFrame(df_data)
    df["日期"] = pd.to_datetime(df["日期"])

    positions = generate_positions(df, config, 2023, 1)
    assert len(positions) >= 2
    assert positions[0]["base_index"] == 30000
    assert positions[0]["date"].strftime("%Y-%m-%d") == "2023-01-02"

def test_max_order_limit():
    config = BacktestConfig(n=0.5, max_order=2)
    df_data = {
        "日期": ["2023-01-02", "2023-01-03", "2023-01-04", "2023-01-18"],
        "開盤": [30000, 30500, 31000, 31500],
        "最高": [30200, 30800, 31500, 31800],
        "最低": [29900, 30400, 30900, 31400],
        "收盤": [30100, 30700, 31300, 31600]
    }
    import pandas as pd
    df = pd.DataFrame(df_data)
    df["日期"] = pd.to_datetime(df["日期"])

    positions = generate_positions(df, config, 2023, 1)
    assert len(positions) <= 2
