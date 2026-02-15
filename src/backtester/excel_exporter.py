import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference

def export_to_excel(yearly_results: dict, output_path: str, year: int = 2023):
    wb = Workbook()
    wb.remove(wb.active)

    tree_sheet = wb.create_sheet("Tree View")

    headers = ["月份", "部位類型", "建立時間", "賣出履約價", "買入履約價",
               "權利金點數", "權利金總額", "結算日收盤價", "總損益"]
    tree_sheet.append(headers)

    for month, month_result in yearly_results.items():
        settlement = month_result.get("settlement_date")
        closing = month_result.get("closing_price", 0)

        tree_sheet.append([f"{year}-{month:02d}", "", "", "", "", "", "", closing, month_result["total_pnl"]])

        for idx, pos in enumerate(month_result["positions"], 1):
            date_str = pos["date"].strftime("%Y-%m-%d")
            total_prem = (400 + 600) * 50

            tree_sheet.append([
                f"{year}-{month:02d}", "賣出買權", date_str, pos["sell_call_strike"], "",
                400, 20000, closing, pos.get("call_pnl", 0)
            ])
            tree_sheet.append([
                f"{year}-{month:02d}", "賣出賣權", date_str, "", pos["sell_put_strike"],
                600, 30000, closing, pos.get("put_pnl", 0)
            ])
            tree_sheet.append([
                f"{year}-{month:02d}", "買權避險單", date_str, pos["call_buy_strike"], pos["call_sell_strike"],
                200, 10000, closing, pos.get("call_spread_pnl", 0)
            ])
            tree_sheet.append([
                f"{year}-{month:02d}", "賣權避險單", date_str, pos["put_buy_strike"], pos["put_sell_strike"],
                200, 10000, closing, pos.get("put_spread_pnl", 0)
            ])

    pnl_sheet = wb.create_sheet("Monthly P&L")

    months = []
    pnls = []
    for month, month_result in yearly_results.items():
        months.append(f"{year}-{month:02d}")
        pnls.append(month_result["total_pnl"])

    pnl_sheet.append(["月份", "總損益"])
    for month, pnl in zip(months, pnls):
        pnl_sheet.append([month, pnl])

    chart = BarChart()
    data = Reference(pnl_sheet, min_col=2, min_row=1, max_row=len(pnls)+1)
    cats = Reference(pnl_sheet, min_col=1, min_row=2, max_row=len(pnls)+1)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.title = "每月總損益"
    chart.x_axis.title = "月份"
    chart.y_axis.title = "損益 (元)"

    pnl_sheet.add_chart(chart, "D2")

    wb.save(output_path)
