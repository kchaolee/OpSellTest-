# OpSell Backtesting Engine Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python backtesting engine for Taiwan stock index option dual-sell strategy with accurate P&L calculations, chain-based position monitoring, and Excel output with tree structure and charts.

**Architecture:** Load historical index data → Calculate settlement dates → Generate positions using chain-based monitoring → Calculate P&L using corrected formulas → Export to Excel with tree view and bar charts.

**Tech Stack:** Python 3.8+, pandas (data processing), openpyxl (Excel), matplotlib (charts), pytest (testing)

---

## Task 1: Setup Project Structure

**Files:**
- Create: `src/__init__.py`
- Create: `src/backtester/__init__.py`
- Create: `src/backtester/config.py`
- Create: `tests/__init__.py`
- Create: `tests/config_test.py`

**Step 1: Create empty package structure**

Run: `mkdir -p src/backtester tests`

**Step 2: Write module __init__ files**

```bash
touch src/__init__.py src/backtester/__init__.py tests/__init__.py
```

**Step 3: Create empty files**

```bash
touch src/backtester/config.py tests/config_test.py
```

**Step 4: Commit**

```bash
git add src tests
git commit -m "feat: create project package structure"
```

---

## Task 2: Implement Configuration Class

**Files:**
- Modify: `src/backtester/config.py`
- Test: `tests/config_test.py`

**Step 1: Write the failing test**

```python
import pytest
from src.backtester.config import BacktestConfig

def test_config_initialization():
    config = BacktestConfig(
        n=3,
        get_sell_call_point=400,
        get_sell_put_point=600,
        cost_buy_call_point=200,
        cost_buy_put_point=200,
        max_order=3
    )
    assert config.n == 3
    assert config.get_sell_call_point == 400
    assert config.get_sell_put_point == 600
    assert config.cost_buy_call_point == 200
    assert config.cost_buy_put_point == 200
    assert config.max_order == 3

def test_config_defaults():
    config = BacktestConfig()
    assert config.contract_multiplier == 50
    assert config.n == 3
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/config_test.py -v`
Expected: FAIL with "module not found" or "class not defined"

**Step 3: Write minimal implementation**

```python
from dataclasses import dataclass

@dataclass
class BacktestConfig:
    n: float = 3.0
    get_sell_call_point: float = 400.0
    get_sell_put_point: float = 600.0
    cost_buy_call_point: float = 200.0
    cost_buy_put_point: float = 200.0
    max_order: int = 5
    contract_multiplier: int = 50
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/config_test.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/backtester/config.py tests/config_test.py
git commit -m "feat: implement BacktestConfig class"
```

---

## Task 3: Implement Data Loader for Index Data

**Files:**
- Create: `src/backtester/data_loader.py`
- Test: `tests/data_loader_test.py`

**Step 1: Write the failing test**

```python
import pandas as pd
from src.backtester.data_loader import load_index_data

def test_load_index_data():
    df = load_index_data("skills/opsell/assets/TSEA_加權指_日線.csv")
    assert isinstance(df, pd.DataFrame)
    assert "日期" in df.columns
    assert "開盤" in df.columns
    assert "收盤" in df.columns
    assert len(df) > 0
    assert df["日期"].dtype.name == "datetime64[ns]"

def test_index_data_filtering():
    df = load_index_data("skills/opsell/assets/TSEA_加權指_日線.csv")
    filtered = df[(df["日期"] >= "2023-01-01") & (df["日期"] < "2023-02-01")]
    assert len(filtered) > 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/data_loader_test.py -v`
Expected: FAIL with "module not found"

**Step 3: Write minimal implementation**

```python
import pandas as pd

def load_index_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df["日期"] = pd.to_datetime(df["日期"], format="%Y/%m/%d")
    df = df.sort_values("日期").reset_index(drop=True)
    return df
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/data_loader_test.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/backtester/data_loader.py tests/data_loader_test.py
git commit -m "feat: implement index data loader"
```

---

## Task 4: Implement Settlement Date Calculator

**Files:**
- Create: `src/backtester/settlement.py`
- Test: `tests/settlement_test.py`

**Step 1: Write the failing test**

```python
import pandas as pd
from datetime import datetime
from src.backtester.settlement import find_settlement_dates

def test_find_settlement_dates():
    dates = [datetime(2023, 1, day) for day in range(1, 32)]
    df = pd.DataFrame({"日期": dates})
    result = find_settlement_dates(df, 2023)
    assert len(result) == 12
    assert 1 in result  # January
    assert "2023-01-18" == result[1].strftime("%Y-%m-%d")  # 3rd Wednesday

def test_settlement_not_in_data():
    dates = [datetime(2023, 1, day) for day in range(1, 16)]  # No 3rd Wednesday
    df = pd.DataFrame({"日期": dates})
    result = find_settlement_dates(df, 2023)
    assert result[1] is None or result[1] > datetime(2023, 1, 15)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/settlement_test.py -v`
