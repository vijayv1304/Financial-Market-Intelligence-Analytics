
-- ============================================================
-- PROJECT: Financial Market Intelligence & Currency Risk Analytics
-- PHASE 6: FX Business Analysis
-- FILE: 06_fx_business_analysis.sql
-- ============================================================

-- BUSINESS QUESTION 1:
-- How have foreign exchange rates changed against INR
-- during the project analysis period?

WITH fx_summary AS (
    SELECT
        base_currency,
        quote_currency,

        COUNT(*) AS total_observations,

        MIN(observation_date) AS first_date,
        MAX(observation_date) AS last_date,

        MIN(exchange_rate) AS minimum_rate,
        MAX(exchange_rate) AS maximum_rate,

        ROUND(AVG(exchange_rate), 4) AS average_rate,

        (ARRAY_AGG(
            exchange_rate
            ORDER BY observation_date ASC
        ))[1] AS opening_rate,

        (ARRAY_AGG(
            exchange_rate
            ORDER BY observation_date DESC
        ))[1] AS closing_rate

    FROM public.fx_rates

    GROUP BY
        base_currency,
        quote_currency
)

SELECT
    base_currency || '/' || quote_currency
        AS currency_pair,

    total_observations,

    first_date,
    last_date,

    opening_rate,
    closing_rate,

    minimum_rate,
    maximum_rate,
    average_rate,

    ROUND(
        closing_rate - opening_rate,
        4
    ) AS absolute_change,

    ROUND(
        (
            (closing_rate - opening_rate)
            / NULLIF(opening_rate, 0)
        ) * 100,
        2
    ) AS percentage_change

FROM fx_summary

ORDER BY percentage_change DESC;


-- ============================================================
-- BUSINESS QUESTION 2:
-- How did FX movements affect INR import payment costs?
--
-- SCENARIO:
-- Fixed foreign-currency invoices of 100,000 units each.
-- Compare opening-date and closing-date INR costs.
-- ============================================================

WITH import_exposure AS (
    SELECT
        'USD' AS currency,
        100000::NUMERIC AS invoice_amount

    UNION ALL

    SELECT 'EUR', 100000::NUMERIC

    UNION ALL

    SELECT 'GBP', 100000::NUMERIC
),

fx_rates_ranked AS (
    SELECT
        base_currency,
        observation_date,
        exchange_rate,

        ROW_NUMBER() OVER (
            PARTITION BY base_currency
            ORDER BY observation_date ASC
        ) AS first_rank,

        ROW_NUMBER() OVER (
            PARTITION BY base_currency
            ORDER BY observation_date DESC
        ) AS last_rank

    FROM public.fx_rates
),

fx_open_close AS (
    SELECT
        base_currency,

        MAX(exchange_rate) FILTER (
            WHERE first_rank = 1
        ) AS opening_rate,

        MAX(exchange_rate) FILTER (
            WHERE last_rank = 1
        ) AS closing_rate

    FROM fx_rates_ranked
    GROUP BY base_currency
)

SELECT
    e.currency,
    e.invoice_amount,

    f.opening_rate,
    f.closing_rate,

    ROUND(
        e.invoice_amount * f.opening_rate,
        2
    ) AS opening_inr_cost,

    ROUND(
        e.invoice_amount * f.closing_rate,
        2
    ) AS closing_inr_cost,

    ROUND(
        e.invoice_amount *
        (f.closing_rate - f.opening_rate),
        2
    ) AS inr_cost_change,

    ROUND(
        (
            (f.closing_rate - f.opening_rate)
            / NULLIF(f.opening_rate, 0)
        ) * 100,
        2
    ) AS cost_change_pct,

    CASE
        WHEN f.closing_rate < f.opening_rate
            THEN 'Favorable - Lower INR Cost'

        WHEN f.closing_rate > f.opening_rate
            THEN 'Unfavorable - Higher INR Cost'

        ELSE 'No Change'
    END AS importer_impact

FROM import_exposure e

JOIN fx_open_close f
    ON e.currency = f.base_currency

ORDER BY e.currency;


