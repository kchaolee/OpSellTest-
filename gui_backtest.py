import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os

# 添加 src 到路徑
sys.path.insert(0, "src")

from backtester.data_loader import load_index_data
from backtester.main import run_monthly_range_backtest, run_yearly_backtest
from backtester.config import BacktestConfig
from backtester.excel_exporter import export_to_excel
import subprocess


class BacktestGUI:
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
        
        # 默認參數
        self.default_params = {
            "data_path": "skills/opsell/assets/TSEA_加權指_日線.csv",
            "n": 3.0,
            "get_sell_call_point": 400.0,
            "get_sell_put_point": 600.0,
            "cost_buy_call_point": 200.0,
            "cost_buy_put_point": 200.0,
            "max_order": 5,
            "contract_multiplier": 50,
            "start_year": 2025,
            "start_month": 8,
            "end_year": 2026,
            "end_month": 1,
            "output_file": "backtest_results.xlsx"
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 設定 Grid 權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # 標題
        title_label = ttk.Label(main_frame, text="回測參數設定", font=("", 16, "bold"))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # 數據文件路徑
        ttk.Label(main_frame, text="數據文件路徑:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.data_path_var = tk.StringVar(value=self.default_params["data_path"])
        data_frame = ttk.Frame(main_frame)
        data_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        data_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(data_frame, textvariable=self.data_path_var, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(data_frame, text="瀏覽", command=self.browse_data_file).grid(row=0, column=1, padx=(5, 0))
        row += 1
        
        # 分隔線
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # 策略參數標題
        strategy_label = ttk.Label(main_frame, text="策略參數", font=("", 12, "bold"))
        strategy_label.grid(row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1
        
        # n - 觸發漲跌幅百分比
        ttk.Label(main_frame, text="觸發漲跌幅百分比 (%):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.n_var = tk.DoubleVar(value=self.default_params["n"])
        ttk.Entry(main_frame, textvariable=self.n_var, width=15).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # get_sell_call_point
        ttk.Label(main_frame, text="賣出買權權利金點數:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.sell_call_point_var = tk.DoubleVar(value=self.default_params["get_sell_call_point"])
        ttk.Entry(main_frame, textvariable=self.sell_call_point_var, width=15).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # get_sell_put_point
        ttk.Label(main_frame, text="賣出賣權權利金點數:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.sell_put_point_var = tk.DoubleVar(value=self.default_params["get_sell_put_point"])
        ttk.Entry(main_frame, textvariable=self.sell_put_point_var, width=15).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # cost_buy_call_point
        ttk.Label(main_frame, text="買入買權避險成本點數:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cost_call_point_var = tk.DoubleVar(value=self.default_params["cost_buy_call_point"])
        ttk.Entry(main_frame, textvariable=self.cost_call_point_var, width=15).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # cost_buy_put_point
        ttk.Label(main_frame, text="買入賣權避險成本點數:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cost_put_point_var = tk.DoubleVar(value=self.default_params["cost_buy_put_point"])
        ttk.Entry(main_frame, textvariable=self.cost_put_point_var, width=15).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # max_order
        ttk.Label(main_frame, text="最大部位數:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.max_order_var = tk.IntVar(value=self.default_params["max_order"])
        ttk.Spinbox(main_frame, from_=1, to=20, textvariable=self.max_order_var, width=10).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # contract_multiplier
        ttk.Label(main_frame, text="契約乘數:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.contract_multiplier_var = tk.IntVar(value=self.default_params["contract_multiplier"])
        ttk.Spinbox(main_frame, from_=1, to=200, textvariable=self.contract_multiplier_var, width=10).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # 分隔線
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # 回測日期標題
        date_label = ttk.Label(main_frame, text="回測日期範圍", font=("", 12, "bold"))
        date_label.grid(row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1
        
        # 日期選擇框架
        date_frame = ttk.Frame(main_frame)
        date_frame.grid(row=row, column=0, columnspan=3, pady=5)
        
        # 起始日期
        ttk.Label(date_frame, text="起始:").grid(row=0, column=0, padx=(0, 5))
        
        ttk.Label(date_frame, text="年").grid(row=0, column=1)
        self.start_year_var = tk.IntVar(value=self.default_params["start_year"])
        start_year_spin = ttk.Spinbox(date_frame, from_=2010, to=2030, textvariable=self.start_year_var, width=8)
        start_year_spin.grid(row=0, column=2, padx=(5, 10))
        
        ttk.Label(date_frame, text="月").grid(row=0, column=3)
        self.start_month_var = tk.IntVar(value=self.default_params["start_month"])
        start_month_spin = ttk.Spinbox(date_frame, from_=1, to=12, textvariable=self.start_month_var, width=5)
        start_month_spin.grid(row=0, column=4, padx=(5, 30))
        
        # 結束日期
        ttk.Label(date_frame, text="結束:").grid(row=0, column=5, padx=(0, 5))
        
        ttk.Label(date_frame, text="年").grid(row=0, column=6)
        self.end_year_var = tk.IntVar(value=self.default_params["end_year"])
        end_year_spin = ttk.Spinbox(date_frame, from_=2010, to=2030, textvariable=self.end_year_var, width=8)
        end_year_spin.grid(row=0, column=7, padx=(5, 10))
        
        ttk.Label(date_frame, text="月").grid(row=0, column=8)
        self.end_month_var = tk.IntVar(value=self.default_params["end_month"])
        end_month_spin = ttk.Spinbox(date_frame, from_=1, to=12, textvariable=self.end_month_var, width=5)
        end_month_spin.grid(row=0, column=9, padx=(5, 0))
        
        row += 1
        
        # 輸出文件
        ttk.Label(main_frame, text="輸出 Excel 文件:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.output_file_var = tk.StringVar(value=self.default_params["output_file"])
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.output_file_var, width=40).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(output_frame, text="瀏覽", command=self.browse_output_file).grid(row=0, column=1, padx=(5, 0))
        row += 1
        
        # 分隔線
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        row += 1
        
        # 按鈕框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="執行回測", command=self.run_backtest).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="重置為預設值", command=self.reset_defaults).grid(row=0, column=1, padx=10)
        row += 1
        
        # 狀態標籤
        self.status_var = tk.StringVar(value="準備就緒")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("", 10))
        status_label.grid(row=row, column=0, columnspan=3, pady=10)
        
        # 添加快捷鍵
        self.root.bind('<Return>', lambda e: self.run_backtest())
    
    def browse_data_file(self):
        file_path = filedialog.askopenfilename(
            title="選擇數據文件",
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.data_path_var.set(file_path)
    
    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="選擇輸出文件",
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if file_path:
            self.output_file_var.set(file_path)
    
    def validate_inputs(self):
        try:
            # 驗證數據文件路徑
            data_path = self.data_path_var.get()
            if not data_path:
                raise ValueError("請輸入數據文件路徑")
            
            if not os.path.exists(data_path):
                raise ValueError(f"數據文件不存在: {data_path}")
            
            # 驗證參數值
            n = self.n_var.get()
            if n <= 0:
                raise ValueError("觸發漲跌幅百分比必須大於 0")
            
            start_year = self.start_year_var.get()
            start_month = self.start_month_var.get()
            end_year = self.end_year_var.get()
            end_month = self.end_month_var.get()
            
            if start_year > end_year or (start_year == end_year and start_month > end_month):
                raise ValueError("起始日期必須早於或等於結束日期")
            
            max_order = self.max_order_var.get()
            if max_order < 1:
                raise ValueError("最大部位數必須大於 0")
            
            contract_multiplier = self.contract_multiplier_var.get()
            if contract_multiplier < 1:
                raise ValueError("契約乘數必須大於 0")
            
            return True
            
        except Exception as e:
            messagebox.showerror("輸入驗證失敗", str(e))
            return False
    
    def run_backtest(self):
        if not self.validate_inputs():
            return
        
        # 禁用按鈕，避免重複點擊
        # (這裡可以添加更多 UI 更新邏輯)
        
        self.status_var.set("正在執行回測...")
        self.root.update()
        
        try:
            # 獲取參數
            config = BacktestConfig(
                n=self.n_var.get(),
                get_sell_call_point=self.sell_call_point_var.get(),
                get_sell_put_point=self.sell_put_point_var.get(),
                cost_buy_call_point=self.cost_call_point_var.get(),
                cost_buy_put_point=self.cost_put_point_var.get(),
                max_order=self.max_order_var.get(),
                contract_multiplier=self.contract_multiplier_var.get()
            )
            
            # 載入數據
            df = load_index_data(self.data_path_var.get())
            
            # 執行回測
            start_year = self.start_year_var.get()
            start_month = self.start_month_var.get()
            end_year = self.end_year_var.get()
            end_month = self.end_month_var.get()
            
            results = run_monthly_range_backtest(df, config, start_year, start_month, end_year, end_month)
            
            # 導出結果
            output_path = self.output_file_var.get()
            export_to_excel(results, output_path, config.__dict__)
            
            self.status_var.set(f"回測完成！結果已儲存至 {output_path}")
            
            # 顯示完成訊息
            messagebox.showinfo("回測完成", f"回測已成功完成！\n結果已儲存至：\n{output_path}")
            
            # 自動打開 Excel 文件
            self.open_excel_file(output_path)
            
        except Exception as e:
            self.status_var.set(f"回測失敗: {str(e)}")
            messagebox.showerror("回測失敗", f"執行回測時發生錯誤：\n{str(e)}")
    
    def open_excel_file(self, file_path):
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS/Linux
                subprocess.call(['open', file_path])
        except Exception as e:
            messagebox.showwarning("無法打開文件", f"無法自動打開 Excel 文件：\n{str(e)}\n\n您可以手動打開：{file_path}")
    
    def reset_defaults(self):
        self.data_path_var.set(self.default_params["data_path"])
        self.n_var.set(self.default_params["n"])
        self.sell_call_point_var.set(self.default_params["get_sell_call_point"])
        self.sell_put_point_var.set(self.default_params["get_sell_put_point"])
        self.cost_call_point_var.set(self.default_params["cost_buy_call_point"])
        self.cost_put_point_var.set(self.default_params["cost_buy_put_point"])
        self.max_order_var.set(self.default_params["max_order"])
        self.contract_multiplier_var.set(self.default_params["contract_multiplier"])
        self.start_year_var.set(self.default_params["start_year"])
        self.start_month_var.set(self.default_params["start_month"])
        self.end_year_var.set(self.default_params["end_year"])
        self.end_month_var.set(self.default_params["end_month"])
        self.output_file_var.set(self.default_params["output_file"])
        
        self.status_var.set("已重置為預設值")


def main():
    root = tk.Tk()
    app = BacktestGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
