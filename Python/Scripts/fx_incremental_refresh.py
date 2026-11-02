
from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from pipeline_logger import get_logger


# --------------------------------------------------
# 1. Project configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

logger = get_logger("FX_Incremental_Refresh")


# --------------------------------------------------
# 2. PostgreSQL connection
# --------------------------------------------------

database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME")
)

engine = create_engine(
    database_url,
    pool_pre_ping=True
)


# --------------------------------------------------
# 3. Identify latest stored FX dates
# --------------------------------------------------

query = text("""
    SELECT
        base_currency,
        MAX(observation_date) AS latest_date,
        COUNT(*) AS total_records
    FROM public.fx_rates
    WHERE quote_currency = 'INR'
    GROUP BY base_currency
    ORDER BY base_currency
""")


with engine.connect() as connection:
    results = connection.execute(query).fetchall()


# --------------------------------------------------
# 4. Log current database state
# --------------------------------------------------

logger.info("FX incremental refresh initialized")

for row in results:
    logger.info(
        "Currency: %s/INR | Latest Date: %s | Records: %s",
        row.base_currency,
        row.latest_date,
        row.total_records
    )

logger.info("FX database baseline verification completed")

engine.dispose()

from datetime import date, timedelta

# --------------------------------------------------
# 5. Calculate incremental refresh date ranges
# --------------------------------------------------

today = date.today()

logger.info("Incremental FX date range calculation started")
logger.info("Current date: %s", today)

for row in results:

    latest_date = row.latest_date

    # Convert to date if PostgreSQL returns a datetime.
    if hasattr(latest_date, "date"):
        latest_date = latest_date.date()

    start_date = latest_date + timedelta(days=1)
    end_date = today

    if start_date > end_date:
        logger.info(
            "%s/INR | No new dates to fetch",
            row.base_currency
        )
    else:
        logger.info(
            "%s/INR | Fetch From: %s | Fetch To: %s",
            row.base_currency,
            start_date,
            end_date
        )

logger.info("Incremental FX date range calculation completed")


# --------------------------------------------------
# 6. Fetch incremental FX data from Frankfurter API
# --------------------------------------------------

import requests

logger.info("Incremental FX API extraction started")

incremental_fx_records = []

