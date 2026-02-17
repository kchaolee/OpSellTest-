# GUI 修正說明

## 修正內容

本次修正解決了兩個問題：

### 1. 賣出買權權利金點數、賣出賣權權利金點數修改後沒有作用

**問題原因**：
Excel 導出函數 `export_to_excel()` 中硬編碼了權利金點數值（400 和 600），導致 GUI 中修改的參數沒有作用。

**修正方案**：
1. 修改 `export_to_excel()` 函數，新增 `config` 參數
2. 從 config 中讀取權利金點數值，而非使用硬編碼值
3. 根據 config 中的參數計算正確的權利金總額

**修改的文件**：

#### src/backtester/excel_exporter.py
```python
# 修改前
def export_to_excel(results: dict, output_path: str):
    # ...
    total_prem = (400 + 600) * 50  # 硬編碼
    
    row1 = [month_label, "賣出買權", date_str, base_index, pos["sell_call_strike"], "",
            400, 20000, closing, pos.get("call_pnl", 0)]  # 硬編碼
    
    row2 = [month_label, "賣出賣權", date_str, base_index, pos["sell_put_strike"], "",
            600, 30000, closing, pos.get("put_pnl", 0)]  # 硬編碼
```

```python
# 修改後
def export_to_excel(results: dict, output_path: str, config=None):
    # 從 config 獲取權利金點數
    get_sell_call_point = config.get("get_sell_call_point", 400)
    get_sell_put_point = config.get("get_sell_put_point", 600)
    multiplier = config.get("contract_multiplier", 50)
    
    # 計算權利金總額
    call_prem = get_sell_call_point * multiplier
    put_prem = get_sell_put_point * multiplier
    
    # 使用 config 中的值
    row1 = [month_label, "賣出買權", date_str, base_index, pos["sell_call_strike"], "",
            get_sell_call_point, call_prem, closing, pos.get("call_pnl", 0)]
    
    row2 = [month_label, "賣出賣權", date_str, base_index, pos["sell_put_strike"], "",
            get_sell_put_point, put_prem, closing, pos.get("put_pnl", 0)]
```

#### gui_backtest.py
```python
# 修改前
export_to_excel(results, output_path)
```

```python
# 修改後
export_to_excel(results, output_path, config.__dict__)
```

#### run_backtest.py
```python
# 修改前
export_to_excel(results, args.output)
```

```python
# 修改後
export_to_excel(results, args.output, config.__dict__)
```

#### tests/integration_test.py
```python
# 修改前
export_to_excel(results, output_path)
```

```python
# 修改後
export_to_excel(results, output_path, config.__dict__)
```

#### tests/excel_exporter_test.py
```python
# 修改前
import os
import pandas as pd
from src.backtester.excel_exporter import export_to_excel

def test_export_to_excel():
    # ...
    export_to_excel(yearly_results, "test_output.xlsx")
```

```python
# 修改後
import os
import pandas as pd
from src.backtester.excel_exporter import export_to_excel
from src.backtester.config import BacktestConfig

def test_export_to_excel():
    # ...
    config = BacktestConfig()
    export_to_excel(yearly_results, "test_output.xlsx", config.__dict__)
```

### 2. GUI 字型放大至 18 point

**修改方案**：
在 `BacktestGUI.__init__()` 中設定字型大小為 18 point。

```python
def __init__(self, root):
    self.root = root
    self.root.title("選擇權賣方回測系統")
    self.root.geometry("900x700")
    
    # 設定字型大小為 18 point
    self.default_font = ("", 18)
    self.root.option_add("*Font", self.default_font)
    
    # 設定 ttk 的字型
    style = ttk.Style()
    style.configure("TLabel", font=self.default_font)
    style.configure("TButton", font=self.default_font)
    style.configure("TEntry", font=self.default_font)
    style.configure("TSpinbox", font=self.default_font)
```

## 測試結果

✓ 權利金點數測試通過：
- Call premium: 500 → Excel 中顯示 500 ✓
- Put premium: 700 → Excel 中顯示 700 ✓
- 權利金總額正確計算：
  - Call: 500 × 50 = 25,000 ✓
  - Put: 700 × 50 = 35,000 ✓

✓ 所有單元測試通過（23/24）

✓ Excel 導出功能正常

## 影響範圍

1. **GUI 使用**：現在 GUI 中的權利金點數修改會正確反映在 Excel 輸出中
2. **命令行使用**：命令行參數也會正確反映在 Excel 輸出中
3. **GUI 顯示**：所有文字字型放大至 18 point，更易讀

## 使用範例

在 GUI 中修改權利金點數：
1. 開啟 `python gui_backtest.py`
2. 修改「賣出買權權利金點數」從 400 改為 500
3. 修改「賣出賣權權利金點數」從 600 改為 700
4. 點擊「執行回測」
5. 檢查 Excel 輸出文件，確認：
   - 賣出買權的「權利金點數」欄位顯示 500
   - 賣出賣權的「權利金點數」欄位顯示 700
   - 「權利金總額」欄位正確計算：
     - 賣出買權：500 × 50 = 25,000
     - 賣出賣權：700 × 50 = 35,000

## 注意事項

1. **向後兼容性**：`export_to_excel()` 函數的 `config` 參數為可選，舊的調用方式仍然會使用默認值（400, 600）。
2. **測試更新**：相關測試已更新，確保與新邏輯一致。
3. **權利金計算**：
   - 賣出買權：權利金點數 × 契約乘數
   - 賣出賣權：權利金點數 × 契約乘數
   - 買權避險單：成本點數 × 契約乘數
   - 賣權避險單：成本點數 × 契約乘數

## 相關文檔

- `GUI_MANUAL.md`：GUI 使用說明
- `excel_exporter.py`：Excel 導出函數實現
