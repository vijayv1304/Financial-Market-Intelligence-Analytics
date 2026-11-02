
# Financial Market Intelligence & Currency Risk Analytics

## Project Overview

An end-to-end financial data analytics portfolio project
designed to support currency risk monitoring and banking
stock market analysis.

The project integrates historical financial market data
from public APIs and transforms it into validated,
analysis-ready datasets using Python and PostgreSQL.

Interactive Power BI dashboards provide insights into
foreign exchange movements, banking stock performance,
and financial market trends.

## Business Scenario

An Indian finance and treasury team needs to monitor
currency movements to understand potential foreign
exchange exposure associated with import payments.

The team also monitors selected Indian banking stocks
to understand broader financial market trends.

## Business Objectives

1. Monitor USD/INR, EUR/INR, and GBP/INR exchange rates.
2. Analyze historical exchange rate movements and volatility.
3. Identify unusual currency fluctuations.
4. Monitor HDFCBANK, ICICIBANK, and SBIN stock performance.
5. Analyze banking stock prices, trading volumes, and outliers.
6. Provide interactive Power BI dashboards for financial analysis.
7. Maintain data quality through automated testing and logging.

## Technology Stack

- Python 3.13
- Pandas
- Jupyter Notebook
- Visual Studio Code
- PostgreSQL
- SQLAlchemy
- Power BI
- DAX
- Power Query
- Pytest
- Git and GitHub

## Data Sources

- Frankfurter API — historical foreign exchange rates.
- Alpha Vantage API — historical Indian banking stock prices.

## Project Datasets

| Dataset | Records | Coverage |
|---|---:|---|
| Foreign Exchange Rates | 312 | May–October 2026 |
| Banking Stocks | 297 | May–October 2026 |

The processed datasets contain validated historical
observations used for financial analysis and reporting.


## End-to-End Data Pipeline

The project follows a structured analytics workflow:

1. Business requirements and KPI identification
2. Financial data extraction from public APIs
3. Raw data storage with ingestion metadata
4. Data profiling, cleaning, and validation
5. Processed dataset generation
6. PostgreSQL database loading and verification
7. Python exploratory data analysis
8. Power BI data modeling and DAX calculations
9. Interactive dashboard development
10. Automated data quality testing and logging

### 1. Data Extraction

**Foreign Exchange Data**
- Source: Frankfurter API
- Currency pairs: USD/INR, EUR/INR, GBP/INR
- Historical period: May 21 – October 13, 2026
- Total raw records: 312

**Banking Stock Data**
- Source: Alpha Vantage API
- Stocks: HDFCBANK.BSE, ICICIBANK.BSE, SBIN.BSE
- Historical market data: OHLC prices and trading volume
- Total raw records: 300

### 2. Data Cleaning and Validation

Python and Pandas were used to validate:
- Required columns and data types
- Missing values and duplicate records
- Currency exchange rate positivity
- Stock OHLC price consistency
- Trading volume validity
- Historical date coverage
- Price and volume outliers

Six FX observations and 21 banking stock observations
were flagged as outliers for further analysis.

Three banking stock records outside the approved
reporting period were excluded from the processed dataset.

### 3. Processed Datasets

| Dataset | Final Records | Missing Values | Duplicates |
|---|---:|---:|---:|
| FX Rates | 312 | 0 | 0 |
| Banking Stocks | 297 | 0 | 0 |

### 4. PostgreSQL Integration

Validated datasets were loaded into PostgreSQL.

Database: `financial_market_analytics`

Tables:
- `public.fx_rates` — 312 records
- `public.banking_stocks` — 297 records

SQL queries were used to verify successful loading
and confirm the expected database record counts.

### 5. Python Analysis

Jupyter notebooks were used for financial data analysis,
including historical trends, price movements, volatility,
and outlier investigation.

### 6. Power BI Reporting

The validated financial datasets were used to develop
interactive Power BI dashboards featuring:

- Currency risk overview
- Banking stock performance overview
- Financial insights
- Stock drillthrough analysis
- Interactive filtering and page navigation
- DAX measures and financial KPIs
- Reset buttons and bookmarks

### 7. Automated Testing and Logging

Pytest was used to execute nine automated data quality
tests covering FX and banking stock datasets.

Final result: 9 passed, 0 failed.

Test report:
`Logs/data_quality_test_results.xml`

Central execution log:
`Logs/pipeline_execution.log`

Structured logging records dataset verification,
data quality results, database record counts,
and analysis input checks.


## Project Folder Structure

