
from pathlib import Path

import pandas as pd


# Locate the project root independently of the terminal location.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

FX_DATA_PATH = (
    PROJECT_ROOT
    / "Data"
    / "processed"
    / "fx_rates_processed.csv"
)


def test_fx_exchange_rates_are_positive():
    """
    Verify that all processed FX exchange rates
    are present and strictly greater than zero.
    """

    df = pd.read_csv(FX_DATA_PATH)

    assert "exchange_rate" in df.columns, (
        "Required column 'exchange_rate' is missing."
    )

    assert not df.empty, "FX dataset is empty."

    assert df["exchange_rate"].notna().all(), (
        "FX dataset contains missing exchange rates."
    )

    assert (df["exchange_rate"] > 0).all(), (
        "FX dataset contains zero or negative exchange rates."
    )

def test_fx_no_duplicate_currency_dates():
    """
    Ensure each currency pair has only one
    exchange rate per observation date.
    """

    df = pd.read_csv(FX_DATA_PATH)

    key_columns = [
        "observation_date",
        "base_currency",
        "quote_currency",
    ]

    assert all(col in df.columns for col in key_columns), (
        "One or more required FX key columns are missing."
    )

    duplicate_count = df.duplicated(
        subset=key_columns
    ).sum()

    assert duplicate_count == 0, (
        f"Found {duplicate_count} duplicate FX records."
    )

def test_fx_currency_pairs_and_record_counts():
    """
    Verify approved FX currency pairs and
    expected historical observation counts.
    """

    df = pd.read_csv(FX_DATA_PATH)

    expected_counts = {
        "USD": 104,
        "EUR": 104,
        "GBP": 104,
    }

    assert len(df) == 312, (
        f"Expected 312 FX records, found {len(df)}."
    )

    assert df["quote_currency"].eq("INR").all(), (
        "Unexpected quote currency detected."
    )

    actual_counts = df["base_currency"].value_counts().to_dict()

    assert actual_counts == expected_counts, (
        f"Currency counts mismatch. "
        f"Expected: {expected_counts}, "
        f"Actual: {actual_counts}"
    )

def test_fx_observation_dates():
    """
    Verify that FX observation dates are valid,
    within the approved period, and fall on weekdays.
    """

    df = pd.read_csv(FX_DATA_PATH)

    dates = pd.to_datetime(
        df["observation_date"],
        format="%Y-%m-%d",
        errors="coerce",
    )

    assert dates.notna().all(), (
        "FX dataset contains invalid observation dates."
    )

    start_date = pd.Timestamp("2026-05-21")
    end_date = pd.Timestamp("2026-10-13")

    assert dates.between(start_date, end_date).all(), (
        "FX dataset contains dates outside the approved period."
    )

    assert (dates.dt.dayofweek < 5).all(), (
        "FX dataset contains weekend observations."
    )

STOCK_DATA_PATH = (
    PROJECT_ROOT
    / "Data"
    / "processed"
    / "banking_stocks_processed.csv"
)

def test_stock_ohlc_price_validation():
    """
    Verify that banking stock OHLC prices
    follow valid financial market rules.
    """

    df = pd.read_csv(STOCK_DATA_PATH)

    price_columns = [
        "open_price",
        "high_price",
        "low_price",
        "close_price",
    ]

    assert not df.empty, "Banking stock dataset is empty."

    assert all(col in df.columns for col in price_columns), (
        "One or more required OHLC columns are missing."
    )

    assert df[price_columns].notna().all().all(), (
        "Banking stock dataset contains missing OHLC prices."
    )

    assert df[price_columns].gt(0).all().all(), (
        "Banking stock dataset contains non-positive prices."
    )

    assert (
        df["high_price"]
        >= df[["open_price", "low_price", "close_price"]].max(axis=1)
    ).all(), "Invalid daily high prices detected."

    assert (
        df["low_price"]
        <= df[["open_price", "high_price", "close_price"]].min(axis=1)
    ).all(), "Invalid daily low prices detected."

def test_stock_trading_volume_validation():
    """
    Verify that banking stock trading volumes
    are present, positive, and whole numbers.
    """

    df = pd.read_csv(STOCK_DATA_PATH)

    assert "volume" in df.columns, (
        "Required column 'volume' is missing."
    )

    assert df["volume"].notna().all(), (
        "Banking stock dataset contains missing volumes."
    )

    assert (df["volume"] > 0).all(), (
        "Banking stock dataset contains zero or negative volumes."
    )

    assert (df["volume"] % 1 == 0).all(), (
        "Banking stock dataset contains fractional volumes."
    )

def test_stock_symbols_and_duplicates():
    """
    Verify approved banking stock symbols
    and unique stock-date combinations.
    """

    df = pd.read_csv(STOCK_DATA_PATH)

    required_columns = [
        "observation_date",
        "stock_symbol",
    ]

    assert all(col in df.columns for col in required_columns), (
        "Required stock identification columns are missing."
    )

    expected_symbols = {
        "HDFCBANK.BSE",
        "ICICIBANK.BSE",
        "SBIN.BSE",
    }

    actual_symbols = set(df["stock_symbol"].dropna())

    assert actual_symbols == expected_symbols, (
        f"Unexpected stock symbols: {actual_symbols}"
    )

    assert df["stock_symbol"].notna().all(), (
        "Missing stock symbols detected."
    )

    duplicate_count = df.duplicated(
        subset=["observation_date", "stock_symbol"]
    ).sum()

    assert duplicate_count == 0, (
        f"Found {duplicate_count} duplicate stock-date records."
    )

    
    # Final processed dataset excludes out-of-period records.
    assert len(df) == 297, (
        f"Expected 297 processed stock records, found {len(df)}."
    )

    stock_counts = df["stock_symbol"].value_counts()

    assert (stock_counts == 99).all(), (
        f"Expected 99 observations per stock. "
        f"Actual: {stock_counts.to_dict()}"
    )

def test_stock_observation_dates():
    """
    Verify that banking stock observation dates
    are valid and within the approved reporting period.
    """

    df = pd.read_csv(STOCK_DATA_PATH)

    assert "observation_date" in df.columns, (
        "Required observation_date column is missing."
    )

    dates = pd.to_datetime(
        df["observation_date"],
        format="%Y-%m-%d",
        errors="coerce",
    )

    assert dates.notna().all(), (
        "Invalid or missing stock observation dates detected."
    )

    start_date = pd.Timestamp("2026-05-22")
    end_date = pd.Timestamp("2026-10-13")

    assert dates.between(start_date, end_date).all(), (
        "Stock records found outside the approved reporting period."
    )

    assert (dates.dt.dayofweek < 5).all(), (
        "Weekend observations detected in banking stock data."
    )

def test_stock_outlier_flag_consistency():
    """
    Verify that the combined outlier flag
    matches price and volume outlier flags.
    """

    df = pd.read_csv(STOCK_DATA_PATH)

    required_columns = [
        "price_outlier",
        "volume_outlier",
        "is_outlier",
    ]

    assert all(col in df.columns for col in required_columns), (
        "Required stock outlier columns are missing."
    )

    assert df[required_columns].notna().all().all(), (
        "Missing stock outlier flags detected."
    )

    expected_flags = (
        df["price_outlier"] | df["volume_outlier"]
    )

    assert df["is_outlier"].eq(expected_flags).all(), (
        "Combined outlier flags do not match "
        "price and volume outlier flags."
    )