-- ============================================================
-- BUSINESS QUESTION 3:
-- Which currency exhibits the highest daily FX volatility?
-- ============================================================
--
-- Business Objective:
-- Measure historical exchange-rate fluctuations to assess
-- currency risk for an Indian import-payment treasury team.
--
-- Method:
-- 1. Calculate previous observation's exchange rate using LAG.
-- 2. Calculate daily percentage returns.
-- 3. Calculate daily return standard deviation.
-- 4. Annualize volatility using SQRT(252).
-- 5. Identify largest positive and negative daily returns.
--
-- Interpretation:
-- Higher volatility indicates greater historical variability
-- in daily FX movements, not necessarily a future loss.
--
-- Data Consideration:
-- Calculations use consecutive available observations.
-- Weekend gaps do not represent separate daily returns.
-- Statistical outliers are retained.


-- ============================================================
-- STEP 6.3: DAILY FX VOLATILITY ANALYSIS
-- ============================================================

WITH fx_daily_rates AS (

    SELECT
        observation_date,
        base_currency,
        quote_currency,
        exchange_rate,

        LAG(exchange_rate) OVER (
            PARTITION BY base_currency, quote_currency
            ORDER BY observation_date
        ) AS previous_rate

    FROM public.fx_rates
),

fx_daily_returns AS (

    SELECT
        observation_date,
        base_currency,
        quote_currency,
        exchange_rate,
        previous_rate,

        (
            (exchange_rate - previous_rate)
            / NULLIF(previous_rate, 0)
        ) * 100 AS daily_return_pct

    FROM fx_daily_rates

    WHERE previous_rate IS NOT NULL
),

fx_volatility AS (

    SELECT
        base_currency,
        quote_currency,

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
        ) AS largest_daily_increase_pct,

        ROUND(
            MIN(daily_return_pct),
            4
        ) AS largest_daily_decrease_pct

    FROM fx_daily_returns

    GROUP BY
        base_currency,
        quote_currency
)

SELECT
    base_currency || '/' || quote_currency
        AS currency_pair,

    return_observations,

    avg_daily_return_pct,

    daily_volatility_pct,

    annualized_volatility_pct,

    largest_daily_increase_pct,

    largest_daily_decrease_pct

FROM fx_volatility

ORDER BY annualized_volatility_pct DESC;


-- ============================================================
-- BUSINESS QUESTION 4:
-- How much additional INR would be required if foreign
-- currencies appreciated by 2% or 5%?
-- ============================================================
--
-- Business Objective:
-- Estimate potential increases in import-payment costs
-- under hypothetical adverse FX movements.
--
-- Scenario Assumptions:
-- USD invoice: 100,000
-- EUR invoice: 100,000
-- GBP invoice: 100,000
--
-- Base Rate:
-- Latest available exchange rate: October 13, 2026.
--
-- Stress Scenarios:
-- Scenario 1: Foreign currency appreciates 2%.
-- Scenario 2: Foreign currency appreciates 5%.
--
-- Business Interpretation:
-- Higher INR payment requirements represent potential
-- additional costs for an unhedged importer.
--
-- Note:
-- This is deterministic scenario analysis, not
-- a probability-based risk forecast.


-- ============================================================
-- STEP 6.4: FX IMPORT EXPOSURE STRESS TEST
-- ============================================================

WITH import_exposure AS (

    SELECT
        'USD' AS currency,
        100000::NUMERIC AS invoice_amount

    UNION ALL

    SELECT 'EUR', 100000::NUMERIC

    UNION ALL

    SELECT 'GBP', 100000::NUMERIC
),

latest_fx_rates AS (

    SELECT DISTINCT ON (base_currency)
        base_currency,
        observation_date,
        exchange_rate AS current_rate

    FROM public.fx_rates

    ORDER BY
        base_currency,
        observation_date DESC
),

exposure_calculation AS (

    SELECT
        e.currency,
        e.invoice_amount,
        f.observation_date AS rate_date,
        f.current_rate,

        e.invoice_amount * f.current_rate
            AS current_inr_exposure

    FROM import_exposure e

    JOIN latest_fx_rates f
        ON e.currency = f.base_currency
)

