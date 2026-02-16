from dataclasses import dataclass

@dataclass
class BacktestConfig:
    n: float = 3.0
    get_sell_call_point: float = 400.0
    get_sell_put_point: float = 600.0
    cost_buy_call_point: float = 200.0
    cost_buy_put_point: float = 200.0
    max_order: int = 3
    contract_multiplier: int = 50
