import pandas as pd
from datetime import datetime

def generate_positions(df: pd.DataFrame, config, year: int, month: int, start_date: datetime = None, settlement_date: datetime = None) -> list:
    if start_date is None or settlement_date is None:
        return []
    
    df_period = df[(df["日期"] >= start_date) & (df["日期"] <= settlement_date)].copy()

    if len(df_period) == 0:
        return []

    positions = []
    first_day = df_period.iloc[0]
    base_index = first_day["開盤"]

    for idx, row in df_period.iterrows():
        if len(positions) >= config.max_order:
            break

        n_percent = config.n / 100
        trigger_distance = base_index * n_percent / 2
        
        min_trigger_distance = 500
        if trigger_distance < min_trigger_distance:
            trigger_distance = min_trigger_distance

        trigger_high = base_index + trigger_distance
        trigger_low = base_index - trigger_distance

        if row["最高"] >= trigger_high or row["最低"] <= trigger_low or idx == df_period.index[0]:
            if idx == df_period.index[0]:
                # 第一天，使用開盤價作為基準指數
                new_base = row["開盤"]
            elif row["最高"] >= trigger_high:
                # 向上觸發，使用觸發點作為基準指數
                new_base = trigger_high
            elif row["最低"] <= trigger_low:
                # 向下觸發，使用觸發點作為基準指數
                new_base = trigger_low
            else:
                # 默認情況，使用開盤價
                new_base = row["開盤"]
            
            pos = create_position(row["日期"], new_base, config)
            positions.append(pos)
            base_index = row["開盤"]

    if not positions:
        pos = create_position(first_day["日期"], first_day["開盤"], config)
        positions.append(pos)

    return positions

def create_position(date: datetime, base_index: float, config) -> dict:
    n_percent = config.n / 100
    sell_call_strike = int(base_index * (1 + n_percent))
    sell_put_strike = int(base_index * (1 - n_percent))

    call_buy_strike = int(sell_call_strike + config.get_sell_call_point)
    call_sell_strike = int(call_buy_strike + base_index * n_percent)

    put_buy_strike = int(sell_put_strike - config.get_sell_put_point)
    put_sell_strike = int(put_buy_strike - base_index * n_percent)

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
