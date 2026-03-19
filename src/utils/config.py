# src/utils/config.py

import os
from dotenv import load_dotenv

load_dotenv()

# Load Streamlit Cloud secrets (when deployed)
try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        for key in ['OPENAI_API_KEY', 'GOOGLE_API_KEY']:
            if key in st.secrets:
                os.environ[key] = st.secrets[key]
except Exception:
    pass

from pydantic import BaseModel


class AppConfig(BaseModel):
    # LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    MODEL_NAME_ADVANCED: str = os.getenv("MODEL_NAME_ADVANCED", "gpt-4o")
    TEMPERATURE: float = 0.3
    TEMPERATURE_CREATIVE: float = 0.6
    MAX_TOKENS: int = 4000
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0

    # Cost per 1M tokens
    COST_PER_1M_INPUT_TOKENS: float = 0.15
    COST_PER_1M_OUTPUT_TOKENS: float = 0.60
    COST_PER_1M_INPUT_ADVANCED: float = 2.50
    COST_PER_1M_OUTPUT_ADVANCED: float = 10.00

    # App Settings
    APP_TITLE: str = "AI Business Report Generator"
    CHART_THEME: str = "plotly_white"
    MAX_FILE_SIZE_MB: int = 50
    MAX_CHART_CATEGORIES: int = 20

    # Report Settings
    COMPANY_NAME: str = "Your Company"
    DEFAULT_REPORT_TITLE: str = "Business Performance Report"


config = AppConfig()
