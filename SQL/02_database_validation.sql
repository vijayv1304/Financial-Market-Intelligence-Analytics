
-- ============================================================
-- PROJECT: Financial Market Intelligence & Currency Risk Analytics
-- PHASE 5: Database Structure and Constraint Validation
-- FILE: 02_database_validation.sql
-- ============================================================

-- 1. Verify database connection
SELECT current_database() AS connected_database;


-- 2. Verify both tables exist
SELECT
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('fx_rates', 'banking_stocks')
ORDER BY table_name;


-- 3. Verify columns and data types
SELECT
    table_name,
    ordinal_position AS column_position,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN ('fx_rates', 'banking_stocks')
ORDER BY table_name, ordinal_position;


-- 4. Verify primary keys and constraints
SELECT
    conrelid::regclass AS table_name,
    conname AS constraint_name,
    contype AS constraint_type,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid IN (
    'public.fx_rates'::regclass,
    'public.banking_stocks'::regclass
)
ORDER BY table_name, constraint_name;


-- 5. Verify tables are empty before data loading
SELECT
    'fx_rates' AS table_name,
    COUNT(*) AS record_count
FROM fx_rates

UNION ALL

SELECT
    'banking_stocks' AS table_name,
    COUNT(*) AS record_count
FROM banking_stocks;