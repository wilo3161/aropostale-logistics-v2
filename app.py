import streamlit as st
import sys
import os

# ==========================================
# 🕵️‍♂️ ZONA DE DIAGNÓSTICO FORENSE (AUDITORÍA)
# ==========================================
# Esto nos dirá exactamente qué ve el servidor de Streamlit
st.set_page_config(layout="wide", page_title="Sistema KPIs Aeropostale", page_icon="✈️")

st.markdown("### 🛠️ Estado del Despliegue")

# 1. Identificar dónde estamos parados
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_path) # FORZAR la ruta actual al sistema

st.write(f"**Directorio de trabajo:** `{os.getcwd()}`")
st.write(f"**Ruta del archivo app.py:** `{current_path}`")

# 2. Listar archivos en la raíz (¿Existe 'modules'?)
files_in_root = os.listdir(current_path)
if "modules" in files_in_root:
    st.success("✅ Carpeta 'modules' detectada en la raíz.")
    
    # 3. Listar contenido de 'modules' (¿Existe '__init__.py'?)
    modules_path = os.path.join(current_path, "modules")
    if os.path.isdir(modules_path):
        files_in_modules = os.listdir(modules_path)
        st.write(f"📂 **Contenido de /modules:** `{files_in_modules}`")
        
        if "__init__.py" in files_in_modules:
            st.success("✅ Archivo '__init__.py' detectado (El paquete es válido).")
        else:
            st.error("❌ CRÍTICO: Falta '__init__.py' dentro de la carpeta 'modules'. Python no puede importar esto.")
            st.stop()
    else:
        st.error("❌ 'modules' existe pero no es una carpeta.")
        st.stop()
else:
    st.error(f"❌ LA CARPETA 'modules' NO EXISTE. Archivos encontrados: {files_in_root}")
    st.warning("Solución: Asegúrate de que la carpeta 'modules' esté al mismo nivel que 'app.py' en GitHub.")
    st.stop()

# ==========================================
# FIN DEL DIAGNÓSTICO - INICIO DE LA APP
# ==========================================

try:
    # Importación segura usando el parche de ruta
    from modules import config, ui, auth, database, pdf_utils, reconciliation, wilo_ai
except ImportError as e:
    st.error(f"💀 Error fatal importando módulos: {e}")
    st.error("Revisa que los archivos dentro de 'modules/' no tengan errores de sintaxis.")
    st.stop()
except Exception as e:
    st.error(f"💀 Error desconocido: {e}")
    st.stop()

# --- LÓGICA PRINCIPAL (CÓDIGO ORIGINAL RESTAURADO) ---
import pandas as pd
import time
from datetime import datetime, timedelta
import plotly.express as px

# Inicialización
auth.init_session_state()
ui.load_css()
wilo_ai.init_wilo_background()

# --- CONTROLADORES DE VISTA ---

