
-- ============================================================
-- PROJECT: Financial Market Intelligence & Currency Risk
-- MODULE: Banking Stock Market Intelligence
-- STEP 6.7: Banking Stock Price Performance
-- ============================================================
--
-- BUSINESS QUESTION:
-- Which banking stock delivered the highest historical
-- price return during the project analysis period?
--
-- BUSINESS OBJECTIVE:
-- Compare historical stock-price performance across
-- HDFC Bank, ICICI Bank, and State Bank of India.
--
-- DATA SOURCE:
-- public.banking_stocks (Alpha Vantage API)
--
-- METHODOLOGY:
-- 1. Identify first and last trading dates.
-- 2. Calculate opening and closing reference prices.
-- 3. Calculate minimum, maximum and average closing prices.
-- 4. Calculate absolute and percentage price changes.
--
-- NOTE:
-- Price return excludes dividends, transaction costs,
-- and corporate-action adjustments unless already
-- reflected in the source price series.
-- ============================================================

WITH stock_summary AS (

    SELECT
        stock_symbol,

        COUNT(*) AS total_observations,

        MIN(observation_date) AS first_trading_date,
        MAX(observation_date) AS last_trading_date,

        MIN(close_price) AS minimum_close_price,
        MAX(close_price) AS maximum_close_price,

        ROUND(
            AVG(close_price),
            2
        ) AS average_close_price,

        (ARRAY_AGG(
            close_price ORDER BY observation_date ASC
        ))[1] AS opening_reference_price,

        (ARRAY_AGG(
            close_price ORDER BY observation_date DESC
        ))[1] AS closing_reference_price

    FROM public.banking_stocks

    GROUP BY stock_symbol
)

SELECT
    stock_symbol,
    total_observations,

    first_trading_date,
    last_trading_date,

    opening_reference_price,
    closing_reference_price,

    minimum_close_price,
    maximum_close_price,
    average_close_price,

    ROUND(
        closing_reference_price - opening_reference_price,
        2
    ) AS absolute_price_change,

    ROUND(
        (
            (closing_reference_price - opening_reference_price)
            / NULLIF(opening_reference_price, 0)
        ) * 100,
        2
    ) AS price_return_pct

FROM stock_summary

ORDER BY price_return_pct DESC;


-- ============================================================
-- BUSINESS QUESTION 2:
-- Which banking stock has the highest historical volatility?
-- ============================================================
--
-- Business Objective:
-- Compare daily stock-price fluctuations to understand
-- relative market risk across three Indian banking stocks.
--
-- Method:
-- 1. Retrieve previous trading day's closing price.
-- 2. Calculate daily percentage returns.
-- 3. Calculate average daily returns.
-- 4. Calculate standard deviation of daily returns.
-- 5. Annualize volatility using SQRT(252).
-- 6. Identify the largest daily gain and loss.
--
-- Interpretation:
-- Higher volatility indicates greater historical
-- variability in daily stock returns.
--
-- Note:
-- Historical volatility does not predict future returns.
-- Consecutive available trading observations are used.
-- ============================================================

-- ============================================================
-- STEP 6.8: BANKING STOCK DAILY RETURN AND VOLATILITY
-- ============================================================

WITH stock_daily_prices AS (

    SELECT
        observation_date,
        stock_symbol,
        close_price,

        LAG(close_price) OVER (
            PARTITION BY stock_symbol
            ORDER BY observation_date
        ) AS previous_close_price

    FROM public.banking_stocks
),

stock_daily_returns AS (

    SELECT
        observation_date,
        stock_symbol,
        close_price,
        previous_close_price,

        (
            (close_price - previous_close_price)
            / NULLIF(previous_close_price, 0)
        ) * 100 AS daily_return_pct

    FROM stock_daily_prices

    WHERE previous_close_price IS NOT NULL
),