SELECT
    currency,
    invoice_amount,
    rate_date,
    current_rate,

    ROUND(
        current_inr_exposure, 2
    ) AS current_inr_exposure,

    ROUND(
        current_inr_exposure * 1.02, 2
    ) AS stressed_inr_cost_2pct,

    ROUND(
        current_inr_exposure * 0.02, 2
    ) AS additional_cost_2pct,

    ROUND(
        current_inr_exposure * 1.05, 2
    ) AS stressed_inr_cost_5pct,

    ROUND(
        current_inr_exposure * 0.05, 2
    ) AS additional_cost_5pct

FROM exposure_calculation

ORDER BY currency;



-- ============================================================
-- BUSINESS QUESTION 5:
-- Which currency exposure should the treasury team
-- prioritize for risk monitoring?
-- ============================================================
--
-- Business Objective:
-- Combine historical FX volatility with outstanding INR
-- exposure to develop a comparative monitoring ranking.
--
-- Method:
-- 1. Calculate daily FX returns.
-- 2. Calculate annualized historical volatility.
-- 3. Calculate current INR exposure.
-- 4. Calculate additional cost under a 5% stress scenario.
-- 5. Rank currencies using an exposure-weighted
--    volatility indicator.
--
-- Risk Indicator:
-- Current INR Exposure * Annualized Volatility
--
-- Interpretation:
-- A higher indicator suggests greater exposure to
-- historical exchange-rate variability.
--
-- Important:
-- This indicator is for comparative monitoring only.
-- It is not Value at Risk, expected loss, or a
-- probability-based estimate of future losses.
-- ============================================================

-- ============================================================
-- STEP 6.5: CURRENCY RISK PRIORITY RANKING
-- ============================================================

WITH import_exposure AS (
    SELECT 'USD' AS currency, 100000::NUMERIC AS invoice_amount
    UNION ALL
    SELECT 'EUR', 100000::NUMERIC
    UNION ALL
    SELECT 'GBP', 100000::NUMERIC
),

fx_daily_rates AS (
    SELECT
        base_currency,
        observation_date,
        exchange_rate,

        LAG(exchange_rate) OVER (
            PARTITION BY base_currency
            ORDER BY observation_date
        ) AS previous_rate

    FROM public.fx_rates
),

fx_daily_returns AS (
    SELECT
        base_currency,

        (
            (exchange_rate - previous_rate)
            / NULLIF(previous_rate, 0)
        ) AS daily_return

    FROM fx_daily_rates
    WHERE previous_rate IS NOT NULL
),

fx_volatility AS (
    SELECT
        base_currency,

        STDDEV_SAMP(daily_return)
            * SQRT(252) AS annualized_volatility

    FROM fx_daily_returns
    GROUP BY base_currency
),

latest_fx AS (
    SELECT DISTINCT ON (base_currency)
        base_currency,
        observation_date,
        exchange_rate

    FROM public.fx_rates

    ORDER BY
        base_currency,
        observation_date DESC
),

risk_calculation AS (
    SELECT
        e.currency,
        e.invoice_amount,
        f.observation_date AS rate_date,
        f.exchange_rate AS current_rate,

        e.invoice_amount * f.exchange_rate
            AS current_inr_exposure,

        v.annualized_volatility,

        (
            e.invoice_amount * f.exchange_rate
            * v.annualized_volatility
        ) AS risk_indicator

    FROM import_exposure e

    JOIN latest_fx f
        ON e.currency = f.base_currency

    JOIN fx_volatility v
        ON e.currency = v.base_currency
)

SELECT
    currency,

    ROUND(current_inr_exposure, 2)
        AS current_inr_exposure,

    ROUND(
        (annualized_volatility * 100)::NUMERIC,
        4
    ) AS annualized_volatility_pct,

    ROUND(
        current_inr_exposure * 0.05,
        2
    ) AS additional_cost_5pct,

    ROUND(
        risk_indicator::NUMERIC,
        2
    ) AS risk_indicator,

    DENSE_RANK() OVER (
        ORDER BY risk_indicator DESC
    ) AS risk_priority_rank

FROM risk_calculation

ORDER BY risk_priority_rank;