Expected: FAIL with "module not found"

**Step 3: Write minimal implementation**

```python
import pandas as pd
from datetime import datetime
from calendar import weekday, monthrange

def get_third_wednesday(year: int, month: int) -> datetime:
    first_day = weekday(year, month, 1)
    wednesday = (3 - first_day) % 7 + 1
    third_wednesday = wednesday + 14
    return datetime(year, month, third_wednesday)

def find_settlement_dates(df: pd.DataFrame, year: int) -> dict:
    df_filtered = df[df["日期"].dt.year == year].copy()
    result = {}

    for month in range(1, 13):
        third_wed = get_third_wednesday(year, month)

        exact = df_filtered[df_filtered["日期"] == third_wed]
        if not exact.empty:
            result[month] = third_wed
        else:
            after = df_filtered[df_filtered["日期"] > third_wed]
            if not after.empty:
                result[month] = after["日期"].iloc[0]
            else:
                result[month] = None

    return result
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/settlement_test.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/backtester/settlement.py tests/settlement_test.py
git commit -m "feat: implement settlement date calculator"
```

---

## Task 5: Implement P&L Calculator (Core Logic)

**Files:**
- Create: `src/backtester/pnl_calculator.py`
- Test: `tests/pnl_calculator_test.py`

**Step 1: Write the failing test**

```python
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
    assert pnl == 30000

def test_sold_put_pnl_out_of_the_money():
    pnl = calculate_sold_put_pnl(29500, 29100, 600, 50)
    assert pnl == -20000

def test_call_spread_pnl_above_both_strikes():
    pnl = calculate_call_spread_pnl(31500, 31400, 32300, 200, 50)
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
    put_pnl = 30000
    call_spread_pnl = -5000
    put_spread_pnl = -10000

    total = calculate_total_pnl(config, call_pnl, put_pnl, call_spread_pnl, put_spread_pnl)
    expected = 400*50 + 600*50 - 200*50 - 200*50 + (-10000) + 30000 + (-5000) + (-10000)
    assert total == expected
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pnl_calculator_test.py -v`
Expected: FAIL with "module not found"

**Step 3: Write minimal implementation**

```python
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pnl_calculator_test.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/backtester/pnl_calculator.py tests/pnl_calculator_test.py
git commit -m "feat: implement P&L calculator with corrected formulas"
```

---

## Task 6: Implement Position Generator (Chain-Based Monitoring)

**Files:**
- Create: `src/backtester/position_generator.py`
- Test: `tests/position_generator_test.py`

**Step 1: Write the failing test**

```python
from src.backtester.position_generator import generate_positions
from src.backtester.config import BacktestConfig

def test_generate_single_position():
    config = BacktestConfig(n=3, max_order=1)
    df_data = {
        "日期": ["2023-01-02", "2023-01-18"],
        "開盤": [30000, 30500],
        "最高": [30200, 30800],
        "最低": [29900, 30400],
        "收盤": [30100, 30700]
    }
    import pandas as pd
    df = pd.DataFrame(df_data)
    df["日期"] = pd.to_datetime(df["日期"])

    positions = generate_positions(df, config, 2023, 1)
    assert len(positions) == 1
    assert positions[0]["sell_call_strike"] == 30900
    assert positions[0]["sell_put_strike"] == 29100

def test_chain_based_monitoring():
    config = BacktestConfig(n=3, max_order=3)
    df_data = {
        "日期": ["2023-01-02", "2023-01-05", "2023-01-10", "2023-01-18"],
        "開盤": [30000, 30500, 31000, 31500],
        "最高": [30200, 30800, 31500, 31800],
        "最低": [29900, 30400, 30900, 31400],
        "收盤": [30100, 30700, 31300, 31600]
    }
    import pandas as pd
    df = pd.DataFrame(df_data)
    df["日期"] = pd.to_datetime(df["日期"])

    positions = generate_positions(df, config, 2023, 1)
    assert len(positions) >= 2
    assert positions[0]["base_index"] == 30000
    assert positions[0]["date"].strftime("%Y-%m-%d") == "2023-01-02"

def test_max_order_limit():
    config = BacktestConfig(n=0.5, max_order=3)
    df_data = {
        "日期": ["2023-01-02", "2023-01-03", "2023-01-04", "2023-01-18"],
        "開盤": [30000, 30500, 31000, 31500],
        "最高": [30200, 30800, 31500, 31800],
        "最低": [29900, 30400, 30900, 31400],
        "收盤": [30100, 30700, 31300, 31600]
    }
    import pandas as pd
    df = pd.DataFrame(df_data)
    df["日期"] = pd.to_datetime(df["日期"])

    positions = generate_positions(df, config, 2023, 1)
    assert len(positions) <= 2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/position_generator_test.py -v`
