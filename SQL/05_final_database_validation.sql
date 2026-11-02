
-- ============================================================
-- PROJECT: Financial Market Intelligence & Currency Risk Analytics
-- PHASE 5: Final PostgreSQL Integration Validation
-- FILE: 05_final_database_validation.sql
-- ============================================================

-- 1. Confirm database connection
SELECT current_database() AS database_name;


-- 2. Combined dataset record counts
SELECT
    'FX Rates' AS dataset,
    COUNT(*) AS total_records
FROM public.fx_rates

UNION ALL

SELECT
    'Banking Stocks' AS dataset,
    COUNT(*) AS total_records
FROM public.banking_stocks;


-- 3. Combined database record count
SELECT
    (SELECT COUNT(*) FROM public.fx_rates)
    +
    (SELECT COUNT(*) FROM public.banking_stocks)
    AS total_database_records;


-- 4. Compare unique observation dates
SELECT
    (SELECT COUNT(DISTINCT observation_date)
     FROM public.fx_rates) AS fx_unique_dates,

    (SELECT COUNT(DISTINCT observation_date)
     FROM public.banking_stocks) AS stock_unique_dates,

    (
        SELECT COUNT(*)
        FROM (
            SELECT DISTINCT observation_date
            FROM public.fx_rates

            INTERSECT

            SELECT DISTINCT observation_date
            FROM public.banking_stocks
        ) AS common_dates
    ) AS shared_dates;


-- 5. Identify stock dates without FX observations
SELECT DISTINCT
    s.observation_date
FROM public.banking_stocks AS s
WHERE NOT EXISTS (
    SELECT 1
    FROM public.fx_rates AS f
    WHERE f.observation_date = s.observation_date
)
ORDER BY s.observation_date;


-- 6. Confirm shared-date coverage for each stock
SELECT
    s.stock_symbol,
    COUNT(*) AS stock_records,

    COUNT(*) FILTER (
        WHERE EXISTS (
            SELECT 1
            FROM public.fx_rates AS f
            WHERE f.observation_date = s.observation_date
        )
    ) AS records_with_fx_date

FROM public.banking_stocks AS s
GROUP BY s.stock_symbol
ORDER BY s.stock_symbol;


-- 7. Validate outlier counts across both datasets
SELECT
    'FX Rates' AS dataset,
    COUNT(*) FILTER (
        WHERE is_outlier = TRUE
    ) AS flagged_outliers
FROM public.fx_rates

UNION ALL

SELECT
    'Banking Stocks' AS dataset,
    COUNT(*) FILTER (
        WHERE is_outlier = TRUE
    ) AS flagged_outliers
FROM public.banking_stocks;


-- 8. Final integrated validation status
WITH validation_checks AS (
    SELECT
        (SELECT COUNT(*) FROM public.fx_rates) = 312
            AS fx_count_valid,

        (SELECT COUNT(*) FROM public.banking_stocks) = 297
            AS stock_count_valid,

        (SELECT COUNT(*) FROM public.fx_rates
         WHERE is_outlier = TRUE) = 6
            AS fx_outliers_valid,

        (SELECT COUNT(*) FROM public.banking_stocks
         WHERE is_outlier = TRUE) = 21
            AS stock_outliers_valid,

        NOT EXISTS (
            SELECT 1
            FROM public.banking_stocks AS s
            WHERE NOT EXISTS (
                SELECT 1
                FROM public.fx_rates AS f
                WHERE f.observation_date = s.observation_date
            )
        ) AS date_alignment_valid
)
SELECT
    *,
    CASE
        WHEN fx_count_valid
         AND stock_count_valid
         AND fx_outliers_valid
         AND stock_outliers_valid
         AND date_alignment_valid
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS overall_status
FROM validation_checks;
