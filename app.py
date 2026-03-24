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
        font=dict(color="#4a5568", family="Inter, Arial", size=11),
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

/* ─── Hero Header Box ─── */
.hero-box{
    background: linear-gradient(135deg, #4c0519 0%, #7f1d1d 30%, #991b1b 60%, #4c0519 100%);
    border-radius: 20px;
    padding: 48px 30px 42px;
    margin: 0 0 24px;
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
    font-size: 3.2rem;
    font-weight: 800;
    color: #FFD700;
    margin: 0 0 12px;
    letter-spacing: -0.5px;
    position: relative;
    z-index: 1;
    text-shadow: 0 2px 12px rgba(0,0,0,0.35), 0 0 30px rgba(255,215,0,0.15);
}
.hero-subtitle{
    font-size: 1.15rem;
    color: #ffffff;
    margin: 0;
    font-weight: 400;
    letter-spacing: 0.5px;
    position: relative;
    z-index: 1;
    text-shadow: 0 1px 6px rgba(0,0,0,0.3);
}
.hero-badge{
    display: inline-block;
    background: rgba(255,215,0,0.2);
    border: 1px solid rgba(255,215,0,0.45);
    border-radius: 20px;
    padding: 5px 18px;
    color: #FFD700 !important;
    font-size: 0.82rem;
    font-weight: 700;
    margin-top: 16px;
    position: relative;
    z-index: 1;
    letter-spacing: 0.6px;
    text-shadow: 0 1px 4px rgba(0,0,0,0.2);
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
# HERO HEADER
# ═══════════════════════════════════════════════════════════
st.markdown(
    """
<div class="hero-box">
    <p class="hero-title">📊 AI Business Report Generator</p>
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
    tone = 
