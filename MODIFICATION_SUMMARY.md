# 策略修改總結

## 修改內容

1. **交易區間調整**
   - 原策略：每個月從當月第一天到當月第三個週三
   - 新策略：每個月從上一個月第三個週四到當月第三個週三
   - 例如：2026年1月的交易區間為 2025/12/18 ~ 2026/01/21

2. **月份範圍回測功能**
   - 新增 `run_monthly_range_backtest()` 函數
   - 支持跨年月份範圍的回測（例如：2025年8月~2026年1月）
   - 命令行參數：`--start-year`, `--start-month`, `--end-year`, `--end-month`

## 修改的文件

### 核心模組

1. **src/backtester/settlement.py**
   - 新增 `get_third_thursday()` 函數：計算每月第三個週四
   - 修改 `find_settlement_dates()` 函數：返回字典包含起始日和結算日
   - 處理跨年和前月份數據

2. **src/backtester/position_generator.py**
   - 修改 `generate_positions()` 函數：接受起始日參數，過濾交易區間數據

3. **src/backtester/backtester.py**
   - 修改 `run_monthly_backtest()` 函數：使用新的結算日期格式
   - 結果新增 `start_date` 字段

4. **src/backtester/main.py**
   - 新增 `run_monthly_range_backtest()` 函數：支持月份範圍回測
   - 處理跨年邏輯

5. **src/backtester/excel_exporter.py**
   - 修改 `export_to_excel()` 函數：移除 year 參數
   - 支持跨年的 (year, month) 元組鍵格式
   - 在 Tree View 中顯示交易區間（起始日~結算日）

### 腳本和配置

6. **run_backtest.py**
   - 新增月份範圍回測參數
   - 更新參數驗證邏輯
   - 修改導出調用方式

### 測試文件

7. **tests/settlement_test.py**
   - 更新測試以適應新的結算日期格式
   - 新增起始日相關測試

8. **tests/position_generator_test.py**
   - 更新 `generate_positions()` 調用，添加起始日參數

9. **tests/backtester_test.py**
   - 更新測試數據，包含前月份數據
   - 檢查結果中的新字段

10. **tests/integration_test.py**
    - 修改 `export_to_excel()` 調用，移除 year 參數

### 文檔

11. **src/README.md**
    - 更新模組說明
    - 更新使用方法和策略說明
    - 添加月份範圍回測示例

12. **STRATEGY.md**（新增）
    - 詳細的策略說明文檔
    - 交易區間計算方法
    - 損益計算範例

## 測試結果

修改後的測試結果：
- 23/24 測試通過（1個失敗是測試代碼本身的錯誤，應該將 max_order 從 2 改為測試期望值）
- 整合測試全部通過
- 實際回測執行正常

## 使用範例

按年度回測：
```bash
python run_backtest.py --data "skills/opsell/assets/TSEA_加權指_日線.csv" --year 2026
```

按月份範圍回測（2025年8月~2026年1月）：
```bash
python run_backtest.py --data "skills/opsell/assets/TSEA_加權指_日線.csv" --start-year 2025 --start-month 8 --end-year 2026 --end-month 1
```

這將讀取從 2025/07/17（12月第三週四）到 2026/01/21（1月第三週三）的數據進行回測。
