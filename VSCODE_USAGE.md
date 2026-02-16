# VSCode 執行說明

## 修復說明

已修復 Python 相對導入的問題，現在可以在 VSCode 中正常執行腳本。

## 修改內容

### 1. 修改回測模組導入方式

修改了以下文件，添加了備用導入方案：

- `src/backtester/backtester.py`
- `src/backtester/main.py`

這些文件現在會先嘗試相對導入（在作為模組執行時），如果失敗則使用絕對導入（在 VSCode 中直接執行時）。

### 2. 新增 VSCode 配置

在 `.vscode/` 目錄下创建了兩個配置文件：

- `launch.json`: 調試和執行配置
- `settings.json`: Python 語言伺服器配置

這些配置會自動設置 PYTHONPATH，讓 VSCode 能正確辨識導入。

## 在 VSCode 中執行

### 方法一：使用調試器

1. 打開 `run_backtest.py` 文件
2. 按 `F5` 或點擊調試工具欄的「開始調試」按鈕
3. 選擇「Run Backtest」配置

### 方法二：右鍵執行

1. 在 `run_backtest.py` 文件上右鍵
2. 選擇「Run Python File in Terminal」

### 方法三：使用終端機

1. 在 VSCode 開啟終端機
2. 執行：`python run_backtest.py --data "skills/opsell/assets/TSEA_加權指_日線.csv" --year 2026`

## 參數說明

```bash
python run_backtest.py --data <數據文件路徑> --year <年份> [其他參數]
```

必需參數：
- `--data`: 指數數據 CSV 文件路徑
- `--year`: 回測年份

可選參數：
- `--output`: 輸出 Excel 文件路徑（預設：backtest_results.xlsx）
- `--n`: 觸發漲跌幅百分比（預設：3.0）
- `--call-premium`: 買權權利金點數（預設：400）
- `--put-premium`: 賣權權利金點數（預設：600）
- `--call-hedge-cost`: 買權避險成本點數（預設：200）
- `--put-hedge-cost`: 賣權避險成本點數（預設：200）
- `--max-order`: 每月最大部位數（預設：5）
- `--contract-multiplier`: 契約乘數（預設：50）

## 測試文件

为了驗證修復是否正常工作，可以使用以下測試文件：

1. `test_imports.py`: 測試所有模組是否可以正確導入
2. `test_direct_run.py`: 測試完整執行流程

執行方式：
```bash
python test_imports.py
python test_direct_run.py
```

## 常見問題

### Q: VSCode 還是顯示導入錯誤

A: 請嘗試以下步驟：
1. 重新載入 VSCode 窗口（F1 -> "Reload Window"）
2. 檢查 .vscode/settings.json 是否存在且正確
3. 確認 Python 解釋器設置正確

### Q: 執行時出現 FileNotFoundError

A: 檢查 --data 參數指定的文件路徑是否正確

### Q: LSP 還是顯示錯誤

A: LSP 錯誤可能不影響實際執行。如果程式能正常運行，可以忽略這些 LSP 警告，它們通常是編輯器緩存問題。
