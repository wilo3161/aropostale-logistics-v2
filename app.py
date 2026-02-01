import streamlit as st
import os
from dotenv import load_dotenv

# --- PARCHE MAESTRO DE RUTAS (SOLUCIÓN DEFINITIVA) ---
# 1. Obtiene la ruta absoluta donde vive ESTE archivo (app.py)
directorio_raiz = os.path.dirname(os.path.abspath(__file__))

# 2. Agrega esa ruta al sistema de Python para que SIEMPRE encuentre 'modules'
#    sin importar desde dónde lance Streamlit la aplicación.
if directorio_raiz not in sys.path:
    sys.path.append(directorio_raiz)

# 3. Diagnóstico (Opcional: te mostrará en pantalla si falta algo)
# st.write(f"DEBUG: Buscando módulos en: {directorio_raiz}")
# st.write(f"DEBUG: Archivos encontrados: {os.listdir(directorio_raiz)}")
# -----------------------------------------------------

# AHORA SÍ, TUS IMPORTS NORMALES
try:
    # Nota: Aquí ya no necesitamos parches raros, solo llamar al paquete
    from modules import config, ui, auth, database, pdf_utils, reconciliation, wilo_ai
except ImportError as e:
    st.error(f"🚨 Error Crítico de Importación: {e}")
    st.info("Asegúrate de que la carpeta se llame 'modules' (minúscula) y tenga un archivo '__init__.py' dentro.")
    st.stop()
if __name__ == "__main__":
    load_dotenv()
    main()
