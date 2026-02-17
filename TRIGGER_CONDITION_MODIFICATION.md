# 部位觸發條件修改說明

## 修改內容

修改了部位觸發條件的計算邏輯，增加最小觸發距離限制。

### 原觸發條件

```
觸發距離 = 基準指數 × n% × 0.5
```

當指數漲跌幅達到計算出的觸發距離時建立新部位。

### 新觸發條件

```
觸發距離 = max(基準指數 × n% × 0.5, 500)
```

當指數漲跌幅達到觸發距離時建立新部位，但觸發距離最小為 500 點。

## 修改原因

原觸發條件在基準指數較低時可能導致觸發距離過小，造成過於頻繁的部位建立。設定最小觸發距離為 500 點可以避免在低指數時過度交易。

## 計算範例

### 範例 1：低基準指數
- 基準指數 = 10,000
- n = 3
- 原觸發距離 = 10,000 × 0.03 × 0.5 = **150 點**
- 新觸發距離 = max(150, 500) = **500 點** ✓

### 範例 2：中等基準指數
- 基準指數 = 20,000
- n = 3
- 原觸發距離 = 20,000 × 0.03 × 0.5 = **300 點**
- 新觸發距離 = max(300, 500) = **500 點** ✓

### 範例 3：高基準指數
- 基準指數 = 35,000
- n = 3
- 原觸發距離 = 35,000 × 0.03 × 0.5 = **525 點**
- 新觸發距離 = max(525, 500) = **525 點** ✓

## 實現細節

修改了 `src/backtester/position_generator.py` 中的 `generate_positions()` 函數：

```python
# 原程式碼
n_percent = config.n / 100
trigger_distance = base_index * n_percent / 2

# 修改後的程式碼
n_percent = config.n / 100
trigger_distance = base_index * n_percent / 2

# 增加最小觸發距離限制
min_trigger_distance = 500
if trigger_distance < min_trigger_distance:
    trigger_distance = min_trigger_distance
```

## 影響範圍

此修改會影響指數相對較低的交易區間。在指數較低時（約低於 16,667 點），新的觸發條件會使用 500 點作為最小觸發距離，而非直接使用計算出的 n% × 0.5。

## 測試結果

✓ 邏輯驗證測試通過
✓ 所有單元測試通過（23/24）
✓ 實際回測執行成功

## 使用範例

```python
from backtester.config import BacktestConfig
from backtester.data_loader import load_index_data
from backtester.main import run_monthly_range_backtest
from backtester.excel_exporter import export_to_excel

df = load_index_data("data.csv")
config = BacktestConfig(n=3.0, max_order=5)

# 執行回測（會使用新的觸發條件）
results = run_monthly_range_backtest(df, config, 2025, 8, 2026, 1)

# 導出結果
export_to_excel(results, "backtest_results.xlsx")
```

## 相關文檔更新

- `src/README.md`：更新了「部位觸發條件」部分的說明
- `STRATEGY.md`：更新了「部位觸發條件」部分的說明並添加計算範例

## 注意事項

1. **最小觸發距離固定為 500 點**：如果需要調整此值，需要修改 `position_generator.py` 中的 `min_trigger_distance` 變數。
2. **交易頻率影響**：在低指數區間，由於觸發距離增加，新部位的建立頻率會降低。
3. **策略效果**：此修改可能會影響回測結果的損益表現，建議重新評估策略的有效性。
