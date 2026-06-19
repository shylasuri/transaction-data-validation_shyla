"""
Page renderers for each section of the platform.
"""
import io
import zipfile
import json
import math

import pandas as pd
import streamlit as st

from modules.validator import validate_dataset, get_error_summary, build_error_log
from modules.cleaner import clean_dataset
from modules.analytics import (
    fig_quality_gauge,
    fig_error_distribution,
    fig_completeness_heatmap,
    fig_duplicate_analysis,
    fig_dtype_breakdown,
    fig_error_trend,
)
from modules.session import get_default_config
from modules.validator import PHONE_PATTERNS


# ─── Helpers ─────────────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-title">{title}</div>
            <div class="page-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value, sub: str = "", color: str = "blue"):
    st.markdown(
        f"""
        <div class="metric-card {color}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_card_start(title: str):
    st.markdown(f'<div class="section-card"><div class="section-title">{title}</div>', unsafe_allow_html=True)


def section_card_end():
    st.markdown("</div>", unsafe_allow_html=True)


def status_badge(status: str) -> str:
    cls = {"pass": "badge-pass", "fail": "badge-fail", "warn": "badge-warn"}.get(status, "badge-info")
    return f'<span class="badge {cls}">{status.upper()}</span>'


def require_data(page_name: str = ""):
    if st.session_state.df is None:
        st.markdown(
            """
            <div class="alert-box alert-info">
                No dataset loaded. Please upload a CSV file from the <b>Upload</b> page first.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return False
    return True


def require_validation(page_name: str = ""):
    if st.session_state.validation_results is None:
        st.markdown(
            """
            <div class="alert-box alert-info">
                Validation has not been run yet. Go to the <b>Data Validation</b> page and run validation first.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return False
    return True


# ─── Upload Page ──────────────────────────────────────────────────────────────
def render_upload_page():
    # ── No page_header here — hero replaces it ────────────────────────────────

    if st.session_state.df is None:
        # ── Full-width hero ───────────────────────────────────────────────────
        st.markdown(
            """
            <div class="lp-hero">
                <div class="lp-hero-left">
                    <div class="lp-hero-tag">Enterprise Data Quality</div>
                    <div class="lp-hero-title">Stop bad data<br>reaching <span>production</span></div>
                    <div class="lp-hero-body">
                        Upload any transaction CSV and get an instant quality score,
                        field-level validation across 8 check types, automated cleaning,
                        and an import-readiness report — in seconds.
                    </div>
                    <div class="lp-steps">
                        <div class="lp-step"><div class="lp-step-num">1</div><div class="lp-step-text">Upload CSV</div></div>
                        <div class="lp-step"><div class="lp-step-num">2</div><div class="lp-step-text">Configure Rules</div></div>
                        <div class="lp-step"><div class="lp-step-num">3</div><div class="lp-step-text">Run Validation</div></div>
                        <div class="lp-step"><div class="lp-step-num">4</div><div class="lp-step-text">Export Clean Data</div></div>
                    </div>
                    <div class="lp-trust-row">
                        <div class="lp-trust-item">
                            <div class="lp-trust-val">8</div>
                            <div class="lp-trust-key">Validation Checks</div>
                        </div>
                        <div class="lp-trust-divider"></div>
                        <div class="lp-trust-item">
                            <div class="lp-trust-val">10+</div>
                            <div class="lp-trust-key">Country Phone Rules</div>
                        </div>
                        <div class="lp-trust-divider"></div>
                        <div class="lp-trust-item">
                            <div class="lp-trust-val">3</div>
                            <div class="lp-trust-key">Export Formats</div>
                        </div>
                    </div>
                </div>
                <div class="lp-hero-right">
                    <div class="lp-upload-card">
                        <div class="lp-upload-icon">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                <polyline points="17 8 12 3 7 8"/>
                                <line x1="12" y1="3" x2="12" y2="15"/>
                            </svg>
                        </div>
                        <div class="lp-upload-title">Upload your dataset</div>
                        <div class="lp-upload-sub">Drop a CSV file below to begin. No account needed.</div>
                        <div class="lp-upload-specs">
                            <span class="lp-spec">CSV format</span>
                            <span class="lp-spec">UTF-8 encoding</span>
                            <span class="lp-spec">Header row required</span>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # File uploader sits right below the hero card area
        uploaded = st.file_uploader(
            "Select a CSV file",
            type=["csv"],
            label_visibility="collapsed",
        )

        if uploaded is not None:
            try:
                df = pd.read_csv(uploaded, low_memory=False)
                st.session_state.df = df
                st.session_state.filename = uploaded.name
                st.session_state.file_size = uploaded.size
                st.session_state.validation_results = None
                st.session_state.df_cleaned = None
                st.session_state.quality_score = None
                cfg = get_default_config()
                cfg.update({k: v for k, v in st.session_state.validation_config.items()
                            if k not in ("amount_columns", "date_columns", "email_columns",
                                         "phone_columns", "payment_mode_columns")})
                st.session_state.validation_config = cfg
                st.rerun()
            except Exception as e:
                st.markdown(
                    f'<div class="alert-box alert-error">Failed to read file: {e}</div>',
                    unsafe_allow_html=True,
                )
                return

        # ── Feature cards ─────────────────────────────────────────────────────
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="lp-features">
                <div class="lp-feature-card">
                    <div class="lp-feature-icon" style="background:#eff6ff">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                    </div>
                    <div class="lp-feature-name">Quality Scoring</div>
                    <div class="lp-feature-desc">0–100% quality score with per-check breakdown and import readiness verdict.</div>
                </div>
                <div class="lp-feature-card">
                    <div class="lp-feature-icon" style="background:#fef3c7">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                    </div>
                    <div class="lp-feature-name">8 Validation Checks</div>
                    <div class="lp-feature-desc">Missing values, duplicates, phone, email, date, amount, payment mode and integrity.</div>
                </div>
                <div class="lp-feature-card">
                    <div class="lp-feature-icon" style="background:#f0fdf4">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                    </div>
                    <div class="lp-feature-name">Configurable Rules</div>
                    <div class="lp-feature-desc">Set country phone patterns, date formats, amount ranges and valid payment modes.</div>
                </div>
                <div class="lp-feature-card">
                    <div class="lp-feature-icon" style="background:#fdf4ff">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#9333ea" stroke-width="2"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>
                    </div>
                    <div class="lp-feature-name">Auto Cleaning</div>
                    <div class="lp-feature-desc">One click strips whitespace, removes duplicates and nullifies invalid field values.</div>
                </div>
                <div class="lp-feature-card">
                    <div class="lp-feature-icon" style="background:#fef2f2">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                    </div>
                    <div class="lp-feature-name">Row-Level Error Log</div>
                    <div class="lp-feature-desc">Every flagged row is logged with field name and error type — ready for Excel.</div>
                </div>
                <div class="lp-feature-card">
                    <div class="lp-feature-icon" style="background:#f0f9ff">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                    </div>
                    <div class="lp-feature-name">3 Export Types</div>
                    <div class="lp-feature-desc">Download the clean CSV, plain-text validation report, or the full error log.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Supported columns reference ───────────────────────────────────────
        st.markdown(
            """
            <div class="lp-ref-card">
                <div class="lp-ref-title">Expected Column Types</div>
                <div class="lp-ref-grid">
                    <div class="lp-ref-item">
                        <div class="lp-ref-col">Order ID / Transaction ID</div>
                        <div class="lp-ref-desc">Unique identifier — checked for completeness</div>
                    </div>
                    <div class="lp-ref-item">
                        <div class="lp-ref-col">Customer Email</div>
                        <div class="lp-ref-desc">RFC-compliant format validation</div>
                    </div>
                    <div class="lp-ref-item">
                        <div class="lp-ref-col">Phone Number</div>
                        <div class="lp-ref-desc">Country-specific regex: IN, US, UK, AU, SG, AE…</div>
                    </div>
                    <div class="lp-ref-item">
                        <div class="lp-ref-col">Order Date / Created At</div>
                        <div class="lp-ref-desc">Accepts YYYY-MM-DD, DD/MM/YYYY and more</div>
                    </div>
                    <div class="lp-ref-item">
                        <div class="lp-ref-col">Amount / Total / Price</div>
                        <div class="lp-ref-desc">Numeric type + configurable min/max range</div>
                    </div>
                    <div class="lp-ref-item">
                        <div class="lp-ref-col">Payment Mode / Method</div>
                        <div class="lp-ref-desc">Whitelist: UPI, Credit Card, Net Banking, COD…</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── File loaded — show metadata + preview ─────────────────────────────────
    # Re-declare uploader so it still exists in the widget tree
    uploaded = st.file_uploader(
        "Replace dataset",
        type=["csv"],
        label_visibility="collapsed",
        key="uploader_loaded",
    )
    if uploaded is not None:
        try:
            df_new = pd.read_csv(uploaded, low_memory=False)
            st.session_state.df = df_new
            st.session_state.filename = uploaded.name
            st.session_state.file_size = uploaded.size
            st.session_state.validation_results = None
            st.session_state.df_cleaned = None
            st.session_state.quality_score = None
            st.rerun()
        except Exception as e:
            st.markdown(f'<div class="alert-box alert-error">Failed to read file: {e}</div>', unsafe_allow_html=True)

    df = st.session_state.df

    st.markdown(
        '<div class="alert-box alert-success">Dataset loaded successfully. Configure validation rules on the <b>Data Validation</b> page.</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Rows", f"{len(df):,}", "records", "blue")
    with col2:
        metric_card("Columns", f"{len(df.columns)}", "fields", "blue")
    with col3:
        size_kb = (st.session_state.file_size or 0) / 1024
        metric_card("File Size", f"{size_kb:.1f} KB", st.session_state.filename or "", "blue")
    with col4:
        null_pct = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
        metric_card("Null Cells", f"{null_pct:.1f}%", "of all cells", "amber" if null_pct > 5 else "green")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Dataset Preview", "Column Overview"])
    with tab1:
        st.dataframe(df.head(100), use_container_width=True, height=400)
        st.caption(f"Showing up to 100 of {len(df):,} rows.")
    with tab2:
        col_info = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str).values,
            "Non-Null": df.notnull().sum().values,
            "Null": df.isnull().sum().values,
            "Null %": (df.isnull().sum() / len(df) * 100).round(2).values,
            "Unique Values": df.nunique().values,
        })
        st.dataframe(col_info, use_container_width=True, hide_index=True)

# ─── Validation Page ──────────────────────────────────────────────────────────

def render_validation_page():
    page_header("Data Validation", "Configure validation rules and run quality checks on your dataset.")

    if not require_data():
        return

    df = st.session_state.df
    cfg = st.session_state.validation_config

    # ── Config Panel ──────────────────────────────────────────────────────────
    with st.expander("Validation Configuration", expanded=True):
        col_options = df.columns.tolist()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Column Assignments**")
            cfg["phone_columns"] = st.multiselect(
                "Phone Number Columns", col_options,
                default=[c for c in cfg.get("phone_columns", []) if c in col_options],
            )
            cfg["email_columns"] = st.multiselect(
                "Email Columns", col_options,
                default=[c for c in cfg.get("email_columns", []) if c in col_options],
            )
            cfg["date_columns"] = st.multiselect(
                "Date/Time Columns", col_options,
                default=[c for c in cfg.get("date_columns", []) if c in col_options],
            )
            cfg["amount_columns"] = st.multiselect(
                "Amount/Value Columns", col_options,
                default=[c for c in cfg.get("amount_columns", []) if c in col_options],
            )
            cfg["payment_mode_columns"] = st.multiselect(
                "Payment Mode Columns", col_options,
                default=[c for c in cfg.get("payment_mode_columns", []) if c in col_options],
            )

        with col2:
            st.markdown("**Validation Rules**")
            cfg["phone_country"] = st.selectbox(
                "Phone Country Code",
                options=list(PHONE_PATTERNS.keys()),
                index=list(PHONE_PATTERNS.keys()).index(cfg.get("phone_country", "IN")),
            )
            cfg["amount_min"] = st.number_input("Min Amount", value=float(cfg.get("amount_min", 0.0)), step=1.0)
            cfg["amount_max"] = st.number_input("Max Amount", value=float(cfg.get("amount_max", 10_000_000.0)), step=1000.0)

            payment_default = "\n".join(cfg.get("valid_payment_modes", []))
            payment_raw = st.text_area("Valid Payment Modes (one per line)", value=payment_default, height=140)
            cfg["valid_payment_modes"] = [p.strip() for p in payment_raw.splitlines() if p.strip()]

        date_fmt_default = ", ".join(cfg.get("date_formats", []))
        date_fmt_raw = st.text_input("Accepted Date Formats (comma-separated)", value=date_fmt_default)
        cfg["date_formats"] = [f.strip() for f in date_fmt_raw.split(",") if f.strip()]

    st.session_state.validation_config = cfg

    if st.button("Run Validation", type="primary", use_container_width=False):
        with st.spinner("Running validation checks..."):
            results = validate_dataset(df, cfg)
            st.session_state.validation_results = results
            st.session_state.quality_score = results["quality_score"]
        st.success("Validation complete.")
        st.rerun()

    if st.session_state.validation_results is None:
        return

    results = st.session_state.validation_results
    score = results["quality_score"]

    # ── Score + Summary ───────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 2])
    with col1:
        st.plotly_chart(fig_quality_gauge(score), use_container_width=True, config={"displayModeBar": False})
    with col2:
        summary_df = get_error_summary(results)
        for _, row in summary_df.iterrows():
            status_lower = row["Status"].lower()
            cls = "alert-success" if status_lower == "pass" else "alert-error" if status_lower == "fail" else "alert-warning"
            badge = status_badge(status_lower)
            st.markdown(
                f'<div class="alert-box {cls}" style="padding:10px 14px;margin-bottom:8px;">'
                f'{badge} &nbsp;<b>{row["Check"]}</b> — {row["Issues Found"]:,} issue(s)</div>',
                unsafe_allow_html=True,
            )

    # ── Detailed Results per Check ────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    checks = results["checks"]

    with st.expander("Missing Values Detail"):
        mv = checks["missing_values"]
        if mv["affected_columns"]:
            rows = [{"Column": col, "Missing Count": info["count"], "Missing %": f"{info['pct']:.2f}%"}
                    for col, info in mv["affected_columns"].items()]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.markdown("No missing values detected.")

    with st.expander("Duplicate Records"):
        dup = checks["duplicates"]
        st.markdown(f"**{dup['count']:,}** duplicate rows found.")
        if dup["duplicate_indices"]:
            st.dataframe(df.iloc[dup["duplicate_indices"][:50]], use_container_width=True, height=250)

    with st.expander("Phone Validation"):
        ph = checks["phone_validation"]
        if ph["columns"]:
            for col, info in ph["columns"].items():
                st.markdown(f"**{col}** — {info['bad_count']} invalid")
                if info["bad_indices"]:
                    st.dataframe(df.loc[info["bad_indices"][:30], [col]], use_container_width=True)
        else:
            st.markdown("No phone columns configured.")

    with st.expander("Date Validation"):
        dv = checks["date_validation"]
        if dv["columns"]:
            for col, info in dv["columns"].items():
                st.markdown(f"**{col}** — {info['bad_count']} invalid")
                if info["bad_indices"]:
                    st.dataframe(df.loc[info["bad_indices"][:30], [col]], use_container_width=True)
        else:
            st.markdown("No date columns configured.")

    with st.expander("Email Validation"):
        ev = checks["email_validation"]
        if ev["columns"]:
            for col, info in ev["columns"].items():
                st.markdown(f"**{col}** — {info['bad_count']} invalid")
                if info["bad_indices"]:
                    st.dataframe(df.loc[info["bad_indices"][:30], [col]], use_container_width=True)
        else:
            st.markdown("No email columns configured.")

    with st.expander("Amount Validation"):
        av = checks["amount_validation"]
        rng = av["range"]
        st.markdown(f"Valid range: **{rng[0]:,.2f}** to **{rng[1]:,.2f}**")
        if av["columns"]:
            for col, info in av["columns"].items():
                st.markdown(f"**{col}** — {info['bad_count']} invalid ({info['out_of_range']} out of range, {info['non_numeric']} non-numeric)")
        else:
            st.markdown("No amount columns configured.")

    with st.expander("Payment Mode Validation"):
        pm = checks["payment_mode_validation"]
        if pm["columns"]:
            for col, info in pm["columns"].items():
                st.markdown(f"**{col}** — {info['bad_count']} invalid")
                if info["invalid_values"]:
                    inv_df = pd.DataFrame(
                        [{"Value": k, "Count": v} for k, v in info["invalid_values"].items()]
                    ).sort_values("Count", ascending=False)
                    st.dataframe(inv_df, use_container_width=True, hide_index=True)
        else:
            st.markdown("No payment mode columns configured.")

    with st.expander("Data Integrity Issues"):
        di = checks["data_integrity"]
        if di["issues"]:
            st.dataframe(pd.DataFrame(di["issues"]), use_container_width=True, hide_index=True)
        else:
            st.markdown("No integrity issues detected.")

    with st.expander("Row-Level Error Log (first 200 rows)"):
        error_log = build_error_log(df, results)
        if not error_log.empty:
            st.dataframe(error_log.head(200), use_container_width=True, hide_index=True)
        else:
            st.markdown("No row-level errors.")


# ─── Cleaning Page ────────────────────────────────────────────────────────────

def render_cleaning_page():
    page_header("Data Cleaning", "Generate a cleaned version of your dataset by resolving detected issues.")

    if not require_data():
        return

    if not require_validation():
        return

    df = st.session_state.df
    cfg = st.session_state.validation_config

    st.markdown(
        """
        <div class="alert-box alert-info">
            Cleaning applies the following operations: strip leading/trailing whitespace, remove duplicate rows,
            and nullify cells that fail phone, email, amount, date, and payment mode validation.
            The original uploaded data is preserved.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Generate Cleaned Dataset", type="primary"):
        with st.spinner("Cleaning dataset..."):
            df_clean, report = clean_dataset(df, cfg)
            st.session_state.df_cleaned = df_clean
            st.session_state.cleaning_report = report
        st.success("Dataset cleaned successfully.")
        st.rerun()

    if st.session_state.df_cleaned is None:
        return

    df_clean = st.session_state.df_cleaned
    report = getattr(st.session_state, "cleaning_report", {})

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Rows Before", f"{report.get('rows_before', len(df)):,}", "original", "blue")
    with col2:
        metric_card("Rows After", f"{report.get('rows_after', len(df_clean)):,}", "after dedup", "green")
    with col3:
        metric_card("Duplicates Removed", f"{report.get('duplicates_removed', 0):,}", "rows", "amber")
    with col4:
        metric_card("Cells Modified", f"{report.get('total_cells_cleaned', 0):,}", "total", "amber")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Cleaning breakdown
    breakdown = {
        "Whitespace Stripped": report.get("whitespace_stripped", 0),
        "Invalid Phones Nulled": report.get("invalid_phones_nulled", 0),
        "Invalid Emails Nulled": report.get("invalid_emails_nulled", 0),
        "Invalid Amounts Nulled": report.get("invalid_amounts_nulled", 0),
        "Invalid Dates Nulled": report.get("invalid_dates_nulled", 0),
        "Invalid Payment Modes Nulled": report.get("invalid_payment_modes_nulled", 0),
    }
    breakdown_df = pd.DataFrame([
        {"Operation": k, "Cells Affected": v} for k, v in breakdown.items()
    ])
    st.subheader("Cleaning Operations Summary")
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

    st.subheader("Cleaned Dataset Preview")
    st.dataframe(df_clean.head(100), use_container_width=True, height=380)
    st.caption(f"Showing up to 100 of {len(df_clean):,} rows.")


# ─── Export Page ──────────────────────────────────────────────────────────────

def render_export_page():
    page_header("Export Results", "Download the cleaned dataset, validation report, and error log.")

    if not require_data():
        return

    df = st.session_state.df
    results = st.session_state.validation_results
    df_cleaned = st.session_state.df_cleaned

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Cleaned Dataset")
        if df_cleaned is not None:
            csv_bytes = df_cleaned.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Cleaned CSV",
                data=csv_bytes,
                file_name="cleaned_dataset.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary",
            )
            st.caption(f"{len(df_cleaned):,} rows · {len(df_cleaned.columns)} columns")
        else:
            st.markdown(
                '<div class="alert-box alert-warning">Run data cleaning first to download the cleaned dataset.</div>',
                unsafe_allow_html=True,
            )

    with col2:
        st.subheader("Validation Report")
        if results is not None:
            summary_df = get_error_summary(results)
            report_buf = io.StringIO()
            report_buf.write("Transaction Data Validation Report\n")
            report_buf.write("=" * 50 + "\n\n")
            report_buf.write(f"Quality Score: {results['quality_score']:.2f}%\n")
            report_buf.write(f"Total Rows: {results['total_rows']:,}\n")
            report_buf.write(f"Total Columns: {results['total_cols']}\n\n")
            report_buf.write("Check Results\n" + "-" * 30 + "\n")
            for _, row in summary_df.iterrows():
                report_buf.write(f"{row['Check']}: {row['Status']} ({row['Issues Found']} issues)\n")
            report_buf.write("\nColumn Statistics\n" + "-" * 30 + "\n")
            for col, stats in results["column_stats"].items():
                report_buf.write(
                    f"{col}: dtype={stats['dtype']}, nulls={stats['null_count']} ({stats['null_pct']}%)\n"
                )
            st.download_button(
                "Download Validation Report",
                data=report_buf.getvalue().encode("utf-8"),
                file_name="validation_report.txt",
                mime="text/plain",
                use_container_width=True,
                type="primary",
            )
        else:
            st.markdown(
                '<div class="alert-box alert-warning">Run validation first to download the report.</div>',
                unsafe_allow_html=True,
            )

    with col3:
        st.subheader("Error Log")
        if results is not None:
            error_log = build_error_log(df, results)
            if not error_log.empty:
                st.download_button(
                    "Download Error Log (CSV)",
                    data=error_log.to_csv(index=False).encode("utf-8"),
                    file_name="error_log.csv",
                    mime="text/csv",
                    use_container_width=True,
                    type="primary",
                )
                st.caption(f"{len(error_log):,} error entries")
            else:
                st.markdown(
                    '<div class="alert-box alert-success">No errors found. Nothing to export.</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="alert-box alert-warning">Run validation first to export the error log.</div>',
                unsafe_allow_html=True,
            )


# ─── CSV Splitting Page ───────────────────────────────────────────────────────

def render_splitting_page():
    page_header("CSV Splitting", "Split large CSV files into smaller chunks and download as a ZIP archive.")

    if not require_data():
        return

    df = st.session_state.df

    st.markdown(
        f'<div class="alert-box alert-info">Dataset has <b>{len(df):,} rows</b>. Configure chunk size below.</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        _min_chunk = min(10, len(df))
        _max_chunk = max(_min_chunk, len(df))
        _default_chunk = max(_min_chunk, min(1000, len(df)))
        _step = max(1, _min_chunk)
        chunk_size = st.number_input(
            "Rows per chunk",
            min_value=_min_chunk,
            max_value=_max_chunk,
            value=_default_chunk,
            step=_step,
        )
    with col2:
        use_cleaned = st.checkbox("Use cleaned dataset (if available)", value=False)

    source_df = st.session_state.df_cleaned if (use_cleaned and st.session_state.df_cleaned is not None) else df

    n_chunks = math.ceil(len(source_df) / chunk_size)
    st.markdown(
        f'<div class="alert-box alert-info">This will create <b>{n_chunks}</b> file(s) of up to <b>{chunk_size:,}</b> rows each.</div>',
        unsafe_allow_html=True,
    )

    if st.button("Generate ZIP Archive", type="primary"):
        with st.spinner(f"Splitting into {n_chunks} chunks..."):
            zip_buf = io.BytesIO()
            base_name = (st.session_state.filename or "dataset").replace(".csv", "")
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for i in range(n_chunks):
                    chunk = source_df.iloc[i * chunk_size: (i + 1) * chunk_size]
                    chunk_csv = chunk.to_csv(index=False)
                    zf.writestr(f"{base_name}_part_{i+1:04d}.csv", chunk_csv)
            zip_buf.seek(0)

        st.success(f"ZIP archive created with {n_chunks} file(s).")
        st.download_button(
            f"Download ZIP ({n_chunks} files)",
            data=zip_buf.getvalue(),
            file_name=f"{base_name}_split.zip",
            mime="application/zip",
            type="primary",
        )

        # Show summary table
        summary_rows = []
        for i in range(n_chunks):
            start = i * chunk_size + 1
            end = min((i + 1) * chunk_size, len(source_df))
            summary_rows.append({
                "File": f"{base_name}_part_{i+1:04d}.csv",
                "Start Row": start,
                "End Row": end,
                "Row Count": end - start + 1,
            })
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)


# ─── Analytics Page ───────────────────────────────────────────────────────────

def render_analytics_page():
    page_header("Analytics", "Visual analysis of data quality, error distribution, and dataset characteristics.")

    if not require_data():
        return

    df = st.session_state.df
    results = st.session_state.validation_results

    tab1, tab2, tab3 = st.tabs(["Quality Overview", "Error Analysis", "Dataset Profile"])

    with tab1:
        if results:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig_quality_gauge(results["quality_score"]),
                                use_container_width=True, config={"displayModeBar": False})
            with col2:
                st.plotly_chart(fig_duplicate_analysis(df),
                                use_container_width=True, config={"displayModeBar": False})

            st.plotly_chart(fig_completeness_heatmap(df),
                            use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown(
                '<div class="alert-box alert-warning">Run validation to see quality analytics.</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(fig_completeness_heatmap(df),
                            use_container_width=True, config={"displayModeBar": False})

    with tab2:
        if results:
            st.plotly_chart(fig_error_distribution(results),
                            use_container_width=True, config={"displayModeBar": False})
            st.plotly_chart(fig_error_trend(results, df),
                            use_container_width=True, config={"displayModeBar": False})

            # Error breakdown table
            summary_df = get_error_summary(results)
            st.subheader("Error Summary Table")
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
        else:
            st.markdown(
                '<div class="alert-box alert-warning">Run validation to see error analysis.</div>',
                unsafe_allow_html=True,
            )

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_dtype_breakdown(df),
                            use_container_width=True, config={"displayModeBar": False})
        with col2:
            # Null heatmap summary
            null_data = df.isnull().sum().reset_index()
            null_data.columns = ["Column", "Null Count"]
            null_data["Null %"] = (null_data["Null Count"] / len(df) * 100).round(2)
            null_data = null_data.sort_values("Null Count", ascending=False)
            st.subheader("Null Value Summary")
            st.dataframe(null_data, use_container_width=True, hide_index=True, height=280)

        # Descriptive stats for numeric columns
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if numeric_cols:
            st.subheader("Numeric Column Statistics")
            st.dataframe(df[numeric_cols].describe().round(2), use_container_width=True)


# ─── Insights Page ────────────────────────────────────────────────────────────

def render_insights_page():
    page_header("Insights", "Dataset health summary, key findings, and import readiness assessment.")

    if not require_data():
        return

    df = st.session_state.df
    results = st.session_state.validation_results

    if results is None:
        st.markdown(
            '<div class="alert-box alert-warning">Run validation to generate insights.</div>',
            unsafe_allow_html=True,
        )
        return

    score = results["quality_score"]
    checks = results["checks"]

    # ── Import Readiness ──────────────────────────────────────────────────────
    if score >= 90:
        readiness = ("Ready for Import", "green", "alert-success",
                     "Dataset quality is excellent. Safe to import into production.")
    elif score >= 75:
        readiness = ("Conditional Import", "amber", "alert-warning",
                     "Dataset has minor issues. Review and clean before importing.")
    elif score >= 50:
        readiness = ("Requires Cleaning", "amber", "alert-warning",
                     "Significant quality issues detected. Data cleaning is required.")
    else:
        readiness = ("Not Ready", "red", "alert-error",
                     "Dataset has critical quality issues. Do not import without thorough remediation.")

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Quality Score", f"{score:.1f}%", "overall", readiness[1])
    with col2:
        metric_card("Total Rows", f"{len(df):,}", "records", "blue")
    with col3:
        total_errors = len(results.get("row_errors", {}))
        metric_card("Rows with Errors", f"{total_errors:,}", f"{total_errors/len(df)*100:.1f}% of total", "red" if total_errors > 0 else "green")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="alert-box {readiness[2]}"><b>Import Readiness: {readiness[0]}</b><br>{readiness[3]}</div>',
        unsafe_allow_html=True,
    )

    # ── Key Issues ────────────────────────────────────────────────────────────
    st.subheader("Key Issues Identified")
    issues = []

    mv = checks["missing_values"]
    if mv["total_missing_rows"] > 0:
        pct = mv["total_missing_rows"] / len(df) * 100
        issues.append(("red", f"{mv['total_missing_rows']:,} rows ({pct:.1f}%) contain missing values "
                       f"across {len(mv['affected_columns'])} column(s)."))

    dup = checks["duplicates"]
    if dup["count"] > 0:
        issues.append(("amber", f"{dup['count']:,} duplicate records detected — these should be removed before import."))

    ph = checks["phone_validation"]
    ph_bad = sum(v["bad_count"] for v in ph["columns"].values())
    if ph_bad > 0:
        issues.append(("amber", f"{ph_bad:,} phone numbers failed validation for country '{ph['country']}'."))

    dv = checks["date_validation"]
    dt_bad = sum(v["bad_count"] for v in dv["columns"].values())
    if dt_bad > 0:
        issues.append(("amber", f"{dt_bad:,} date values could not be parsed with the configured formats."))

    ev = checks["email_validation"]
    em_bad = sum(v["bad_count"] for v in ev["columns"].values())
    if em_bad > 0:
        issues.append(("amber", f"{em_bad:,} email addresses failed format validation."))

    av = checks["amount_validation"]
    amt_bad = sum(v["bad_count"] for v in av["columns"].values())
    if amt_bad > 0:
        issues.append(("red", f"{amt_bad:,} amount values are out of range or non-numeric."))

    pm = checks["payment_mode_validation"]
    pm_bad = sum(v["bad_count"] for v in pm["columns"].values())
    if pm_bad > 0:
        issues.append(("amber", f"{pm_bad:,} payment mode values are not in the accepted list."))

    di = checks["data_integrity"]
    di_total = sum(i["count"] for i in di["issues"])
    if di_total > 0:
        issues.append(("blue", f"{di_total:,} cells contain leading or trailing whitespace."))

    if not issues:
        st.markdown(
            '<div class="alert-box alert-success">No significant issues detected. Dataset looks clean.</div>',
            unsafe_allow_html=True,
        )
    else:
        color_map = {"red": "#dc2626", "amber": "#d97706", "blue": "#2563eb", "green": "#16a34a"}
        items_html = ""
        for color, text in issues:
            items_html += f"""
            <div class="insight-item">
                <div class="insight-dot" style="background:{color_map[color]}"></div>
                <div class="insight-text">{text}</div>
            </div>
            """
        st.markdown(f'<div class="section-card">{items_html}</div>', unsafe_allow_html=True)

    # ── Recommended Actions ───────────────────────────────────────────────────
    st.subheader("Recommended Actions")
    actions = []

    if mv["total_missing_rows"] > 0:
        actions.append("Review and address missing values — consider imputation or removal depending on business rules.")
    if dup["count"] > 0:
        actions.append("Remove duplicate records using the Data Cleaning module before import.")
    if ph_bad > 0 or em_bad > 0:
        actions.append("Validate contact information at the source. Update country phone rules if needed.")
    if amt_bad > 0:
        actions.append("Investigate out-of-range amounts — these may indicate data entry errors or currency mismatches.")
    if pm_bad > 0:
        actions.append("Standardize payment mode values. Expand the accepted modes list if new modes have been introduced.")
    if di_total > 0:
        actions.append("Strip whitespace from text fields. This is handled automatically by Data Cleaning.")
    if not actions:
        actions.append("No corrective actions required. Dataset is ready for production import.")

    for i, action in enumerate(actions, 1):
        st.markdown(
            f"""
            <div class="insight-item">
                <div class="insight-dot" style="background:#2563eb;margin-top:5px"></div>
                <div class="insight-text"><span style="font-weight:600;color:#0f172a">{i}.</span> {action}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Column Health Summary ─────────────────────────────────────────────────
    st.subheader("Column Health Summary")
    col_health = []
    for col, stats in results["column_stats"].items():
        null_pct = stats["null_pct"]
        if null_pct == 0:
            health = "Complete"
        elif null_pct < 10:
            health = "Minor Gaps"
        elif null_pct < 50:
            health = "Significant Gaps"
        else:
            health = "Mostly Null"
        col_health.append({
            "Column": col,
            "Data Type": stats["dtype"],
            "Null %": f"{null_pct:.1f}%",
            "Unique Values": stats["unique_count"],
            "Health": health,
        })
    health_df = pd.DataFrame(col_health)
    st.dataframe(health_df, use_container_width=True, hide_index=True)