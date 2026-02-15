import pandas as pd
from datetime import datetime
from calendar import weekday, monthrange

def get_third_wednesday(year: int, month: int) -> datetime:
    first_day = weekday(year, month, 1)
    wednesday = (2 - first_day) % 7 + 1
    third_wednesday = wednesday + 14
    return datetime(year, month, third_wednesday)

def find_settlement_dates(df: pd.DataFrame, year: int) -> dict:
    df_filtered = df[df["日期"].dt.year == year].copy()
    result = {}

    for month in range(1, 13):
        third_wed = get_third_wednesday(year, month)

        exact = df_filtered[df_filtered["日期"] == third_wed]
        if not exact.empty:
            result[month] = third_wed
        else:
            after = df_filtered[df_filtered["日期"] > third_wed]
            if not after.empty:
                result[month] = after["日期"].iloc[0]
            else:
                result[month] = None

    return result
