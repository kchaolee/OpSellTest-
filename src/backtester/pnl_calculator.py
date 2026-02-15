def calculate_sold_call_pnl(closing_price: float, strike_price: float,
                           premium_points: float, multiplier: int) -> float:
    premium = premium_points * multiplier
    intrinsic_value = max(0, closing_price - strike_price) * multiplier
    return premium - intrinsic_value

def calculate_sold_put_pnl(closing_price: float, strike_price: float,
                          premium_points: float, multiplier: int) -> float:
    premium = premium_points * multiplier
    intrinsic_value = max(0, strike_price - closing_price) * multiplier
    return premium - intrinsic_value

def calculate_call_spread_pnl(closing_price: float, buy_strike: float,
                             sell_strike: float, cost_points: float,
                             multiplier: int) -> float:
    if closing_price < buy_strike:
        return -cost_points * multiplier
    elif buy_strike <= closing_price < sell_strike:
        return (closing_price - buy_strike) * multiplier - cost_points * multiplier
    else:
        return (sell_strike - buy_strike) * multiplier - cost_points * multiplier

def calculate_put_spread_pnl(closing_price: float, buy_strike: float,
                            sell_strike: float, cost_points: float,
                            multiplier: int) -> float:
    if closing_price < sell_strike:
        return (buy_strike - sell_strike) * multiplier - cost_points * multiplier
    elif sell_strike <= closing_price < buy_strike:
        return (buy_strike - closing_price) * multiplier - cost_points * multiplier
    else:
        return -cost_points * multiplier

def calculate_total_pnl(config: dict, call_pnl: float, put_pnl: float,
                        call_spread_pnl: float, put_spread_pnl: float) -> float:
    m = config["contract_multiplier"]
    premium_income = (config["get_sell_call_point"] + config["get_sell_put_point"]) * m
    hedge_cost = (config["cost_buy_call_point"] + config["cost_buy_put_point"]) * m
    return premium_income - hedge_cost + call_pnl + put_pnl + call_spread_pnl + put_spread_pnl
