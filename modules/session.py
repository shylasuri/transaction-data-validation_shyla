"""Session state management"""
import streamlit as st


def init_session_state():
    defaults = {
        "current_page": "upload",
        "df": None,
        "df_cleaned": None,
        "filename": None,
        "file_size": None,
        "validation_results": None,
        "quality_score": None,
        "error_log": [],
        "validation_config": get_default_config(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_default_config():
    return {
        "phone_country": "IN",
        "date_formats": ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"],
        "amount_min": 0.0,
        "amount_max": 10_000_000.0,
        "valid_payment_modes": [
            "credit card", "debit card", "cash", "upi", "net banking",
            "wallet", "emi", "cod", "bank transfer", "cheque", "neft", "rtgs", "imps",
        ],
        "email_required": True,
        "phone_required": True,
        "amount_columns": [],
        "date_columns": [],
        "email_columns": [],
        "phone_columns": [],
        "payment_mode_columns": [],
    }
