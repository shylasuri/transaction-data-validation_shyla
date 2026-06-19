"""
Data cleaning module — produces a cleaned copy of the uploaded dataset.
"""
import re
import pandas as pd
from datetime import datetime


PHONE_PATTERNS = {
    "IN": r"^(\+91|91)?[6-9]\d{9}$",
    "US": r"^(\+1)?[2-9]\d{2}[2-9]\d{6}$",
    "UK": r"^(\+44|0)7\d{9}$",
    "AU": r"^(\+61|0)[4-5]\d{8}$",
    "CA": r"^(\+1)?[2-9]\d{2}[2-9]\d{6}$",
    "SG": r"^(\+65)?[89]\d{7}$",
    "AE": r"^(\+971|0)?5[0-9]\d{7}$",
    "DE": r"^(\+49|0)?1[5-7]\d{9,10}$",
    "FR": r"^(\+33|0)[67]\d{8}$",
    "ANY": r"^\+?[1-9]\d{6,14}$",
}


def clean_dataset(df: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, dict]:
    """
    Apply all cleaning operations and return (cleaned_df, cleaning_report).
    """
    df_clean = df.copy()
    report = {
        "duplicates_removed": 0,
        "whitespace_stripped": 0,
        "invalid_phones_nulled": 0,
        "invalid_emails_nulled": 0,
        "invalid_amounts_nulled": 0,
        "invalid_dates_nulled": 0,
        "invalid_payment_modes_nulled": 0,
        "rows_before": len(df),
        "rows_after": 0,
    }

    # ── 1. Strip Whitespace ───────────────────────────────────────────────────
    for col in df_clean.select_dtypes(include=["object"]).columns:
        before = df_clean[col].copy()
        df_clean[col] = df_clean[col].str.strip()
        changed = (before != df_clean[col]) & before.notna()
        report["whitespace_stripped"] += int(changed.sum())

    # ── 2. Remove Duplicates ──────────────────────────────────────────────────
    before_len = len(df_clean)
    df_clean = df_clean.drop_duplicates(keep="first").reset_index(drop=True)
    report["duplicates_removed"] = before_len - len(df_clean)

    # ── 3. Nullify Invalid Phones ─────────────────────────────────────────────
    phone_cols = config.get("phone_columns", [])
    phone_country = config.get("phone_country", "IN")
    pattern = PHONE_PATTERNS.get(phone_country, PHONE_PATTERNS["ANY"])
    for col in phone_cols:
        if col not in df_clean.columns:
            continue
        def _valid_phone(v):
            try:
                cleaned = re.sub(r"[\s\-\(\)\.]+", "", str(v))
                return bool(re.match(pattern, cleaned))
            except Exception:
                return False
        mask = df_clean[col].notna() & ~df_clean[col].apply(_valid_phone)
        report["invalid_phones_nulled"] += int(mask.sum())
        df_clean.loc[mask, col] = None

    # ── 4. Nullify Invalid Emails ─────────────────────────────────────────────
    EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
    email_cols = config.get("email_columns", [])
    for col in email_cols:
        if col not in df_clean.columns:
            continue
        def _valid_email(v):
            try:
                return bool(EMAIL_RE.match(str(v).strip()))
            except Exception:
                return False
        mask = df_clean[col].notna() & ~df_clean[col].apply(_valid_email)
        report["invalid_emails_nulled"] += int(mask.sum())
        df_clean.loc[mask, col] = None

    # ── 5. Nullify Invalid Amounts ────────────────────────────────────────────
    amount_cols = config.get("amount_columns", [])
    amt_min = config.get("amount_min", 0.0)
    amt_max = config.get("amount_max", 10_000_000.0)
    for col in amount_cols:
        if col not in df_clean.columns:
            continue
        def _check_amount(v):
            try:
                n = float(str(v).replace(",", "").strip())
                return amt_min <= n <= amt_max
            except ValueError:
                return False
        mask = df_clean[col].notna() & ~df_clean[col].apply(_check_amount)
        report["invalid_amounts_nulled"] += int(mask.sum())
        df_clean.loc[mask, col] = None

    # ── 6. Nullify Invalid Dates ──────────────────────────────────────────────
    date_cols = config.get("date_columns", [])
    date_formats = config.get("date_formats", ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"])
    for col in date_cols:
        if col not in df_clean.columns:
            continue
        def _check_date(v):
            for fmt in date_formats:
                try:
                    datetime.strptime(str(v).strip(), fmt)
                    return True
                except ValueError:
                    pass
            return False
        mask = df_clean[col].notna() & ~df_clean[col].apply(_check_date)
        report["invalid_dates_nulled"] += int(mask.sum())
        df_clean.loc[mask, col] = None

    # ── 7. Nullify Invalid Payment Modes ──────────────────────────────────────
    payment_cols = config.get("payment_mode_columns", [])
    valid_modes = [m.lower().strip() for m in config.get("valid_payment_modes", [])]
    for col in payment_cols:
        if col not in df_clean.columns:
            continue
        def _valid_mode(v):
            try:
                return str(v).lower().strip() in valid_modes
            except Exception:
                return False
        mask = df_clean[col].notna() & ~df_clean[col].apply(_valid_mode)
        report["invalid_payment_modes_nulled"] += int(mask.sum())
        df_clean.loc[mask, col] = None

    report["rows_after"] = len(df_clean)
    report["total_cells_cleaned"] = (
        report["whitespace_stripped"]
        + report["invalid_phones_nulled"]
        + report["invalid_emails_nulled"]
        + report["invalid_amounts_nulled"]
        + report["invalid_dates_nulled"]
        + report["invalid_payment_modes_nulled"]
    )

    return df_clean, report