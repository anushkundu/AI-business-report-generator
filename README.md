<!-- README.md -->

<div align="center">
  
# 📊 AI Business Report Generator

### Transform Raw Data into Executive-Ready Reports in Under 2 Minutes

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.37-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.18-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![LLM](https://img.shields.io/badge/LLM-Groq%20|%20Gemini%20|%20OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](#api-keys)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

**Upload any business dataset** → **AI analyzes trends, anomalies & KPIs** → **GPT writes narrative report** → **Download as HTML with charts**

<br/>

[🚀 Live Demo](https://your-app.streamlit.app) · [📄 Report Sample](#sample-report) · [🐛 Report Bug](https://github.com/YOUR_USERNAME/ai-report-generator/issues)

<br/>

---

</div>

## 📌 Problem Statement

> Data analysts spend **4-6 hours** per report manually analyzing data, creating charts, writing insights, and formatting deliverables. Most reports follow the same structure — KPIs, trends, anomalies, recommendations — yet the process is repeated from scratch every time.

**This tool automates the entire pipeline in under 2 minutes**, producing an executive-ready report with domain-specific analysis, interactive visualizations, and AI-generated narrative — all from a single CSV upload.

---

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 🔍 Smart Data Understanding
- Auto-detects column types and business metrics
- Maps columns to domain-specific roles
- Handles CSV, Excel (.xlsx, .xls) formats
- Auto-parses dates, cleans column names
- Data quality scoring (completeness %)

</td>
<td width="50%">

### 📊 Domain-Aware Analysis
- **7 business domains** with custom analysis logic
- Domain-specific KPIs (COUNT patients ≠ SUM revenue)
- Cross-tabulations (Gender × Diagnosis for healthcare)
- Derived metrics (salary bands, age groups, funnel metrics)
- Top/bottom performer identification

</td>
</tr>
<tr>
<td width="50%">

### 📈 Trend & Anomaly Detection
- MoM, QoQ, YoY growth rate calculation
- Trend direction with R² confidence score
- Seasonality detection with monthly patterns
- Momentum analysis (accelerating/decelerating)
- IQR + Z-score outlier detection
- Business rule violation alerts

</td>
<td width="50%">

### 🤖 AI-Powered Narrative
- Domain-aware vocabulary enforcement
- 3 adjustable tones (Executive / Manager / Analyst)
- Multi-provider LLM support (Groq, Gemini, OpenAI)
- Automatic provider failover
- Report quality scoring (0-100)
- Zero-cost operation with free APIs

</td>
</tr>
<tr>
<td width="50%">

### 📉 Intelligent Visualizations
- Domain-specific chart recommendations
- 10 chart types (line, bar, pie, scatter, box, etc.)
- Auto-annotated peaks, troughs, and bounds
- Growth rate waterfall charts
- Anomaly highlight scatter plots
- Professional consistent styling

</td>
<td width="50%">

### 📄 Export & Delivery
- Beautiful HTML report with embedded interactive charts
- KPI dashboard cards in report header
- Markdown and plain text downloads
- Self-contained HTML (opens in any browser)
- Print-ready formatting
- Deployable to Streamlit Cloud

</td>
</tr>
</table>

---

## 🏢 Supported Business Domains

Each domain has its own **KPI definitions, aggregation logic, chart types, cross-tabulations, and AI vocabulary** — ensuring the analysis is contextually accurate.

| Domain | Icon | Primary Metric | Aggregation | Example KPIs | Example Charts |
|--------|------|----------------|-------------|-------------|----------------|
| **Sales & Revenue** | 💰 | Revenue | SUM | Total Revenue, Profit Margin, AOV | Revenue trend, Region bar, Category pie |
| **HR & Workforce** | 👥 | Employee ID | COUNT | Headcount, Avg Salary, Attrition Rate | Dept bar, Salary histogram, Attrition grouped bar |
| **Healthcare** | 🏥 | Patient ID | COUNT | Patient Count, Avg LOS, Avg Cost | Diagnosis bar, Gender pie, Age histogram |
| **Financial** | 🏦 | Amount | SUM | Budget Variance, Total Spend | Category bar, Spending pie, Amount trend |
| **E-Commerce** | 🛒 | Revenue | SUM | Total Orders, Revenue/Customer, Avg Rating | Product bar, Channel pie, Rating scatter |
| **Operations** | 🏭 | Quantity | SUM | Avg Lead Time, Defect Rate | Supplier bar, Lead time histogram, Cost box |
| **Marketing** | 📣 | Ad Spend | SUM | CTR, CPC, ROAS, Conversion Rate | Campaign bar, Channel pie, Spend vs Conversions |

### Why Domain Awareness Matters