Expected: FAIL with "module not found"

**Step 3: Write minimal implementation**

```python
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

        if row["最高"] >= trigger_high or row["最低"] <= trigger_low:
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/position_generator_test.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/backtester/position_generator.py tests/position_generator_test.py
git commit -m "feat: implement position generator with chain-based monitoring"
```

---

## Task 7: Implement Monthly Backtest Executor

**Files:**
- Create: `src/backtester/backtester.py`
- Test: `tests/backtester_test.py`

**Step 1: Write the failing test**

```python
import pandas as pd
from src.backtester.backtester import run_monthly_backtest
from src.backtester.config import BacktestConfig

def test_run_monthly_backtest():
    config = BacktestConfig(n=3, max_order=3)
    df_data = {
        "日期": pd.date_range("2023-01-02", "2023-01-31"),
        "開盤": [30000 + i*10 for i in range(30)],
        "最高": [30200 + i*10 for i in range(30)],
        "最低": [29900 + i*10 for i in range(30)],
        "收盤": [30100 + i*10 for i in range(30)]
    }
    df = pd.DataFrame(df_data)

    result = run_monthly_backtest(df, config, 2023, 1)
    assert "positions" in result
    assert "settlement_date" in result
    assert "total_pnl" in result
    assert len(result["positions"]) > 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/backtester_test.py -v`
Expected: FAIL with "module not found"

**Step 3: Write minimal implementation**

```python
import pandas as pd
from .position_generator import generate_positions
from .settlement import find_settlement_dates
from .pnl_calculator import (
    calculate_sold_call_pnl, calculate_sold_put_pnl,
    calculate_call_spread_pnl, calculate_put_spread_pnl,
    calculate_total_pnl
)

def run_monthly_backtest(df: pd.DataFrame, config, year: int, month: int) -> dict:
    settlement_dates = find_settlement_dates(df, year)
    settlement_date = settlement_dates.get(month, None)

    positions = generate_positions(df, config, year, month, settlement_date)

    if not positions or settlement_date is None:
        return {"positions": [], "settlement_date": settlement_date, "total_pnl": 0}

    settlement_row = df[df["日期"] == settlement_date]
    if settlement_row.empty:
        closing_price = df[df["日期"].dt.month == month].iloc[-1]["收盤"]
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
        "settlement_date": settlement_date,
        "closing_price": closing_price,
        "total_pnl": total_pnl
    }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/backtester_test.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/backtester/backtester.py tests/backtester_test.py
git commit -m "feat: implement monthly backtest executor"
```

---

## Task 8: Implement Full Year Backtest

**Files:**
- Create: `src/backtester/main.py`
- Test: `tests/main_test.py`

**Step 1: Write the failing test**

```python
import pandas as pd
from src.backtester.main import run_yearly_backtest
from src.backtester.config import BacktestConfig

def test_run_yearly_backtest():
    config = BacktestConfig(n=3, max_order=3)
    df_data = {
        "日期": pd.date_range("2023-01-01", "2023-12-31"),
        "開盤": [30000 + i*50 for i in range(365)],
        "最高": [30200 + i*50 for i in range(365)],
        "最低": [29900 + i*50 for i in range(365)],
        "收盤": [30100 + i*50 for i in range(365)]
    }
    df = pd.DataFrame(df_data)

    result = run_yearly_backtest(df, config, 2023)
    assert len(result) == 12
    assert all("total_pnl" in month for month in result.values())
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/main_test.py -v`
Expected: FAIL with "module not found"

**Step 3: Write minimal implementation**

```python
import pandas as pd
from .backtester import run_monthly_backtest

def run_yearly_backtest(df: pd.DataFrame, config, year: int) -> dict:
    results = {}

    for month in range(1, 13):
        result = run_monthly_backtest(df, config, year, month)
        results[month] = result

    return results
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/main_test.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/backtester/main.py tests/main_test.py
git commit -m "feat: implement yearly backtest runner"
```

---

## Task 9: Implement Excel Exporter

**Files:**
- Create: `src/backtester/excel_exporter.py`
- Test: `tests/excel_exporter_test.py`

