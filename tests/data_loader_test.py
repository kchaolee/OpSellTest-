import pandas as pd
from src.backtester.data_loader import load_index_data

def test_load_index_data():
    df = load_index_data("skills/opsell/assets/TSEA_加權指_日線.csv")
    assert isinstance(df, pd.DataFrame)
    assert "日期" in df.columns
    assert "開盤" in df.columns
    assert "收盤" in df.columns
    assert len(df) > 0
    assert df["日期"].dtype.name == "datetime64[us]"

def test_index_data_filtering():
    df = load_index_data("skills/opsell/assets/TSEA_加權指_日線.csv")
    filtered = df[(df["日期"] >= "2023-11-01") & (df["日期"] < "2023-12-01")]
    assert len(filtered) > 0
