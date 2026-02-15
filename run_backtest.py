import argparse
import sys
sys.path.insert(0, "src")

from backtester.data_loader import load_index_data
from backtester.main import run_yearly_backtest
from backtester.config import BacktestConfig
from backtester.excel_exporter import export_to_excel

def main():
    parser = argparse.ArgumentParser(description="Run options backtesting engine")
    parser.add_argument("--data", required=True, help="Path to index data CSV file")
    parser.add_argument("--output", default="backtest_results.xlsx", help="Output Excel path (default: backtest_results.xlsx)")
    parser.add_argument("--year", required=True, type=int, help="Year to backtest")
    parser.add_argument("--n", default=3.0, type=float, help="Strike distance percentage (default: 3.0)")
    parser.add_argument("--call-premium", default=400.0, type=float, help="Call premium points (default: 400)")
    parser.add_argument("--put-premium", default=600.0, type=float, help="Put premium points (default: 600)")
    parser.add_argument("--call-hedge-cost", default=200.0, type=float, help="Call spread cost points (default: 200)")
    parser.add_argument("--put-hedge-cost", default=200.0, type=float, help="Put spread cost points (default: 200)")
    parser.add_argument("--max-order", default=5, type=int, help="Max positions per month (default: 5)")
    
    args = parser.parse_args()
    
    config = BacktestConfig(
        n=args.n,
        get_sell_call_point=args.call_premium,
        get_sell_put_point=args.put_premium,
        cost_buy_call_point=args.call_hedge_cost,
        cost_buy_put_point=args.put_hedge_cost,
        max_order=args.max_order,
    )
    
    df = load_index_data(args.data)
    results = run_yearly_backtest(df, config, args.year)
    export_to_excel(results, args.output, args.year)
    
    print(f"Backtest complete! Results saved to {args.output}")

if __name__ == "__main__":
    main()