```text
Financial_Market_Intelligence_Analytics/
│
├── Business_Insights/
│   └── Business findings and recommendations
│
├── Config/
│   └── Project configuration files
│
├── Data/
│   ├── raw/
│   │   └── Raw API datasets and ingestion metadata
│   ├── processed/
│   │   ├── PowerBI/
│   │   └── Cleaned and validated datasets
│   └── validation/
│       └── Data quality and validation reports
│
├── Python/
│   ├── Notebooks/
│   │   ├── 00_Environment_Test.ipynb
│   │   ├── 01_FX_API_Ingestion.ipynb
│   │   ├── 02_Banking_Stocks_API_Ingestion.ipynb
│   │   ├── 03_FX_Data_Validation.ipynb
│   │   ├── 04_Banking_Stocks_Data_Validation.ipynb
│   │   ├── 05_FX_PostgreSQL_Loading.ipynb
│   │   ├── 06_Banking_Stocks_PostgreSQL_Loading.ipynb
│   │   └── 07_Financial_Data_Analysis.ipynb
│   │
│   ├── Scripts/
│   │   ├── pipeline_logger.py
│   │   └── test_db_connection.py
│   │
│   └── Visualizations/
│       └── Python analysis charts
│
├── SQL/
│   └── Database scripts and SQL analysis
│
├── PowerBI/
│   └── Power BI dashboard files
│
├── Tests/
│   └── test_data_quality.py
│
├── Logs/
│   ├── pipeline_execution.log
│   └── data_quality_test_results.xml
│
└── README.md
```

### Folder Descriptions

| Folder | Purpose |
|---|---|
| Business_Insights | Business findings and recommendations |
| Config | Project configuration |
| Data/raw | Original API responses and metadata |
| Data/processed | Cleaned, validated datasets |
| Data/validation | Data quality reports |
| Python/Notebooks | API ingestion, validation, database loading, and analysis |
| Python/Scripts | Reusable Python utilities |
| Python/Visualizations | Exploratory analysis charts |
| SQL | PostgreSQL scripts and analytical queries |
| PowerBI | Interactive financial dashboards |
| Tests | Automated data quality tests |
| Logs | Pipeline logs and test reports |

### Security and Reproducibility

Database credentials and API keys are managed through
environment variables.

The `.env` file and Python virtual environment should
remain excluded from Git version control.

Raw and processed datasets are retained separately to
preserve traceability throughout the analytics workflow.


## Power BI Dashboard

The project includes an interactive Power BI reporting
solution designed for currency risk monitoring and
Indian banking stock market analysis.

### Dashboard Pages

#### 1. Currency Risk Overview

Provides an overview of historical foreign exchange
movements for:

- USD/INR
- EUR/INR
- GBP/INR

Key analytical areas:
- Exchange rate trends
- Currency performance comparisons
- Historical rate fluctuations
- Currency volatility monitoring
- Identification of unusual exchange rate movements

Business purpose:
Help an Indian finance or treasury team understand
currency movements relevant to import payment exposure.

#### 2. Banking Stock Overview

Analyzes three Indian banking stocks:

- HDFCBANK.BSE
- ICICIBANK.BSE
- SBIN.BSE

Key analytical areas:
- Historical stock price movements
- Closing price comparisons
- Trading volume trends
- Price and volume fluctuations
- Unusual market activity

Business purpose:
Provide a consolidated view of selected Indian
banking stocks and their historical market performance.

#### 3. Financial Insights

Combines financial analysis into a dedicated
insights page.

Key analytical areas:
- Currency market observations
- Banking stock performance patterns
- Historical trends
- Financial risk indicators
- Comparative analysis

Business purpose:
Support interpretation of financial market data
and communicate findings to business stakeholders.

#### 4. Stock Drillthrough

Provides detailed analysis for a selected banking
stock through Power BI drillthrough functionality.

This page is hidden from normal page navigation
and accessed through drillthrough interactions.

### Interactive Dashboard Features

- Page navigation buttons
- Interactive slicers and filters
- Drill-down analysis
- Stock-specific drillthrough
- DAX measures and calculated KPIs
- Bookmarks and reset functionality
- Conditional formatting and visual indicators

### Dashboard Validation

The Power BI dashboard completed eight final
validation checks covering its functionality
and reporting behavior.

The dashboard is designed to help stakeholders
explore historical financial data and identify
patterns requiring further investigation.


## Business Findings and Recommendations

### 1. Foreign Exchange Risk Monitoring

**Finding:**