**Step 1: Write the failing test**

```python
import os
from src.backtester.excel_exporter import export_to_excel

def test_export_to_excel():
    yearly_results = {
        1: {
            "positions": [
                {
                    "date": pd.Timestamp("2023-01-02"),
                    "sell_call_strike": 30900,
                    "sell_put_strike": 29100,
                    "closing_price": 31500,
                    "pos_pnl": -10000
                }
            ],
            "settlement_date": pd.Timestamp("2023-01-18")
        }
    }

    export_to_excel(yearly_results, "test_output.xlsx")

    assert os.path.exists("test_output.xlsx")
    os.remove("test_output.xlsx")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/excel_exporter_test.py -v`
Expected: FAIL with "module not found"

**Step 3: Write minimal implementation**

```python
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference

def export_to_excel(yearly_results: dict, output_path: str):
    wb = Workbook()
    wb.remove(wb.active)

    tree_sheet = wb.create_sheet("Tree View")

    headers = ["月份", "部位類型", "建立時間", "賣出履約價", "買入履約價",
               "權利金點數", "權利金總額", "結算日收盤價", "總損益"]
    tree_sheet.append(headers)

    for month, month_result in yearly_results.items():
        settlement = month_result.get("settlement_date")
        closing = month_result.get("closing_price", 0)

        group_row = len(tree_sheet.iter_rows(min_row=1)) + 1
        tree_sheet.append([f"2023-{month:02d}", "", "", "", "", "", "", closing, month_result["total_pnl"]])

        for idx, pos in enumerate(month_result["positions"], 1):
            date_str = pos["date"].strftime("%Y-%m-%d")
            total_prem = (400 + 600) * 50

            tree_sheet.append([
                f"2023-{month:02d}", "賣出買權", date_str, pos["sell_call_strike"], "",
                400, 20000, closing, pos.get("call_pnl", 0)
            ])
            tree_sheet.append([
                f"2023-{month:02d}", "賣出賣權", date_str, "", pos["sell_put_strike"],
                600, 30000, closing, pos.get("put_pnl", 0)
            ])
            tree_sheet.append([
                f"2023-{month:02d}", "買權避險單", date_str, pos["call_buy_strike"], pos["call_sell_strike"],
                200, 10000, closing, pos.get("call_spread_pnl", 0)
            ])
            tree_sheet.append([
                f"2023-{month:02d}", "賣權避險單", date_str, pos["put_buy_strike"], pos["put_sell_strike"],
                200, 10000, closing, pos.get("put_spread_pnl", 0)
            ])

    pnl_sheet = wb.create_sheet("Monthly P&L")

    months = []
    pnls = []
    for month, month_result in yearly_results.items():
        months.append(f"2023-{month:02d}")
        pnls.append(month_result["total_pnl"])

    pnl_sheet.append(["月份", "總損益"])
    for month, pnl in zip(months, pnls):
        pnl_sheet.append([month, pnl])

    chart = BarChart()
    data = Reference(pnl_sheet, min_col=2, min_row=1, max_row=len(pnls)+1)
    cats = Reference(pnl_sheet, min_col=1, min_row=2, max_row=len(pnls)+1)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.title = "每月總損益"
    chart.x_axis.title = "月份"
    chart.y_axis.title = "損益 (元)"

    pnl_sheet.add_chart(chart, "D2")

    wb.save(output_path)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/excel_exporter_test.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/backtester/excel_exporter.py tests/excel_exporter_test.py
git commit -m "feat: implement Excel exporter with tree view and charts"
```

---

## Task 10: Create CLI Entry Point

**Files:**
- Create: `run_backtest.py`

**Step 1: Create CLI script**

