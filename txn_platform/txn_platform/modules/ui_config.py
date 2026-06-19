"""UI styling and configuration"""
print("UI CONFIG LOADED")
import streamlit as st


def apply_styles():
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

        <style>
        /* ── Base ── */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        .stApp { background-color: #f0f2f8; }
        #MainMenu, footer, header { visibility: hidden; }
        .block-container {
            padding: 0 2.5rem 2rem 2rem;
            max-width: 1400px;
        }

        /* ── Top App Bar ── */
        .top-bar {
            position: sticky;
            top: 0;
            z-index: 999;
            background: #ffffff;
            border-bottom: 1px solid #e2e8f0;
            padding: 0 2.5rem;
            height: 62px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 0 -2.5rem 28px -2rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        }
        .top-bar-left {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .top-bar-logo {
            width: 36px; height: 36px;
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            border-radius: 9px;
            display: flex; align-items: center; justify-content: center;
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 800; font-size: 13px; color: #fff;
            letter-spacing: 0.04em;
            box-shadow: 0 2px 8px rgba(37,99,235,0.35);
        }
        .top-bar-name {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 700;
            font-size: 15px;
            color: #0f172a;
            letter-spacing: -0.01em;
        }
        .top-bar-name span {
            color: #2563eb;
        }
        .top-bar-right {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        .top-bar-pill {
            background: #eff6ff;
            color: #1d4ed8;
            font-size: 11px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 99px;
            letter-spacing: 0.04em;
            border: 1px solid #bfdbfe;
        }
        .top-bar-version {
            font-size: 11px;
            color: #94a3b8;
            font-weight: 500;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid #1e293b;
        }
        [data-testid="stSidebar"] > div:first-child { padding: 0; }

        .sidebar-header {
            display: flex; align-items: center; gap: 12px;
            padding: 24px 20px 20px;
        }
        .sidebar-logo {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: #fff; font-weight: 800; font-size: 13px;
            font-family: 'Plus Jakarta Sans', sans-serif;
            letter-spacing: 0.05em;
            width: 38px; height: 38px; border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
            box-shadow: 0 2px 8px rgba(37,99,235,0.4);
        }
        .sidebar-title {
            color: #f1f5f9; font-size: 12px; font-weight: 600;
            line-height: 1.4; letter-spacing: 0.01em;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .sidebar-divider { height: 1px; background: #1e293b; margin: 8px 0; }
        .nav-label {
            color: #475569; font-size: 10px; font-weight: 700;
            letter-spacing: 0.12em; padding: 12px 20px 6px;
        }

        /* ── Sidebar Buttons ── */
        [data-testid="stSidebar"] .stButton button {
            background: transparent !important; color: #94a3b8 !important;
            border: none !important; border-radius: 6px !important;
            font-size: 13px !important; font-weight: 500 !important;
            text-align: left !important; padding: 9px 20px !important;
            margin: 1px 8px !important; width: calc(100% - 16px) !important;
            transition: all 0.15s ease !important; box-shadow: none !important;
        }
        [data-testid="stSidebar"] .stButton button:hover {
            background: #1e293b !important; color: #e2e8f0 !important;
        }
        [data-testid="stSidebar"] .stButton button[kind="primary"] {
            background: #1e40af !important; color: #dbeafe !important;
            font-weight: 600 !important;
        }

        /* ── Sidebar Info / Score ── */
        .info-card {
            background: #1e293b; border-radius: 8px;
            padding: 12px 14px; margin: 8px 16px; font-size: 12px;
        }
        .info-card.muted { color: #64748b; line-height: 1.5; }
        .info-row { display: flex; justify-content: space-between; align-items: center; padding: 3px 0; }
        .info-key { color: #64748b; }
        .info-val { color: #e2e8f0; font-weight: 500; }
        .truncate { max-width: 100px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .score-card {
            background: #1e293b; border-radius: 8px;
            padding: 12px 14px; margin: 8px 16px; text-align: center;
        }
        .score-label { color: #64748b; font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 4px; }
        .score-value { font-size: 28px; font-weight: 700; }

        /* ── Page Header ── */
        .page-header { margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px solid #e2e8f0; }
        .page-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 24px; font-weight: 800; color: #0f172a;
            margin: 0 0 4px; letter-spacing: -0.03em;
        }
        .page-subtitle { font-size: 14px; color: #64748b; margin: 0; }

        /* ── Metric Cards ── */
        .metric-card {
            background: #fff; border: 1px solid #e2e8f0;
            border-radius: 12px; padding: 20px;
        }
        .metric-label {
            font-size: 11px; color: #64748b; font-weight: 600;
            letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 10px;
        }
        .metric-value {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 30px; font-weight: 800; color: #0f172a; line-height: 1;
        }
        .metric-sub { font-size: 12px; color: #94a3b8; margin-top: 6px; }
        .metric-card.green { border-left: 3px solid #16a34a; }
        .metric-card.red   { border-left: 3px solid #dc2626; }
        .metric-card.amber { border-left: 3px solid #d97706; }
        .metric-card.blue  { border-left: 3px solid #2563eb; }

        /* ── Section Card ── */
        .section-card {
            background: #fff; border: 1px solid #e2e8f0;
            border-radius: 12px; padding: 24px; margin-bottom: 20px;
        }
        .section-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 15px; font-weight: 700; color: #0f172a;
            margin: 0 0 16px; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9;
        }

        /* ── Hero / Empty State ── */
        .hero-wrap {
            background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 50%, #2563eb 100%);
            border-radius: 16px;
            padding: 52px 48px;
            margin-bottom: 28px;
            position: relative;
            overflow: hidden;
        }
        .hero-wrap::before {
            content: '';
            position: absolute;
            top: -60px; right: -60px;
            width: 280px; height: 280px;
            background: rgba(255,255,255,0.05);
            border-radius: 50%;
        }
        .hero-wrap::after {
            content: '';
            position: absolute;
            bottom: -80px; right: 100px;
            width: 200px; height: 200px;
            background: rgba(255,255,255,0.04);
            border-radius: 50%;
        }
        .hero-tag {
            display: inline-block;
            background: rgba(255,255,255,0.15);
            color: #bfdbfe;
            font-size: 11px; font-weight: 700;
            letter-spacing: 0.1em; text-transform: uppercase;
            padding: 5px 12px; border-radius: 99px;
            margin-bottom: 18px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .hero-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 34px; font-weight: 800; color: #fff;
            line-height: 1.15; letter-spacing: -0.03em;
            margin: 0 0 14px; max-width: 560px;
        }
        .hero-title span { color: #93c5fd; }
        .hero-body {
            font-size: 15px; color: #bfdbfe; line-height: 1.65;
            max-width: 520px; margin-bottom: 32px;
        }
        .hero-steps {
            display: flex; gap: 10px; flex-wrap: wrap;
        }
        .hero-step {
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 8px; padding: 10px 16px;
            display: flex; align-items: center; gap: 10px;
        }
        .hero-step-num {
            background: rgba(255,255,255,0.2);
            color: #fff; font-size: 11px; font-weight: 700;
            width: 22px; height: 22px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
        }
        .hero-step-text { font-size: 12px; color: #e0f2fe; font-weight: 500; }

        /* ── Upload Drop Zone ── */
        .upload-zone-wrap {
            background: #fff;
            border: 2px dashed #c7d2fe;
            border-radius: 14px;
            padding: 40px 32px;
            text-align: center;
            transition: border-color 0.2s;
            margin-bottom: 20px;
        }
      /* ── Landing Page Hero ── */
        .lp-hero {
            display: grid;
            grid-template-columns: 1fr 420px;
            gap: 32px;
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 60%, #1d4ed8 100%);
            border-radius: 18px;
            padding: 48px 44px;
            margin-bottom: 28px;
            align-items: center;
            min-height: 380px;
            position: relative;
            overflow: hidden;
        }
        .lp-hero::after {
            content: '';
            position: absolute;
            width: 360px; height: 360px;
            background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%);
            top: -80px; right: 360px;
            border-radius: 50%;
        }
        .lp-hero-left { position: relative; z-index: 1; }
        .lp-hero-tag {
            display: inline-block;
            background: rgba(255,255,255,0.12);
            color: #bfdbfe;
            font-size: 11px; font-weight: 700; letter-spacing: 0.1em;
            text-transform: uppercase; padding: 5px 14px;
            border-radius: 99px; margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.18);
        }
        .lp-hero-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 40px; font-weight: 800; color: #fff;
            line-height: 1.1; letter-spacing: -0.04em;
            margin: 0 0 16px;
        }
        .lp-hero-title span { color: #93c5fd; }
        .lp-hero-body {
            font-size: 14.5px; color: #93c5fd; line-height: 1.7;
            max-width: 440px; margin-bottom: 28px;
        }
        .lp-steps { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 32px; }
        .lp-step {
            display: flex; align-items: center; gap: 8px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 8px; padding: 8px 14px;
        }
        .lp-step-num {
            background: rgba(255,255,255,0.2); color: #fff;
            font-size: 11px; font-weight: 700;
            width: 20px; height: 20px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
        }
        .lp-step-text { font-size: 12px; color: #e0f2fe; font-weight: 500; }
        .lp-trust-row { display: flex; align-items: center; gap: 20px; }
        .lp-trust-item { text-align: left; }
        .lp-trust-val {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 26px; font-weight: 800; color: #fff;
        }
        .lp-trust-key { font-size: 11px; color: #64748b; margin-top: 2px; }
        .lp-trust-divider { width: 1px; height: 36px; background: rgba(255,255,255,0.12); }

        /* ── Upload Card (inside hero) ── */
        .lp-hero-right { position: relative; z-index: 1; }
        .lp-upload-card {
            background: #fff;
            border-radius: 16px;
            padding: 32px 28px 24px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .lp-upload-icon {
            width: 60px; height: 60px; background: #eff6ff;
            border-radius: 14px; display: flex; align-items: center;
            justify-content: center; margin-bottom: 18px;
        }
        .lp-upload-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 18px; font-weight: 800; color: #0f172a; margin-bottom: 6px;
        }
        .lp-upload-sub { font-size: 13px; color: #64748b; line-height: 1.55; margin-bottom: 16px; }
        .lp-upload-specs { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
        .lp-spec {
            background: #f1f5f9; border: 1px solid #e2e8f0;
            border-radius: 6px; padding: 3px 9px;
            font-size: 11px; color: #64748b; font-weight: 500;
        }

        /* ── Feature Cards ── */
        .lp-features {
            display: grid; grid-template-columns: repeat(3, 1fr);
            gap: 14px; margin-bottom: 20px;
        }
        .lp-feature-card {
            background: #fff; border: 1px solid #e2e8f0;
            border-radius: 12px; padding: 20px;
            transition: box-shadow 0.2s, transform 0.2s;
        }
        .lp-feature-card:hover {
            box-shadow: 0 6px 20px rgba(0,0,0,0.08);
            transform: translateY(-2px);
        }
        .lp-feature-icon {
            width: 40px; height: 40px; border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 12px;
        }
        .lp-feature-name {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 5px;
        }
        .lp-feature-desc { font-size: 12px; color: #64748b; line-height: 1.55; }

        /* ── Reference Card ── */
        .lp-ref-card {
            background: #fff; border: 1px solid #e2e8f0;
            border-radius: 12px; padding: 24px; margin-bottom: 20px;
        }
        .lp-ref-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 14px; font-weight: 700; color: #0f172a;
            margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9;
        }
        .lp-ref-grid {
            display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;
        }
        .lp-ref-item {
            padding: 10px 14px; background: #f8fafc;
            border-radius: 8px; border: 1px solid #f1f5f9;
        }
        .lp-ref-col {
            font-size: 13px; font-weight: 600; color: #2563eb; margin-bottom: 3px;
        }
        .lp-ref-desc { font-size: 12px; color: #64748b; line-height: 1.4; }

        /* ── Feature Cards (empty state — legacy, kept for compatibility) ── */
        .feature-grid {
            display: grid; grid-template-columns: repeat(3, 1fr);
            gap: 16px; margin-bottom: 24px;
        }
        .feature-card {
            background: #fff; border: 1px solid #e2e8f0;
            border-radius: 12px; padding: 22px 20px;
            transition: box-shadow 0.2s;
        }
        .feature-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.07); }
        .feature-icon {
            width: 40px; height: 40px; border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 18px; margin-bottom: 14px;
        }
        .feature-name {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 6px;
        }
        .feature-desc { font-size: 12px; color: #64748b; line-height: 1.55; }

        /* ── Supported format table ── */
        .format-card {
            background: #fff; border: 1px solid #e2e8f0;
            border-radius: 12px; padding: 22px 24px; margin-bottom: 20px;
        }
        .format-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 14px;
        }
        .format-row {
            display: flex; align-items: flex-start; gap: 12px;
            padding: 9px 0; border-bottom: 1px solid #f8f9fb; font-size: 13px;
        }
        .format-row:last-child { border-bottom: none; }
        .format-col { color: #2563eb; font-weight: 600; min-width: 160px; }
        .format-type { color: #94a3b8; font-size: 11px; margin-top: 1px; }

        /* ── Status Badges ── */
        .badge {
            display: inline-block; padding: 2px 8px;
            border-radius: 20px; font-size: 11px; font-weight: 600; letter-spacing: 0.04em;
        }
        .badge-pass { background: #dcfce7; color: #15803d; }
        .badge-fail { background: #fee2e2; color: #dc2626; }
        .badge-warn { background: #fef3c7; color: #b45309; }
        .badge-info { background: #dbeafe; color: #1d4ed8; }

        /* ── Alert Boxes ── */
        .alert-box {
            border-radius: 8px; padding: 14px 18px;
            margin-bottom: 16px; font-size: 13px; line-height: 1.5;
        }
        .alert-success { background: #f0fdf4; border: 1px solid #86efac; color: #14532d; }
        .alert-error   { background: #fef2f2; border: 1px solid #fca5a5; color: #7f1d1d; }
        .alert-warning { background: #fffbeb; border: 1px solid #fde68a; color: #78350f; }
        .alert-info    { background: #eff6ff; border: 1px solid #93c5fd; color: #1e3a8a; }

        /* ── Table Tweaks ── */
        .stDataFrame { border-radius: 10px; overflow: hidden; border: 1px solid #e2e8f0 !important; }
        .stDataFrame thead th {
            background: #f8f9fb !important; font-size: 12px !important;
            font-weight: 600 !important; color: #374151 !important;
        }

        /* ── Expander ── */
        .streamlit-expanderHeader {
            font-size: 13px !important; font-weight: 600 !important;
            color: #374151 !important; background: #f8f9fb !important;
            border-radius: 6px !important;
        }

        /* ── Insight Items ── */
        .insight-item {
            display: flex; gap: 12px; padding: 12px 0;
            border-bottom: 1px solid #f1f5f9; align-items: flex-start;
        }
        .insight-item:last-child { border-bottom: none; }
        .insight-dot {
            width: 8px; height: 8px; border-radius: 50%;
            margin-top: 5px; flex-shrink: 0;
        }
        .insight-text { font-size: 13px; color: #374151; line-height: 1.5; }

        /* ── Main Buttons ── */
        .stButton button[kind="primary"] {
            background: #2563eb !important; border-color: #2563eb !important;
            font-weight: 600 !important; border-radius: 7px !important;
            font-family: 'Inter', sans-serif !important;
        }
        .stButton button[kind="secondary"] { border-radius: 7px !important; }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            background: #f1f5f9; border-radius: 8px; padding: 4px; gap: 2px; border: none;
        }
        .stTabs [data-baseweb="tab"] {
            background: transparent; border: none; border-radius: 6px;
            font-size: 13px; font-weight: 500; color: #64748b; padding: 6px 16px;
        }
        .stTabs [aria-selected="true"] {
            background: #fff !important; color: #0f172a !important;
            font-weight: 600 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }

        /* ── File uploader override ── */
        [data-testid="stFileUploader"] {
            background: transparent !important;
        }
        [data-testid="stFileUploaderDropzone"] {
            border: none !important;
            background: transparent !important;
            padding: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_top_bar():
    st.markdown(
        """
        <div class="top-bar">
            <div class="top-bar-left">
                <div class="top-bar-logo">TDV</div>
                <div class="top-bar-name">Transaction <span>Data Validation</span> Platform</div>
            </div>
            <div class="top-bar-right">
                <span class="top-bar-pill">Production Ready</span>
                <span class="top-bar-version">v1.0.0</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )