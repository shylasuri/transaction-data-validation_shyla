# Transaction Data Validation & Quality Intelligence Platform

A production-ready Streamlit application for validating, cleaning, analyzing, and processing transaction datasets before importing into production systems.

## Features

- **Upload & Preview** — Upload CSV datasets with metadata display and column overview
- **Data Validation** — Configurable rules for missing values, duplicates, phone numbers, dates, emails, amounts, and payment modes
- **Data Cleaning** — Automated cleaning with a preserved copy of the original data
- **Export** — Download cleaned CSV, validation report (TXT), and error log (CSV)
- **CSV Splitting** — Split large files into chunks packaged as a ZIP archive
- **Analytics** — Interactive Plotly charts for quality metrics, error distribution, and dataset profile
- **Insights** — Dataset health summary, key issues, recommended actions, and import readiness assessment

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`.

## Project Structure

```
txn_platform/
├── app.py                      # Main entry point
├── requirements.txt
├── sample_transactions.csv     # Sample dataset for testing
├── .streamlit/
│   └── config.toml             # Streamlit theme configuration
└── modules/
    ├── __init__.py
    ├── session.py              # Session state management
    ├── ui_config.py            # CSS styles and theme
    ├── validator.py            # Validation engine
    ├── cleaner.py              # Data cleaning engine
    ├── analytics.py            # Plotly chart builders
    └── pages.py                # Page renderers
```

## Supported Validations

| Check | Description |
|-------|-------------|
| Missing Values | Detects null/empty cells per column |
| Duplicates | Row-level duplicate detection |
| Phone Numbers | Country-specific regex validation (IN, US, UK, AU, CA, SG, AE, DE, FR, ANY) |
| Date/Time | Multi-format parsing validation |
| Email | RFC-compliant format check |
| Amount | Numeric range validation with configurable bounds |
| Payment Mode | Whitelist-based validation with configurable modes |
| Data Integrity | Whitespace detection |

## Quality Score

The quality score (0–100%) penalises the following (capped per category):

- Missing rows: up to 30 points
- Duplicates: up to 20 points
- Phone errors: up to 10 points
- Date errors: up to 10 points
- Email errors: up to 10 points
- Amount errors: up to 10 points
- Payment mode errors: up to 10 points

## Using the Sample Dataset

A sample CSV (`sample_transactions.csv`) is included with intentional errors:
- Duplicate row (ORD001)
- Missing values (customer_name, email, phone)
- Invalid email formats
- Invalid phone numbers
- Invalid date format
- Out-of-range amount
- Invalid payment mode

Configure validation columns after upload:
- Phone: `phone`
- Email: `email`
- Date: `order_date`
- Amount: `amount`
- Payment Mode: `payment_mode`
