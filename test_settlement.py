import pandas as pd
import sys
sys.path.insert(0, "src")
from backtester.settlement import find_settlement_dates

# 載入數據
df = pd.read_csv("skills/opsell/assets/TSEA_加權指_日線.csv", encoding='big5')
df.columns = ["日期", "開盤", "最高", "最低", "收盤", "漲跌"]
df["日期"] = pd.to_datetime(df["日期"], format="%Y/%m/%d")

# 測試 2020 年的結算日期
year = 2020
settlement_dates = find_settlement_dates(df, year)

print(f"Year {year} Settlement Dates:")
print("=" * 60)
for month, dates in settlement_dates.items():
    print(f"Month {month:2d}: {dates['start_date'].strftime('%Y-%m-%d')} ~ {dates['settlement_date'].strftime('%Y-%m-%d')}")

print()
print(f"Found {len(settlement_dates)} months with settlement dates")
