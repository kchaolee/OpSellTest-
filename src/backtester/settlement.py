import pandas as pd
from datetime import datetime
from calendar import weekday, monthrange

def get_third_wednesday(year: int, month: int) -> datetime:
    first_day = weekday(year, month, 1)
    wednesday = (2 - first_day) % 7 + 1
    third_wednesday = wednesday + 14
    return datetime(year, month, third_wednesday)

def get_third_thursday(year: int, month: int) -> datetime:
    first_day = weekday(year, month, 1)
    thursday = (3 - first_day) % 7 + 1
    third_thursday = thursday + 14
    return datetime(year, month, third_thursday)

def find_settlement_dates(df: pd.DataFrame, year: int) -> dict:
    df_all = df.copy()
    result = {}

    for month in range(1, 13):
        third_wed = get_third_wednesday(year, month)
        
        prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
        third_thu_prev = get_third_thursday(prev_year, prev_month)
        
        wed_exact = df_all[df_all["日期"] == third_wed]
        if not wed_exact.empty:
            settlement_date = third_wed
        else:
            wed_after = df_all[df_all["日期"] > third_wed]
            if not wed_after.empty:
                settlement_date = wed_after["日期"].iloc[0]
            else:
                settlement_date = None
        
        if settlement_date is None:
            continue
            
        thu_exact = df_all[df_all["日期"] == third_thu_prev]
        if not thu_exact.empty:
            start_date = third_thu_prev
        else:
            thu_after = df_all[df_all["日期"] > third_thu_prev]
            if not thu_after.empty:
                start_date = thu_after["日期"].iloc[0]
            else:
                continue
        
        result[month] = {
            "start_date": start_date,
            "settlement_date": settlement_date
        }

    return result
