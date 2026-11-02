
-- ============================================================
-- PROJECT: Financial Market Intelligence & Currency Risk Analytics
-- PHASE 5: FX Data Reconciliation
-- FILE: 03_fx_data_reconciliation.sql
-- ============================================================

-- 1. Total records and unique business keys
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT (
        observation_date,
        base_currency,
        quote_currency
    )) AS unique_business_keys
FROM public.fx_rates;


-- 2. Currency pair distribution
SELECT
    base_currency,
    quote_currency,
    COUNT(*) AS observation_count,
    MIN(observation_date) AS first_date,
    MAX(observation_date) AS last_date
FROM public.fx_rates
GROUP BY base_currency, quote_currency
ORDER BY base_currency;


-- 3. Missing mandatory values
SELECT
    COUNT(*) FILTER (
        WHERE observation_date IS NULL
           OR base_currency IS NULL
           OR quote_currency IS NULL
           OR exchange_rate IS NULL
           OR source IS NULL
           OR is_outlier IS NULL
    ) AS records_with_missing_values
FROM public.fx_rates;


-- 4. Invalid exchange rates
SELECT
    COUNT(*) AS invalid_exchange_rates
FROM public.fx_rates
WHERE exchange_rate <= 0;


-- 5. Outlier reconciliation
SELECT
    base_currency,
    COUNT(*) AS total_records,
    COUNT(*) FILTER (
        WHERE is_outlier = TRUE
    ) AS flagged_outliers
FROM public.fx_rates
GROUP BY base_currency
ORDER BY base_currency;


-- 6. Source verification
SELECT
    source,
    COUNT(*) AS record_count
FROM public.fx_rates
GROUP BY source;


-- 7. Overall date coverage
SELECT
    MIN(observation_date) AS earliest_date,
    MAX(observation_date) AS latest_date,
    COUNT(DISTINCT observation_date) AS unique_dates
FROM public.fx_rates;


-- 8. Overall reconciliation summary
SELECT
    COUNT(*) AS total_records,
    COUNT(*) FILTER (
        WHERE is_outlier = TRUE
    ) AS total_outliers,
    MIN(exchange_rate) AS minimum_exchange_rate,
    MAX(exchange_rate) AS maximum_exchange_rate,
    ROUND(AVG(exchange_rate), 4) AS average_exchange_rate
FROM public.fx_rates;
