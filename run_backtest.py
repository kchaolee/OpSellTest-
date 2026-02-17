import argparse
import os
import sys
sys.path.insert(0, "src")

from backtester.data_loader import load_index_data
from backtester.main import run_yearly_backtest, run_monthly_range_backtest
from backtester.config import BacktestConfig
from backtester.excel_exporter import export_to_excel

def main():
    parser = argparse.ArgumentParser(description="Run options backtesting engine")
    parser.add_argument("--data", required=True, help="Path to index data CSV file")
    parser.add_argument("--output", default="backtest_results.xlsx", help="Output Excel path (default: backtest_results.xlsx)")
    parser.add_argument("--year", type=int, help="Year to backtest (whole year)")
    parser.add_argument("--start-year", type=int, help="Start year for monthly range")
    parser.add_argument("--start-month", type=int, help="Start month (1-12)")
    parser.add_argument("--end-year", type=int, help="End year for monthly range")
    parser.add_argument("--end-month", type=int, help="End month (1-12)")
    parser.add_argument("--n", default=3.0, type=float, help="Strike distance percentage (default: 3.0)")
    parser.add_argument("--call-premium", default=400.0, type=float, help="Call premium points (default: 400)")
    parser.add_argument("--put-premium", default=600.0, type=float, help="Put premium points (default: 600)")
    parser.add_argument("--call-hedge-cost", default=200.0, type=float, help="Call spread cost points (default: 200)")
    parser.add_argument("--put-hedge-cost", default=200.0, type=float, help="Put spread cost points (default: 200)")
    parser.add_argument("--max-order", default=5, type=int, help="Max positions per month (default: 5)")
    parser.add_argument("--contract-multiplier", default=50, type=int, help="Contract multiplier (default: 50)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data):
        print(f"錯誤：數據文件不存在: {args.data}")
        sys.exit(1)
    
    if args.year is not None and args.start_month is not None:
        print(f"錯誤：不應該同時指定 --year 和 --start-month/--end-month")
        sys.exit(1)
    
    if args.year is None and args.start_month is None:
        print(f"錯誤：必須指定 --year 或 --start-month/--end-month")
        sys.exit(1)
    
    config = BacktestConfig(
        n=args.n,
        get_sell_call_point=args.call_premium,
        get_sell_put_point=args.put_premium,
        cost_buy_call_point=args.call_hedge_cost,
        cost_buy_put_point=args.put_hedge_cost,
        max_order=args.max_order,
        contract_multiplier=args.contract_multiplier
    )
    
    try:
        df = load_index_data(args.data)
        
        if args.year is not None:
            results = run_yearly_backtest(df, config, args.year)
        else:
            start_year = args.start_year if args.start_year else args.end_year
            start_month = args.start_month
            end_year = args.end_year
            end_month = args.end_month
            results = run_monthly_range_backtest(df, config, start_year, start_month, end_year, end_month)
        
        export_to_excel(results, args.output, config.__dict__)
        
        print(f"回測完成！結果已儲存至 {args.output}")
    except Exception as e:
        print(f"執行回測時發生錯誤: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
