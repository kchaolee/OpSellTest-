import openpyxl

# 創建一個工作簿對象
wb = openpyxl.load_workbook("backtest_full_2020_2025.xlsx")

# 讀取 Tree View sheet
tree_sheet = wb["Tree View"]

# 查看前 20 行
print("Tree View 資料前 20 行：")
print("=" * 120)
for row_idx, row in enumerate(tree_sheet.iter_rows(min_row=1, max_row=20, values_only=True), start=1):
    print(f"Row {row_idx:3d}: {row}")
print("=" * 120)
print()
