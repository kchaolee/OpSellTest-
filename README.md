# Options Backtesting Engine

A Python-based backtesting engine for options trading strategies, specifically designed for Taiwan Stock Exchange Index options (TSEA).

## Features

- Load historical index data from CSV files
- Generate options positions based on configurable parameters
- Calculate monthly P&L for each position
- Export results to Excel with detailed Tree View and P&L charts
- Command-line interface for easy execution
- Comprehensive test coverage

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run backtest from command line:

```bash
python run_backtest.py --data <path_to_csv> --year <year> [options]
```

### Example

```bash
python run_backtest.py --data skills/opsell/assets/TSEA_加權指_日線.csv --year 2023 --output backtest_results.xlsx
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--data` | str | required | Path to index data CSV file |
| `--output` | str | `backtest_results.xlsx` | Output Excel file path |
| `--year` | int | required | Year to backtest |
| `--n` | float | `3.0` | Strike distance percentage |
| `--call-premium` | float | `400` | Call premium points |
| `--put-premium` | float | `600` | Put premium points |
| `--call-hedge-cost` | float | `200` | Call spread cost points |
| `--put-hedge-cost` | float | `200` | Put spread cost points |
| `--max-order` | int | `5` | Max positions per month |

## Testing

Run all tests:

```bash
pytest tests/ -v
```

Run specific test file:

```bash
pytest tests/integration_test.py -v
```

## Output

The backtest generates an Excel file with two sheets:

### Tree View

Displays detailed breakdown for each position:
- Month
- Position type (賣出買權, 賣出賣權, 買權避險單, 賣權避險單)
- Creation date
- Strike prices
- Premium points and totals
- Settlement closing price
- Total P&L

### Monthly P&L

Summary of monthly P&L with bar chart visualization.

## Data Format

Input CSV should contain:
- `日期`: Date in `YYYY/MM/DD` format
- Other columns required by the trading strategy

## License

Internal use only.
