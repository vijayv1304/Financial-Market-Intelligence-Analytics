
-- ============================================================
-- PROJECT: Financial Market Intelligence & Currency Risk Analytics
-- PHASE 5: PostgreSQL Database Design
-- FILE: 01_database_schema.sql
-- DATABASE: financial_market_analytics
-- ============================================================

-- Business Objective:
-- Store validated FX and banking stock data in structured
-- relational tables for SQL analysis and Power BI reporting.

-- ============================================================
-- TABLE 1: FX RATES
-- ============================================================

CREATE TABLE IF NOT EXISTS fx_rates (

    observation_date DATE NOT NULL,

    base_currency VARCHAR(3) NOT NULL,

    quote_currency VARCHAR(3) NOT NULL,

    exchange_rate NUMERIC(18,6) NOT NULL,

    source VARCHAR(50) NOT NULL,

    is_outlier BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT pk_fx_rates
        PRIMARY KEY (
            observation_date,
            base_currency,
            quote_currency
        ),

    CONSTRAINT chk_fx_positive_rate
        CHECK (exchange_rate > 0),

    CONSTRAINT chk_fx_base_currency
        CHECK (base_currency IN ('USD', 'EUR', 'GBP')),

    CONSTRAINT chk_fx_quote_currency
        CHECK (quote_currency = 'INR')
);


-- ============================================================
-- TABLE 2: BANKING STOCKS
-- ============================================================

CREATE TABLE IF NOT EXISTS banking_stocks (

    observation_date DATE NOT NULL,

    stock_symbol VARCHAR(30) NOT NULL,

    open_price NUMERIC(18,4) NOT NULL,

    high_price NUMERIC(18,4) NOT NULL,

    low_price NUMERIC(18,4) NOT NULL,

    close_price NUMERIC(18,4) NOT NULL,

    volume BIGINT NOT NULL,

    source VARCHAR(50) NOT NULL,

    price_outlier BOOLEAN NOT NULL DEFAULT FALSE,

    volume_outlier BOOLEAN NOT NULL DEFAULT FALSE,

    is_outlier BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT pk_banking_stocks
        PRIMARY KEY (
            observation_date,
            stock_symbol
        ),

    CONSTRAINT chk_stock_positive_prices
        CHECK (
            open_price > 0
            AND high_price > 0
            AND low_price > 0
            AND close_price > 0
        ),

    CONSTRAINT chk_stock_price_range
        CHECK (
            high_price >= open_price
            AND high_price >= close_price
            AND low_price <= open_price
            AND low_price <= close_price
            AND high_price >= low_price
        ),

    CONSTRAINT chk_stock_volume
        CHECK (volume >= 0),

    CONSTRAINT chk_stock_symbol
        CHECK (
            stock_symbol IN (
                'HDFCBANK.BSE',
                'ICICIBANK.BSE',
                'SBIN.BSE'
            )
        )
);

-- ============================================================
-- END OF DATABASE SCHEMA
-- ============================================================
