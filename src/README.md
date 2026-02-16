# 選擇權賣方回測系統

本系統用於回測選擇權賣方策略，計算跨式價差部位在歷史數據上的損益表現。

## 專案結構

```
src/
├── __init__.py
└── backtester/
    ├── __init__.py
    ├── main.py              # 主入口，執行年度回測
    ├── backtester.py        # 執行每月回測
    ├── config.py            # 回測配置參數
    ├── data_loader.py       # 數據加載
    ├── excel_exporter.py    # 導出結果到 Excel
    ├── pnl_calculator.py    # 損益計算
    ├── position_generator.py # 部位生成
    └── settlement.py        # 結算日查找
```

## 模組說明

### main.py
提供回測入口函數：
- `run_yearly_backtest()`: 遍歷一年中的12個月，分別執行每月回測並返回結果
- `run_monthly_range_backtest()`: 執行指定月份範圍的回測（可跨年）

### backtester.py
核心回測模組，提供 `run_monthly_backtest()` 函數，執行單月回測流程：
- 查找結算日
- 生成部位
- 計算各部位損益
- 匯總結果

### config.py
定義 `BacktestConfig` 類，包含以下參數：
- `n`: 觸發漲跌幅百分比（預設 3.0%）
- `get_sell_call_point`: 賣出買權權利金點數（預設 400點）
- `get_sell_put_point`: 賣出賣權權利金點數（預設 600點）
- `cost_buy_call_point`: 買入買權避險成本點數（預設 200點）
- `cost_buy_put_point`: 買入賣權避險成本點數（預設 200點）
- `max_order`: 最大部位數（預設 5個）
- `contract_multiplier`: 契約乘數（預設 50）

### data_loader.py
提供 `load_index_data()` 函數，從 CSV 文件加載指數數據。

### excel_exporter.py
提供 `export_to_excel()` 函數，將回測結果導出到 Excel 文件：
- Tree View 工作表：顯示詳細部位資訊
- Monthly P&L 工作表：顯示每月總損益長條圖

### pnl_calculator.py
提供多個損益計算函數：
- `calculate_sold_call_pnl()`: 計算賣出買權損益
- `calculate_sold_put_pnl()`: 計算賣出賣權損益
- `calculate_call_spread_pnl()`: 計算買權價差損益
- `calculate_put_spread_pnl()`: 計算賣權價差損益
- `calculate_total_pnl()`: 計算總損益

### position_generator.py
提供部位生成功能：
- `generate_positions()`: 根據價格走勢生成部位
- `create_position()`: 創建單個部位，計算各履約價

### settlement.py
提供結算日查找功能：
- `get_third_wednesday()`: 計算每月第三個星期三
- `get_third_thursday()`: 計算每月第三個星期四
- `find_settlement_dates()`: 在數據中查找各月交易區間（起始日和結算日）

## 使用方法

### 按年回測

```python
from backtester.config import BacktestConfig
from backtester.data_loader import load_index_data
from backtester.main import run_yearly_backtest
from backtester.excel_exporter import export_to_excel

# 載入數據
df = load_index_data("data.csv")

# 設定配置
config = BacktestConfig(
    n=3.0,
    get_sell_call_point=400.0,
    get_sell_put_point=600.0,
    cost_buy_call_point=200.0,
    cost_buy_put_point=200.0,
    max_order=5,
    contract_multiplier=50
)

# 執行回測
year = 2023
results = run_yearly_backtest(df, config, year)

# 導出結果
export_to_excel(results, "backtest_results.xlsx")
```

### 按月範圍回測（可跨年）

```python
from backtester.main import run_monthly_range_backtest

# 執行回測：2025年8月 到 2026年1月
results = run_monthly_range_backtest(df, config, 2025, 8, 2026, 1)

# 導出結果
export_to_excel(results, "backtest_2025_08_2026_01.xlsx")
```

### 命令行使用

按年回測：
```bash
python run_backtest.py --data "data.csv" --year 2023
```

按月範圍回測：
```bash
python run_backtest.py --data "data.csv" --start-year 2025 --start-month 8 --end-year 2026 --end-month 1
```

## 數據格式要求

輸入的 CSV 文件需包含以下欄位：
- `日期`: 日期格式為 YYYY/MM/DD
- `開盤`: 開盤價
- `最高`: 最高價
- `最低`: 最低價
- `收盤`: 收盤價

## 策略說明

本系統實施的選擇權賣方策略包括：

### 1. 交易區間

每個月的交易區間定義如下：
- **起始日期**：上一個月的第三個週四
- **結算日期**：當月的第三個週三

範例：2026年1月的交易區間為 2025/12/18（12月第三週四）至 2026/01/21（1月第三週三）

### 2. 賣出跨式部位
   - 賣出買權（Call）：履約價 = 基準指數 × (1 + n%)
   - 賣出賣權（Put）：履約價 = 基準指數 × (1 - n%)
   - 權利金收入：50,000點（買權400點 + 賣權600點）× 契約乘數（50）

### 3. 價差部位對沖
   - 買權價差：買入較高位履約價買權（+400點），賣出更高位履約價買權（+n%基準指數）
   - 賣權價差：買入較低位履約價賣權（-600點），賣出更低位履約價賣權（-n%基準指數）
   - 避險成本：20,000點（各200點）× 契約乘數（50）

### 4. 部位觸發條件
   - 當指數漲跌幅度達到 n% × 0.5 或月份第一天時建立新部位
   - 每月最多建立 max_order 個部位

### 5. 結算
   - 每月第三個星期三進行結算
   - 若無交易資料，則使用交易區間最後一日收盤價