The project analyzed 312 historical FX observations
across USD/INR, EUR/INR, and GBP/INR.

Six observations were flagged as statistical outliers,
indicating unusual movements requiring further review.

**Business Implication:**

Currency fluctuations can affect the INR cost of
foreign-currency import payments.

**Recommendation:**

- Monitor currency trends regularly.
- Investigate flagged exchange rate observations.
- Compare currency movements against upcoming
  foreign-currency payment obligations.
- Consider appropriate treasury risk management
  strategies based on business exposure.

### 2. Banking Stock Market Monitoring

**Finding:**

The processed dataset contains 297 historical
observations across three Indian banking stocks.

Data validation identified 21 volume outlier records
and no price outliers under the project's detection rules.

**Business Implication:**

Unusual trading volume may indicate periods of
heightened market activity that warrant investigation.

**Recommendation:**

- Monitor stock price and trading volume trends.
- Review unusual volume observations.
- Compare performance across the selected stocks.
- Investigate market events associated with
  significant changes in trading activity.

### 3. Financial Data Quality

**Finding:**

The processed FX and banking stock datasets contain
no missing values or duplicate business-key records.

Three stock observations outside the approved
reporting period were excluded during processing.

All nine automated data quality tests passed.

**Business Implication:**

Validated and consistently structured datasets
improve confidence in historical financial reporting.

**Recommendation:**

- Continue automated data quality testing.
- Maintain separate raw and processed datasets.
- Retain ingestion metadata and validation reports.
- Review pipeline logs after each execution.

### 4. Decision Support

The Power BI dashboards consolidate historical
currency and banking stock information into an
interactive analytical reporting solution.

The dashboards support:
- Historical performance monitoring
- Comparative financial analysis
- Outlier investigation
- Currency risk awareness
- Data-driven business discussions

### Project Limitations

- Historical observations do not guarantee future
  financial market performance.
- Statistical outliers do not automatically indicate
  incorrect data or significant market events.
- Actual currency exposure depends on payment
  amounts, timing, and treasury policies.
- This project provides analytical decision support,
  not investment recommendations or automated trading.


## Project Setup and Execution

### Prerequisites

The following tools are required:

- Python 3.13
- PostgreSQL
- Visual Studio Code
- Jupyter Notebook
- Power BI Desktop
- Git

### 1. Clone the Repository

```powershell
git clone <repository-url>
cd Financial_Market_Intelligence_Analytics
```

Replace `<repository-url>` with the actual GitHub
repository URL after publishing the project.

### 2. Create a Python Virtual Environment

```powershell
python -m venv .venv
```

Activate the environment in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Python Dependencies

Install the required Python packages using the
project's dependency file once it is generated:

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

Configure the following variables:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=financial_market_analytics
DB_USER=your_database_username
DB_PASSWORD=your_database_password

ALPHA_VANTAGE_API_KEY=your_api_key
```

Use the API key variable name expected by the
ingestion notebook if it differs from this example.

Never commit the `.env` file or actual credentials
to GitHub.

### 5. Prepare PostgreSQL

Create the PostgreSQL database:

```sql
CREATE DATABASE financial_market_analytics;
```

Use the SQL scripts in the `SQL/` directory
to prepare the required database objects.

### 6. Execute the Python Workflow

Run the notebooks in the following order:

1. `00_Environment_Test.ipynb`
2. `01_FX_API_Ingestion.ipynb`
3. `02_Banking_Stocks_API_Ingestion.ipynb`
4. `03_FX_Data_Validation.ipynb`
5. `04_Banking_Stocks_Data_Validation.ipynb`
6. `05_FX_PostgreSQL_Loading.ipynb`
7. `06_Banking_Stocks_PostgreSQL_Loading.ipynb`
8. `07_Financial_Data_Analysis.ipynb`

**Important:** Database loading notebooks contain
insertion logic and should not be rerun against
already populated tables without reviewing the
existing records.

Alpha Vantage API rate limits must also be respected.

### 7. Run Automated Data Quality Tests

From the project root, execute:

```powershell
python -m pytest Tests/test_data_quality.py -v --junitxml=Logs/data_quality_test_results.xml
```

Latest verified result:

**9 tests passed, 0 failed.**

### 8. Review Pipeline Logs

The project uses Python's logging module to
record validation and verification results.

Log file:

`Logs/pipeline_execution.log`

### 9. Open the Power BI Dashboard

Open the Power BI report file located in the
`PowerBI/` directory.

Review the data source configuration and refresh
the report if necessary.
