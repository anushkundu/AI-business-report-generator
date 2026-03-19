# src/utils/config.py  (REPLACE your existing config.py with this)

"""
APPLICATION CONFIGURATION
"""

from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()


class AppConfig(BaseModel):
    # LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    MODEL_NAME_ADVANCED: str = os.getenv("MODEL_NAME_ADVANCED", "gpt-4o")
    TEMPERATURE: float = 0.3
    TEMPERATURE_CREATIVE: float = 0.6     # for recommendations section
    MAX_TOKENS: int = 4000
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0             # seconds

    # Cost per 1M tokens (as of 2024-2025)
    COST_PER_1M_INPUT_TOKENS: float = 0.15      # gpt-4o-mini
    COST_PER_1M_OUTPUT_TOKENS: float = 0.60     # gpt-4o-mini
    COST_PER_1M_INPUT_ADVANCED: float = 2.50    # gpt-4o
    COST_PER_1M_OUTPUT_ADVANCED: float = 10.00  # gpt-4o

    # App Settings
    APP_TITLE: str = "AI Business Report Generator"
    CHART_THEME: str = "plotly_white"
    MAX_FILE_SIZE_MB: int = 50
    MAX_CHART_CATEGORIES: int = 20

    # Report Settings
    COMPANY_NAME: str = "Your Company"
    DEFAULT_REPORT_TITLE: str = "Business Performance Report"


config = AppConfig()