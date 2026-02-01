import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# --- PARCHE MAESTRO DE RUTAS ---
# Usamos Pathlib para mayor robustez en entornos Linux/Cloud
current_dir = Path(__file__).parent.absolute()

if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# --- IMPORTACIÓN DE MÓDULOS ---
try:
    # Importamos config primero para asegurar que las variables de entorno estén listas
    from modules import config, ui, auth, database, pdf_utils, reconciliation, wilo_ai
except ImportError as e:
    st.error(f"🚨 Error Crítico de Importación: {e}")
    st.info("Revisión: Verifica que 'modules/__init__.py' exista y que los nombres de archivos coincidan.")
    st.stop()

def main():
    """
    Punto de entrada principal de la aplicación.
    """
    # Configuración de página (Debe ser la primera instrucción de Streamlit)
    st.set_page_config(
        page_title="Aeropostale Logistics v2",
        page_icon="🚀",
        layout="wide"
    )

    # Autenticación (Supuesto: auth tiene una función de login)
    if not auth.check_password():
        st.stop()

    # Interfaz Principal (Llamada a tu módulo UI)
    ui.render_sidebar()
    ui.render_header()
    
    st.success("Conexión con módulos establecida correctamente.")
    
    # Ejemplo de acción de base de datos
    if st.sidebar.button("Probar Conexión DB"):
        database.test_connection()

if __name__ == "__main__":
    load_dotenv()
    main()
