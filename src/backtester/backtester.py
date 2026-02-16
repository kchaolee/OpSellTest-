import pandas as pd
try:
    from .position_generator import generate_positions
    from .settlement import find_settlement_dates
    from .pnl_calculator import (
        calculate_sold_call_pnl, calculate_sold_put_pnl,
        calculate_call_spread_pnl, calculate_put_spread_pnl,
        calculate_total_pnl
    )
except ImportError:
    from backtester.position_generator import generate_positions
    from backtester.settlement import find_settlement_dates
    from backtester.pnl_calculator import (
        calculate_sold_call_pnl, calculate_sold_put_pnl,
        calculate_call_spread_pnl, calculate_put_spread_pnl,
        calculate_total_pnl
    )

def run_monthly_backtest(df: pd.DataFrame, config, year: int, month: int) -> dict:
    settlement_dates = find_settlement_dates(df, year)
    month_dates = settlement_dates.get(month, None)
    
    if month_dates is None:
        return {"positions": [], "settlement_date": None, "start_date": None, "total_pnl": 0}
    
    start_date = month_dates["start_date"]
    settlement_date = month_dates["settlement_date"]

    positions = generate_positions(df, config, year, month, start_date, settlement_date)

    if not positions:
        return {"positions": [], "settlement_date": settlement_date, "start_date": start_date, "total_pnl": 0}

    settlement_row = df[df["日期"] == settlement_date]
    if settlement_row.empty:
        closing_price = df[df["日期"] <= settlement_date].iloc[-1]["收盤"]
    else:
        closing_price = settlement_row.iloc[0]["收盤"]

    position_results = []
    total_pnl = 0
    p = config.__dict__

    for pos in positions:
        call_pnl = calculate_sold_call_pnl(
            closing_price, pos["sell_call_strike"],
            p["get_sell_call_point"], p["contract_multiplier"]
        )
        put_pnl = calculate_sold_put_pnl(
            closing_price, pos["sell_put_strike"],
            p["get_sell_put_point"], p["contract_multiplier"]
        )
        call_spread_pnl = calculate_call_spread_pnl(
            closing_price, pos["call_buy_strike"], pos["call_sell_strike"],
            p["cost_buy_call_point"], p["contract_multiplier"]
        )
        put_spread_pnl = calculate_put_spread_pnl(
            closing_price, pos["put_buy_strike"], pos["put_sell_strike"],
            p["cost_buy_put_point"], p["contract_multiplier"]
        )

        pos_pnl = calculate_total_pnl(p, call_pnl, put_pnl, call_spread_pnl, put_spread_pnl)
        total_pnl += pos_pnl

        position_results.append({
            **pos,
            "closing_price": closing_price,
            "call_pnl": call_pnl,
            "put_pnl": put_pnl,
            "call_spread_pnl": call_spread_pnl,
            "put_spread_pnl": put_spread_pnl,
            "pos_pnl": pos_pnl
        })

    return {
        "positions": position_results,
        "start_date": start_date,
        "settlement_date": settlement_date,
        "closing_price": closing_price,
        "total_pnl": total_pnl
    }