for row in results:

    latest_date = row.latest_date

    if hasattr(latest_date, "date"):
        latest_date = latest_date.date()

    start_date = latest_date + timedelta(days=1)
    end_date = date.today()

    if start_date > end_date:
        logger.info(
            "%s/INR | No new dates available",
            row.base_currency
        )
        continue

    url = (
        f"https://api.frankfurter.dev/v1/"
        f"{start_date.isoformat()}..{end_date.isoformat()}"
    )

    params = {
        "base": row.base_currency,
        "symbols": "INR"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        rates = data.get("rates", {})
        currency_count = 0

        for observation_date, currency_rates in rates.items():

            api_date = date.fromisoformat(observation_date)

            # Skip observations already covered by PostgreSQL
            if api_date < start_date:
                logger.info(
                    "%s/INR | Skipping stale API observation: %s",
                    row.base_currency,
                    observation_date
                )
                continue

            # Reject observations beyond the requested end date
            if api_date > end_date:
                raise ValueError(
                    f"{row.base_currency}/INR returned "
                    f"an unexpected future date: {observation_date}"
                )

            exchange_rate = currency_rates.get("INR")

            if exchange_rate is None:
                continue

            incremental_fx_records.append({
                "observation_date": observation_date,
                "base_currency": row.base_currency,
                "quote_currency": "INR",
                "exchange_rate": exchange_rate
            })

            currency_count += 1

        logger.info(
            "%s/INR | HTTP: %s | New API Records: %s",
            row.base_currency,
            response.status_code,
            currency_count
        )

    except requests.RequestException as error:
        logger.error(
            "%s/INR | API extraction failed: %s",
            row.base_currency,
            error
        )
        raise

logger.info(
    "Incremental FX API extraction completed | Total Records: %s",
    len(incremental_fx_records)
)

# --------------------------------------------------
# 7. Validate incremental FX records
# --------------------------------------------------

import pandas as pd

logger.info("Incremental FX data validation started")

fx_df = pd.DataFrame(
    incremental_fx_records,
    columns=[
        "observation_date",
        "base_currency",
        "quote_currency",
        "exchange_rate"
    ]
)

if fx_df.empty:
    logger.info("No incremental FX records to validate")

else:
    # 1. Validate required fields
    missing_values = int(fx_df.isnull().sum().sum())

    # 2. Validate dates
    fx_df["observation_date"] = pd.to_datetime(
        fx_df["observation_date"],
        errors="coerce"
    )

    invalid_dates = int(
        fx_df["observation_date"].isna().sum()
    )

    # 3. Validate duplicate business keys
    key_columns = [
        "observation_date",
        "base_currency",
        "quote_currency"
    ]

    duplicate_records = int(
        fx_df.duplicated(subset=key_columns).sum()
    )

    # 4. Validate currency pairs
    valid_currencies = {"USD", "EUR", "GBP"}

    invalid_currency_pairs = int((
        ~fx_df["base_currency"].isin(valid_currencies)
        | (fx_df["quote_currency"] != "INR")
    ).sum())

    # 5. Validate positive exchange rates
    fx_df["exchange_rate"] = pd.to_numeric(
        fx_df["exchange_rate"],
        errors="coerce"
    )

    invalid_rates = int((
        fx_df["exchange_rate"].isna()
        | (fx_df["exchange_rate"] <= 0)
        | ~fx_df["exchange_rate"].apply(
            lambda value: pd.notna(value)
            and value != float("inf")
            and value != float("-inf")
        )
    ).sum())

    # 6. Validate observation date boundaries
    date_boundaries = {
        row.base_currency: (
            pd.Timestamp(row.latest_date)
            + pd.Timedelta(days=1)
        )
        for row in results
    }

    invalid_date_ranges = 0

    for _, record in fx_df.iterrows():

        minimum_date = date_boundaries.get(
            record["base_currency"]
        )

        if (
            pd.isna(record["observation_date"])
            or minimum_date is None
            or record["observation_date"] < minimum_date
            or record["observation_date"] > pd.Timestamp(date.today())
        ):
            invalid_date_ranges += 1

    # 7. Check existing PostgreSQL keys
    existing_keys_query = text("""
        SELECT
            observation_date,
            base_currency,
            quote_currency
        FROM public.fx_rates
    """)

    with engine.connect() as connection:
        existing_keys = pd.read_sql(
            existing_keys_query,
            connection
        )

    existing_keys["observation_date"] = pd.to_datetime(
        existing_keys["observation_date"]
    )

    matched_records = fx_df.merge(
        existing_keys,
        on=key_columns,
        how="inner"
    )

    existing_record_count = len(matched_records)

    # 8. Log validation results
    logger.info("Total API Records: %s", len(fx_df))
    logger.info("Missing Values: %s", missing_values)
    logger.info("Invalid Dates: %s", invalid_dates)
    logger.info("Duplicate Records: %s", duplicate_records)
    logger.info("Invalid Currency Pairs: %s", invalid_currency_pairs)
    logger.info("Invalid Exchange Rates: %s", invalid_rates)
    logger.info("Invalid Date Ranges: %s", invalid_date_ranges)
    logger.info("Already Existing DB Records: %s", existing_record_count)

    validation_errors = (
        missing_values
        + invalid_dates
        + duplicate_records
        + invalid_currency_pairs
        + invalid_rates
        + invalid_date_ranges
        + existing_record_count
    )

    if validation_errors == 0:
        logger.info(
            "FX VALIDATION PASSED | Records ready for loading: %s",
            len(fx_df)
        )
    else:
        logger.error(
            "FX VALIDATION FAILED | Total validation findings: %s",
            validation_errors
        )
        raise ValueError(
            "Incremental FX data validation failed"
        )


# --------------------------------------------------
# 8. Incremental PostgreSQL loading
# --------------------------------------------------

from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import insert

logger.info("Incremental FX PostgreSQL loading started")

if fx_df.empty:
    logger.info("No new FX records to load")

else:
    # --------------------------------------------------
    # 8.1 Load existing PostgreSQL table structure
    # --------------------------------------------------

    metadata = MetaData()

    fx_table = Table(
        "fx_rates",
        metadata,
        schema="public",
        autoload_with=engine
    )

    # --------------------------------------------------
    # 8.2 Prepare validated records for insertion
    # --------------------------------------------------

    records_to_insert = fx_df[
        [
            "observation_date",
            "base_currency",
            "quote_currency",
            "exchange_rate"
        ]
    ].copy()

    # Mandatory PostgreSQL source column
    records_to_insert["source"] = "Frankfurter"

    # Temporary default until incremental outlier
    # detection is implemented
    records_to_insert["is_outlier"] = False

    # Convert pandas timestamps into Python date objects
    records_to_insert["observation_date"] = (
        records_to_insert["observation_date"].dt.date
    )

    insert_records = records_to_insert.to_dict(
        orient="records"
    )

    logger.info(
        "FX records prepared for loading: %s",
        len(insert_records)
    )

    # --------------------------------------------------
    # 8.3 Insert records with duplicate protection
    # --------------------------------------------------

    statement = insert(fx_table).values(
        insert_records
    )

    statement = statement.on_conflict_do_nothing(
        index_elements=[
            "observation_date",
            "base_currency",
            "quote_currency"
        ]
    )

    # Automatically commits on success
    # and rolls back on failure
    with engine.begin() as connection:
        result = connection.execute(statement)

        inserted_count = result.rowcount

    skipped_count = len(insert_records) - inserted_count

    logger.info(
        "FX PostgreSQL loading completed | Inserted Records: %s",
        inserted_count
    )

    logger.info(
        "Duplicate/conflicting records skipped: %s",
        skipped_count
    )

    # --------------------------------------------------
    # 8.4 Verify updated PostgreSQL records
    # --------------------------------------------------

    verification_query = text("""
        SELECT
            base_currency,
            COUNT(*) AS total_records,
            MAX(observation_date) AS latest_date
        FROM public.fx_rates
        WHERE quote_currency = 'INR'
        GROUP BY base_currency
        ORDER BY base_currency
    """)

    with engine.connect() as connection:

        verification_results = connection.execute(
            verification_query
        )

        for row in verification_results:

            logger.info(
                "POST-LOAD | %s/INR | Records: %s | Latest Date: %s",
                row.base_currency,
                row.total_records,
                row.latest_date
            )


# --------------------------------------------------
# 9. Recalculate FX outliers using IQR
# --------------------------------------------------

logger.info("FX IQR outlier recalculation started")

historical_query = text("""
    SELECT
        observation_date,
        base_currency,
        quote_currency,
        exchange_rate,
        is_outlier
    FROM public.fx_rates
    WHERE quote_currency = 'INR'
""")

with engine.connect() as connection:
    df_all_fx = pd.read_sql(historical_query, connection)

if df_all_fx.empty:
    logger.info("No FX records available for IQR recalculation")

else:
    df_all_fx["exchange_rate"] = pd.to_numeric(
        df_all_fx["exchange_rate"]
    )

    df_all_fx["recalculated_outlier"] = False

    for currency, group in df_all_fx.groupby("base_currency"):

        q1 = group["exchange_rate"].quantile(0.25)
        q3 = group["exchange_rate"].quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        df_all_fx.loc[group.index, "recalculated_outlier"] = (
            (group["exchange_rate"] < lower_bound) |
            (group["exchange_rate"] > upper_bound)
        )

        logger.info(
            "%s/INR | IQR Lower: %.4f | Upper: %.4f | Outliers: %s",
            currency,
            lower_bound,
            upper_bound,
            int(
                df_all_fx.loc[
                    group.index, "recalculated_outlier"
                ].sum()
            )
        )

    changed_records = df_all_fx[
        df_all_fx["is_outlier"] !=
        df_all_fx["recalculated_outlier"]
    ]

    logger.info(
        "FX outlier flags requiring updates: %s",
        len(changed_records)
    )

    update_query = text("""
        UPDATE public.fx_rates
        SET is_outlier = :is_outlier
        WHERE observation_date = :observation_date
          AND base_currency = :base_currency
          AND quote_currency = :quote_currency
    """)

    update_records = [
        {
            "observation_date": row.observation_date,
            "base_currency": row.base_currency,
            "quote_currency": row.quote_currency,
            "is_outlier": bool(row.recalculated_outlier)
        }
        for row in changed_records.itertuples(index=False)
    ]

    if update_records:
        with engine.begin() as connection:
            result = connection.execute(
                update_query,
                update_records
            )

            if result.rowcount != len(update_records):
                raise RuntimeError(
                    "FX outlier update count mismatch"
                )

    logger.info(
        "FX IQR recalculation completed | Updated flags: %s",
        len(update_records)
    )

logger.info(
    "Incremental FX pipeline execution completed"
)

engine.dispose()