```python
import argparse
from src.backtester.main import run_yearly_backtest
from src.backtester.data_loader import load_index_data
from src.backtester.config import BacktestConfig
from src.backtester.excel_exporter import export_to_excel

def main():
    parser = argparse.ArgumentParser(description="OpSell Strategy Backtester")
    parser.add_argument("--data", required=True, help="Path to index data CSV")
    parser.add_argument("--output", default="backtest_results.xlsx", help="Output Excel path")
    parser.add_argument("--year", type=int, required=True, help="Year to backtest")
    parser.add_argument("--n", type=float, default=3.0, help="Strike distance percentage")
    parser.add_argument("--call-premium", type=float, default=400, help="Call premium points")
    parser.add_argument("--put-premium", type=float, default=600, help="Put premium points")
    parser.add_argument("--call-hedge-cost", type=float, default=200, help="Call spread cost points")
    parser.add_argument("--put-hedge-cost", type=float, default=200, help="Put spread cost points")
    parser.add_argument("--max-order", type=int, default=5, help="Max positions per month")

    args = parser.parse_args()

    config = BacktestConfig(
        n=args.n,
        get_sell_call_point=args.call_premium,
        get_sell_put_point=args.put_premium,
        cost_buy_call_point=args.call_hedge_cost,
        cost_buy_put_point=args.put_hedge_cost,
        max_order=args.max_order
    )

    print(f"Loading data from {args.data}...")
    df = load_index_data(args.data)

    print(f"Running backtest for year {args.year}...")
    results = run_yearly_backtest(df, config, args.year)

    total = sum(month["total_pnl"] for month in results.values())
    print(f"Year {args.year} Total P&L: {total:,.0f} TWD")

    print(f"Exporting results to {args.output}...")
    export_to_excel(results, args.output)

    print("Backtest complete!")

if __name__ == "__main__":
    main()
```

**Step 2: Test CLI**

Run: `python run_backtest.py --data skills/opsell/assets/TSEA_加權指_日線.csv --year 2023 --output test_results.xlsx`
Expected: Execute successfully and create test_results.xlsx

**Step 3: Commit**

```bash
git add run_backtest.py
git commit -m "feat: add CLI entry point for backtesting"
```

---

## Task 11: Add Requirements File

**Files:**
- Create: `requirements.txt`

**Step 1: Create requirements file**

```text
pandas>=2.0.0
openpyxl>=3.1.0
matplotlib>=3.7.0
pytest>=7.4.0
```

**Step 2: Test installation**

Run: `pip install -r requirements.txt`
Expected: All packages installed successfully

**Step 3: Commit**

```bash
git add requirements.txt
git commit -m "feat: add Python dependencies"
```

---

## Task 12: Integration Test with Real Data

**Files:**
- Create: `tests/integration_test.py`

**Step 1: Write integration test**

```python
import os
from src.backtester.main import run_yearly_backtest
from src.backtester.data_loader import load_index_data
from src.backtester.config import BacktestConfig
from src.backtester.excel_exporter import export_to_excel

def test_full_backtest_pipeline():
    config = BacktestConfig(n=3, max_order=3)

    df = load_index_data("skills/opsell/assets/TSEA_加權指_日線.csv")
    assert len(df) > 0

    results = run_yearly_backtest(df, config, 2023)
    assert len(results) == 12

    export_to_excel(results, "integration_test_output.xlsx")
    assert os.path.exists("integration_test_output.xlsx")

    os.remove("integration_test_output.xlsx")

    total_pnl = sum(month["total_pnl"] for month in results.values())
    assert isinstance(total_pnl, (int, float))
```

**Step 2: Run integration test**

Run: `pytest tests/integration_test.py -v -s`
Expected: PASS with output showing year summary

**Step 3: Commit**

```bash
git add tests/integration_test.py
git commit -m "test: add integration test with real data"
```

---

## Task 13: Create README Documentation

**Files:**
- Create: `README.md`

**Step 1: Create README**

```markdown
# OpSell Backtesting Engine

Taiwan stock index option dual-sell strategy backtesting system with accurate P&L calculations.

## Features

- Accurate P&L calculation with corrected formulas
- Chain-based position monitoring for continuous position building
- Settlement date calculation (3rd Wednesday of each month)
- Excel output with tree view and bar charts

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python run_backtest.py --data skills/opsell/assets/TSEA_加權指_日線.csv --year 2023
```

## Parameters

- `--data`: Path to index data CSV
- `--year`: Year to backtest
- `--n`: Strike distance percentage (default: 3.0)
- `--call-premium`: Call premium points (default: 400)
- `--put-premium`: Put premium points (default: 600)
- `--call-hedge-cost`: Call spread cost points (default: 200)
- `--put-hedge-cost`: Put spread cost points (default: 200)
- `--max-order`: Max positions per month (default: 5)

## Testing

```bash
pytest tests/ -v
```

## Output

Excel file with two sheets:
1. **Tree View**: Hierarchical display of positions
2. **Monthly P&L**: Bar chart showing monthly performance
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with usage instructions"
```

---

## Task 14: Push to Remote Repository

**Files:**
- Push feature branch

**Step 1: Push to remote**

```bash
git push origin feature/backtesting-engine
```

**Step 2: Create pull request (if applicable)**

```bash
gh pr create --title "Implement OpSell backtesting engine" --body "Add complete backtesting system with corrected P&L formulas"
```

**Step 3: Commit**

```bash
git commit --allow-empty -m "feat: push backtesting engine to remote"
```