def view_dashboard_kpis():
    ui.render_header("📊 Dashboard de KPIs", "Control Logístico en Tiempo Real")
    c1, c2 = st.columns(2)
    f_inicio = c1.date_input("Inicio", datetime.now().date())
    f_fin = c2.date_input("Fin", datetime.now().date())
    
    df = database.cargar_historico_db(f_inicio.strftime("%Y-%m-%d"), f_fin.strftime("%Y-%m-%d"))
    
    if df.empty:
        st.info("⚠️ No hay datos registrados en este período.")
        return

    total_prod = df['cantidad'].sum()
    meta_total = df['meta'].sum()
    cumplimiento = (total_prod / meta_total * 100) if meta_total > 0 else 0
    
    st.markdown("<div class='kpi-tower'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: ui.render_kpi_card("Producción", f"{total_prod:,.0f}", f"Meta: {meta_total:,.0f}", "📦")
    with c2: ui.render_kpi_card("Cumplimiento", f"{cumplimiento:.1f}%", "Global", "🎯", "positive" if cumplimiento >= 90 else "negative")
    with c3: ui.render_kpi_card("Registros", str(len(df)), "Entradas", "📝")
    st.markdown("</div>", unsafe_allow_html=True)
    
    df_team = df.groupby('equipo')['cantidad'].sum().reset_index()
    fig = px.bar(df_team, x='equipo', y='cantidad', color='equipo', title="Producción Total por Equipo")
    st.plotly_chart(fig, use_container_width=True)

def view_analisis_historico():
    ui.render_header("📈 Análisis Histórico", "Tendencias y Exportación")
    df = database.cargar_historico_db()
    if df.empty:
        st.warning("Base de datos vacía.")
        return
    st.dataframe(df, use_container_width=True)

def view_gestion_distribuciones():
    auth.require_auth("admin")
    ui.render_header("📦 Gestión de Distribución", "Control Semanal")
    fecha_actual = datetime.now().date()
    inicio_semana = (fecha_actual - timedelta(days=fecha_actual.weekday())).strftime("%Y-%m-%d")
    
    datos = database.obtener_distribuciones_semana(inicio_semana)
    
    with st.form("form_dist"):
        st.subheader(f"Semana del {inicio_semana}")
        c1, c2 = st.columns(2)
        tempo = c1.number_input("Tempo Distribuciones", value=int(datos.get('tempo_distribuciones', 0)))
        luis = c2.number_input("Luis Perugachi", value=int(datos.get('luis_distribuciones', 0)))
        meta = st.number_input("Meta Semanal", value=int(datos.get('meta_semanal', 7500)))
        
        if st.form_submit_button("Guardar"):
            if database.guardar_distribuciones_semanales(inicio_semana, tempo, luis, meta):
                st.success("Guardado"); time.sleep(1); st.rerun()
            else: st.error("Error al guardar")

def view_ingreso_datos():
    auth.require_auth("admin")
    ui.render_header("📥 Ingreso Diario", "Registro de Producción")
    fecha = st.date_input("Fecha", datetime.now())
    trabajadores = database.obtener_trabajadores()
    
    if trabajadores.empty: st.warning("No hay trabajadores."); return
        
    with st.form("main_input"):
        datos = {}
        for equipo in trabajadores['equipo'].unique():
            st.subheader(f"👥 {equipo}")
            for _, t in trabajadores[trabajadores['equipo'] == equipo].iterrows():
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(t['nombre'])
                cant = c2.number_input("Cant.", key=f"c_{t['nombre']}", min_value=0)
                horas = c3.number_input("Horas", key=f"h_{t['nombre']}", value=8.0)
                if cant > 0:
                    datos[t['nombre']] = {"cantidad": cant, "horas_trabajo": horas, "meta": 1000, "equipo": equipo, "eficiencia": (cant/1000*100), "productividad": cant/horas, "actividad": equipo, "comentario": "", "meta_mensual": 0}
        if st.form_submit_button("Guardar Todo"):
            if database.guardar_datos_db(fecha.strftime("%Y-%m-%d"), datos):
                st.success("Datos guardados"); time.sleep(1); st.rerun()

def view_novedades_correo():
    auth.require_auth("admin")
    ui.render_header("📧 Wilo AI: Novedades", "Análisis de Correos")
    if st.button("🚀 Escanear Bandeja"):
        engine = wilo_ai.WiloAIEngine()
        if engine.connect_imap():
            st.success("Conectado a IMAP. (Lógica de escaneo simulada por seguridad)")
        else:
            st.error("Error conectando al correo. Revisa secrets.toml")

def view_generar_guias_wrapper():
    auth.require_auth("user")
    ui.render_header("📦 Guías", "Generador PDF")
    with st.form("g"):
        tienda = st.selectbox("Tienda", ["Norte", "Sur"])
        if st.form_submit_button("Generar"): st.success("Guía simulada generada")

def view_etiquetas_wrapper():
    auth.require_auth("user")
    ui.render_header("🏷️ Etiquetas", "Generador")
    with st.form("e"):
        ref = st.text_input("Ref")
        if st.form_submit_button("Generar"): st.success("Etiqueta simulada")

def main():
    if st.session_state.show_login:
        auth.login_form(); return

    with st.sidebar:
        st.title("AEROPOSTALE v2")
        opciones = [
            ("Dashboard KPIs", "📊", view_dashboard_kpis, "public"),
            ("Ingreso Datos", "📥", view_ingreso_datos, "admin"),
            ("Gestión Distribución", "🚛", view_gestion_distribuciones, "admin"),
            ("Reconciliación", "⚖️", lambda: st.info("Módulo Reconciliación"), "admin"),
            ("Generar Guías", "📋", view_generar_guias_wrapper, "user"),
            ("Etiquetas", "🏷️", view_etiquetas_wrapper, "user"),
            ("Wilo Novedades", "📧", view_novedades_correo, "admin"),
            ("Análisis Histórico", "📈", view_analisis_historico, "public"),
        ]
        
        for i, (lbl, icon, func, rol) in enumerate(opciones):
            if st.button(f"{icon} {lbl}", key=f"btn_{i}", use_container_width=True):
                st.session_state.selected_menu = i
        
        if st.session_state.user_type:
            if st.button("Salir"): st.session_state.user_type = None; st.rerun()
        else:
            if st.button("Login Admin"): st.session_state.show_login = True; st.session_state.login_type = "admin"; st.rerun()

    # Router
    idx = st.session_state.get('selected_menu', 0)
    if idx < len(opciones):
        lbl, icon, func, rol = opciones[idx]
        authorized = (rol == "public") or (rol == "user" and st.session_state.user_type) or (rol == "admin" and st.session_state.user_type == "admin")
        if authorized: func()
        else: st.error("🔒 Acceso denegado"); st.button("Login", on_click=lambda: setattr(st.session_state, 'show_login', True))

if __name__ == "__main__":
    main()
