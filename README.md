# 📊 AI Business Report Generator

> **Upload any business data → Get instant AI-powered analysis → Download executive-ready reports**

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.37-red.svg)
![Plotly](https://img.shields.io/badge/Plotly-5.x-purple.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Business teams spend **5–10 hours per week** manually profiling data, computing KPIs, building charts, and writing report narratives. This tool automates the entire pipeline — from raw CSV to a downloadable, executive-ready report — in **under 2 minutes**.

---

## 🎯 The Problem I Solved

Most auto-report tools treat every dataset the same — they slap "Revenue by X" on everything regardless of context. A healthcare dataset would get a "Revenue by Gender" bar chart instead of "Patient Count by Diagnosis." An HR dataset would show revenue histograms instead of salary distributions.

**This system is domain-aware.** It automatically adapts KPIs, aggregation logic, chart types, axis labels, and AI narrative vocabulary based on the detected (or selected) business domain.

| Domain | Aggregation | Example Chart | Y-Axis Label |
|--------|------------|---------------|-------------|
| 💰 Sales | **SUM** revenue | Revenue trend line | Total Revenue ($) |
| 👥 HR | **MEAN** salary / **COUNT** employees | Salary by Department box plot | Average Salary |
| 🏥 Healthcare | **COUNT** patients | Patient Count by Diagnosis | Count |
| 🏦 Financial | **SUM** amount | Budget variance bars | Total Amount |
| 🛒 E-Commerce | **SUM** revenue | Orders over time | Revenue |
| 🏭 Operations | **SUM** quantity | Lead time distribution | Quantity |
| 📣 Marketing | **SUM** spend | CTR trend line | Spend |


---

## ⚡ Key Features

- **7 Business Domains** — Auto-detected or manually selected, each with custom KPIs, chart preferences, and vocabulary
- **Smart Column Mapping** — Automatically maps arbitrary column names (`"Total Sales"`, `"Amt"`, `"Revenue"`) to semantic business roles
- **Trend Detection** — Direction, growth rates, CAGR, seasonality, and momentum analysis
- **Anomaly Detection** — IQR outliers + Z-score spikes + business rule alerts with 3 sensitivity levels
- **AI-Recommended Charts** — Up to 8 domain-appropriate Plotly visualizations per dataset
- **GPT-4 / Groq / Gemini Narrative** — 5-section AI-written report with domain vocabulary enforcement
- **Quality Scoring** — 4-dimension automated report quality assessment
- **Multi-Format Export** — HTML (with embedded charts), Markdown, Plain Text

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/ai-report-generator.git
cd ai-report-generator

# Setup
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure API key (pick one — Groq is free)
echo "GROQ_API_KEY=gsk_your_key_here" > .env
# OR: GEMINI_API_KEY=...
# OR: OPENAI_API_KEY=sk-...

# Run
streamlit run app.py

# Run
streamlit run app.py
The app opens at http://localhost:8501. Upload any CSV/Excel or click Load Sample Sales Data in the sidebar.

---

📁 Project Structure
text

ai-report-generator/
├── app.py                          # Streamlit dashboard (7 tabs)
├── requirements.txt
├── .env                            # API keys (not committed)
├── src/
│   ├── ingestion/
│   │   ├── data_loader.py          # CSV/Excel auto-parser
│   │   └── data_profiler.py        # Schema & quality profiling
│   ├── analysis/
│   │   ├── domain_config.py        # 7 domain configurations (Pydantic)
│   │   ├── smart_kpi_calculator.py # Domain-specific KPI engine
│   │   ├── descriptive.py          # Stats, group-by, cross-tabs, correlations
│   │   ├── trend_detector.py       # Time series analysis
│   │   └── anomaly_detector.py     # Outlier & spike detection
│   ├── visualization/
│   │   ├── chart_recommender.py    # Domain-aware chart picker
│   │   └── chart_builder.py        # Plotly chart factory
│   ├── narrative/
│   │   ├── prompts.py              # LLM prompt templates
│   │   ├── narrator.py             # 5-section report generator
│   │   └── quality_scorer.py       # Report quality scoring
│   ├── report/
│   │   └── html_generator.py       # Branded HTML export
│   └── utils/
│       ├── config.py               # App configuration
│       ├── llm_client.py           # Multi-provider LLM client
│       └── logger.py               # Logging
└── data/
    └── sample_sales.csv            # Built-in sample dataset

```

---

## 📊 Dashboard Preview

The Streamlit app has 7 tabs:

Tab	What You See

📊 Data Overview	Row/column counts, quality score, date range, raw preview

🎯 Key Metrics	Domain-detected KPIs with formatting and category breakdowns

📈 Analysis	Summary stats, domain analyses, cross-tabs, top/bottom performers, correlations

📉 Trends & Anomalies	Trend direction + growth + seasonality / Anomaly alerts by severity

🖼️ Visualizations	Up to 8 interactive Plotly charts organized by section

📝 AI Report	Generate, score, and download the AI-written report

ℹ️ About	Architecture, capabilities, tech stack


## 🛠️ Tech Stack

Layer	Technology

Frontend	Streamlit

Data Processing	Pandas, NumPy, SciPy

Visualization	Plotly
AI / LLM	Groq (free) · Google Gemini (free) · OpenAI GPT-4 (paid)
Config Validation	Pydantic
HTML Templating	Jinja2
Excel Support	OpenPyXL


## 🔑 LLM Provider Setup
The system supports 3 providers with automatic failover. You only need one:

Provider	Cost	.env Variable	Notes
Groq	Free	GROQ_API_KEY=gsk_...	Recommended — fast & free
Gemini	Free	GEMINI_API_KEY=...	Google's free tier
OpenAI	Paid	OPENAI_API_KEY=sk-...	GPT-4o, highest quality
If the primary provider fails, the system automatically retries with exponential backoff, then falls back to the next available provider.

## 📈 Impact
Metric	Before	After
Report creation time	4+ hours	< 2 minutes
Manual effort	100%	< 10%
Domain accuracy	Generic (wrong charts/KPIs)	Domain-specific
Cost to run	—	$0 (free-tier LLMs)

## 👨‍💻 Author
Anush Kundu — Data Scientist
MSc Data Science, Kingston University London

📄 License
MIT License — see LICENSE for details.



