import pandas as pd
from datetime import datetime

def generate_positions(df: pd.DataFrame, config, year: int, month: int, settlement_date: datetime = None) -> list:
    df_month = df[df["日期"].dt.month == month].copy()

    if settlement_date is None:
        settlement_date = df_month.iloc[-1]["日期"]

    df_month = df_month[df_month["日期"] <= settlement_date].copy()

    if len(df_month) == 0:
        return []

    positions = []
    first_day = df_month.iloc[0]
    base_index = first_day["開盤"]

    for idx, row in df_month.iterrows():
        if len(positions) >= config.max_order:
            break

        n_percent = config.n / 100
        trigger_distance = base_index * n_percent / 2

        trigger_high = base_index + trigger_distance
        trigger_low = base_index - trigger_distance

        if row["最高"] >= trigger_high or row["最低"] <= trigger_low or idx == df_month.index[0]:
            pos = create_position(row["日期"], base_index, config)
            positions.append(pos)
            base_index = row["開盤"]

    if not positions:
        pos = create_position(first_day["日期"], first_day["開盤"], config)
        positions.append(pos)

    return positions

def create_position(date: datetime, base_index: float, config) -> dict:
    n_percent = config.n / 100
    sell_call_strike = base_index * (1 + n_percent)
    sell_put_strike = base_index * (1 - n_percent)

    call_buy_strike = sell_call_strike + config.get_sell_call_point
    call_sell_strike = call_buy_strike + base_index * n_percent

    put_buy_strike = sell_put_strike - config.get_sell_put_point
    put_sell_strike = put_buy_strike - base_index * n_percent

    return {
        "date": date,
        "base_index": base_index,
        "sell_call_strike": sell_call_strike,
        "sell_put_strike": sell_put_strike,
        "call_buy_strike": call_buy_strike,
        "call_sell_strike": call_sell_strike,
        "put_buy_strike": put_buy_strike,
        "put_sell_strike": put_sell_strike
    }
