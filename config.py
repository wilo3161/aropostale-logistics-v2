import os
import logging
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_secret(key, default=None):
    if hasattr(st, "secrets") and key in st.secrets:
        return st.secrets[key]
    return os.getenv(key, default)

SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")
ADMIN_PASSWORD = get_secret("ADMIN_PASSWORD")
USER_PASSWORD = get_secret("USER_PASSWORD")
GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
EMAIL_USER = get_secret("EMAIL_USER")
EMAIL_PASS = get_secret("EMAIL_PASS")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(APP_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)
