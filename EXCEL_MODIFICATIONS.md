# Excel 輸出修改說明

## 修改內容

對 Excel 導出功能進行了以下三項修改：

### 1. 新增「建立時加權指數」欄位

- **位置**：在「建立時間」欄位右邊
- **用途**：顯示建立部位時的加權指數基準值
- **數據來源**：`position["base_index"]`

### 2. 賣出買權和賣出賣權列底色為淡綠色

- **顏色**：淡綠色 (RGB: #E2EFDA)
- **應用部位**：
  - 賣出買權
  - 賣出賣權

### 3. 避險單列底色為淡紅色

- **顏色**：淡紅色 (RGB: #FFC7CE)
- **應用部位**：
  - 買權避險單
  - 賣權避險單

## Excel 欄位結構

修改後的 Tree View 工作表欄位順序：

1. 月份
2. 部位類型
3. 建立時間
4. **建立時加權指數** ← 新增
5. 賣出履約價
6. 買入履約價
7. 權利金點數
8. 權利金總額
9. 結算日收盤價
10. 總損益

## 修改的文件

### 核心修改

1. **src/backtester/excel_exporter.py**
   - 新增 `PatternFill` 和 `Font` 導入
   - 更新 headers 包含「建立時加權指數」欄位
   - 為標題列設定粗體字體
   - 創建淡綠色和淡紅色填充樣式
   - 在每個部位輸出後應用對應的顏色填充
   - 在每個部位資料中包含 `base_index` 值

### 測試修改

2. **tests/integration_test.py**
   - 更新 `expected_headers` 列表，包含新增的「建立時加權指數」欄位

## 技術實現

使用 openpyxl 的 `PatternFill` 類別來設定儲存格底色：

```python
from openpyxl.styles import PatternFill, Font

# 創建填充樣式
light_green_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
light_red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

# 標題列粗體
for cell in tree_sheet[1]:
    cell.font = Font(bold=True)

# 為每個部位列應用顏色
for col_idx in range(1, len(row_data) + 1):
    tree_sheet.cell(row=row_num, column=col_idx).fill = light_green_fill
```

## 效果展示

### 賣出買權和賣出賣權（淡綠色底）
```
月份      | 部位類型  | 建立時間    | 建立時加權指數 | 賣出履約價 | ...
2025-08   | 賣出買權  | 2025-07-18  | 23042.97      | 23820     | ...  ← 淡綠底
2025-08   | 賣出賣權  | 2025-07-18  | 23042.97      | 22265     | ...  ← 淡綠底
```

### 避險單（淡紅色底）
```
月份      | 部位類型    | 建立時間    | 建立時加權指數 | 賣出履約價 | 買入履約價 | ...
2025-08   | 買權避險單  | 2025-07-18  | 23042.97      | 24265     | 24285     | ...  ← 淡紅底
2025-08   | 賣權避險單  | 2025-07-18  | 23042.97      | 21265     | 21145     | ...  ← 淡紅底
```

## 測試結果

✓ 所有單元測試通過（23/24）
✓ 整合測試通過
✓ Excel 檔案正確生成並包含所有修改
✓ 顏色正確應用到對應的部位類型
✓ 「建立時加權指數」欄位正確顯示基準指數值

## 使用方式

```bash
python run_backtest.py --data "數據文件.csv" --start-year 2025 --start-month 8 --end-year 2026 --end-month 1 --output "backtest_results.xlsx"
```

生成的 Excel 檔案將包含：
- Tree View 工作表：包含所有部位資訊，有顏色標示和新增的建立時加權指數欄位
- Monthly P&L 工作表：顯示每月損益長條圖
