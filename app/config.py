import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def _get_secret(name: str, default: str = "") -> str:
    """Сначала окружение/.env, затем st.secrets (Streamlit Cloud)."""
    val = os.getenv(name)
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(name, default)
    except Exception:
        return default


GROQ_API_KEY = _get_secret("GROQ_API_KEY")
MODEL = _get_secret("GROQ_MODEL", "llama-3.3-70b-versatile")
TEMPERATURE = float(_get_secret("TEMPERATURE", "0.3"))
MAX_TOKENS = int(_get_secret("MAX_TOKENS", "1024"))

QUESTIONS_FILE = DATA_DIR / "questions.json"
RUBRICS_FILE = DATA_DIR / "rubrics.json"
REFERENCE_FILE = DATA_DIR / "reference_answers.json"

MAX_FOLLOWUPS = 2

# Верификатор обнуляе балл если нет улючевых слов
VERIFIER_ENABLED = _get_secret("VERIFIER_ENABLED", "true").lower() in ("1", "true", "yes")