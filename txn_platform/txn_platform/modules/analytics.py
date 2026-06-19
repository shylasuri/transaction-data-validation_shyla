"""
Analytics module — builds Plotly figures for the analytics page.
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


PALETTE = {
    "primary": "#2563eb",
    "success": "#16a34a",
    "warning": "#d97706",
    "danger": "#dc2626",
    "muted": "#94a3b8",
    "bg": "#f8f9fb",
    "border": "#e2e8f0",
}

LAYOUT_DEFAULTS = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Inter, -apple-system, sans-serif", size=12, color="#374151"),
    margin=dict(l=16, r=16, t=36, b=16),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
)


def fig_quality_gauge(score: float) -> go.Figure:
    color = PALETTE["success"] if score >= 80 else PALETTE["warning"] if score >= 60 else PALETTE["danger"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 36, "color": "#0f172a", "family": "Inter"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": PALETTE["muted"]},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": PALETTE["bg"],
            "bordercolor": PALETTE["border"],
            "steps": [
                {"range": [0, 60], "color": "#fef2f2"},
                {"range": [60, 80], "color": "#fffbeb"},
                {"range": [80, 100], "color": "#f0fdf4"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.8,
                "value": score,
            },
        },
        title={"text": "Overall Quality Score", "font": {"size": 13, "color": "#64748b"}},
    ))
    fig.update_layout(**LAYOUT_DEFAULTS, height=260)
    return fig


def fig_error_distribution(results: dict) -> go.Figure:
    checks = results["checks"]
    categories = []
    counts = []

    mappings = [
        ("missing_values", "Missing Values", lambda c: c["total_missing_cells"]),
        ("duplicates", "Duplicates", lambda c: c["count"]),
        ("phone_validation", "Phone", lambda c: sum(v["bad_count"] for v in c["columns"].values())),
        ("date_validation", "Date", lambda c: sum(v["bad_count"] for v in c["columns"].values())),
        ("email_validation", "Email", lambda c: sum(v["bad_count"] for v in c["columns"].values())),
        ("amount_validation", "Amount", lambda c: sum(v["bad_count"] for v in c["columns"].values())),
        ("payment_mode_validation", "Payment Mode", lambda c: sum(v["bad_count"] for v in c["columns"].values())),
    ]

    for key, label, extractor in mappings:
        if key in checks:
            count = extractor(checks[key])
            if count > 0:
                categories.append(label)
                counts.append(count)

    if not categories:
        fig = go.Figure()
        fig.add_annotation(text="No errors detected", x=0.5, y=0.5, showarrow=False,
                           font=dict(size=14, color=PALETTE["muted"]))
        fig.update_layout(**LAYOUT_DEFAULTS, height=300)
        return fig

    colors = [PALETTE["danger"], PALETTE["warning"], "#f97316", "#8b5cf6",
              "#06b6d4", "#ec4899", "#84cc16"]

    fig = go.Figure(go.Bar(
        x=categories,
        y=counts,
        marker_color=colors[:len(categories)],
        text=counts,
        textposition="outside",
        textfont=dict(size=11, color="#374151"),
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="Error Count by Category", font=dict(size=13, color="#374151"), x=0),
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor=PALETTE["border"], title="Count"),
        height=300,
    )
    return fig


def fig_completeness_heatmap(df: pd.DataFrame) -> go.Figure:
    null_pct = (df.isnull().sum() / len(df) * 100).round(1)
    completeness = (100 - null_pct).clip(0, 100)

    fig = go.Figure(go.Bar(
        x=completeness.values,
        y=completeness.index.tolist(),
        orientation="h",
        marker=dict(
            color=completeness.values,
            colorscale=[[0, PALETTE["danger"]], [0.5, PALETTE["warning"]], [1, PALETTE["success"]]],
            cmin=0,
            cmax=100,
            showscale=True,
            colorbar=dict(title="% Complete", thickness=12, len=0.8),
        ),
        text=[f"{v:.1f}%" for v in completeness.values],
        textposition="outside",
        textfont=dict(size=10),
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="Column Completeness (%)", font=dict(size=13, color="#374151"), x=0),
        xaxis=dict(range=[0, 115], showgrid=True, gridcolor=PALETTE["border"], title="Completeness (%)"),
        yaxis=dict(title=None, automargin=True),
        height=max(300, len(df.columns) * 28),
    )
    return fig


def fig_duplicate_analysis(df: pd.DataFrame) -> go.Figure:
    dup_count = int(df.duplicated().sum())
    unique_count = len(df) - dup_count

    fig = go.Figure(go.Pie(
        labels=["Unique Records", "Duplicate Records"],
        values=[unique_count, dup_count],
        hole=0.55,
        marker=dict(colors=[PALETTE["success"], PALETTE["danger"]]),
        textinfo="label+percent",
        textfont=dict(size=12),
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="Record Uniqueness", font=dict(size=13, color="#374151"), x=0),
        showlegend=False,
        height=280,
        annotations=[dict(
            text=f"<b>{len(df):,}</b><br>Total",
            x=0.5, y=0.5,
            font=dict(size=13, color="#0f172a"),
            showarrow=False,
        )],
    )
    return fig


def fig_dtype_breakdown(df: pd.DataFrame) -> go.Figure:
    dtype_counts = df.dtypes.astype(str).value_counts()
    labels = dtype_counts.index.tolist()
    values = dtype_counts.values.tolist()

    colors = [PALETTE["primary"], "#7c3aed", "#0891b2", "#b45309", "#be185d"]
    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors[:len(labels)],
        text=values,
        textposition="outside",
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="Column Data Types", font=dict(size=13, color="#374151"), x=0),
        xaxis=dict(title=None, showgrid=False),
        yaxis=dict(title="Count", showgrid=True, gridcolor=PALETTE["border"]),
        height=260,
    )
    return fig


def fig_error_trend(results: dict, df: pd.DataFrame) -> go.Figure:
    """Show error density across row buckets."""
    total = len(df)
    if total == 0 or not results.get("row_errors"):
        fig = go.Figure()
        fig.add_annotation(text="No error data available", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(**LAYOUT_DEFAULTS, height=250)
        return fig

    error_rows = sorted(results["row_errors"].keys())
    n_buckets = min(20, total)
    bucket_size = max(1, total // n_buckets)

    buckets = list(range(0, total, bucket_size))
    bucket_labels = [f"{b+1}-{min(b+bucket_size, total)}" for b in buckets]
    bucket_counts = []
    for b in buckets:
        count = sum(1 for r in error_rows if b <= r < b + bucket_size)
        bucket_counts.append(count)

    fig = go.Figure(go.Scatter(
        x=bucket_labels,
        y=bucket_counts,
        mode="lines+markers",
        line=dict(color=PALETTE["danger"], width=2),
        marker=dict(color=PALETTE["danger"], size=5),
        fill="tozeroy",
        fillcolor="rgba(220,38,38,0.08)",
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="Error Density Across Dataset (Row Buckets)", font=dict(size=13, color="#374151"), x=0),
        xaxis=dict(title="Row Range", showgrid=False, tickangle=-30),
        yaxis=dict(title="Errors in Bucket", showgrid=True, gridcolor=PALETTE["border"]),
        height=260,
    )
    return fig
