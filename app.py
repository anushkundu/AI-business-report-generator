# app.py

"""
AI BUSINESS REPORT GENERATOR — PROFESSIONAL DASHBOARD
─────────────────────────────────────────────────────
Crimson & Gold Theme · Tabbed Interface · Production Ready
"""

import streamlit as st
import pandas as pd
import re
from datetime import datetime

# ── Our Modules ─────────────────────────────────────────
from src.ingestion.data_loader import DataLoader
from src.ingestion.data_profiler import DataProfiler
from src.analysis.descriptive import DescriptiveAnalyzer
from src.analysis.smart_kpi_calculator import SmartKPICalculator
from src.analysis.trend_detector import TrendDetector
from src.analysis.anomaly_detector import AnomalyDetector
from src.analysis.domain_config import get_domain_options, get_domain_config
from src.visualization.chart_recommender import ChartRecommender
from src.visualization.chart_builder import ChartBuilder
from src.narrative.narrator import ReportNarrator
from src.narrative.quality_scorer import ReportQualityScorer
from src.utils.llm_client import llm
from src.report.html_generator import HTMLReportGenerator


# ═══════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ═══════════════════════════════════════════════════════════
# HELPER — Style Plotly Charts (title on top, legend below)
# ═══════════════════════════════════════════════════════════
def style_plotly_chart(fig):
    """Apply crimson/gold theme. Title stays on top, legend sits below x-axis."""
    fig.update_layout(
        title=dict(
            y=0.97, x=0.5,
            xanchor="center", yanchor="top",
            font=dict(size=14, color="#FFD700", family="Arial"),
        ),
        legend=dict(
            orientation="h",
            yanchor="top", y=-0.22,
            xanchor="center", x=0.5,
            font=dict(size=10, color="#FFE4B5"),
            bgcolor="rgba(26,10,14,0.6)",
            bordercolor="rgba(184,134,11,0.4)",
            borderwidth=1,
        ),
        hoverlabel=dict(
            bgcolor="#1a0a0e",
            font_size=13,
            font_family="Arial",
            font_color="#FFD700",
            bordercolor="#DC143C",
        ),
        paper_bgcolor="rgba(15,8,12,0.9)",
        plot_bgcolor="rgba(20,10,15,0.7)",
        font=dict(color="#FFE4B5", family="Arial", size=11),
        margin=dict(t=60, b=100, l=55, r=25),
        colorway=[
            "#DC143C", "#FFD700", "#FF6347", "#DAA520",
            "#FF4500", "#FFA500", "#CD853F", "#B22222",
            "#FF69B4", "#DEB887",
        ],
    )
    try:
        fig.update_xaxes(
            gridcolor="rgba(184,134,11,0.1)",
            color="#DAA520",
            linecolor="rgba(184,134,11,0.25)",
            tickfont=dict(color="#DAA520", size=10),
        )
        fig.update_yaxes(
            gridcolor="rgba(184,134,11,0.1)",
            color="#DAA520",
            linecolor="rgba(184,134,11,0.25)",
            tickfont=dict(color="#DAA520", size=10),
        )
    except Exception:
        pass
    return fig


