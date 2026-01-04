import streamlit as st
import config
from modules import ui, auth, database, wilo_ai, pdf_utils, reconciliation
import time

st.set_page_config(layout="wide", page_title="Sistema KPIs Aeropostale", page_icon="✈️")
ui.load_css()
wilo_engine = wilo_ai.get_wilo_engine()

def view_dashboard():
    ui.render_header("📊 Dashboard KPIs", "Control Logístico")
    df = database.fetch_data("daily_kpis", order_by=("fecha", True))
    if df.empty: st.info("No hay datos")
    else: st.dataframe(df, use_container_width=True)

def view_guides():
    auth.require_auth("user")
    ui.render_header("📦 Guías", "Generador")
    with st.form("guide"):
        store = st.selectbox("Tienda", ["Norte", "Sur"])
        brand = st.radio("Marca", ["Fashion", "Tempo"])
        url = st.text_input("URL")
        if st.form_submit_button("Generar"):
            pdf = pdf_utils.generate_shipping_guide(store, brand, url, "CEDI", f"TRK-{int(time.time())}")
            st.download_button("Descargar", pdf, "guia.pdf")

def view_wilo():
    auth.require_auth("admin")
    ui.render_header("🧠 Wilo AI", "Admin Panel")
    st.success(f"Motor activo: {wilo_engine.last_check}")

def main():
    with st.sidebar:
        st.title("AEROPOSTALE")
        menu = st.radio("Menú", ["Dashboard", "Guías", "Wilo AI"])
        if st.session_state.get('user_type'):
            if st.button("Salir"): st.session_state.user_type = None; st.rerun()
    
    if menu == "Dashboard": view_dashboard()
    elif menu == "Guías": view_guides()
    elif menu == "Wilo AI": view_wilo()

if __name__ == "__main__":
    main()