stock_volatility AS (

    SELECT
        stock_symbol,

        COUNT(*) AS return_observations,

        ROUND(
            AVG(daily_return_pct),
            4
        ) AS avg_daily_return_pct,

        ROUND(
            STDDEV_SAMP(daily_return_pct),
            4
        ) AS daily_volatility_pct,

        ROUND(
            (
                STDDEV_SAMP(daily_return_pct)
                * SQRT(252)
            )::NUMERIC,
            4
        ) AS annualized_volatility_pct,

        ROUND(
            MAX(daily_return_pct),
            4
        ) AS largest_daily_gain_pct,

        ROUND(
            MIN(daily_return_pct),
            4
        ) AS largest_daily_loss_pct

    FROM stock_daily_returns

    GROUP BY stock_symbol
)

SELECT
    stock_symbol,
    return_observations,
    avg_daily_return_pct,
    daily_volatility_pct,
    annualized_volatility_pct,
    largest_daily_gain_pct,
    largest_daily_loss_pct

FROM stock_volatility

ORDER BY annualized_volatility_pct DESC;


-- ============================================================
-- BUSINESS QUESTION 3:
-- Which banking stock experienced the highest trading
-- volume and unusual market activity?
-- ============================================================
--
-- Business Objective:
-- Compare historical trading activity across HDFC Bank,
-- ICICI Bank, and SBI.
--
-- Method:
-- 1. Calculate total and average daily traded volume.
-- 2. Identify minimum and maximum daily volume.
-- 3. Count volume outliers identified during validation.
-- 4. Calculate the percentage of outlier observations.
--
-- Interpretation:
-- Higher trading volume indicates more shares traded.
-- It does not automatically indicate higher liquidity
-- or positive investment performance.
--
-- Data Quality:
-- Previously flagged volume outliers are retained.
-- The existing volume_outlier flag is reused.
-- ============================================================

-- ============================================================
-- STEP 6.9: BANKING STOCK TRADING VOLUME ANALYSIS
-- ============================================================

SELECT
    stock_symbol,

    COUNT(*) AS trading_observations,

    SUM(volume) AS total_traded_volume,

    ROUND(
        AVG(volume),
        2
    ) AS avg_daily_volume,

    MIN(volume) AS minimum_daily_volume,

    MAX(volume) AS maximum_daily_volume,

    COUNT(*) FILTER (
        WHERE volume_outlier = TRUE
    ) AS volume_outlier_days,

    ROUND(
        (
            COUNT(*) FILTER (
                WHERE volume_outlier = TRUE
            ) * 100.0
            / NULLIF(COUNT(*), 0)
        ),
        2
    ) AS volume_outlier_pct

FROM public.banking_stocks

GROUP BY stock_symbol

ORDER BY avg_daily_volume DESC;


-- ============================================================
-- BUSINESS QUESTION 4:
-- How strongly are daily returns correlated across
-- HDFC Bank, ICICI Bank, and SBI?
-- ============================================================
--
-- Business Objective:
-- Evaluate historical co-movement among banking stocks.
--
-- Method:
-- 1. Calculate daily percentage returns using LAG.
-- 2. Align returns by observation_date.
-- 3. Calculate pairwise Pearson correlations.
-- 4. Count matched return observations.
--
-- Interpretation:
-- +1 = Perfect positive correlation
--  0 = No linear correlation
-- -1 = Perfect negative correlation
--
-- Note:
-- Correlation is historical and may change over time.
-- ============================================================

-- ============================================================
-- STEP 6.10: BANKING STOCK RETURN CORRELATION
-- ============================================================

WITH stock_daily_prices AS (

    SELECT
        observation_date,
        stock_symbol,
        close_price,

        LAG(close_price) OVER (
            PARTITION BY stock_symbol
            ORDER BY observation_date
        ) AS previous_close_price

    FROM public.banking_stocks
),

stock_daily_returns AS (

    SELECT
        observation_date,
        stock_symbol,

        (
            (close_price - previous_close_price)
            / NULLIF(previous_close_price, 0)
        ) * 100 AS daily_return_pct

    FROM stock_daily_prices

    WHERE previous_close_price IS NOT NULL
),