# ═══════════════════════════════════════════════════════════
# CRIMSON & GOLD — FULL THEME CSS
# ═══════════════════════════════════════════════════════════
st.markdown(
    """
<style>
/* ─── App Background ─── */
.stApp {
    background: linear-gradient(160deg, #0d1f12 0%, #0a1810 50%, #0d1f12 100%);
}
[data-testid="stHeader"]{
    background:rgba(13,5,10,0.95);
    border-bottom:2px solid #DC143C;
}

/* ─── Sidebar ─── */
[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#1a0a0e,#0d0510);
    border-right:2px solid #B8860B;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] p{color:#FFE4B5!important}

/* ─── Headers ─── */
.main-header{
    font-size:2.6rem;font-weight:800;
    background:linear-gradient(90deg,#DC143C,#FFD700,#DC143C);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    text-align:center;padding:12px 0 4px;letter-spacing:1px;
}
.sub-header{
    text-align:center;color:#DAA520!important;
    font-size:1.05rem;margin-bottom:20px;font-weight:300;
}
h1,h2,h3{color:#FFD700!important}
h4,h5{color:#DAA520!important}

/* ─── Body text ─── */
p,span,label,li,
.stMarkdown,
[data-testid="stText"]{color:#FFE4B5!important}
.stCaption,[data-testid="stCaption"]{color:#DAA520!important}

/* ─── Tabs ─── */
.stTabs [data-baseweb="tab-list"]{
    gap:4px;background:rgba(26,10,14,0.6);
    border-radius:10px;padding:5px;border:1px solid #B8860B;
}
.stTabs [data-baseweb="tab"]{
    background:rgba(26,10,14,0.8);color:#FFE4B5!important;
    border-radius:8px;border:1px solid transparent;
    padding:10px 18px;font-weight:600;
}
.stTabs [data-baseweb="tab"]:hover{
    background:rgba(220,20,60,0.25);border-color:#DC143C;
}
.stTabs [aria-selected="true"]{
    background:linear-gradient(135deg,#DC143C,#8B0000)!important;
    color:#FFD700!important;border-color:#FFD700!important;font-weight:700;
}
.stTabs [data-baseweb="tab-panel"]{padding-top:20px}

/* ─── Metrics ─── */
[data-testid="stMetric"]{
    background:linear-gradient(135deg,rgba(220,20,60,0.12),rgba(184,134,11,0.08));
    border:1px solid #B8860B;border-radius:10px;padding:15px;
}
[data-testid="stMetricValue"]{color:#FFD700!important;font-weight:700}
[data-testid="stMetricLabel"]{color:#FFE4B5!important}
[data-testid="stMetricDelta"]{font-weight:600}

/* ─── Form Inputs ─── */
.stSelectbox [data-baseweb="select"]>div,
.stTextInput>div>div>input,
.stNumberInput>div>div>input{
    background-color:rgba(26,10,14,0.85)!important;
    color:#FFE4B5!important;
    border:1px solid #B8860B!important;
    border-radius:8px!important;
}
.stSelectbox label,.stTextInput label,.stRadio label{
    color:#FFD700!important;font-weight:600;
}
[data-baseweb="select"] span{color:#FFE4B5!important}
[data-baseweb="popover"] ul,
[data-baseweb="menu"]{
    background-color:#1a0a0e!important;
    border:1px solid #DC143C!important;
}
[data-baseweb="menu"] li{color:#FFE4B5!important}
[data-baseweb="menu"] li:hover{background:rgba(220,20,60,0.3)!important}

/* ─── Buttons ─── */
.stButton>button{
    background:linear-gradient(90deg,#DC143C,#B22222)!important;
    color:#FFD700!important;border:1px solid #FFD700!important;
    border-radius:8px!important;font-weight:700!important;
    transition:all .3s ease!important;
}
.stButton>button:hover{
    background:linear-gradient(90deg,#FFD700,#DAA520)!important;
    color:#1a0a0e!important;border-color:#DC143C!important;
    box-shadow:0 4px 15px rgba(220,20,60,0.4);
}
button[kind="primary"]{
    background:linear-gradient(90deg,#FFD700,#DAA520)!important;
    color:#1a0a0e!important;border-color:#DC143C!important;
}

/* ─── Download Buttons ─── */
.stDownloadButton>button{
    background:linear-gradient(90deg,#B8860B,#DAA520)!important;
    color:#1a0a0e!important;border:1px solid #FFD700!important;
    border-radius:8px!important;font-weight:600!important;
}
.stDownloadButton>button:hover{
    background:linear-gradient(90deg,#FFD700,#FFA500)!important;
    box-shadow:0 4px 15px rgba(255,215,0,0.4);
}

/* ─── Expanders ─── */
[data-testid="stExpander"]{
    background:rgba(26,10,14,0.45);
    border:1px solid rgba(184,134,11,0.5);border-radius:10px;
}
[data-testid="stExpander"] summary span{color:#FFD700!important;font-weight:600}

/* ─── File Uploader ─── */
[data-testid="stFileUploader"]{
    border:2px dashed #B8860B!important;border-radius:12px;
}
[data-testid="stFileUploader"] label{color:#FFD700!important}
[data-testid="stFileUploader"] section{
    background:rgba(26,10,14,0.4)!important;border-radius:12px;padding:15px;
}
[data-testid="stFileUploader"] button{
    background:rgba(220,20,60,0.3)!important;color:#FFD700!important;
    border:1px solid #B8860B!important;border-radius:6px!important;
}

/* ─── Progress Bar ─── */
.stProgress>div>div>div{
    background:linear-gradient(90deg,#DC143C,#FFD700)!important;
}

/* ─── Divider ─── */
hr{border-color:rgba(184,134,11,0.3)!important}

/* ─── Alerts ─── */
[data-testid="stAlert"]{border-radius:8px!important}

/* ─── DataFrames ─── */
[data-testid="stDataFrame"]{border:1px solid rgba(184,134,11,0.35);border-radius:8px}

/* ─── Slider ─── */
[data-testid="stSlider"] label{color:#FFD700!important}

/* ─── Radio ─── */
.stRadio>div label span{color:#FFE4B5!important}

/* ─── Scrollbar ─── */
::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-track{background:#0d0d1a}
::-webkit-scrollbar-thumb{background:#DC143C;border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:#FFD700}

/* ─── Domain Card Grid ─── */
.domain-grid{
    display:flex;flex-wrap:wrap;gap:10px;
    justify-content:center;margin:12px 0 18px;
}
.domain-card{
    background:linear-gradient(135deg,rgba(220,20,60,0.1),rgba(184,134,11,0.06));
    border:1px solid rgba(184,134,11,0.4);border-radius:12px;
    padding:10px 14px;text-align:center;min-width:105px;flex:1;
    transition:all .3s ease;
}
.domain-card:hover{
    border-color:#FFD700;
    background:linear-gradient(135deg,rgba(220,20,60,0.2),rgba(184,134,11,0.12));
    transform:translateY(-2px);box-shadow:0 4px 12px rgba(220,20,60,0.25);
}
.domain-icon{font-size:1.6rem;display:block;margin-bottom:3px}
.domain-name{color:#FFE4B5;font-weight:600;font-size:0.78rem}
.format-note{
    text-align:center;color:#B8860B;font-size:0.78rem;margin-top:4px;
}

/* ─── About Tab — Problem Card ─── */
.problem-card{
    background:linear-gradient(135deg,rgba(220,20,60,0.12),rgba(184,134,11,0.06));
    border:1px solid #B8860B;border-radius:14px;
    padding:28px 32px;margin:10px 0 20px;
}
.problem-card h3{color:#FFD700!important;margin-bottom:12px;font-size:1.3rem}
.problem-card p{color:#FFE4B5!important;line-height:1.8;font-size:0.95rem}
.highlight-crimson{color:#DC143C!important;font-weight:700}
.highlight-gold{color:#FFD700!important;font-weight:700}

/* ─── About Tab — Architecture Steps ─── */
.arch-step{
    background:linear-gradient(135deg,rgba(220,20,60,0.1),rgba(184,134,11,0.06));
    border:1px solid rgba(184,134,11,0.5);border-radius:12px;
    padding:18px 10px;text-align:center;min-height:130px;
    transition:all .3s ease;
}
.arch-step:hover{
    border-color:#FFD700;transform:translateY(-3px);
    box-shadow:0 6px 18px rgba(220,20,60,0.25);
}
.arch-icon{font-size:2rem;margin-bottom:6px}
.arch-title{color:#FFD700;font-weight:700;font-size:0.9rem;margin-bottom:4px}
.arch-desc{color:#DAA520;font-size:0.72rem;white-space:pre-line;line-height:1.4}
.arch-arrow{
    display:flex;align-items:center;justify-content:center;
    font-size:1.8rem;color:#DC143C;height:130px;
}

/* ─── About Tab — Feature Cards ─── */
.feature-card{
    background:linear-gradient(135deg,rgba(220,20,60,0.1),rgba(184,134,11,0.06));
    border:1px solid rgba(184,134,11,0.4);border-radius:12px;
    padding:22px 18px;text-align:center;margin-bottom:12px;
    transition:all .3s ease;min-height:160px;
}
.feature-card:hover{
    border-color:#FFD700;transform:translateY(-2px);
    box-shadow:0 4px 14px rgba(220,20,60,0.2);
}
.feature-icon{font-size:2.2rem;margin-bottom:8px}
.feature-value{color:#FFD700;font-size:1.5rem;font-weight:800;margin-bottom:4px}
.feature-label{color:#FFE4B5;font-size:0.85rem;font-weight:600;margin-bottom:4px}
.feature-sub{color:#DAA520;font-size:0.72rem}

/* ─── About Tab — Tech Pills ─── */
.tech-pill{
    display:inline-block;
    background:linear-gradient(135deg,rgba(220,20,60,0.2),rgba(184,134,11,0.1));
    border:1px solid rgba(184,134,11,0.5);border-radius:20px;
    padding:6px 16px;margin:4px;color:#FFD700!important;
    font-size:0.82rem;font-weight:600;
    transition:all .3s ease;
}
.tech-pill:hover{
    background:linear-gradient(135deg,rgba(220,20,60,0.35),rgba(184,134,11,0.2));
    border-color:#FFD700;transform:scale(1.05);
}

/* ─── About Tab — Profile Card ─── */
.profile-card{
    background:linear-gradient(135deg,rgba(220,20,60,0.1),rgba(184,134,11,0.06));
    border:1px solid #B8860B;border-radius:14px;
    padding:28px 32px;margin:20px 0;
}
.profile-card h3{color:#FFD700!important;margin:0 0 4px;font-size:1.25rem}
.profile-card .subtitle{color:#DC143C!important;font-weight:600;margin:0 0 6px;font-size:0.9rem}
.profile-card .edu{color:#DAA520!important;font-size:0.82rem;margin:0 0 10px;line-height:1.5}
.profile-card a{
    color:#FFD700!important;text-decoration:none;font-weight:600;
    transition:color .2s;
}
.profile-card a:hover{color:#DC143C!important;text-decoration:underline}

/* ─── Footer ─── */
.custom-footer{
    text-align:center;padding:30px 20px 20px;
    margin-top:50px;
    border-top:2px solid rgba(184,134,11,0.4);
    background:linear-gradient(180deg,rgba(26,10,14,0.0),rgba(26,10,14,0.4));
}
.custom-footer p{margin:0;padding:2px 0}
.custom-footer .footer-title{
    font-size:0.92rem;color:#FFD700!important;font-weight:600;margin-bottom:6px;
}
.custom-footer .footer-tech{
    font-size:0.8rem;color:#DAA520!important;margin-bottom:8px;
}
.footer-links a{
    color:#DC143C!important;text-decoration:none;font-weight:600;
    transition:color .2s;
}
.footer-links a:hover{color:#FFD700!important;text-decoration:underline}
.custom-footer .footer-copy{
    font-size:0.72rem;color:#B8860B!important;margin-top:8px;
}
</style>
""",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════
st.markdown(
    '<h1 class="main-header">📊 AI Business Report Generator</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Upload your data · Get instant analysis · AI writes your report</p>',
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════
# SIDEBAR — Compact Config
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Report Settings")
    report_title = st.text_input("Report Title", "Monthly Business Performance Report")
    report_period = st.text_input("Report Period", "January 2025")
    tone = st.selectbox("Narrative Tone", ["executive", "manager", "analyst"])
    sensitivity = st.select_slider(
        "Anomaly Sensitivity", options=["low", "medium", "high"], value="medium"
    )

    st.divider()
    st.markdown("### 🚀 Quick Start")
    use_sample = st.button("📊 Load Sample Sales Data", use_container_width=True)

    st.divider()
    st.markdown("### 📋 Pipeline Status")
    status_container = st.container()


# ═══════════════════════════════════════════════════════════
# MAIN — Dataset Type + File Upload (above tabs)
# ═══════════════════════════════════════════════════════════
col_type, col_upload = st.columns([1, 2])

with col_type:
    st.markdown("##### 📂 Select Dataset Type")
    domain_options = get_domain_options()
    selected_domain_label = st.selectbox(
        "Dataset type",
        list(domain_options.keys()),
        index=0,
        help="Selecting the correct type improves analysis accuracy.",
        label_visibility="collapsed",
    )
    selected_domain_id = domain_options[selected_domain_label]

    if selected_domain_id != "auto":
        cfg = get_domain_config(selected_domain_id)
        st.caption(f"_{cfg.description}_")
        with st.expander("📋 Domain KPIs"):
            for kpi in cfg.kpi_definitions:
                st.markdown(f"- {kpi.icon} **{kpi.name}**: _{kpi.description}_")
    else:
        st.caption("_System will auto-detect the domain_")

with col_upload:
    st.markdown("##### 📤 Upload Your Data")
    uploaded_file = st.file_uploader(
        "Drop CSV or Excel",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed",
    )

# Supported-domains card strip
st.markdown(
    """
<div class="domain-grid">
    <div class="domain-card"><span class="domain-icon">💰</span><span class="domain-name">Sales &amp; Revenue</span></div>
    <div class="domain-card"><span class="domain-icon">👥</span><span class="domain-name">HR &amp; Workforce</span></div>
    <div class="domain-card"><span class="domain-icon">🏥</span><span class="domain-name">Healthcare</span></div>
    <div class="domain-card"><span class="domain-icon">🏦</span><span class="domain-name">Financial</span></div>
    <div class="domain-card"><span class="domain-icon">🛒</span><span class="domain-name">E-Commerce</span></div>
    <div class="domain-card"><span class="domain-icon">🏭</span><span class="domain-name">Operations</span></div>
    <div class="domain-card"><span class="domain-icon">📣</span><span class="domain-name">Marketing</span></div>
</div>
<p class="format-note">📁 Supported formats: <strong>CSV</strong> · <strong>XLSX</strong> · <strong>XLS</strong>&ensp;|&ensp;Auto-detection available for all domains</p>
""",
    unsafe_allow_html=True,
)

st.markdown("---")


# ═══════════════════════════════════════════════════════════
# DATA SOURCE RESOLUTION
# ═══════════════════════════════════════════════════════════
data_source = None
if uploaded_file is not None:
    data_source = "upload"
elif use_sample:
    data_source = "sample"
    st.session_state["use_sample"] = True
if data_source is None and st.session_state.get("use_sample"):
    data_source = "sample"


# ═══════════════════════════════════════════════════════════
# PIPELINE + TABBED DISPLAY
# ═══════════════════════════════════════════════════════════
if data_source:

    # ── 1. LOAD DATA ────────────────────────────────────
    loader = DataLoader()
    try:
        if data_source == "upload":
            df = loader.load(uploaded_file=uploaded_file)
        else:
            df = loader.load(file_path="data/sample_sales.csv")
            st.toast("📊 Sample data loaded!", icon="✅")
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.stop()
    with status_container:
        st.success("✅ Data Loaded")

    # ── 2. PROFILE ──────────────────────────────────────
    profiler = DataProfiler()
    profile = profiler.profile(df)
    with status_container:
        st.success("✅ Data Profiled")

    # ── 3. KPIs ─────────────────────────────────────────
    smart_kpi = SmartKPICalculator(domain_id=selected_domain_id)
    kpi_results = smart_kpi.calculate(df)
    kpi_data = kpi_results["kpis"]
    kpi_defs = kpi_results["kpi_definitions"]
    with status_container:
        st.success("✅ KPIs Calculated")

    # ── 4. DESCRIPTIVE ANALYSIS ─────────────────────────
    desc_analyzer = DescriptiveAnalyzer(
        domain_id=selected_domain_id,
        column_mapping=kpi_results.get("column_mapping", {}),
    )
    desc_results = desc_analyzer.analyze(df)
    with status_container:
        st.success("✅ Analysis Complete")

    # ── 5. TRENDS ───────────────────────────────────────
    trend_detector = TrendDetector()
    trend_results = trend_detector.analyze(df)
    with status_container:
        st.success("✅ Trends Analyzed")

    # ── 6. ANOMALIES ────────────────────────────────────
    anomaly_detector = AnomalyDetector()
    anomaly_results = anomaly_detector.detect(df, sensitivity=sensitivity)
    with status_container:
        st.success("✅ Anomalies Detected")

    # ── 7. CHARTS ───────────────────────────────────────
    recommender = ChartRecommender(
        domain_id=selected_domain_id,
        column_mapping=kpi_results.get("column_mapping", {}),
    )
    chart_specs = recommender.recommend(
        df,
        trend_results=trend_results,
        anomaly_results=anomaly_results,
        max_charts=8,
    )
    builder = ChartBuilder()
    chart_figures = builder.build_all(
        df,
        chart_specs,
        trend_results=trend_results,
        anomaly_results=anomaly_results,
    )
    for cd in chart_figures:
        cd["figure"] = style_plotly_chart(cd["figure"])

    with status_container:
        st.success("✅ Charts Generated")
        st.success("✅ Ready for AI Report")

    # ═══════════════════════════════════════════════════
    # TABBED DASHBOARD
    # ═══════════════════════════════════════════════════
    (
        tab_overview,
        tab_kpis,
        tab_analysis,
        tab_trends,
        tab_viz,
        tab_report,
        tab_about,
    ) = st.tabs(
        [
            "📊 Data Overview",
            "🎯 Key Metrics",
            "📈 Analysis",
            "📉 Trends & Anomalies",
            "🖼️ Visualizations",
            "📝 AI Report",
            "ℹ️ About System",
        ]
    )

    # ──────────────────────────────────────────────────
    # TAB 1 — DATA OVERVIEW
    # ──────────────────────────────────────────────────
    with tab_overview:
        overview = profile["overview"]
        quality = profile["quality"]

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("📋 Rows", f"{overview['total_rows']:,}")
        c2.metric("📊 Columns", overview["total_columns"])
        c3.metric("🔢 Numeric", overview["numeric_columns"])
        c4.metric("📝 Categorical", overview["categorical_columns"])
        c5.metric("✅ Quality", f"{quality['completeness_score']}%")

        if profile.get("date_info"):
            di = profile["date_info"]
            st.info(
                f"📅 **Date Range:** {di['start_date']} → {di['end_date']}  ({di['total_days']} days)"
            )

        with st.expander("👀 Preview Raw Data"):
            st.dataframe(df.head(20), use_container_width=True, height=300)

        with st.expander("📋 Column Details"):
            col_data = []
            for cn, ci in profile["columns"].items():
                col_data.append(
                    {
                        "Column": cn,
                        "Type": ci["dtype"],
                        "Non-Null": ci["non_null_count"],
                        "Null %": f"{ci['null_percentage']}%",
                        "Unique": ci["unique_values"],
                    }
                )
            st.dataframe(
                pd.DataFrame(col_data), use_container_width=True, hide_index=True
            )

    # ──────────────────────────────────────────────────
    # TAB 2 — KEY METRICS (KPIs)
    # ──────────────────────────────────────────────────
    with tab_kpis:
        dc1, dc2 = st.columns([1, 2])
        with dc1:
            st.success(f"{kpi_results['domain_icon']} **{kpi_results['domain_name']}**")
            if selected_domain_id == "auto":
                st.caption("💡 _Auto-detected. Select manually for better accuracy._")
        with dc2:
            with st.expander("🔗 Column Mapping"):
                if kpi_results.get("column_mapping"):
                    st.table(
                        pd.DataFrame(
                            [
                                {
                                    "Role": r.replace("_", " ").title(),
                                    "Column": f"`{c}`",
                                }
                                for r, c in kpi_results["column_mapping"].items()
                            ]
                        )
                    )

        if kpi_defs:
            for i in range(0, len(kpi_defs), 4):
                cols = st.columns(4)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(kpi_defs):
                        kd = kpi_defs[idx]
                        val = kpi_data[kd["key"]]
                        col.metric(
                            f"{kd['icon']} {kd['name']}",
                            kd["format"].format(val),
                        )
        else:
            st.warning("⚠️ No KPIs calculated. Select the correct dataset type.")

        if kpi_results.get("category_breakdown"):
            st.markdown("### 📊 Breakdown by Category")
            cat_tabs = st.tabs(list(kpi_results["category_breakdown"].keys()))
            for cat_tab, (cat, cdata) in zip(
                cat_tabs, kpi_results["category_breakdown"].items()
            ):
                with cat_tab:
                    if cdata.get("insight"):
                        st.info(f"💡 {cdata['insight']}")
                    st.dataframe(
                        pd.DataFrame(cdata["data"]),
                        use_container_width=True,
                        hide_index=True,
                    )

    # ──────────────────────────────────────────────────
    # TAB 3 — STATISTICAL ANALYSIS
    # ──────────────────────────────────────────────────
    with tab_analysis:
        sub1, sub2, sub3, sub4, sub5 = st.tabs(
            [
                "📊 Summary Stats",
                "📋 Domain Analyses",
                "🔄 Cross-Tabs",
                "🏆 Top / Bottom",
                "🔗 Correlations",
            ]
        )

        with sub1:
            stats = desc_results.get("summary_stats", {})
            if stats:
                rows = [
                    {
                        "Metric": cn,
                        "Role": cs.get("role", "-"),
                        "Mean": f"{cs['mean']:,.2f}",
                        "Median": f"{cs['median']:,.2f}",
                        "Std": f"{cs['std']:,.2f}",
                        "Min": f"{cs['min']:,.2f}",
                        "Max": f"{cs['max']:,.2f}",
                    }
                    for cn, cs in stats.items()
                ]
                st.dataframe(
                    pd.DataFrame(rows), use_container_width=True, hide_index=True
                )
            else:
                st.info("No summary statistics available.")

        with sub2:
            gbs = desc_results.get("group_by_analyses", [])
            if gbs:
                st.caption(
                    f"📊 Analyses for **{desc_results.get('domain_name', '')}**"
                )
                for gb in gbs:
                    st.subheader(f"📋 {gb['title']}")
                    st.caption(
                        f"_{gb.get('description', '')}_ | **{gb['aggregation'].upper()}** of {gb['metric_role']}"
                    )
                    if gb.get("insight"):
                        st.info(f"💡 {gb['insight']}")
                    gb_df = pd.DataFrame(gb["data"])
                    if "percentage" in gb_df.columns:
                        gb_df.columns = ["Name", "Value", "% Share"]
                    else:
                        gb_df.columns = ["Name", "Value"]
                    st.dataframe(
                        gb_df, use_container_width=True, hide_index=True
                    )
                    st.divider()

                derived = desc_results.get("derived_metrics", {})
                if derived:
                    st.markdown("### 📈 Additional Insights")
                    for key, data in derived.items():
                        st.markdown(f"**{data.get('title', key)}**")
                        if data.get("insight"):
                            st.info(f"💡 {data['insight']}")
                        if data.get("data"):
                            if isinstance(data["data"], dict):
                                st.dataframe(
                                    pd.DataFrame(
                                        list(data["data"].items()),
                                        columns=["Category", "Count"],
                                    ),
                                    use_container_width=True,
                                    hide_index=True,
                                )
                            elif isinstance(data["data"], list):
                                st.dataframe(
                                    pd.DataFrame(data["data"]),
                                    use_container_width=True,
                                    hide_index=True,
                                )
                        st.divider()
            else:
                st.info("No domain analyses available.")

        with sub3:
            cts = desc_results.get("cross_tabs", [])
            if cts:
                for ct in cts:
                    st.subheader(f"🔄 {ct['title']}")
                    st.caption(
                        f"_{ct.get('description', '')}_ | {ct['row_column']} × {ct['col_column']} ({ct['aggregation']})"
                    )
                    if ct.get("insight"):
                        st.info(f"💡 {ct['insight']}")
                    if "table_df" in ct:
                        st.dataframe(ct["table_df"], use_container_width=True)
                    st.divider()
            else:
                st.info("No cross-tabulations available.")

        with sub4:
            tb = desc_results.get("top_bottom", {})
            if tb:
                for key, data in tb.items():
                    st.subheader(f"📊 {data.get('title', key)}")
                    st.caption(
                        f"{data.get('aggregation', '').upper()} | Entity: {data.get('entity', '')}"
                    )
                    ct_col, cb_col = st.columns(2)
                    with ct_col:
                        st.markdown("**🏆 Top 3:**")
                        for item in data.get("top_3", []):
                            delta = (
                                f"{item['pct_of_total']}%"
                                if "pct_of_total" in item
                                else ""
                            )
                            st.metric(
                                item["name"], f"{item['total']:,.2f}", delta
                            )
                    with cb_col:
                        st.markdown("**📉 Bottom 3:**")
                        for item in data.get("bottom_3", []):
                            delta = (
                                f"{item['pct_of_total']}%"
                                if "pct_of_total" in item
                                else ""
                            )
                            st.metric(
                                item["name"], f"{item['total']:,.2f}", delta
                            )
                    if data.get("concentration"):
                        st.caption(
                            f"💡 Top 3 = **{data['concentration']}%** of total"
                        )
                    st.divider()
            else:
                st.info("No performer analysis available.")

        with sub5:
            corrs = desc_results.get("correlations", [])
            if corrs:
                st.caption("Domain-relevant correlations only")
                for c in corrs:
                    emoji = (
                        "🟢"
                        if c["strength"] in ["very strong", "strong"]
                        else "🟡" if c["strength"] == "moderate" else "🟠"
                    )
                    st.markdown(
                        f"{emoji} **{c['role_1']}** ↔ **{c['role_2']}**: r = **{c['correlation']}** ({c['strength']})"
                    )
                    st.caption(f"_{c['interpretation']}_")
                    st.divider()
            else:
                st.info("No significant correlations found.")

    # ──────────────────────────────────────────────────
    # TAB 4 — TRENDS & ANOMALIES
    # ──────────────────────────────────────────────────
    with tab_trends:
        trend_sec, anom_sec = st.tabs(["📈 Trend Analysis", "⚠️ Anomaly Detection"])

        with trend_sec:
            if trend_results.get("available"):
                overall = trend_results["overall_trend"]
                growth = trend_results.get("growth_analysis", {})
                comparison = trend_results.get("period_comparison", {})
                momentum = trend_results.get("momentum", {})

                tc1, tc2, tc3, tc4 = st.columns(4)
                tc1.metric(
                    f"{overall['emoji']} Direction",
                    overall["direction"].title(),
                    f"{overall['strength']} (R²={overall['r_squared']})",
                )
                if growth:
                    tc2.metric(
                        "📊 Latest Growth",
                        f"{growth['latest_growth_rate']:+.1f}%",
                        f"Avg: {growth['avg_growth_rate']:+.1f}%",
                    )
                if comparison.get("available"):
                    tc3.metric(
                        f"{comparison['emoji']} vs Previous",
                        f"{comparison['change_percentage']:+.1f}%",
                        f"{comparison['change_absolute']:+,.0f}",
                    )
                if momentum.get("available"):
                    tc4.metric(
                        f"{momentum['emoji']} Momentum",
                        momentum["status"].title(),
                    )

                tt1, tt2, tt3 = st.tabs(
                    ["📋 Summary", "📊 Growth", "🌡️ Seasonality"]
                )
                with tt1:
                    st.markdown(f"**Overall:** {overall['interpretation']}")
                    if comparison.get("available"):
                        st.markdown(
                            f"**Comparison:** {comparison['interpretation']}"
                        )
                    bw = trend_results.get("best_worst_periods", {})
                    if bw:
                        bw1, bw2 = st.columns(2)
                        bw1.success(
                            f"🏆 **Best:** {bw['best_period']['date']} — **{bw['best_period']['value']:,.0f}**"
                        )
                        bw2.error(
                            f"📉 **Worst:** {bw['worst_period']['date']} — **{bw['worst_period']['value']:,.0f}**"
                        )
                with tt2:
                    if growth:
                        st.markdown(
                            f"**{growth.get('interpretation', '')}**"
                        )
                        gc1, gc2, gc3 = st.columns(3)
                        gc1.metric(
                            "Best Growth",
                            f"{growth['max_growth']['rate']:+.1f}%",
                        )
                        gc2.metric(
                            "Worst Growth",
                            f"{growth['max_decline']['rate']:+.1f}%",
                        )
                        gc3.metric(
                            "Volatility", f"{growth['volatility']:.1f}%"
                        )
                        if growth.get("cagr") is not None:
                            st.info(f"📊 **CAGR:** {growth['cagr']:+.1f}%")
                with tt3:
                    season = trend_results.get("seasonality", {})
                    if season.get("detected"):
                        st.success(
                            f"✅ {season.get('interpretation', '')}"
                        )
                        if season.get("monthly_pattern"):
                            st.dataframe(
                                pd.DataFrame(
                                    list(season["monthly_pattern"].items()),
                                    columns=["Month", "Avg"],
                                ),
                                use_container_width=True,
                                hide_index=True,
                            )
                    else:
                        st.info("No seasonal pattern detected.")
            else:
                st.warning(
                    f"⚠️ {trend_results.get('reason', 'Not available')}"
                )
                trend_results = None

        with anom_sec:
            summary = anomaly_results["summary"]
            ac1, ac2, ac3, ac4 = st.columns(4)
            ac1.metric(
                f"{summary['severity_emoji']} Severity",
                summary["overall_severity"].title(),
            )
            ac2.metric("📊 Outliers", summary["column_anomalies_count"])
            ac3.metric("⚡ Spikes", summary["time_anomalies_count"])
            ac4.metric("⚠️ Alerts", summary["business_alerts_count"])

            alerts = anomaly_results.get("alerts", [])
            if alerts:
                st.markdown("### 🚨 Alerts")
                for a in alerts[:8]:
                    if a["severity"] == "critical":
                        st.error(
                            f"{a['emoji']} **{a['title']}** — {a['message']}"
                        )
                    elif a["severity"] == "high":
                        st.warning(
                            f"{a['emoji']} **{a['title']}** — {a['message']}"
                        )
                    elif a["severity"] == "medium":
                        st.info(
                            f"{a['emoji']} **{a['title']}** — {a['message']}"
                        )
                    else:
                        st.success(
                            f"{a['emoji']} **{a['title']}** — {a['message']}"
                        )
            else:
                st.success("✅ No significant anomalies. Data looks clean!")

    # ──────────────────────────────────────────────────
    # TAB 5 — VISUALIZATIONS
    # ──────────────────────────────────────────────────
    with tab_viz:
        if chart_figures:
            sections_viz = {}
            for cf in chart_figures:
                sec = cf["spec"].section
                sections_viz.setdefault(sec, []).append(cf)

            section_titles = {
                "trends": "📈 Trends",
                "comparison": "📊 Comparison",
                "composition": "🥧 Composition",
                "distribution": "📉 Distribution",
                "relationships": "🔗 Relationships",
                "anomalies": "⚠️ Anomalies",
                "general": "📊 General",
            }

            for sec_key, sec_charts in sections_viz.items():
                st.markdown(
                    f"#### {section_titles.get(sec_key, sec_key)}"
                )
                chart_cols = st.columns(2)
                for i, cd in enumerate(sec_charts):
                    with chart_cols[i % 2]:
                        st.plotly_chart(
                            cd["figure"], use_container_width=True
                        )
                        st.caption(f"💡 _{cd['spec'].reason}_")
        else:
            st.info("No charts generated.")

    # ──────────────────────────────────────────────────
    # TAB 6 — AI REPORT
    # ──────────────────────────────────────────────────
    with tab_report:
        if not llm.is_available():
            st.error(
                "⚠️ **OpenAI API key not configured.** Add it to your `.env` file and restart."
            )
        else:
            gc1, gc2 = st.columns(2)
            with gc1:
                gen_mode = st.radio(
                    "Generation Mode",
                    ["📝 Section by Section", "⚡ Full Report"],
                )
            with gc2:
                st.caption(f"📊 Tone: **{tone.title()}**")
                st.caption(f"📅 Period: **{report_period}**")
                st.caption(
                    f"🏢 Domain: **{kpi_results.get('domain_name', 'Auto')}**"
                )

            generate_clicked = st.button(
                "🚀 Generate AI Report",
                type="primary",
                use_container_width=True,
            )

            if generate_clicked:
                analysis_bundle = {
                    "profile": profile,
                    "kpis": kpi_results,
                    "descriptive": desc_results,
                    "trends": (
                        trend_results
                        if trend_results and trend_results.get("available")
                        else {}
                    ),
                    "anomalies": anomaly_results,
                    "report_title": report_title,
                    "report_period": report_period,
                    "tone": tone,
                    "domain": selected_domain_id,
                }

                narrator = ReportNarrator(tone=tone)

                if "Section" in gen_mode:
                    st.markdown("---")
                    st.markdown("### 📄 Generated Report")

                    progress = st.progress(0)
                    status_text = st.empty()

                    section_names = [
                        ("executive_summary", "📋 Executive Summary"),
                        ("kpi_analysis", "📊 KPI Analysis"),
                        ("trend_analysis", "📈 Trend Analysis"),
                        ("anomalies_alerts", "⚠️ Anomalies & Alerts"),
                        ("recommendations", "🎯 Recommendations"),
                    ]

                    report_sections = {}
                    containers = {k: st.container() for k, _ in section_names}
                    prepared = narrator._prepare_data_texts(analysis_bundle)

                    for i, (key, display) in enumerate(section_names):
                        progress.progress(i / len(section_names))
                        status_text.markdown(f"✍️ *Generating {display}...*")
                        try:
                            if key == "executive_summary":
                                content = narrator._generate_executive_summary(
                                    prepared, analysis_bundle
                                )
                            elif key == "kpi_analysis":
                                content = narrator._generate_kpi_section(
                                    prepared, analysis_bundle
                                )
                            elif key == "trend_analysis":
                                content = narrator._generate_trend_section(
                                    prepared, analysis_bundle
                                )
                            elif key == "anomalies_alerts":
                                content = narrator._generate_anomaly_section(
                                    prepared, analysis_bundle
                                )
                            elif key == "recommendations":
                                content = narrator._generate_recommendations(
                                    prepared, analysis_bundle
                                )
                            else:
                                content = ""

                            report_sections[key] = content
                            with containers[key]:
                                st.markdown(f"## {display}")
                                st.markdown(content)
                                st.markdown("---")
                        except Exception as e:
                            report_sections[key] = f"*Error: {e}*"
                            with containers[key]:
                                st.error(f"❌ {display}: {e}")

                    progress.progress(1.0)
                    status_text.markdown("✅ *Report complete!*")

                else:
                    st.markdown("---")
                    with st.spinner("🚀 Generating full report…"):
                        try:
                            full = narrator.generate_full_report(
                                analysis_bundle, title=report_title
                            )
                            report_sections = {"full_report": full}
                            st.markdown("### 📄 Generated Report")
                            st.markdown(full)
                        except Exception as e:
                            st.error(f"❌ {e}")
                            report_sections = {}

                # ── Quality Score + Download ──
                if report_sections:
                    st.markdown("---")
                    st.markdown("### 📊 Report Quality")

                    scorer = ReportQualityScorer()
                    qual = scorer.score_report(report_sections, analysis_bundle)
                    api_stats = llm.get_session_stats()

                    qc1, qc2, qc3 = st.columns(3)
                    qc1.metric(
                        f"{qual['emoji']} Quality",
                        f"{qual['overall_score']}/100",
                        qual["rating"],
                    )
                    qc2.metric(
                        "💰 Cost",
                        api_stats["total_cost_formatted"],
                        f"{api_stats['total_calls']} calls",
                    )
                    qc3.metric(
                        "📝 Tokens",
                        f"{api_stats['total_input_tokens'] + api_stats['total_output_tokens']:,}",
                    )

                    with st.expander("📋 Section Scores"):
                        for sn, sc in qual["section_scores"].items():
                            scols = st.columns(5)
                            scols[0].markdown(
                                f"**{sn.replace('_', ' ').title()}**"
                            )
                            scols[1].caption(
                                f"📊 Data: {sc['data_grounding']}/25"
                            )
                            scols[2].caption(
                                f"📋 Structure: {sc['structure']}/25"
                            )
                            scols[3].caption(
                                f"🎯 Action: {sc['actionability']}/25"
                            )
                            scols[4].caption(
                                f"📏 Length: {sc['conciseness']}/25"
                            )

                    if qual.get("suggestions"):
                        with st.expander("💡 Suggestions"):
                            for s in qual["suggestions"]:
                                st.markdown(f"- {s}")

                    # ── DOWNLOADS ──
                    st.markdown("---")
                    st.markdown("### 📥 Download Report")

                    html_gen = HTMLReportGenerator()
                    html_report = html_gen.generate(
                        title=report_title,
                        period=report_period,
                        domain_name=kpi_results.get("domain_name", "General"),
                        domain_icon=kpi_results.get("domain_icon", "📊"),
                        kpis=kpi_results,
                        narrative_sections=report_sections,
                        chart_figures=chart_figures if chart_figures else [],
                        quality_score=qual,
                        llm_stats=api_stats,
                    )

                    md = f"# {report_title}\n"
                    md += f"**Period:** {report_period} | "
                    md += f"**Generated:** {datetime.now().strftime('%B %d, %Y')}\n\n---\n\n"
                    for k, v in report_sections.items():
                        if k != "full_report":
                            md += f"## {k.replace('_', ' ').title()}\n\n"
                        md += v + "\n\n---\n\n"

                    dl1, dl2, dl3 = st.columns(3)
                    with dl1:
                        st.download_button(
                            "📄 Download HTML Report",
                            html_report,
                            f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                            "text/html",
                            use_container_width=True,
                        )
                    with dl2:
                        st.download_button(
                            "📝 Download Markdown",
                            md,
                            f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                            "text/markdown",
                            use_container_width=True,
                        )
                    with dl3:
                        plain = re.sub(r"\*\*(.*?)\*\*", r"\1", md)
                        plain = re.sub(r"#{1,4}\s", "", plain)
                        st.download_button(
                            "📃 Download Plain Text",
                            plain,
                            f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                            "text/plain",
                            use_container_width=True,
                        )

                    with st.expander("👀 Preview HTML Report"):
                        st.components.v1.html(
                            html_report, height=800, scrolling=True
                        )

    # ──────────────────────────────────────────────────
    # TAB 7 — ABOUT SYSTEM
    # ──────────────────────────────────────────────────
    with tab_about:

        # ── Problem Statement ──
        st.markdown("""
        <div class="problem-card">
            <h3>🎯 Problem Statement</h3>
            <p>
                Business teams spend
                <strong class="highlight-crimson">5–10 hours per week</strong>
                manually creating reports from raw data — profiling datasets, calculating KPIs,
                identifying trends, detecting anomalies, building charts, and writing narratives.
                This system uses <strong class="highlight-gold">AI-powered automation</strong>
                to transform any uploaded dataset into a complete, executive-ready business report
                in under <strong class="highlight-gold">2 minutes</strong>, reducing manual effort by
                <strong class="highlight-crimson">90%+</strong> and ensuring analytical consistency
                across all reporting.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Architecture ──
        st.markdown("### 🏗️ System Architecture")

        arch_cols = st.columns([2, 1, 2, 1, 2, 1, 2, 1, 2])

        arch_steps = [
            ("📤", "Data Upload", "CSV / Excel\nIngestion"),
            ("➡️", "", ""),
            ("🔍", "Profiler", "Auto-detect\nSchema & Quality"),
            ("➡️", "", ""),
            ("📊", "Analyzer", "KPIs · Trends\nAnomalies"),
            ("➡️", "", ""),
            ("🖼️", "Visualizer", "Smart Charts\nPlotly Engine"),
            ("➡️", "", ""),
            ("🤖", "GPT-4", "AI Narrative\nReport Writer"),
        ]

        for i, (icon, title, desc) in enumerate(arch_steps):
            with arch_cols[i]:
                if title:
                    st.markdown(f"""
                    <div class="arch-step">
                        <div class="arch-icon">{icon}</div>
                        <div class="arch-title">{title}</div>
                        <div class="arch-desc">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="arch-arrow">{icon}</div>
                    """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Key Capabilities ──
        st.markdown("### 🏆 Key Capabilities")

        cap_data = [
            ("🧠", "7 Domains", "Auto-detected", "Sales · HR · Healthcare · Finance · E-Commerce · Ops · Marketing"),
            ("📊", "Smart KPIs", "Domain-Aware", "Auto-calculates relevant metrics per dataset type"),
            ("📈", "Trend Engine", "Multi-Signal", "Direction · Growth · Seasonality · Momentum analysis"),
            ("⚠️", "Anomaly AI", "3 Sensitivity", "Statistical outliers · Time spikes · Business alerts"),
            ("🖼️", "Auto Charts", "Up to 8", "AI-recommended Plotly visualizations per dataset"),
            ("📝", "GPT-4 Writer", "5 Sections", "Executive Summary · KPIs · Trends · Anomalies · Recommendations"),
        ]

        for row_start in range(0, len(cap_data), 3):
            cap_cols = st.columns(3)
            for j, col in enumerate(cap_cols):
                idx = row_start + j
                if idx < len(cap_data):
                    icon, title, badge, desc = cap_data[idx]
                    with col:
                        st.markdown(f"""
                        <div class="feature-card">
                            <div class="feature-icon">{icon}</div>
                            <div class="feature-value">{title}</div>
                            <div class="feature-label">{badge}</div>
                            <div class="feature-sub">{desc}</div>
                        </div>
                        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Pipeline Features ──
        st.markdown("### ⚡ Full Pipeline Features")

        pipe_col1, pipe_col2 = st.columns(2)
        with pipe_col1:
            st.markdown("""
            - 📤 **Data Ingestion** — CSV & Excel auto-parsing with type inference
            - 🔍 **Data Profiling** — Schema, quality scores, date range detection
            - 🎯 **Smart KPIs** — Domain-specific metric calculation with formatting
            - 📋 **Descriptive Stats** — Summary, group-by, cross-tabs, correlations
            - 🏆 **Top / Bottom** — Performer analysis with concentration metrics
            """)
        with pipe_col2:
            st.markdown("""
            - 📈 **Trend Detection** — Direction, growth rates, CAGR, momentum
            - 🌡️ **Seasonality** — Monthly pattern detection and analysis
            - ⚠️ **Anomaly Detection** — IQR outliers, Z-score spikes, business alerts
            - 🖼️ **Chart Recommender** — AI picks best chart types per data shape
            - 📝 **AI Narrator** — GPT-4 generates publication-ready report sections
            """)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Output Formats ──
        st.markdown("### 📥 Output Formats")

        fmt_cols = st.columns(4)
        fmt_data = [
            ("📄", "HTML Report", "Styled, self-contained, print-ready"),
            ("📝", "Markdown", "GitHub-compatible, structured text"),
            ("📃", "Plain Text", "Universal, email-friendly format"),
            ("📊", "Interactive", "Live Plotly charts in dashboard"),
        ]
        for col, (icon, title, desc) in zip(fmt_cols, fmt_data):
            with col:
                st.markdown(f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-value" style="font-size:1.1rem">{title}</div>
                    <div class="feature-sub">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Tech Stack ──
        st.markdown("### 🛠️ Technology Stack")
        st.markdown("""
        <div style="margin:12px 0 20px;text-align:center;">
            <span class="tech-pill">Python</span>
            <span class="tech-pill">Streamlit</span>
            <span class="tech-pill">OpenAI GPT-4</span>
            <span class="tech-pill">Plotly</span>
            <span class="tech-pill">Pandas</span>
            <span class="tech-pill">NumPy</span>
            <span class="tech-pill">SciPy</span>
            <span class="tech-pill">scikit-learn</span>
            <span class="tech-pill">LangChain</span>
            <span class="tech-pill">Jinja2</span>
            <span class="tech-pill">OpenPyXL</span>
            <span class="tech-pill">python-dotenv</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Quality Assurance ──
        st.markdown("### ✅ Quality Assurance")

        qa_cols = st.columns(3)
        qa_data = [
            ("🎯", "Report Scoring", "Automated 4-dimension quality scoring: Data Grounding · Structure · Actionability · Conciseness"),
            ("💰", "Cost Tracking", "Real-time token usage and API cost monitoring per session with formatted breakdowns"),
            ("🔒", "Data Privacy", "All processing runs locally — your data never leaves the session. Only AI narrative calls use OpenAI API"),
        ]
        for col, (icon, title, desc) in zip(qa_cols, qa_data):
            with col:
                st.markdown(f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-value" style="font-size:1rem">{title}</div>
                    <div class="feature-sub">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── About the Builder ──
        st.markdown("### 👨‍💻 Built By")
        st.markdown("""
        <div class="profile-card">
            <div style="display:flex;align-items:center;gap:1.5rem;">
                <div style="
                    width:75px;height:75px;border-radius:50%;
                    background:linear-gradient(135deg,#DC143C,#FFD700);
                    display:flex;align-items:center;justify-content:center;
                    font-size:2.2rem;flex-shrink:0;
                ">👨‍💻</div>
                <div>
                    <h3>Anush Kundu</h3>
                    <p class="subtitle">Data Scientist</p>
                    <p class="edu">
                        MSc Data Science, Kingston University London&ensp;|&ensp;
                        2.5 years experience&ensp;|&ensp;
                        Retail &amp; Commercial Analytics
                    </p>
                    <div style="margin-top:10px;">
                        <a href="https://linkedin.com/in/anushkundu" target="_blank">🔗 LinkedIn</a>
                        <span style="margin:0 10px;color:#B8860B;">|</span>
                        <a href="https://github.com/anushkundu" target="_blank">🐙 GitHub</a>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


    # ═══════════════════════════════════════════════════
    # FOOTER (always visible when data is loaded)
    # ═══════════════════════════════════════════════════
    st.markdown("""
    <div class="custom-footer">
        <p class="footer-title">
            📊 AI Business Report Generator — Intelligent Analytics Dashboard v1.0
        </p>
        <p class="footer-tech">
            Built with Python · Streamlit · OpenAI GPT-4 · Plotly · Pandas · scikit-learn
        </p>
        <div class="footer-links" style="margin-top:8px;">
            <a href="https://github.com/anushkundu" target="_blank">🐙 GitHub</a> ·
            <a href="https://linkedin.com/in/anushkundu" target="_blank">🔗 LinkedIn</a>
        </div>
        <p class="footer-copy">
            © 2025 Anush Kundu. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# LANDING PAGE (no data loaded)
# ═══════════════════════════════════════════════════════════
else:
    st.markdown("---")
    lc, rc = st.columns(2)
    with lc:
        st.markdown(
            """
        ### 🚀 How It Works
        1. **Select** your dataset type above
        2. **Upload** any business data (CSV / Excel)
        3. **AI analyzes** → KPIs, trends, anomalies, charts
        4. **GPT-4 writes** an executive-ready report
        5. **Download** as HTML, Markdown or Plain Text
        """
        )
    with rc:
        st.markdown(
            """
        ### ✨ Key Features
        - 🎯 Smart KPI detection per domain
        - 📈 Automated trend & seasonality analysis
        - ⚠️ Anomaly detection with severity alerts
        - 📊 AI-recommended visualizations
        - 📝 GPT-4 narrative report generation
        - 📥 One-click HTML / MD / TXT download
        """
        )

    st.markdown(
        """
    <div style='text-align:center;color:#B8860B;padding:30px;'>
        <p style='font-size:1.15rem;'>👆 Select a dataset type and upload a file — or click
        <strong style='color:#FFD700;'>Load Sample Sales Data</strong> in the sidebar to get started.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Footer on landing page too
    st.markdown("""
    <div class="custom-footer">
        <p class="footer-title">
            📊 AI Business Report Generator — Intelligent Analytics Dashboard v1.0
        </p>
        <p class="footer-tech">
            Built with Python · Streamlit · OpenAI GPT-4 · Plotly · Pandas · scikit-learn
        </p>
        <div class="footer-links" style="margin-top:8px;">
            <a href="https://github.com/anushkundu" target="_blank">🐙 GitHub</a> ·
            <a href="https://linkedin.com/in/anushkundu" target="_blank">🔗 LinkedIn</a>
        </div>
        <p class="footer-copy">
            © 2025 Anush Kundu. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)
