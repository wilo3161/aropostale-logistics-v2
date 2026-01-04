import threading
import time
import logging
import google.generativeai as genai
import config
import streamlit as st
from datetime import datetime

logger = logging.getLogger(__name__)

class WiloMonitorEngine:
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_check = datetime.now()
        
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            logger.info("🤖 Wilo AI Monitor iniciado")
            
    def _run_loop(self):
        while self.running:
            try:
                self.last_check = datetime.now()
                time.sleep(300) 
            except Exception:
                time.sleep(60)

    def analyze_email_content(self, subject, body):
        if not config.GEMINI_API_KEY: return {"error": "No API Key"}
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Analiza correo logística. Asunto: {subject}. Cuerpo: {body[:1000]}."
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return {"error": str(e)}

@st.cache_resource
def get_wilo_engine():
    engine = WiloMonitorEngine()
    engine.start()
    return engine
