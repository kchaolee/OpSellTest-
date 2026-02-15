---
name: 2026-02-16-opsell-accuracy-improvements-design
description: Design document for accuracy improvements in Taiwan stock index option dual-sell strategy backtesting system
---

# Taiwan Stock Index Option Dual-Sell Strategy Accuracy Improvements

## Problem Statement

The original opsell backtesting specification contained several critical issues affecting calculation accuracy:

1. **Incorrect P&L calculation formulas** - Impossible condition checks in spread positions
2. **Inconsistent variable naming** - GetSellCallPoint vs GetSellCallPoint0
3. **Ambiguous Excel fields** - Unclear if rights premium shows points or total value
4. **Unclear monitoring mechanism** - Which index price to use for continuous position building

## Design Analysis

### Critical Issue: P&L Calculation Formulas (Lines 42-49)

**Original Problem:**
- Line 44: `當賣出履約價 < 結算日收盤價 < 賣出履約價` - Impossible condition
- Missing hedging cost consideration in spread position P&L

**Root Cause:**
Formulas didn't account for the cost paid to establish spread positions (CostBuyCallPoint, CostBuyPutPoint).

**Solution Implemented:**

**Call Spread P&L:**
1. 當結算日收盤價 > 賣出履約價時損益= （賣出履約價-買入履約價）* 50 * 1 - CostBuyCallPoint*50
2. 當買入履約價 < 結算日收盤價 < 賣出履約價時損益= （結算日收盤價-買入履約價）* 50 * 1 - CostBuyCallPoint*50
3. 當結算日收盤價 < 買入履約價時損益為 -CostBuyCallPoint*50

**Put Spread P&L:**
1. 當結算日收盤價 < 賣出履約價時損益= （買入履約價-賣出履約價）* 50 * 1 - CostBuyPutPoint*50
2. 當賣出履約價 < 結算日收盤價 < 買入履約價時損益= （買入履約價-結算日收盤價）* 50 * 1 - CostBuyPutPoint*50
3. 當結算日收盤價 > 買入履約價時損益為 -CostBuyPutPoint*50

**Total Position P&L:**
```
Total P&L = GetSellCallPoint*50 + GetSellPutPoint*50 - CostBuyCallPoint*50 - CostBuyPutPoint*50 +
            賣出買權部位損益 + 賣出賣權部位損益 + 買權避險組合單損益 + 賣權避險組合單損益
```

### Variable Naming Consistency

**Original:**
- GetSellCallPoint (Line 15) vs GetSellCallPoint0 (Line 50)
- GetSellPutPoint (Line 18) vs GetSellPutPoint0 (Line 50)
- CostBuyCallPoint (Line 20) vs CostCallPoint0 (Line 50)
- CostBuyPutPoint (Line 23) vs CostPutPoint0 (Line 50)

**Solution:**
Standardized to GetSellCallPoint, GetSellPutPoint, CostBuyCallPoint, CostBuyPutPoint throughout all formulas.

### Excel Field Structure

**Original:**
Single "權利金" column with ambiguous units

**Solution:**
Split into two columns:
| 權利金點數 | 權利金總額 |
|-----------|-----------|
| 400 | 20000 |

Updated all example data to clearly show both point values and total amounts (points * 50).

### Continuous Position Building Mechanism

**Original:**
"使用上一個建立部位指數價格" - Ambiguous when multiple positions exist

**Solution:**
Implemented chain-based monitoring:
- First position established at initial index price
- When index breaks through trigger range, establish new position at current index
- NEW position's establishment index becomes the NEW monitoring baseline
- Each position monitors independently using its own establishment index

**Example:**
- Position 1: Established at 30000, monitors 30000 ± 450 (n/2%)
- Index reaches 31000 → Position 2 established
- Position 2: Monitors 31000 ± 465 (31000 * 1.5%)
- Position 1 continues to exist until settlement date

## Implementation Requirements

### Core Parameters
- n (strike distance percentage)
- GetSellCallPoint (call rights premium points)
- GetSellPutPoint (put rights premium points)
- CostBuyCallPoint (call spread establishment cost)
- CostBuyPutPoint (put spread establishment cost)
- MaxOrder (maximum positions per month)

### Data Source
- Input: `assets\TSEA_加權指_日線.csv`
- Required fields: 日期, 開盤, 最高, 最低, 收盤

### Output Format
**Excel Sheet 1 - Tree View:**
- Parent level: Position sequence number
- Child level columns:
  | 月份 | 部位類型 | 建立時間 | 賣出履約價 | 買入履約價 | 權利金點數 | 權利金總額 | 結算日收盤價 | 總損益 |

**Excel Sheet 2 - Monthly P&L:**
- Bar chart showing each position's profit/loss

## Validation

### Verified Example Calculations

**Example 1 (Sold Call):**
- Index: 30000, n=3%, Strike: 30900, Premium: 400 points (20000)
- Settlement: 31500
- P&L: 400*50 - (31500-30900)*50 = -10000 ✓

**Example 2 (Sold Put):**
- Index: 30000, n=3%, Strike: 29100, Premium: 600 points (30000)
- Settlement: 31500
- P&L: 600*50 - 0 = 30000 ✓

**Example 3 (Call Spread):**
- Buy Strike: 31400, Sell Strike: 32300, Cost: 200 points (10000)
- Settlement: 31500 (between strikes)
- P&L: (31500-31400)*50 - 10000 = -5000 ✓

**Example 4 (Put Spread):**
- Buy Strike: 28500, Sell Strike: 27600, Cost: 200 points (10000)
- Settlement: 31500 (above both strikes)
- Both puts expire worthless
- P&L: -10000 ✓

## Technical Considerations

### Edge Cases
1. **Weekdays vs Settlement Date**: Find nearest trading day if 3rd Wednesday not in data
2. **Max Order Limit**: Enforce monthly position ceiling to prevent overtrading
3. **Index Price Selection**: Use opening price for initial establishment, high/low for triggers

### Performance Optimization
- Pre-calculate settlement dates for all months
- Chain-based monitoring O(n) where n = number of trading days
- Position management O(m) where m = max positions per month

## Testing Requirements

### Unit Tests
1. P&L calculation formulas under all market scenarios
2. Settlement date detection algorithm
3. Chain-based monitoring trigger logic

### Integration Tests
1. Monthly backtest with known historical results
2. Edge cases (index at extremes, minimal volatility)

### Validation Tests
1. Compare output against manual calculations
2. Verify Excel tree structure and data integrity

## Risk Mitigation

### Known Limitations
1. Historical option pricing data not available - using parameterized premiums
2. Spread legs may not have exact match in real market
3. No consideration of implied volatility changes

### Mitigation Strategies
1. Allow flexible premium parameter tuning
2. Document assumptions clearly in code
3. Add warning flags for unrealistic scenarios

## Next Steps

1. Implement Python backtesting engine
2. Create Excel output module with tree structure and charts
3. Build parameter configuration system
4. Add comprehensive test suite
5. Validate against historical data

## References

- Original specification: `skills/opsell/SKILL.md`
- Historical index data: `skills/opsell/assets/TSEA_加權指_日線.csv`
