
# FX Currency Risk — Business Insights

## Project
Financial Market Intelligence & Currency Risk Analytics

## Business Objective
Evaluate foreign-exchange exposure for an Indian import-payment
treasury team using historical USD/INR, EUR/INR, and GBP/INR rates.

## Analysis Period
May 21, 2026 – October 13, 2026

## Data Source
Frankfurter API

## Data Coverage
- 312 validated FX observations
- 104 observations per currency pair
- 103 daily returns per currency pair
- Six IQR-flagged observations retained for review

## 1. Historical Exchange Rate Performance

| Currency | Opening Rate | Closing Rate | Change |
|---|---:|---:|---:|
| USD/INR | 96.2100 | 95.2800 | -0.97% |
| GBP/INR | 129.1100 | 126.2100 | -2.25% |
| EUR/INR | 111.5885 | 106.6000 | -4.47% |

Finding:
All three foreign currencies weakened against INR between
the first and last observation dates.

## 2. Import Payment Cost Analysis

Assumption:
A hypothetical invoice of 100,000 foreign-currency units
for each of USD, EUR, and GBP.

- Opening total INR cost: ₹3,36,90,850
- Closing total INR cost: ₹3,28,09,000
- Illustrative cost reduction: ₹8,81,850

Finding:
The strengthening of INR reduced the hypothetical
settlement cost between the two observation dates.

## 3. Historical FX Volatility

| Currency | Daily Volatility | Annualized Volatility |
|---|---:|---:|
| GBP/INR | 0.3864% | 6.1332% |
| EUR/INR | 0.3713% | 5.8938% |
| USD/INR | 0.3104% | 4.9279% |

Finding:
GBP/INR demonstrated the highest historical volatility.
Annualized values use a 252-trading-day convention.

## 4. Import Exposure Stress Testing

Total illustrative INR exposure: ₹3,28,09,000

- 2% adverse currency movement: ₹6,56,180 additional cost
- 5% adverse currency movement: ₹16,40,450 additional cost

Finding:
An adverse 5% exchange-rate movement across all three
currencies would increase the hypothetical INR payment
requirement by ₹16.40 lakh.

## 5. Currency Risk Priority Ranking

| Priority | Currency | Risk Indicator (INR) |
|---|---|---:|
| 1 | GBP | 774,065.09 |
| 2 | EUR | 628,278.85 |
| 3 | USD | 469,531.50 |

Method:
Risk Indicator = Current INR Exposure × Annualized Volatility

Finding:
GBP represents the highest monitoring priority within
this illustrative portfolio.

The risk indicator is not a formal Value at Risk measure.

## 6. Treasury Recommendations

1. Monitor GBP exposure more closely because of its
   relatively high volatility and INR exposure.
2. Track payment due dates and outstanding invoices.
3. Use adverse FX scenarios for cash-flow planning.
4. Evaluate hedging requirements against treasury
   policies, existing contracts, and hedging costs.
5. Refresh exchange-rate data and risk indicators regularly.

## 7. Limitations

- Invoice amounts are hypothetical, not actual company data.
- Historical volatility does not predict future movements.
- Stress scenarios are assumptions, not forecasts.
- Transaction costs and existing hedges are excluded.
- Outlier observations are retained pending review.
- Currency risk rankings depend on the assumed exposures.
- Results are historical as of October 13, 2026.

## 8. Business Conclusion

The analysis demonstrates how historical exchange-rate
movements affect INR-denominated import-payment costs.

GBP/INR has the highest exposure-weighted volatility
indicator in the illustrative portfolio.

These findings support treasury monitoring, cash-flow
scenario planning, and risk prioritization.
