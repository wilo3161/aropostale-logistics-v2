import streamlit as st
import imaplib
import email
from email.header import decode_header
import google.generativeai as genai
import pandas as pd
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from . import config
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

# --- Clases de Lógica de Negocio ---

class WiloAIEngine:
    def __init__(self):
        self.email_conf = config.get_email_secrets()
        self.gemini_key = config.get_gemini_key()
        
    def connect_imap(self):
        try:
            mail = imaplib.IMAP4_SSL(self.email_conf["imap_server"], 993)
            mail.login(self.email_conf["username"], self.email_conf["password"])
            return mail
        except Exception as e:
            logger.error(f"Error IMAP: {e}")
            return None

    def analyze_text(self, text, context="logistica"):
        """Usa Gemini para analizar texto."""
        if not self.gemini_key:
            return {"error": "Sin API Key"}
            
        try:
            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Actúa como un asistente logístico experto. Analiza el siguiente texto de un correo:
            "{text[:2000]}"
            
            Determina:
            1. Tipo de problema (Faltante, Daño, Urgencia, Informativo, Otro)
            2. Gravedad (Alta, Media, Baja)
            3. Resumen en 1 linea.
            4. Acción sugerida.
            
            Responde SOLO en JSON formato:
            {{ "tipo": "...", "gravedad": "...", "resumen": "...", "accion": "..." }}
            """
            
            response = model.generate_content(prompt)
            return json.loads(response.text.replace('```json', '').replace('```', ''))
        except Exception as e:
            logger.error(f"Error AI: {e}")
            return {"tipo": "Error", "gravedad": "N/A", "resumen": "Error en análisis AI", "accion": "Revisar manual"}

class BackgroundMonitor:
    """Clase para manejar tareas en segundo plano (Singleton en session_state)"""
    def __init__(self):
        self.running = False
        self.last_check = None
        self.alerts = []
        self._thread = None

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
    
    def _monitor_loop(self):
        while self.running:
            self.last_check = datetime.now()
            # Aquí iría la lógica real de polling IMAP cada X minutos
            # Por ahora simulamos actividad para no saturar conexiones en dev
            time.sleep(300) 

# --- Funciones de Vista (UI) ---

def render_wilo_dashboard():
    """Renderiza el dashboard de IA."""
    st.markdown("""
    <div class='dashboard-header'>
        <h1 class='header-title'>🧠 WILO AI - Centro de Comando</h1>
        <div class='header-subtitle'>Monitoreo Inteligente y Predicciones</div>
    </div>
    """, unsafe_allow_html=True)

    # Estado del sistema
    col1, col2, col3 = st.columns(3)
    col1.metric("🤖 Motor IA", "ONLINE", delta="v1.5-Flash")
    col2.metric("📧 Monitor Correo", "ACTIVO", delta="IMAP Secure")
    col3.metric("⏱️ Último Escaneo", datetime.now().strftime("%H:%M"))

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Análisis de Correos", "🔮 Predicciones", "⚙️ Configuración"])

    with tab1:
        st.subheader("Análisis de Bandeja de Entrada")
        if st.button("🚀 Ejecutar Análisis Ahora"):
            with st.spinner("Conectando con servidor de correo y procesando con Gemini..."):
                engine = WiloAIEngine()
                mail = engine.connect_imap()
                if mail:
                    mail.select("INBOX")
                    # Buscar últimos 5 correos para demo
                    _, msg_ids = mail.search(None, 'ALL')
                    ids = msg_ids[0].split()[-5:]
                    
                    results = []
                    for i in reversed(ids):
                        _, data = mail.fetch(i, '(RFC822)')
                        msg = email.message_from_bytes(data[0][1])
                        subject = decode_header(msg["Subject"])[0][0]
                        if isinstance(subject, bytes): subject = subject.decode()
                        
                        # Extraer cuerpo simple
                        body = "Contenido del correo..." 
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode(errors='ignore')
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode(errors='ignore')

                        analysis = engine.analyze_text(body)
                        results.append({
                            "Asunto": subject,
                            "Remitente": msg["From"],
                            "Tipo": analysis.get("tipo"),
                            "Gravedad": analysis.get("gravedad"),
                            "Acción": analysis.get("accion")
                        })
                    
                    mail.logout()
                    st.dataframe(pd.DataFrame(results))
                else:
                    st.error("No se pudo conectar al correo. Revise credenciales.")

    with tab2:
        st.subheader("Predicción de Eficiencia")
        # Datos simulados para el gráfico de predicción
        dates = pd.date_range(start=datetime.now(), periods=7)
        values = [95, 96, 94, 98, 97, 99, 98]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=values, mode='lines+markers', name='Predicción IA'))
        fig.update_layout(title="Proyección de Eficiencia Semanal", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.info("Configuración cargada desde secrets.toml")
        st.json(config.get_email_secrets())

def init_wilo_background():
    """Inicializa el monitor en session_state si no existe."""
    if 'wilo_monitor' not in st.session_state:
        st.session_state.wilo_monitor = BackgroundMonitor()
        st.session_state.wilo_monitor.start()
