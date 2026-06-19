"""
Transaction Data Validation & Quality Intelligence Platform
Main application entry point
"""

import streamlit as st
from modules.ui_config import apply_styles
from modules.session import init_session_state
from modules.pages import (
    render_upload_page,
    render_validation_page,
    render_cleaning_page,
    render_export_page,
    render_splitting_page,
    render_analytics_page,
    render_insights_page,
)

st.set_page_config(
    page_title="Transaction Data Validation Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()
init_session_state()


def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-header">
                <div class="sidebar-logo">TDV</div>
                <div class="sidebar-title">Transaction Data<br>Validation Platform</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

        nav_items = [
            ("Upload", "upload", "Upload & Preview"),
            ("Validate", "validation", "Data Validation"),
            ("Clean", "cleaning", "Data Cleaning"),
            ("Export", "export", "Export Results"),
            ("Split", "splitting", "CSV Splitting"),
            ("Analytics", "analytics", "Analytics"),
            ("Insights", "insights", "Insights"),
        ]

        st.markdown("<div class='nav-label'>NAVIGATION</div>", unsafe_allow_html=True)

        for label, page_key, full_label in nav_items:
            is_active = st.session_state.current_page == page_key
            active_class = "nav-btn-active" if is_active else "nav-btn"

            if st.button(
                full_label,
                key=f"nav_{page_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

        if st.session_state.df is not None:
            df = st.session_state.df
            st.markdown("<div class='nav-label'>DATASET INFO</div>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="info-card">
                    <div class="info-row"><span class="info-key">Rows</span><span class="info-val">{len(df):,}</span></div>
                    <div class="info-row"><span class="info-key">Columns</span><span class="info-val">{len(df.columns)}</span></div>
                    <div class="info-row"><span class="info-key">File</span><span class="info-val truncate">{st.session_state.filename or '—'}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.session_state.quality_score is not None:
                score = st.session_state.quality_score
                score_color = "#16a34a" if score >= 80 else "#d97706" if score >= 60 else "#dc2626"
                st.markdown(
                    f"""
                    <div class="score-card">
                        <div class="score-label">Quality Score</div>
                        <div class="score-value" style="color:{score_color}">{score:.1f}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
                <div class="info-card muted">
                    No dataset loaded.<br>Upload a CSV to begin.
                </div>
                """,
                unsafe_allow_html=True,
            )


def main():
    render_sidebar()

    page = st.session_state.current_page

    if page == "upload":
        render_upload_page()
    elif page == "validation":
        render_validation_page()
    elif page == "cleaning":
        render_cleaning_page()
    elif page == "export":
        render_export_page()
    elif page == "splitting":
        render_splitting_page()
    elif page == "analytics":
        render_analytics_page()
    elif page == "insights":
        render_insights_page()


if __name__ == "__main__":
    main()
