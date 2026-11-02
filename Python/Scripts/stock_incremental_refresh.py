
# --------------------------------------------------
# Financial Market Intelligence & Currency Risk Analytics
# Banking Stocks Incremental Refresh Pipeline
# --------------------------------------------------

# 1. Import required libraries
import os
from pathlib import Path
from datetime import date, timedelta

import pandas as pd
import requests

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from pipeline_logger import get_logger


# --------------------------------------------------
# 2. Initialize environment and logger
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

logger = get_logger("Stock_Incremental_Refresh")

logger.info("Stock incremental refresh initialized")


# --------------------------------------------------
# 3. Establish PostgreSQL connection
# --------------------------------------------------

database_url = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME")
)

engine = create_engine(database_url)

with engine.connect() as connection:
    connection.execute(text("SELECT 1"))

logger.info("Stock PostgreSQL connection successful")

# --------------------------------------------------
# 4. Verify existing banking stock records
# --------------------------------------------------

logger.info("Stock database baseline verification started")

stock_baseline_query = text("""
    SELECT
        stock_symbol,
        COUNT(*) AS total_records,
        MIN(observation_date) AS earliest_date,
        MAX(observation_date) AS latest_date
    FROM public.banking_stocks
    GROUP BY stock_symbol
    ORDER BY stock_symbol
""")

with engine.connect() as connection:
    stock_results = connection.execute(
        stock_baseline_query
    ).fetchall()

expected_stocks = {
    "HDFCBANK.BSE",
    "ICICIBANK.BSE",
    "SBIN.BSE"
}

actual_stocks = {
    row.stock_symbol for row in stock_results
}

if actual_stocks != expected_stocks:
    raise ValueError(
        f"Stock symbols mismatch. "
        f"Expected: {expected_stocks}, "
        f"Found: {actual_stocks}"
    )

for row in stock_results:
    logger.info(
        "Stock: %s | Records: %s | "
        "Earliest Date: %s | Latest Date: %s",
        row.stock_symbol,
        row.total_records,
        row.earliest_date,
        row.latest_date
    )

logger.info("Stock database baseline verification completed")

# --------------------------------------------------
# 5. Calculate incremental stock date ranges
# --------------------------------------------------

logger.info("Incremental stock date range calculation started")

current_date = date.today()

logger.info("Current date: %s", current_date)

stock_date_ranges = []

for row in stock_results:

    latest_date = row.latest_date

    if hasattr(latest_date, "date"):
        latest_date = latest_date.date()

    start_date = latest_date + timedelta(days=1)
    end_date = current_date

    if start_date > end_date:
        logger.info(
            "%s | No new dates available",
            row.stock_symbol
        )
        continue

    stock_date_ranges.append({
        "stock_symbol": row.stock_symbol,
        "start_date": start_date,
        "end_date": end_date
    })

    logger.info(
        "%s | Fetch From: %s | Fetch To: %s",
        row.stock_symbol,
        start_date,
        end_date
    )

logger.info(
    "Incremental stock date range calculation completed"
)

# --------------------------------------------------
# 6. Extract incremental stock data from Alpha Vantage
# --------------------------------------------------

import time

logger.info("Incremental stock API extraction started")

api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

if not api_key:
    raise ValueError("ALPHA_VANTAGE_API_KEY is missing from .env")

incremental_stock_records = []

