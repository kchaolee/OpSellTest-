import pandas as pd

def load_index_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df["日期"] = pd.to_datetime(df["日期"], format="%Y/%m/%d")
    df = df.sort_values("日期").reset_index(drop=True)
    return df
