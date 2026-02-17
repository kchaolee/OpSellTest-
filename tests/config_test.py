import pytest
from src.backtester.config import BacktestConfig

def test_config_initialization():
    config = BacktestConfig(
        n=3,
        get_sell_call_point=400,
        get_sell_put_point=600,
        cost_buy_call_point=200,
        cost_buy_put_point=200,
        max_order=5
    )
    assert config.n == 3
    assert config.get_sell_call_point == 400
    assert config.get_sell_put_point == 600
    assert config.cost_buy_call_point == 200
    assert config.cost_buy_put_point == 200
    assert config.max_order == 5

def test_config_defaults():
    config = BacktestConfig()
    assert config.contract_multiplier == 50
    assert config.n == 3