stock_pairs AS (

    SELECT
        a.stock_symbol AS stock_1,
        b.stock_symbol AS stock_2,
        a.observation_date,
        a.daily_return_pct AS return_1,
        b.daily_return_pct AS return_2

    FROM stock_daily_returns a

    JOIN stock_daily_returns b
        ON a.observation_date = b.observation_date
        AND a.stock_symbol < b.stock_symbol
)

SELECT
    stock_1,
    stock_2,

    COUNT(*) AS matched_return_days,

    ROUND(
        CORR(
            return_1::DOUBLE PRECISION,
            return_2::DOUBLE PRECISION
        )::NUMERIC,
        4
    ) AS correlation_coefficient

FROM stock_pairs

GROUP BY
    stock_1,
    stock_2

ORDER BY
    correlation_coefficient DESC;


-- ============================================================
-- BUSINESS QUESTION 5:
-- Which banking stock demonstrated the most favorable
-- historical return-to-volatility relationship?
-- ============================================================
--
-- Business Objective:
-- Compare historical price performance and volatility
-- across three Indian banking stocks.
--
-- Method:
-- 1. Calculate first and last closing prices.
-- 2. Calculate total price return.
-- 3. Calculate daily percentage returns.
-- 4. Calculate annualized volatility.
-- 5. Annualize the arithmetic average daily return.
-- 6. Calculate return-to-volatility ratio.
-- 7. Rank stocks by this indicator.
--
-- Return-to-Volatility Ratio:
-- Annualized Average Daily Return / Annualized Volatility
--
-- Important:
-- This is not a Sharpe ratio.
-- Annualized average daily return is an arithmetic
-- approximation, not a compounded annual return.
-- ============================================================

-- ============================================================
-- STEP 6.11: BANKING STOCK RISK-PERFORMANCE RANKING
-- ============================================================

WITH stock_prices AS (

    SELECT
        observation_date,
        stock_symbol,
        close_price,

        FIRST_VALUE(close_price) OVER (
            PARTITION BY stock_symbol
            ORDER BY observation_date
        ) AS first_close_price,

        LAG(close_price) OVER (
            PARTITION BY stock_symbol
            ORDER BY observation_date
        ) AS previous_close_price

    FROM public.banking_stocks
),

stock_returns AS (

    SELECT
        observation_date,
        stock_symbol,
        close_price,
        first_close_price,

        (
            (close_price - previous_close_price)
            / NULLIF(previous_close_price, 0)
        ) AS daily_return

    FROM stock_prices
),

stock_metrics AS (

    SELECT
        stock_symbol,

        COUNT(*) AS price_observations,

        MAX(first_close_price) AS first_close_price,

        (
            ARRAY_AGG(
                close_price ORDER BY observation_date DESC
            )
        )[1] AS last_close_price,

        AVG(daily_return) AS avg_daily_return,

        STDDEV_SAMP(daily_return) AS daily_volatility

    FROM stock_returns

    GROUP BY stock_symbol
),

performance_metrics AS (

    SELECT
        stock_symbol,
        price_observations,

        (
            (last_close_price - first_close_price)
            / NULLIF(first_close_price, 0)
        ) * 100 AS total_price_return_pct,

        avg_daily_return * 252 * 100
            AS annualized_avg_return_pct,

        daily_volatility * SQRT(252) * 100
            AS annualized_volatility_pct,

        (
            avg_daily_return * 252
            / NULLIF(
                daily_volatility * SQRT(252),
                0
            )
        ) AS return_volatility_ratio

    FROM stock_metrics
)

SELECT
    stock_symbol,

    price_observations,

    ROUND(
        total_price_return_pct,
        2
    ) AS total_price_return_pct,

    ROUND(
        annualized_avg_return_pct::NUMERIC,
        2
    ) AS annualized_avg_return_pct,

    ROUND(
        annualized_volatility_pct::NUMERIC,
        4
    ) AS annualized_volatility_pct,

    ROUND(
        return_volatility_ratio::NUMERIC,
        4
    ) AS return_volatility_ratio,

    DENSE_RANK() OVER (
        ORDER BY return_volatility_ratio DESC NULLS LAST
    ) AS performance_rank

FROM performance_metrics

ORDER BY performance_rank;
