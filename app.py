# app.py

"""
AI BUSINESS REPORT GENERATOR — PROFESSIONAL DASHBOARD
─────────────────────────────────────────────────────
Crimson Professional Theme · Tabbed Interface · Production Ready
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
# HELPER — Style Plotly Charts (crimson professional theme)
# ═══════════════════════════════════════════════════════════
def style_plotly_chart(fig):
    """Apply crimson professional theme to Plotly charts."""
    fig.update_layout(
        title=dict(
            y=0.97, x=0.5,
            xanchor="center", yanchor="top",
            font=dict(size=14, color="#5c0a1a", family="Inter, Arial"),
        ),
        legend=dict(
            orientation="h",
            yanchor="top", y=-0.22,
            xanchor="center", x=0.5,
            font=dict(size=10, color="#4a5568"),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(226,232,240,0.8)",
            borderwidth=1,
        ),
        hoverlabel=dict(
            bgcolor="#ffffff",
            font_size=13,
            font_family="Inter, Arial",
            font_color="#5c0a1a",
            bordercolor="#dc143c",
        ),
        paper_bgcolor="rgba(255,255,255,0.95)",
        plot_bgcolor="rgba(252,248,248,0.9)",
        font=dict(color="#4a5568", family="Inter, Arial", size=14),
        margin=dict(t=60, b=100, l=55, r=25),
        colorway=[
            "#dc143c", "#10b981", "#f59e0b", "#8b1a2b",
            "#8b5cf6", "#06b6d4", "#ec4899", "#f97316",
            "#14b8a6", "#6366f1",
        ],
    )
    try:
        fig.update_xaxes(
            gridcolor="rgba(226,232,240,0.6)",
            color="#64748b",
            linecolor="rgba(226,232,240,0.8)",
            tickfont=dict(color="#64748b", size=10),
        )
        fig.update_yaxes(
            gridcolor="rgba(226,232,240,0.6)",
            color="#64748b",
            linecolor="rgba(226,232,240,0.8)",
            tickfont=dict(color="#64748b", size=10),
        )
    except Exception:
        pass
    return fig


# ═══════════════════════════════════════════════════════════
# CRIMSON PROFESSIONAL — FULL THEME CSS
# ═══════════════════════════════════════════════════════════
st.markdown(
    """
