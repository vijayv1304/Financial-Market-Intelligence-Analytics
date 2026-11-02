
# Banking Stock Market Intelligence — Business Insights

## Project
Financial Market Intelligence & Currency Risk Analytics

## Business Objective
Analyze historical stock performance, volatility, trading
activity, and correlations for three Indian banking stocks.

The objective is to support financial market monitoring,
comparative performance analysis, and risk assessment.

## Analysis Period
May 22, 2026 – October 13, 2026

## Data Source
Alpha Vantage API

## Data Coverage
- 300 raw banking stock observations
- 3 out-of-period records excluded from analysis
- 297 validated and processed observations
- 99 observations per banking stock
- 98 daily return observations per stock
- 21 volume outliers retained for review

## 1. Historical Stock Price Performance

| Stock | First Close | Last Close | Price Return |
|---|---:|---:|---:|
| ICICI Bank | 1264.90 | 1360.20 | +7.53% |
| SBI | 949.10 | 955.90 | +0.72% |
| HDFC Bank | 766.40 | 714.20 | -6.81% |

Finding:
ICICI Bank delivered the highest historical price return.
HDFC Bank experienced a negative price return.

## 2. Historical Stock Volatility

| Stock | Daily Volatility | Annualized Volatility |
|---|---:|---:|
| HDFC Bank | 1.3787% | 21.8859% |
| SBI | 1.1630% | 18.4617% |
| ICICI Bank | 1.1173% | 17.7367% |

Finding:
HDFC Bank exhibited the highest historical volatility,
while ICICI Bank demonstrated the lowest volatility.

Annualized volatility uses a 252-trading-day convention.

## 3. Trading Volume Analysis

| Stock | Total Volume | Average Daily Volume | Outlier Days |
|---|---:|---:|---:|
| HDFC Bank | 207894787 | 2099947.34 | 2 |
| ICICI Bank | 93793998 | 947414.12 | 10 |
| SBI | 69476314 | 701780.95 | 9 |

Finding:
HDFC Bank recorded the highest average daily share volume.

ICICI Bank recorded the highest number of volume outliers.

Volume outliers were retained rather than automatically
removed during data validation.

## 4. Stock Return Correlation Analysis

| Stock Pair | Correlation |
|---|---:|
| ICICI Bank – SBI | 0.4874 |
| HDFC Bank – SBI | 0.3204 |
| HDFC Bank – ICICI Bank | 0.2295 |

Finding:
All three pairs exhibited positive historical correlations.

ICICI Bank and SBI demonstrated the strongest co-movement,
while HDFC Bank and ICICI Bank showed the weakest.

Correlations were calculated from 98 aligned daily
return observations per stock pair.

## 5. Risk and Performance Ranking

| Rank | Stock | Price Return | Annualized Volatility | Return/Volatility Ratio |
|---|---|---:|---:|---:|
| 1 | ICICI Bank | +7.53% | 17.7367% | 1.1413 |
| 2 | SBI | +0.72% | 18.4617% | 0.1908 |
| 3 | HDFC Bank | -6.81% | 21.8859% | -0.7199 |

Method:
Return-to-Volatility Ratio =
Annualized Arithmetic Average Daily Return /
Annualized Historical Volatility

Finding:
ICICI Bank demonstrated the most favorable historical
return-to-volatility relationship.

This indicator is not a Sharpe ratio.

## 6. Business Recommendations

1. Monitor ICICI Bank as the strongest historical
   performer within the analyzed sample.

2. Investigate HDFC Bank's negative price performance
   and comparatively high volatility.

3. Review unusually high-volume trading dates,
   especially for ICICI Bank and SBI.

4. Monitor correlations to understand potential
   concentration risk within banking-sector exposure.

5. Use return, volatility, and trading activity together
   rather than relying on a single performance metric.

## 7. Limitations

- Historical performance does not predict future returns.
- Price returns exclude dividends and transaction costs.
- Corporate-action adjustments are not independently verified.
- Trading volume alone does not establish market liquidity.
- Correlations may change during periods of market stress.
- Volume outliers remain flagged pending further review.
- Annualized average returns are arithmetic approximations.
- The analysis covers only three banking stocks.
- Banking stock analysis is separate from the import-payment
  currency exposure calculations.

## 8. Business Conclusion

ICICI Bank achieved the highest historical price return
and lowest annualized volatility among the three stocks.

HDFC Bank recorded the highest trading volume and volatility,
but experienced negative price performance.

All three stocks exhibited positive historical correlations,
with varying degrees of co-movement.

The findings support comparative banking stock market
intelligence and historical risk monitoring.
