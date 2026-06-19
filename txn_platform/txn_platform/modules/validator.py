"""
Core validation engine for transaction data
"""
import re
import pandas as pd
from datetime import datetime


# ─── Country phone patterns ──────────────────────────────────────────────────
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

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


def _clean_phone(val: str) -> str:
    return re.sub(r"[\s\-\(\)\.]+", "", str(val))


def validate_dataset(df: pd.DataFrame, config: dict) -> dict:
    """
    Run all validation checks and return a structured results dict.
    """
    results = {
        "total_rows": len(df),
        "total_cols": len(df.columns),
        "checks": {},
        "row_errors": {},  # {row_index: [error_strings]}
        "column_stats": {},
    }

    errors_by_row = {}

    def add_error(idx, msg):
        errors_by_row.setdefault(idx, []).append(msg)

    # ── 1. Missing Values ─────────────────────────────────────────────────────
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_cols = {col: {"count": int(missing[col]), "pct": float(missing_pct[col])}
                    for col in df.columns if missing[col] > 0}

    for col, info in missing_cols.items():
        null_idx = df[df[col].isnull()].index.tolist()
        for i in null_idx:
            add_error(i, f"Missing value in '{col}'")

    results["checks"]["missing_values"] = {
        "status": "fail" if missing_cols else "pass",
        "affected_columns": missing_cols,
        "total_missing_cells": int(missing.sum()),
        "total_missing_rows": int(df.isnull().any(axis=1).sum()),
    }

    # ── 2. Duplicate Records ──────────────────────────────────────────────────
    dup_mask = df.duplicated(keep="first")
    dup_rows = df[dup_mask].index.tolist()
    for i in dup_rows:
        add_error(i, "Duplicate record")

    results["checks"]["duplicates"] = {
        "status": "fail" if dup_rows else "pass",
        "count": len(dup_rows),
        "duplicate_indices": dup_rows[:200],
    }

    # ── 3. Phone Validation ───────────────────────────────────────────────────
    phone_cols = config.get("phone_columns", [])
    phone_country = config.get("phone_country", "IN")
    pattern = PHONE_PATTERNS.get(phone_country, PHONE_PATTERNS["ANY"])

    phone_errors = {}
    for col in phone_cols:
        if col not in df.columns:
            continue
        bad_idx = []
        for i, val in df[col].items():
            if pd.isnull(val):
                continue
            cleaned = _clean_phone(val)
            if not re.match(pattern, cleaned):
                bad_idx.append(i)
                add_error(i, f"Invalid phone in '{col}': {val}")
        phone_errors[col] = {"bad_count": len(bad_idx), "bad_indices": bad_idx[:200]}

    results["checks"]["phone_validation"] = {
        "status": "fail" if any(v["bad_count"] > 0 for v in phone_errors.values()) else "pass",
        "country": phone_country,
        "columns": phone_errors,
    }

    # ── 4. Date/Time Validation ───────────────────────────────────────────────
    date_cols = config.get("date_columns", [])
    date_formats = config.get("date_formats", ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"])

    date_errors = {}
    for col in date_cols:
        if col not in df.columns:
            continue
        bad_idx = []
        for i, val in df[col].items():
            if pd.isnull(val):
                continue
            parsed = False
            for fmt in date_formats:
                try:
                    datetime.strptime(str(val).strip(), fmt)
                    parsed = True
                    break
                except ValueError:
                    pass
            if not parsed:
                bad_idx.append(i)
                add_error(i, f"Invalid date in '{col}': {val}")
        date_errors[col] = {"bad_count": len(bad_idx), "bad_indices": bad_idx[:200]}

    results["checks"]["date_validation"] = {
        "status": "fail" if any(v["bad_count"] > 0 for v in date_errors.values()) else "pass",
        "columns": date_errors,
    }

    # ── 5. Email Validation ───────────────────────────────────────────────────
    email_cols = config.get("email_columns", [])
    email_errors = {}
    for col in email_cols:
        if col not in df.columns:
            continue
        bad_idx = []
        for i, val in df[col].items():
            if pd.isnull(val):
                continue
            if not EMAIL_RE.match(str(val).strip()):
                bad_idx.append(i)
                add_error(i, f"Invalid email in '{col}': {val}")
        email_errors[col] = {"bad_count": len(bad_idx), "bad_indices": bad_idx[:200]}

    results["checks"]["email_validation"] = {
        "status": "fail" if any(v["bad_count"] > 0 for v in email_errors.values()) else "pass",
        "columns": email_errors,
    }

    # ── 6. Amount Validation ──────────────────────────────────────────────────
    amount_cols = config.get("amount_columns", [])
    amt_min = config.get("amount_min", 0.0)
    amt_max = config.get("amount_max", 10_000_000.0)
    amount_errors = {}
    for col in amount_cols:
        if col not in df.columns:
            continue
        bad_idx = []
        non_numeric = []
        for i, val in df[col].items():
            if pd.isnull(val):
                continue
            try:
                num = float(str(val).replace(",", "").strip())
                if not (amt_min <= num <= amt_max):
                    bad_idx.append(i)
                    add_error(i, f"Amount out of range in '{col}': {val}")
            except ValueError:
                non_numeric.append(i)
                add_error(i, f"Non-numeric amount in '{col}': {val}")
        amount_errors[col] = {
            "bad_count": len(bad_idx) + len(non_numeric),
            "out_of_range": len(bad_idx),
            "non_numeric": len(non_numeric),
            "bad_indices": (bad_idx + non_numeric)[:200],
        }

    results["checks"]["amount_validation"] = {
        "status": "fail" if any(v["bad_count"] > 0 for v in amount_errors.values()) else "pass",
        "range": [amt_min, amt_max],
        "columns": amount_errors,
    }

    # ── 7. Payment Mode Validation ────────────────────────────────────────────
    payment_cols = config.get("payment_mode_columns", [])
    valid_modes = [m.lower().strip() for m in config.get("valid_payment_modes", [])]
    payment_errors = {}
    for col in payment_cols:
        if col not in df.columns:
            continue
        bad_idx = []
        invalid_vals = {}
        for i, val in df[col].items():
            if pd.isnull(val):
                continue
            if str(val).lower().strip() not in valid_modes:
                bad_idx.append(i)
                invalid_vals[str(val)] = invalid_vals.get(str(val), 0) + 1
                add_error(i, f"Invalid payment mode in '{col}': {val}")
        payment_errors[col] = {
            "bad_count": len(bad_idx),
            "invalid_values": invalid_vals,
            "bad_indices": bad_idx[:200],
        }

    results["checks"]["payment_mode_validation"] = {
        "status": "fail" if any(v["bad_count"] > 0 for v in payment_errors.values()) else "pass",
        "columns": payment_errors,
    }

    # ── 8. Data Integrity ─────────────────────────────────────────────────────
    integrity_issues = []
    for col in df.select_dtypes(include=["object"]).columns:
        stripped = df[col].dropna().str.strip()
        whitespace_count = int((stripped != df[col].dropna()).sum())
        if whitespace_count > 0:
            integrity_issues.append({"column": col, "issue": "leading/trailing whitespace", "count": whitespace_count})

    results["checks"]["data_integrity"] = {
        "status": "warn" if integrity_issues else "pass",
        "issues": integrity_issues,
    }

    # ── 9. Column Stats ───────────────────────────────────────────────────────
    for col in df.columns:
        results["column_stats"][col] = {
            "dtype": str(df[col].dtype),
            "null_count": int(df[col].isnull().sum()),
            "null_pct": round(df[col].isnull().sum() / len(df) * 100, 2),
            "unique_count": int(df[col].nunique()),
            "sample_values": df[col].dropna().head(3).astype(str).tolist(),
        }

    # ── Aggregate errors by row ───────────────────────────────────────────────
    results["row_errors"] = errors_by_row

    # ── Quality Score ─────────────────────────────────────────────────────────
    results["quality_score"] = _compute_quality_score(df, results)

    return results


def _compute_quality_score(df: pd.DataFrame, results: dict) -> float:
    total = len(df)
    if total == 0:
        return 100.0

    penalty = 0.0

    # Missing values: up to 30 pts
    mv = results["checks"]["missing_values"]
    missing_row_pct = mv["total_missing_rows"] / total
    penalty += min(30, missing_row_pct * 100)

    # Duplicates: up to 20 pts
    dup_pct = results["checks"]["duplicates"]["count"] / total
    penalty += min(20, dup_pct * 100)

    # Phone: up to 10 pts
    phone = results["checks"]["phone_validation"]
    phone_bad = sum(v["bad_count"] for v in phone["columns"].values())
    if phone_bad:
        penalty += min(10, phone_bad / total * 100)

    # Date: up to 10 pts
    date = results["checks"]["date_validation"]
    date_bad = sum(v["bad_count"] for v in date["columns"].values())
    if date_bad:
        penalty += min(10, date_bad / total * 100)

    # Email: up to 10 pts
    email = results["checks"]["email_validation"]
    email_bad = sum(v["bad_count"] for v in email["columns"].values())
    if email_bad:
        penalty += min(10, email_bad / total * 100)

    # Amount: up to 10 pts
    amt = results["checks"]["amount_validation"]
    amt_bad = sum(v["bad_count"] for v in amt["columns"].values())
    if amt_bad:
        penalty += min(10, amt_bad / total * 100)

    # Payment mode: up to 10 pts
    pm = results["checks"]["payment_mode_validation"]
    pm_bad = sum(v["bad_count"] for v in pm["columns"].values())
    if pm_bad:
        penalty += min(10, pm_bad / total * 100)

    return max(0.0, 100.0 - penalty)


def get_error_summary(results: dict) -> pd.DataFrame:
    """Return a summary DataFrame of all check results."""
    checks = results["checks"]
    rows = []
    mapping = {
        "missing_values": "Missing Values",
        "duplicates": "Duplicate Records",
        "phone_validation": "Phone Validation",
        "date_validation": "Date Validation",
        "email_validation": "Email Validation",
        "amount_validation": "Amount Validation",
        "payment_mode_validation": "Payment Mode Validation",
        "data_integrity": "Data Integrity",
    }
    for key, label in mapping.items():
        if key not in checks:
            continue
        c = checks[key]
        status = c.get("status", "pass")
        # Count affected
        if key == "missing_values":
            affected = c["total_missing_cells"]
        elif key == "duplicates":
            affected = c["count"]
        elif key in ("phone_validation", "date_validation", "email_validation",
                     "amount_validation", "payment_mode_validation"):
            affected = sum(v.get("bad_count", 0) for v in c.get("columns", {}).values())
        elif key == "data_integrity":
            affected = sum(i.get("count", 0) for i in c.get("issues", []))
        else:
            affected = 0

        rows.append({
            "Check": label,
            "Status": status.upper(),
            "Issues Found": affected,
        })
    return pd.DataFrame(rows)


def build_error_log(df: pd.DataFrame, results: dict) -> pd.DataFrame:
    """Build a detailed per-row error log."""
    rows = []
    for idx, errors in results["row_errors"].items():
        for err in errors:
            row_data = df.iloc[idx].to_dict() if idx < len(df) else {}
            rows.append({
                "Row Index": idx,
                "Error Description": err,
                "Row Preview": str({k: v for k, v in list(row_data.items())[:4]}),
            })
    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["Row Index", "Error Description", "Row Preview"]
    )