for index, stock in enumerate(stock_date_ranges):

    symbol = stock["stock_symbol"]
    start_date = stock["start_date"]
    end_date = stock["end_date"]

    # Space API requests to reduce rate-limit risk
    if index > 0:
        time.sleep(2)

    response = requests.get(
        "https://www.alphavantage.co/query",
        params={
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "compact",
            "apikey": api_key
        },
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    # API errors and rate-limit responses must not be
    # treated as an empty stock dataset.
    if "Error Message" in data:
        raise RuntimeError(
            f"{symbol} | Alpha Vantage error: "
            f"{data['Error Message']}"
        )

    if "Note" in data or "Information" in data:
        raise RuntimeError(
            f"{symbol} | Alpha Vantage API limit/message: "
            f"{data.get('Note', data.get('Information'))}"
        )

    daily_prices = data.get("Time Series (Daily)")

    if not isinstance(daily_prices, dict):
        raise RuntimeError(
            f"{symbol} | Expected daily price data missing"
        )

    new_count = 0
    stale_count = 0

    for observation_date, prices in daily_prices.items():

        trading_date = date.fromisoformat(observation_date)

        if trading_date < start_date:
            stale_count += 1
            continue

        if trading_date > end_date:
            raise ValueError(
                f"{symbol} | Unexpected future date: "
                f"{observation_date}"
            )

        incremental_stock_records.append({
            "observation_date": observation_date,
            "stock_symbol": symbol,
            "open_price": prices["1. open"],
            "high_price": prices["2. high"],
            "low_price": prices["3. low"],
            "close_price": prices["4. close"],
            "volume": prices["5. volume"]
        })

        new_count += 1

    logger.info(
        "%s | HTTP: %s | New Records: %s | "
        "Stale Records Skipped: %s",
        symbol,
        response.status_code,
        new_count,
        stale_count
    )

logger.info(
    "Incremental stock API extraction completed | "
    "Total New Records: %s",
    len(incremental_stock_records)
)

# --------------------------------------------------
# 7. Validate incremental banking stock data
# --------------------------------------------------

logger.info("Incremental stock data validation started")

stock_columns = [
    "observation_date",
    "stock_symbol",
    "open_price",
    "high_price",
    "low_price",
    "close_price",
    "volume"
]

stock_df = pd.DataFrame(
    incremental_stock_records,
    columns=stock_columns
)

if stock_df.empty:
    logger.info("No incremental stock records to validate")

else:
    stock_df["observation_date"] = pd.to_datetime(
        stock_df["observation_date"],
        errors="coerce"
    )

    price_columns = [
        "open_price",
        "high_price",
        "low_price",
        "close_price"
    ]

    for column in price_columns + ["volume"]:
        stock_df[column] = pd.to_numeric(
            stock_df[column],
            errors="coerce"
        )

    missing_values = int(
        stock_df.isna().sum().sum()
    )

    invalid_dates = int(
        stock_df["observation_date"].isna().sum()
    )

    duplicate_records = int(
        stock_df.duplicated(
            subset=["observation_date", "stock_symbol"]
        ).sum()
    )

    invalid_symbols = int(
        (~stock_df["stock_symbol"].isin(expected_stocks)).sum()
    )

    invalid_prices = int(
        (
            (stock_df[price_columns] <= 0).any(axis=1)
        ).sum()
    )

    invalid_ohlc = int(
        (
            (stock_df["high_price"] < stock_df["low_price"]) |
            (
                stock_df["high_price"] <
                stock_df[["open_price", "close_price"]].max(axis=1)
            ) |
            (
                stock_df["low_price"] >
                stock_df[["open_price", "close_price"]].min(axis=1)
            )
        ).sum()
    )

    invalid_volume = int(
        (
            (stock_df["volume"] < 0) |
            (stock_df["volume"] % 1 != 0)
        ).sum()
    )

    date_range_map = {
        item["stock_symbol"]: item
        for item in stock_date_ranges
    }

    invalid_date_ranges = 0

    for row in stock_df.itertuples(index=False):
        if pd.isna(row.observation_date):
            continue

        bounds = date_range_map.get(row.stock_symbol)

        if bounds is None or not (
            bounds["start_date"]
            <= row.observation_date.date()
            <= bounds["end_date"]
        ):
            invalid_date_ranges += 1

    logger.info("Total API Records: %s", len(stock_df))
    logger.info("Missing Values: %s", missing_values)
    logger.info("Invalid Dates: %s", invalid_dates)
    logger.info("Duplicate Records: %s", duplicate_records)
    logger.info("Invalid Stock Symbols: %s", invalid_symbols)
    logger.info("Invalid Prices: %s", invalid_prices)
    logger.info("Invalid OHLC Relationships: %s", invalid_ohlc)
    logger.info("Invalid Volume: %s", invalid_volume)
    logger.info("Invalid Date Ranges: %s", invalid_date_ranges)

    validation_findings = sum([
        missing_values,
        duplicate_records,
        invalid_symbols,
        invalid_prices,
        invalid_ohlc,
        invalid_volume,
        invalid_date_ranges
    ])

    if validation_findings > 0:
        logger.error(
            "STOCK VALIDATION FAILED | Findings: %s",
            validation_findings
        )
        raise ValueError(
            "Incremental stock data validation failed"
        )

    logger.info(
        "Incremental stock data validation PASSED | Records: %s",
        len(stock_df)
    )

# --------------------------------------------------
# 8. Incremental PostgreSQL stock loading
# --------------------------------------------------

from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import insert

logger.info("Incremental stock PostgreSQL loading started")

if stock_df.empty:
    logger.info("No new stock records to load")

else:
    metadata = MetaData()

    stock_table = Table(
        "banking_stocks",
        metadata,
        schema="public",
        autoload_with=engine
    )

    records_to_insert = stock_df[
        [
            "observation_date",
            "stock_symbol",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume"
        ]
    ].copy()

    # Required source column
    records_to_insert["source"] = "Alpha Vantage"

    # Temporary flags; statistical outlier
    # detection will be implemented next
    records_to_insert["price_outlier"] = False
    records_to_insert["volume_outlier"] = False
    records_to_insert["is_outlier"] = False

    records_to_insert["observation_date"] = (
        records_to_insert["observation_date"].dt.date
    )

    records_to_insert["volume"] = (
        records_to_insert["volume"].astype("int64")
    )

    insert_records = records_to_insert.to_dict(
        orient="records"
    )

    logger.info(
        "Stock records prepared for loading: %s",
        len(insert_records)
    )

    statement = insert(stock_table).values(insert_records)

    statement = statement.on_conflict_do_nothing(
        index_elements=[
            "observation_date",
            "stock_symbol"
        ]
    )

    with engine.begin() as connection:
        result = connection.execute(statement)
        inserted_count = result.rowcount

    skipped_count = len(insert_records) - inserted_count

    logger.info(
        "Stock PostgreSQL loading completed | Inserted: %s",
        inserted_count
    )

    logger.info(
        "Duplicate/conflicting records skipped: %s",
        skipped_count
    )

    verification_query = text("""
        SELECT
            stock_symbol,
            COUNT(*) AS total_records,
            MAX(observation_date) AS latest_date
        FROM public.banking_stocks
        GROUP BY stock_symbol
        ORDER BY stock_symbol
    """)

    with engine.connect() as connection:
        verification_results = connection.execute(
            verification_query
        )

        for row in verification_results:
            logger.info(
                "POST-LOAD | %s | Records: %s | Latest Date: %s",
                row.stock_symbol,
                row.total_records,
                row.latest_date
            )

logger.info(
    "Incremental stock pipeline execution completed"
)

engine.dispose()

# --------------------------------------------------
# 9. Recalculate historical banking stock outliers
# --------------------------------------------------

logger.info("Banking stock outlier recalculation started")

historical_query = text("""
    SELECT
        observation_date,
        stock_symbol,
        close_price,
        volume,
        price_outlier,
        volume_outlier,
        is_outlier
    FROM public.banking_stocks
    ORDER BY stock_symbol, observation_date
""")

with engine.connect() as connection:
    df_stock_history = pd.read_sql(
        historical_query,
        connection
    )

if df_stock_history.empty:
    logger.info("No historical stock records available")

else:
    df_stock_history["close_price"] = pd.to_numeric(
        df_stock_history["close_price"]
    )

    df_stock_history["volume"] = pd.to_numeric(
        df_stock_history["volume"]
    )

    # Preserve existing flags for comparison
    previous_flags = df_stock_history[
        ["price_outlier", "volume_outlier", "is_outlier"]
    ].copy()

    df_stock_history["price_outlier"] = False
    df_stock_history["volume_outlier"] = False

    for symbol, group in df_stock_history.groupby(
        "stock_symbol"
    ):

        for column, flag_column in [
            ("close_price", "price_outlier"),
            ("volume", "volume_outlier")
        ]:
            q1 = group[column].quantile(0.25)
            q3 = group[column].quantile(0.75)

            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outlier_mask = (
                (group[column] < lower_bound) |
                (group[column] > upper_bound)
            )

            df_stock_history.loc[
                group.index, flag_column
            ] = outlier_mask

        logger.info(
            "%s | Price Outliers: %s | Volume Outliers: %s",
            symbol,
            int(
                df_stock_history.loc[
                    group.index, "price_outlier"
                ].sum()
            ),
            int(
                df_stock_history.loc[
                    group.index, "volume_outlier"
                ].sum()
            )
        )

    df_stock_history["is_outlier"] = (
        df_stock_history["price_outlier"] |
        df_stock_history["volume_outlier"]
    )

    flag_columns = [
        "price_outlier",
        "volume_outlier",
        "is_outlier"
    ]

    changed_mask = (
        df_stock_history[flag_columns]
        .ne(previous_flags)
        .any(axis=1)
    )

    changed_records = df_stock_history.loc[
        changed_mask
    ]

    logger.info(
        "Stock records requiring flag updates: %s",
        len(changed_records)
    )

    update_query = text("""
        UPDATE public.banking_stocks
        SET
            price_outlier = :price_outlier,
            volume_outlier = :volume_outlier,
            is_outlier = :is_outlier
        WHERE
            observation_date = :observation_date
            AND stock_symbol = :stock_symbol
    """)

    update_records = []

    for row in changed_records.itertuples(index=False):
        update_records.append({
            "observation_date": row.observation_date,
            "stock_symbol": row.stock_symbol,
            "price_outlier": bool(row.price_outlier),
            "volume_outlier": bool(row.volume_outlier),
            "is_outlier": bool(row.is_outlier)
        })

    if update_records:
        with engine.begin() as connection:
            connection.execute(
                update_query,
                update_records
            )

    logger.info(
        "Total Historical Records: %s",
        len(df_stock_history)
    )

    logger.info(
        "Total Price Outliers: %s",
        int(df_stock_history["price_outlier"].sum())
    )

    logger.info(
        "Total Volume Outliers: %s",
        int(df_stock_history["volume_outlier"].sum())
    )

    logger.info(
        "Total Unique Flagged Records: %s",
        int(df_stock_history["is_outlier"].sum())
    )

logger.info("Banking stock outlier recalculation completed")
