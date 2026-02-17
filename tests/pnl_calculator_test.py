import pytest
from src.backtester.pnl_calculator import (
    calculate_sold_call_pnl,
    calculate_sold_put_pnl,
    calculate_call_spread_pnl,
    calculate_put_spread_pnl,
    calculate_total_pnl
)

def test_sold_call_pnl_in_the_money():
    pnl = calculate_sold_call_pnl(31500, 30900, 400, 50)
    assert pnl == -10000

def test_sold_call_pnl_out_of_the_money():
    pnl = calculate_sold_call_pnl(30500, 30900, 400, 50)
    assert pnl == 20000

def test_sold_put_pnl_in_the_money():
    pnl = calculate_sold_put_pnl(28500, 29100, 600, 50)
    assert pnl == 0

def test_sold_put_pnl_out_of_the_money():
    pnl = calculate_sold_put_pnl(29500, 29100, 600, 50)
    assert pnl == 30000

def test_call_spread_pnl_above_both_strikes():
    pnl = calculate_call_spread_pnl(32500, 31400, 32300, 200, 50)
    assert pnl == (32300 - 31400) * 50 - 200 * 50

def test_call_spread_pnl_between_strikes():
    pnl = calculate_call_spread_pnl(31500, 31400, 32300, 200, 50)
    assert pnl == (31500 - 31400) * 50 - 200 * 50

def test_call_spread_pnl_below_both_strikes():
    pnl = calculate_call_spread_pnl(31300, 31400, 32300, 200, 50)
    assert pnl == -10000

def test_put_spread_pnl_below_both_strikes():
    pnl = calculate_put_spread_pnl(27500, 28500, 27600, 200, 50)
    assert pnl == (28500 - 27600) * 50 - 200 * 50

def test_put_spread_pnl_between_strikes():
    pnl = calculate_put_spread_pnl(28000, 28500, 27600, 200, 50)
    assert pnl == (28500 - 28000) * 50 - 200 * 50

def test_put_spread_pnl_above_both_strikes():
    pnl = calculate_put_spread_pnl(29000, 28500, 27600, 200, 50)
    assert pnl == -10000

def test_total_pnl_calculation():
    config = {"get_sell_call_point": 400, "get_sell_put_point": 600,
              "cost_buy_call_point": 200, "cost_buy_put_point": 200,
              "contract_multiplier": 50}
    call_pnl = -10000
    put_pnl = 0
    call_spread_pnl = -5000
    put_spread_pnl = -10000

    total = calculate_total_pnl(config, call_pnl, put_pnl, call_spread_pnl, put_spread_pnl)
    expected = call_pnl + put_pnl + call_spread_pnl + put_spread_pnl
    assert total == expected
