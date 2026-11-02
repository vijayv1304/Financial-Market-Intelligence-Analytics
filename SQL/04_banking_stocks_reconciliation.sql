
-- ============================================================
-- PROJECT: Financial Market Intelligence & Currency Risk Analytics
-- PHASE 5: Banking Stock Data Reconciliation
-- FILE: 04_banking_stocks_reconciliation.sql
-- ============================================================

-- 1. Total records and unique business keys
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT (
        observation_date,
        stock_symbol
    )) AS unique_business_keys
FROM public.banking_stocks;


-- 2. Stock-wise record distribution and date coverage
SELECT
    stock_symbol,
    COUNT(*) AS observation_count,
    MIN(observation_date) AS first_date,
    MAX(observation_date) AS last_date,
    COUNT(DISTINCT observation_date) AS unique_dates
FROM public.banking_stocks
GROUP BY stock_symbol
ORDER BY stock_symbol;


-- 3. Missing mandatory values
SELECT
    COUNT(*) FILTER (
        WHERE observation_date IS NULL
           OR stock_symbol IS NULL
           OR open_price IS NULL
           OR high_price IS NULL
           OR low_price IS NULL
           OR close_price IS NULL
           OR volume IS NULL
           OR source IS NULL
           OR price_outlier IS NULL
           OR volume_outlier IS NULL
           OR is_outlier IS NULL
    ) AS records_with_missing_values
FROM public.banking_stocks;


-- 4. Invalid OHLC prices and trading volumes
SELECT
    COUNT(*) FILTER (
        WHERE open_price <= 0
           OR high_price <= 0
           OR low_price <= 0
           OR close_price <= 0
    ) AS invalid_prices,

    COUNT(*) FILTER (
        WHERE high_price < open_price
           OR high_price < close_price
           OR low_price > open_price
           OR low_price > close_price
           OR high_price < low_price
    ) AS invalid_ohlc_relationships,

    COUNT(*) FILTER (
        WHERE volume < 0
    ) AS negative_volume_records

FROM public.banking_stocks;


-- 5. Statistical outlier reconciliation
SELECT
    stock_symbol,
    COUNT(*) AS total_records,

    COUNT(*) FILTER (
        WHERE price_outlier = TRUE
    ) AS price_outliers,

    COUNT(*) FILTER (
        WHERE volume_outlier = TRUE
    ) AS volume_outliers,

    COUNT(*) FILTER (
        WHERE is_outlier = TRUE
    ) AS total_flagged_records

FROM public.banking_stocks
GROUP BY stock_symbol
ORDER BY stock_symbol;


-- 6. Verify outlier flag consistency
SELECT
    COUNT(*) AS inconsistent_outlier_flags
FROM public.banking_stocks
WHERE is_outlier IS DISTINCT FROM
      (price_outlier OR volume_outlier);


-- 7. Verify source and approved stock symbols
SELECT
    stock_symbol,
    source,
    COUNT(*) AS record_count
FROM public.banking_stocks
GROUP BY stock_symbol, source
ORDER BY stock_symbol;


-- 8. Verify project date boundaries
SELECT
    MIN(observation_date) AS earliest_date,
    MAX(observation_date) AS latest_date,

    COUNT(*) FILTER (
        WHERE observation_date < DATE '2026-05-21'
           OR observation_date > DATE '2026-10-13'
    ) AS records_outside_project_period

FROM public.banking_stocks;


-- 9. Verify stock trading dates against FX dates
SELECT
    COUNT(*) AS stock_records_without_fx_date
FROM public.banking_stocks AS s
WHERE NOT EXISTS (
    SELECT 1
    FROM public.fx_rates AS f
    WHERE f.observation_date = s.observation_date
);


-- 10. Overall banking stock reconciliation
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT stock_symbol) AS total_stocks,

    COUNT(*) FILTER (
        WHERE is_outlier = TRUE
    ) AS total_outliers,

    MIN(close_price) AS minimum_close_price,
    MAX(close_price) AS maximum_close_price,

    SUM(volume) AS total_trading_volume

FROM public.banking_stocks;