<style>
/* ══════ Google Font ══════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ─── App Background ─── */
.stApp {
    background: linear-gradient(160deg, #fdf2f4 0%, #f8e8eb 50%, #fdf2f4 100%);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
[data-testid="stHeader"]{
    background: rgba(255,255,255,0.95);
    border-bottom: 1px solid #f5c6ce;
    backdrop-filter: blur(10px);
}

/* ─── Sidebar ─── */
[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #4c0519 0%, #3b0412 100%);
    border-right: none;
    box-shadow: 4px 0 20px rgba(76,5,25,0.2);
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] p{
    color: #fecdd3 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3{
    color: #ffffff !important;
}
[data-testid="stSidebar"] hr{
    border-color: rgba(255,255,255,0.15) !important;
}
[data-testid="stSidebar"] .stAlert{
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: #fecdd3 !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] p{
    color: #fecdd3 !important;
}

/* ─── Hero Title Box (dark box — title only) ─── */
.hero-box{
    background: linear-gradient(135deg, #4c0519 0%, #7f1d1d 30%, #991b1b 60%, #4c0519 100%);
    border-radius: 20px;
    padding: 52px 30px 48px;
    margin: 0 0 0;
    text-align: center;
    box-shadow: 0 8px 32px rgba(76,5,25,0.35),
                0 2px 8px rgba(76,5,25,0.15);
    position: relative;
    overflow: hidden;
}
.hero-box::before{
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(220,20,60,0.12) 0%, transparent 60%);
    animation: heroGlow 8s ease-in-out infinite;
}
@keyframes heroGlow{
    0%, 100%{ transform: translate(0, 0); }
    50%{ transform: translate(30px, -20px); }
}
.hero-title{
    font-size: 2.4rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.5px;
    position: relative;
    z-index: 1;
    text-shadow: 0 2px 12px rgba(0,0,0,0.35), 0 0 30px rgba(255,255,255,0.08);
}

/* ─── Hero Below-Box Area (subtitle + badge) ─── */
.hero-below{
    text-align: center;
    padding: 18px 20px 8px;
    margin: 0 0 24px;
}
.hero-subtitle{
    font-size: 1.18rem;
    color: #5c0a1a !important;
    margin: 0 0 12px;
    font-weight: 500;
    letter-spacing: 0.3px;
}
.hero-badge{
    display: inline-block;
    background: linear-gradient(135deg, #fff1f2 0%, #fef2f2 100%);
    border: 1.5px solid #f9a8b8;
    border-radius: 24px;
    padding: 7px 22px;
    color: #881337 !important;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.6px;
    box-shadow: 0 2px 8px rgba(220,20,60,0.1);
}

/* ─── Section Headers ─── */
h1{ color: #5c0a1a !important; font-weight: 800 !important; }
h2{ color: #5c0a1a !important; font-weight: 700 !important; }
h3{ color: #8b1a2b !important; font-weight: 600 !important; }
h4, h5{ color: #a83246 !important; font-weight: 600 !important; }

/* ─── Body Text ─── */
p, span, label, li,
.stMarkdown,
[data-testid="stText"]{
    color: #334155 !important;
}
.stCaption, [data-testid="stCaption"]{
    color: #64748b !important;
}

/* ─── Glass Card (reusable) ─── */
.glass-card{
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(245,198,206,0.6);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.04),
                0 1px 4px rgba(0,0,0,0.02);
    transition: all 0.3s ease;
}
.glass-card:hover{
    box-shadow: 0 8px 28px rgba(0,0,0,0.08),
                0 2px 8px rgba(0,0,0,0.04);
    transform: translateY(-2px);
}
.glass-card-static{
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(245,198,206,0.6);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.04);
}

/* ─── Info Strip ─── */
.info-strip{
    background: linear-gradient(135deg, #fff1f2 0%, #fef2f2 100%);
    border: 1px solid #fecdd3;
    border-left: 4px solid #dc143c;
    border-radius: 10px;
    padding: 14px 20px;
    margin: 8px 0;
}
.info-strip p{ color: #881337 !important; margin: 0; font-size: 0.9rem; }

/* ─── Tabs ─── */
.stTabs [data-baseweb="tab-list"]{
    gap: 4px;
    background: rgba(255,255,255,0.6);
    border-radius: 12px;
    padding: 5px;
    border: 1px solid #f5c6ce;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.stTabs [data-baseweb="tab"]{
    background: transparent;
    color: #64748b !important;
    border-radius: 8px;
    border: 1px solid transparent;
    padding: 10px 18px;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    transition: all 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover{
    background: rgba(220,20,60,0.06);
    color: #dc143c !important;
    border-color: rgba(220,20,60,0.2);
}
.stTabs [aria-selected="true"]{
    background: linear-gradient(135deg, #dc143c, #b91c3c) !important;
    color: #ffffff !important;
    border-color: transparent !important;
    font-weight: 700;
    box-shadow: 0 4px 12px rgba(220,20,60,0.3);
}
.stTabs [data-baseweb="tab-panel"]{ padding-top: 20px; }

/* ─── Metrics ─── */
[data-testid="stMetric"]{
    background: rgba(255,255,255,0.9);
    border: 1px solid #f5c6ce;
    border-radius: 14px;
    padding: 18px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    transition: all 0.3s ease;
}
[data-testid="stMetric"]:hover{
    box-shadow: 0 6px 20px rgba(0,0,0,0.07);
    transform: translateY(-2px);
}
[data-testid="stMetricValue"]{
    color: #5c0a1a !important;
    font-weight: 800 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stMetricLabel"]{
    color: #64748b !important;
    font-weight: 500 !important;
}
[data-testid="stMetricDelta"]{ font-weight: 600; }

/* ─── Form Inputs ─── */
.stSelectbox [data-baseweb="select"]>div,
.stTextInput>div>div>input,
.stNumberInput>div>div>input{
    background-color: #ffffff !important;
    color: #334155 !important;
    border: 1.5px solid #e8b4bc !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
}
.stSelectbox [data-baseweb="select"]>div:focus-within,
.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus{
    border-color: #dc143c !important;
    box-shadow: 0 0 0 3px rgba(220,20,60,0.12) !important;
}
.stSelectbox label, .stTextInput label, .stRadio label{
    color: #5c0a1a !important;
    font-weight: 600;
}
[data-baseweb="select"] span{ color: #334155 !important; }
[data-baseweb="popover"] ul,
[data-baseweb="menu"]{
    background-color: #ffffff !important;
    border: 1px solid #f5c6ce !important;
    border-radius: 10px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
}
[data-baseweb="menu"] li{ color: #334155 !important; }
[data-baseweb="menu"] li:hover{
    background: rgba(220,20,60,0.06) !important;
}

/* ─── Buttons ─── */
.stButton>button{
    background: linear-gradient(135deg, #dc143c, #b91c3c) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(220,20,60,0.25) !important;
}
.stButton>button:hover{
    background: linear-gradient(135deg, #b91c3c, #9f1239) !important;
    box-shadow: 0 6px 20px rgba(220,20,60,0.35) !important;
    transform: translateY(-1px) !important;
}
button[kind="primary"]{
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: #ffffff !important;
    box-shadow: 0 2px 8px rgba(16,185,129,0.3) !important;
}
button[kind="primary"]:hover{
    background: linear-gradient(135deg, #059669, #047857) !important;
    box-shadow: 0 6px 20px rgba(16,185,129,0.4) !important;
}

/* ─── Download Buttons ─── */
.stDownloadButton>button{
    background: linear-gradient(135deg, #5c0a1a, #8b1a2b) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(92,10,26,0.2) !important;
}
.stDownloadButton>button:hover{
    background: linear-gradient(135deg, #8b1a2b, #a83246) !important;
    box-shadow: 0 6px 20px rgba(92,10,26,0.3) !important;
    transform: translateY(-1px) !important;
}

/* ─── Expanders ─── */
[data-testid="stExpander"]{
    background: rgba(255,255,255,0.7);
    border: 1px solid #f5c6ce;
    border-radius: 12px;
    overflow: hidden;
}
[data-testid="stExpander"] summary span{
    color: #5c0a1a !important;
    font-weight: 600;
}

/* ─── File Uploader ─── */
[data-testid="stFileUploader"]{
    border: 2px dashed #e8b4bc !important;
    border-radius: 14px;
    transition: all 0.3s ease;
}
[data-testid="stFileUploader"]:hover{
    border-color: #dc143c !important;
}
[data-testid="stFileUploader"] label{
    color: #5c0a1a !important;
}
[data-testid="stFileUploader"] section{
    background: rgba(253,242,244,0.8) !important;
    border-radius: 14px;
    padding: 15px;
}
[data-testid="stFileUploader"] button{
    background: rgba(220,20,60,0.08) !important;
    color: #dc143c !important;
    border: 1px solid #f9a8b8 !important;
    border-radius: 8px !important;
}

/* ─── Progress Bar ─── */
.stProgress>div>div>div{
    background: linear-gradient(90deg, #dc143c, #10b981) !important;
    border-radius: 10px;
}

/* ─── Divider ─── */
hr{ border-color: rgba(245,198,206,0.6) !important; }

/* ─── Alerts ─── */
[data-testid="stAlert"]{ border-radius: 10px !important; }

/* ─── DataFrames ─── */
[data-testid="stDataFrame"]{
    border: 1px solid #f5c6ce;
    border-radius: 10px;
    overflow: hidden;
}

/* ─── Slider ─── */
[data-testid="stSlider"] label{ color: #5c0a1a !important; }

/* ─── Radio ─── */
.stRadio>div label span{ color: #334155 !important; }

/* ─── Scrollbar ─── */
::-webkit-scrollbar{ width: 8px; height: 8px; }
::-webkit-scrollbar-track{ background: #fdf2f4; }
::-webkit-scrollbar-thumb{
    background: #d4a0a9;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover{ background: #b97a86; }

/* ─── Domain Card Grid ─── */
.domain-grid{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    margin: 12px 0 18px;
}
.domain-card{
    background: rgba(255,255,255,0.8);
    border: 1px solid #f5c6ce;
    border-radius: 12px;
    padding: 12px 14px;
    text-align: center;
    min-width: 108px;
    flex: 1;
    transition: all 0.3s ease;
    cursor: default;
}
.domain-card:hover{
    border-color: #dc143c;
    background: rgba(220,20,60,0.04);
    transform: translateY(-3px);
    box-shadow: 0 6px 18px rgba(220,20,60,0.12);
}
.domain-icon{ font-size: 1.6rem; display: block; margin-bottom: 4px; }
.domain-name{
    color: #334155;
    font-weight: 600;
    font-size: 0.78rem;
}
.format-note{
    text-align: center;
    color: #64748b !important;
    font-size: 0.78rem;
    margin-top: 4px;
}

/* ─── About Tab — Problem Card ─── */
.problem-card{
    background: linear-gradient(135deg, #fff1f2, #fef2f2);
    border: 1px solid #fecdd3;
    border-left: 5px solid #dc143c;
    border-radius: 16px;
    padding: 28px 32px;
    margin: 10px 0 20px;
}
.problem-card h3{
    color: #5c0a1a !important;
    margin-bottom: 12px;
    font-size: 1.3rem;
}
.problem-card p{
    color: #334155 !important;
    line-height: 1.8;
    font-size: 0.95rem;
}
.highlight-blue{
    color: #dc143c !important;
    font-weight: 700;
}
.highlight-green{
    color: #059669 !important;
    font-weight: 700;
}

/* ─── Architecture Steps ─── */
.arch-step{
    background: rgba(255,255,255,0.9);
    border: 1px solid #f5c6ce;
    border-radius: 14px;
    padding: 18px 10px;
    text-align: center;
    min-height: 130px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.arch-step:hover{
    border-color: #dc143c;
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(220,20,60,0.12);
}
.arch-icon{ font-size: 2rem; margin-bottom: 6px; }
.arch-title{
    color: #5c0a1a;
    font-weight: 700;
    font-size: 0.9rem;
    margin-bottom: 4px;
}
.arch-desc{
    color: #64748b;
    font-size: 0.72rem;
    white-space: pre-line;
    line-height: 1.4;
}
.arch-arrow{
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    color: #dc143c;
    height: 130px;
}

/* ─── Feature Cards ─── */
.feature-card{
    background: rgba(255,255,255,0.9);
    border: 1px solid #f5c6ce;
    border-radius: 14px;
    padding: 24px 18px;
    text-align: center;
    margin-bottom: 12px;
    transition: all 0.3s ease;
    min-height: 160px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.feature-card:hover{
    border-color: #dc143c;
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(220,20,60,0.12);
}
.feature-icon{ font-size: 2.2rem; margin-bottom: 10px; }
.feature-value{
    color: #5c0a1a;
    font-size: 1.5rem;
    font-weight: 800;
    margin-bottom: 4px;
}
.feature-label{
    color: #334155;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 4px;
}
.feature-sub{
    color: #64748b;
    font-size: 0.72rem;
    line-height: 1.4;
}

/* ─── Tech Pills ─── */
.tech-pill{
    display: inline-block;
    background: linear-gradient(135deg, #fff1f2, #f0fdf4);
    border: 1px solid #fecdd3;
    border-radius: 20px;
    padding: 6px 16px;
    margin: 4px;
    color: #881337 !important;
    font-size: 0.82rem;
    font-weight: 600;
    transition: all 0.3s ease;
}
.tech-pill:hover{
    background: linear-gradient(135deg, #fee2e2, #d1fae5);
    border-color: #dc143c;
    transform: scale(1.05);
    box-shadow: 0 2px 8px rgba(220,20,60,0.15);
}

/* ─── Profile Card ─── */
.profile-card{
    background: rgba(255,255,255,0.9);
    border: 1px solid #f5c6ce;
    border-radius: 16px;
    padding: 28px 32px;
    margin: 20px 0;
    box-shadow: 0 4px 16px rgba(0,0,0,0.04);
}
.profile-card h3{
    color: #5c0a1a !important;
    margin: 0 0 4px;
    font-size: 1.25rem;
}
.profile-card .subtitle{
    color: #dc143c !important;
    font-weight: 600;
    margin: 0 0 6px;
    font-size: 0.9rem;
}
.profile-card .edu{
    color: #64748b !important;
    font-size: 0.82rem;
    margin: 0 0 10px;
    line-height: 1.5;
}
.profile-card a{
    color: #b91c3c !important;
    text-decoration: none;
    font-weight: 600;
    transition: color 0.2s;
}
.profile-card a:hover{
    color: #9f1239 !important;
    text-decoration: underline;
}

/* ─── Stat Box (landing page) ─── */
.stat-box{
    background: rgba(255,255,255,0.9);
    border: 1px solid #f5c6ce;
    border-radius: 14px;
    padding: 20px 16px;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.stat-box:hover{
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.07);
}
.stat-number{
    font-size: 2rem;
    font-weight: 800;
    color: #5c0a1a;
    margin-bottom: 4px;
}
.stat-label{
    font-size: 0.82rem;
    color: #64748b;
    font-weight: 500;
}

/* ─── Step Card (landing page how-it-works) ─── */
.step-card{
    background: rgba(255,255,255,0.9);
    border: 1px solid #f5c6ce;
    border-top: 4px solid #dc143c;
    border-radius: 14px;
    padding: 22px 18px;
    text-align: center;
    min-height: 140px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.step-card:hover{
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(220,20,60,0.1);
    border-top-color: #10b981;
}
.step-number{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #dc143c, #b91c3c);
    color: #fff;
    border-radius: 50%;
    font-weight: 700;
    font-size: 0.9rem;
    margin-bottom: 10px;
}
.step-title{
    color: #5c0a1a;
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 6px;
}
.step-desc{
    color: #64748b;
    font-size: 0.78rem;
    line-height: 1.4;
}

/* ─── Footer ─── */
.custom-footer{
    text-align: center;
    padding: 30px 20px 20px;
    margin-top: 50px;
    border-top: 1px solid #f5c6ce;
    background: linear-gradient(180deg, rgba(253,242,244,0), rgba(248,232,235,0.8));
}
.custom-footer p{ margin: 0; padding: 2px 0; }
.custom-footer .footer-title{
    font-size: 0.92rem;
    color: #5c0a1a !important;
    font-weight: 600;
    margin-bottom: 6px;
}
.custom-footer .footer-tech{
    font-size: 0.8rem;
    color: #64748b !important;
    margin-bottom: 8px;
}
.footer-links a{
    color: #dc143c !important;
    text-decoration: none;
    font-weight: 600;
    transition: color 0.2s;
}
.footer-links a:hover{
    color: #9f1239 !important;
    text-decoration: underline;
}
.custom-footer .footer-copy{
    font-size: 0.72rem;
    color: #94a3b8 !important;
    margin-top: 8px;
}

/* ─── Section Divider with Label ─── */
.section-divider{
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 24px 0 18px;
}
.section-divider::before,
.section-divider::after{
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, #e8b4bc, transparent);
}
.section-divider span{
    color: #64748b !important;
    font-size: 0.82rem;
    font-weight: 600;
    white-space: nowrap;
    letter-spacing: 1px;
    text-transform: uppercase;
}
</style>
""",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════
# HERO HEADER — SPLIT: Title in box, subtitle + badge below
# ═══════════════════════════════════════════════════════════
st.markdown(
    """
<div class="hero-box">
    <p class="hero-title">📊 AI Business Report Generator</p>
</div>
<div class="hero-below">
    <p class="hero-subtitle">Upload your data · Get instant analysis · AI writes your report</p>
    <span class="hero-badge">✦ POWERED BY GPT-4 &nbsp;·&nbsp; MULTI-DOMAIN &nbsp;·&nbsp; ONE-CLICK REPORTS</span>
</div>
""",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════
# SIDEBAR — Compact Config
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Report Settings")
    report_title = st.text_input(
        "Report Title", "Monthly Business Performance Report"
    )
    report_period = st.text_input("Report Period", "January 2025")
    tone = st.selectbox("Narrative Tone", ["executive", "manager", "analyst"])
    sensitivity = st.select_slider(
        "Anomaly Sensitivity",
        options=["low", "medium", "high"],
        value="medium",
    )

    st.divider()
    st.markdown("### 🚀 Quick Start")
    use_sample = st.button(
        "📊 Load Sample Sales Data", use_container_width=True
    )

    st.divider()
    st.markdown("### 📋 Pipeline Status")
    status_container = st.container()


# ═══════════════════════════════════════════════════════════
# MAIN — Dataset Type + File Upload
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
                st.markdown(
                    f"- {kpi.icon} **{kpi.name}**: _{kpi.description}_"
                )
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
            st.markdown(
                f"""
            <div class="info-strip">
                <p>📅 <strong>Date Range:</strong> {di['start_date']} → {di['end_date']} &nbsp;({di['total_days']} days)</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with st.expander("👀 Preview Raw Data"):
            st.dataframe(
                df.head(20), use_container_width=True, height=300
            )

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
                pd.DataFrame(col_data),
                use_container_width=True,
                hide_index=True,
            )

    # ──────────────────────────────────────────────────
    # TAB 2 — KEY METRICS (KPIs)
    # ──────────────────────────────────────────────────
    with tab_kpis:
        dc1, dc2 = st.columns([1, 2])
        with dc1:
            st.success(
                f"{kpi_results['domain_icon']} **{kpi_results['domain_name']}**"
            )
            if selected_domain_id == "auto":
                st.caption(
                    "💡 _Auto-detected. Select manually for better accuracy._"
                )
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
                                for r, c in kpi_results[
                                    "column_mapping"
                                ].items()
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
            st.warning(
                "⚠️ No KPIs calculated. Select the correct dataset type."
            )

        if kpi_results.get("category_breakdown"):
            st.markdown(
                '<div class="section-divider"><span>Category Breakdown</span></div>',
                unsafe_allow_html=True,
            )
            cat_tabs = st.tabs(
                list(kpi_results["category_breakdown"].keys())
            )
            for cat_tab, (cat, cdata) in zip(
                cat_tabs,
                kpi_results["category_breakdown"].items(),
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
                    pd.DataFrame(rows),
                    use_container_width=True,
                    hide_index=True,
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
                        gb_df,
                        use_container_width=True,
                        hide_index=True,
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
                        st.dataframe(
                            ct["table_df"], use_container_width=True
                        )
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
                                item["name"],
                                f"{item['total']:,.2f}",
                                delta,
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
                                item["name"],
                                f"{item['total']:,.2f}",
                                delta,
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
                        else "🟡"
                        if c["strength"] == "moderate"
                        else "🟠"
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
        trend_sec, anom_sec = st.tabs(
            ["📈 Trend Analysis", "⚠️ Anomaly Detection"]
        )

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
                    st.markdown(
                        f"**Overall:** {overall['interpretation']}"
                    )
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
                            "Volatility",
                            f"{growth['volatility']:.1f}%",
                        )
                        if growth.get("cagr") is not None:
                            st.markdown(
                                f"""
                            <div class="info-strip">
                                <p>📊 <strong>CAGR:</strong> {growth['cagr']:+.1f}%</p>
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )
                with tt3:
                    season = trend_results.get("seasonality", {})
                    if season.get("detected"):
                        st.success(
                            f"✅ {season.get('interpretation', '')}"
                        )
                        if season.get("monthly_pattern"):
                            st.dataframe(
                                pd.DataFrame(
                                    list(
                                        season[
                                            "monthly_pattern"
                                        ].items()
                                    ),
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
                st.markdown(
                    '<div class="section-divider"><span>Alerts</span></div>',
                    unsafe_allow_html=True,
                )
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
                st.success(
                    "✅ No significant anomalies. Data looks clean!"
                )

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
            # Config summary in a card
            st.markdown(
                f"""
            <div class="glass-card-static" style="margin-bottom:20px;">
                <div style="display:flex;justify-content:space-around;text-align:center;flex-wrap:wrap;gap:10px;">
                    <div>
                        <div style="font-size:0.75rem;color:#64748b;font-weight:500;">TONE</div>
                        <div style="font-size:1rem;color:#5c0a1a;font-weight:700;">{tone.title()}</div>
                    </div>
                    <div>
                        <div style="font-size:0.75rem;color:#64748b;font-weight:500;">PERIOD</div>
                        <div style="font-size:1rem;color:#5c0a1a;font-weight:700;">{report_period}</div>
                    </div>
                    <div>
                        <div style="font-size:0.75rem;color:#64748b;font-weight:500;">DOMAIN</div>
                        <div style="font-size:1rem;color:#5c0a1a;font-weight:700;">{kpi_results.get('domain_name', 'Auto')}</div>
                    </div>
                    <div>
                        <div style="font-size:0.75rem;color:#64748b;font-weight:500;">SENSITIVITY</div>
                        <div style="font-size:1rem;color:#5c0a1a;font-weight:700;">{sensitivity.title()}</div>
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            gc1, gc2 = st.columns([2, 1])
            with gc1:
                gen_mode = st.radio(
                    "Generation Mode",
                    ["📝 Section by Section", "⚡ Full Report"],
                    horizontal=True,
                )
            with gc2:
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
                        (
                            "anomalies_alerts",
                            "⚠️ Anomalies & Alerts",
                        ),
                        ("recommendations", "🎯 Recommendations"),
                    ]

                    report_sections = {}
                    containers = {
                        k: st.container() for k, _ in section_names
                    }
                    prepared = narrator._prepare_data_texts(
                        analysis_bundle
                    )

                    for i, (key, display) in enumerate(section_names):
                        progress.progress(i / len(section_names))
                        status_text.markdown(
                            f"✍️ *Generating {display}...*"
                        )
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
                    st.markdown(
                        '<div class="section-divider"><span>Report Quality & Downloads</span></div>',
                        unsafe_allow_html=True,
                    )

                    scorer = ReportQualityScorer()
                    qual = scorer.score_report(
                        report_sections, analysis_bundle
                    )
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
                    st.markdown(
                        '<div class="section-divider"><span>Download Report</span></div>',
                        unsafe_allow_html=True,
                    )

                    html_gen = HTMLReportGenerator()
                    html_report = html_gen.generate(
                        title=report_title,
                        period=report_period,
                        domain_name=kpi_results.get(
                            "domain_name", "General"
                        ),
                        domain_icon=kpi_results.get(
                            "domain_icon", "📊"
                        ),
                        kpis=kpi_results,
                        narrative_sections=report_sections,
                        chart_figures=(
                            chart_figures if chart_figures else []
                        ),
                        quality_score=qual,
                        llm_stats=api_stats,
                    )

                    md = f"# {report_title}\n"
                    md += f"**Period:** {report_period} | "
                    md += f"**Generated:** {datetime.now().strftime('%B %d, %Y')}\n\n---\n\n"
                    for k, v in report_sections.items():
                        if k != "full_report":
                            md += (
                                f"## {k.replace('_', ' ').title()}\n\n"
                            )
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
        st.markdown(
            """
        <div class="problem-card">
            <h3>🎯 Problem Statement</h3>
            <p>
                Business teams spend
                <strong class="highlight-blue">5–10 hours per week</strong>
                manually creating reports from raw data — profiling datasets, calculating KPIs,
                identifying trends, detecting anomalies, building charts, and writing narratives.
                This system uses <strong class="highlight-green">AI-powered automation</strong>
                to transform any uploaded dataset into a complete, executive-ready business report
                in under <strong class="highlight-green">2 minutes</strong>, reducing manual effort by
                <strong class="highlight-blue">90%+</strong> and ensuring analytical consistency
                across all reporting.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

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
                    st.markdown(
                        f"""
                    <div class="arch-step">
                        <div class="arch-icon">{icon}</div>
                        <div class="arch-title">{title}</div>
                        <div class="arch-desc">{desc}</div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                    <div class="arch-arrow">{icon}</div>
                    """,
                        unsafe_allow_html=True,
                    )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Key Capabilities ──
        st.markdown("### 🏆 Key Capabilities")

        cap_data = [
            (
                "🧠",
                "7 Domains",
                "Auto-detected",
                "Sales · HR · Healthcare · Finance · E-Commerce · Ops · Marketing",
            ),
            (
                "📊",
                "Smart KPIs",
                "Domain-Aware",
                "Auto-calculates relevant metrics per dataset type",
            ),
            (
                "📈",
                "Trend Engine",
                "Multi-Signal",
                "Direction · Growth · Seasonality · Momentum analysis",
            ),
            (
                "⚠️",
                "Anomaly AI",
                "3 Sensitivity",
                "Statistical outliers · Time spikes · Business alerts",
            ),
            (
                "🖼️",
                "Auto Charts",
                "Up to 8",
                "AI-recommended Plotly visualizations per dataset",
            ),
            (
                "📝",
                "GPT-4 Writer",
                "5 Sections",
                "Executive Summary · KPIs · Trends · Anomalies · Recommendations",
            ),
        ]

        for row_start in range(0, len(cap_data), 3):
            cap_cols = st.columns(3)
            for j, col in enumerate(cap_cols):
                idx = row_start + j
                if idx < len(cap_data):
                    icon, title, badge, desc = cap_data[idx]
                    with col:
                        st.markdown(
                            f"""
                        <div class="feature-card">
                            <div class="feature-icon">{icon}</div>
                            <div class="feature-value">{title}</div>
                            <div class="feature-label">{badge}</div>
                            <div class="feature-sub">{desc}</div>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Pipeline Features ──
        st.markdown("### ⚡ Full Pipeline Features")

        st.markdown(
            """
        <div class="glass-card-static" style="margin-bottom:20px;">
        """,
            unsafe_allow_html=True,
        )
        pipe_col1, pipe_col2 = st.columns(2)
        with pipe_col1:
            st.markdown(
                """
            - 📤 **Data Ingestion** — CSV & Excel auto-parsing with type inference
            - 🔍 **Data Profiling** — Schema, quality scores, date range detection
            - 🎯 **Smart KPIs** — Domain-specific metric calculation with formatting
            - 📋 **Descriptive Stats** — Summary, group-by, cross-tabs, correlations
            - 🏆 **Top / Bottom** — Performer analysis with concentration metrics
            """
            )
        with pipe_col2:
            st.markdown(
                """
            - 📈 **Trend Detection** — Direction, growth rates, CAGR, momentum
            - 🌡️ **Seasonality** — Monthly pattern detection and analysis
            - ⚠️ **Anomaly Detection** — IQR outliers, Z-score spikes, business alerts
            - 🖼️ **Chart Recommender** — AI picks best chart types per data shape
            - 📝 **AI Narrator** — GPT-4 generates publication-ready report sections
            """
            )
        st.markdown("</div>", unsafe_allow_html=True)

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
                st.markdown(
                    f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-value" style="font-size:1.1rem">{title}</div>
                    <div class="feature-sub">{desc}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Tech Stack ──
        st.markdown("### 🛠️ Technology Stack")
        st.markdown(
            """
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
        """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Quality Assurance ──
        st.markdown("### ✅ Quality Assurance")

        qa_cols = st.columns(3)
        qa_data = [
            (
                "🎯",
                "Report Scoring",
                "Automated 4-dimension quality scoring: Data Grounding · Structure · Actionability · Conciseness",
            ),
            (
                "💰",
                "Cost Tracking",
                "Real-time token usage and API cost monitoring per session with formatted breakdowns",
            ),
            (
                "🔒",
                "Data Privacy",
                "All processing runs locally — your data never leaves the session. Only AI narrative calls use OpenAI API",
            ),
        ]
        for col, (icon, title, desc) in zip(qa_cols, qa_data):
            with col:
                st.markdown(
                    f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-value" style="font-size:1rem">{title}</div>
                    <div class="feature-sub">{desc}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── About the Builder ──
        st.markdown("### 👨‍💻 Built By")
        st.markdown(
            """
        <div class="profile-card">
            <div style="display:flex;align-items:center;gap:1.5rem;">
                <div style="
                    width:75px;height:75px;border-radius:50%;
                    background:linear-gradient(135deg, #dc143c, #10b981);
                    display:flex;align-items:center;justify-content:center;
                    font-size:2.2rem;flex-shrink:0;
                    box-shadow: 0 4px 16px rgba(220,20,60,0.3);
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
                        <span style="margin:0 10px;color:#94a3b8;">|</span>
                        <a href="https://github.com/anushkundu" target="_blank">🐙 GitHub</a>
                    </div>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # ═══════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════
    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════
# LANDING PAGE (no data loaded)
# ═══════════════════════════════════════════════════════════
else:
    st.markdown("---")

    # ── How It Works — Step Cards ──
    st.markdown("### 🚀 How It Works")
    step_cols = st.columns(5)
    steps = [
        ("1", "Select Domain", "Choose your dataset type for optimized analysis"),
        ("2", "Upload Data", "Drop any CSV or Excel business dataset"),
        ("3", "AI Analyzes", "KPIs, trends, anomalies & charts auto-generated"),
        ("4", "GPT-4 Writes", "Executive-ready narrative report created"),
        ("5", "Download", "Get HTML, Markdown, or Plain Text report"),
    ]
    for col, (num, title, desc) in zip(step_cols, steps):
        with col:
            st.markdown(
                f"""
            <div class="step-card">
                <div class="step-number">{num}</div>
                <div class="step-title">{title}</div>
                <div class="step-desc">{desc}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stats Bar ──
    st.markdown("### ✨ Platform Highlights")
    stat_cols = st.columns(4)
    highlights = [
        ("7+", "Business Domains"),
        ("< 2 min", "Report Generation"),
        ("90%+", "Time Saved"),
        ("5", "Report Sections"),
    ]
    for col, (val, label) in zip(stat_cols, highlights):
        with col:
            st.markdown(
                f"""
            <div class="stat-box">
                <div class="stat-number">{val}</div>
                <div class="stat-label">{label}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Key Features in Cards ──
    st.markdown("### 🎯 Key Features")
    feat_cols = st.columns(3)
    features = [
        (
            "📊",
            "Smart KPI Detection",
            "Automatically identifies and calculates domain-relevant metrics from your data",
        ),
        (
            "📈",
            "Trend & Seasonality",
            "Detects direction, growth rates, CAGR, momentum, and seasonal patterns",
        ),
        (
            "⚠️",
            "Anomaly Detection",
            "Statistical outliers, time-series spikes, and business-rule alerts",
        ),
        (
            "🖼️",
            "AI Visualizations",
            "Recommends and builds the best chart types for your specific data shape",
        ),
        (
            "📝",
            "GPT-4 Narratives",
            "Generates executive summary, KPI analysis, trend insights, and recommendations",
        ),
        (
            "📥",
            "One-Click Export",
            "Download complete reports as styled HTML, Markdown, or Plain Text",
        ),
    ]
    for i, (icon, title, desc) in enumerate(features):
        with feat_cols[i % 3]:
            st.markdown(
                f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <div class="feature-value" style="font-size:1.05rem;">{title}</div>
                <div class="feature-sub">{desc}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Call to Action ──
    st.markdown(
        """
    <div class="glass-card-static" style="text-align:center;padding:32px 24px;">
        <p style="font-size:1.15rem;color:#5c0a1a !important;margin-bottom:8px;font-weight:600;">
            👆 Select a dataset type and upload a file — or click
            <strong style="color:#dc143c !important;">Load Sample Sales Data</strong>
            in the sidebar to get started.
        </p>
        <p style="font-size:0.85rem;color:#64748b !important;margin:0;">
            Works with any tabular business data · No coding required · Results in under 2 minutes
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Footer on landing page
    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )
