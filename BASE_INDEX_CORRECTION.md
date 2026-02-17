# 基準指數修正說明

## 問題描述

在部位觸發後，新部位的「建立時加權指數」（base_index）計算有誤。原系統使用觸發日當天的開盤價作為新部位的基準指數，這與實際策略不符。

### 範例

用戶報告的問題：
- 前次建立的部位指數：23042.97
- 計算觸發距離：23042.97 × 3% / 2 = 345.64455
- 由於 345.64455 < 500，使用 500 作為最小觸發距離
- 向上觸發點：23042.97 + 500 = 23542.97
- 觸發日開盤價：23550.21

**原行為**：使用 23550.21（開盤價）作為新部位的基準指數
**正確行為**：應使用 23542.97（觸發點）作為新部位的基準指數

## 修正方案

修改部位觸發邏輯，當觸發發生時，使用觸發點而非開盤價作為新部位的基準指數：

### 向上觸發
```python
if row["最高"] >= trigger_high:
    new_base = trigger_high  # 使用觸發點，而非開盤價
```

### 向下觸發
```python
if row["最低"] <= trigger_low:
    new_base = trigger_low  # 使用觸發點，而非開盤價
```

### 第一天（初始部位）
```python
if idx == df_period.index[0]:
    new_base = row["開盤"]  # 第一天使用開盤價
```

## 修改的文件

### src/backtester/position_generator.py

```python
# 原程式碼
if row["最高"] >= trigger_high or row["最低"] <= trigger_low or idx == df_period.index[0]:
    pos = create_position(row["日期"], base_index, config)
    positions.append(pos)
    base_index = row["開盤"]

# 修改後的程式碼
if row["最高"] >= trigger_high or row["最低"] <= trigger_low or idx == df_period.index[0]:
    if idx == df_period.index[0]:
        # 第一天，使用開盤價作為基準指數
        new_base = row["開盤"]
    elif row["最高"] >= trigger_high:
        # 向上觸發，使用觸發點作為基準指數
        new_base = trigger_high
    elif row["最低"] <= trigger_low:
        # 向下觸發，使用觸發點作為基準指數
        new_base = trigger_low
    else:
        # 默認情況，使用開盤價
        new_base = row["開盤"]
    
    pos = create_position(row["日期"], new_base, config)
    positions.append(pos)
    base_index = row["開盤"]  # 計算下一個部位的觸發距離使用開盤價
```

## 重要說明

### 基準指數的兩個用途

1. **計算觸發距離**：用於檢測何時建立新部位
   - 初始基準指數：第一天的開盤價
   - 後續基準指數：當天觸發後的開盤價

2. **計算履約價**：用於計算當前部位的選擇權履約價
   - 初始部位：第一天的開盤價
   - 後後續部位：觸發點（trigger_high 或 trigger_low）

### 為什麼下一個部位的觸發距離仍使用開盤價？

下一個部位的觸發距離計算使用開盤價，因為這是實際市場中建立部位的價格。觸發點只是理論觸發價位，實際交易發生時，市場價格可能與觸發點不同。

## 測試結果

### 向上觸發測試
- 基準指數：23042.97
- 觸發距離：500
- 向上觸發點：23542.97
- 觸發日開盤價：23550.21
- 預期基準指數：23542.97（觸發點） ✓
- 實際基準指數：23542.97 ✓

### 向下觸發測試
- 基準指數：23042.97
- 觸發距離：500
- 向下觸發點：22542.97
- 觸發日開盤價：22500.00
- 預期基準指數：22542.97（觸發點） ✓
- 實際基準指數：22542.97 ✓

## 影響範圍

此修改會影響所有觸發後建立的部位：
- 基準指數從觸發日開盤價改為觸發點
- 履約價會相應調整
- 可能影響損益計算結果

## 使用範例

```python
from backtester.config import BacktestConfig
from backtester.data_loader import load_index_data
from backtester.main import run_monthly_range_backtest
from backtester.excel_exporter import export_to_excel

df = load_index_data("data.csv")
config = BacktestConfig(n=3.0, max_order=5)

# 執行回測（會使用修正後的基準指數計算）
results = run_monthly_range_backtest(df, config, 2025, 8, 2025, 9)

# 導出結果
export_to_excel(results, "backtest_results.xlsx")
```

Excel 輸出中的「建立時加權指數」欄位現在會正確顯示觸發點而非開盤價。

## 注意事項

1. **基準指數與開盤價不同**：基準指數用於計算履約價，開盤價用於計算下一個部位的觸發距離。
2. **觸發點精確性**：觸發點是基於前次基準指數計算的理論觸發價位，可能與實際市場價格略有差異。
3. **履約價影響**：基準指數的變化會直接影響所有履約價的計算（賣出買權、賣出賣權、避險單）。
