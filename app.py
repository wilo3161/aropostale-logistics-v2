import streamlit as st
import os
import sys

# ==========================================
# 🕵️‍♂️ AUDITORÍA DE ENTORNO (DIAGNÓSTICO)
# ==========================================
st.set_page_config(layout="wide", page_title="Diagnóstico de Despliegue")

st.title("🛠️ Modo de Auditoría de Archivos")

# 1. ¿DÓNDE ESTOY?
current_dir = os.getcwd()
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)

st.write(f"📍 **Directorio de Trabajo (CWD):** `{current_dir}`")
st.write(f"📍 **Ubicación de app.py:** `{script_path}`")

# 2. ¿QUÉ ARCHIVOS HAY AQUÍ?
st.write("📂 **Archivos en el directorio del script:**")
try:
    files_in_root = os.listdir(script_dir)
    st.code(files_in_root)
except Exception as e:
    st.error(f"Error leyendo directorio: {e}")

# 3. ¿EXISTE LA CARPETA MODULES?
if "modules" in files_in_root:
    st.success("✅ La carpeta 'modules' FUE ENCONTRADA.")
    
    # 4. ¿QUÉ HAY DENTRO DE MODULES?
    modules_path = os.path.join(script_dir, "modules")
    if os.path.isdir(modules_path):
        files_in_modules = os.listdir(modules_path)
        st.write("📦 **Contenido de /modules:**")
        st.code(files_in_modules)
        
        if "__init__.py" in files_in_modules:
            st.success("✅ '__init__.py' existe. El paquete es válido.")
        else:
            st.error("❌ CRÍTICO: Falta '__init__.py' dentro de modules.")
    else:
        st.error("⚠️ 'modules' existe pero NO es una carpeta.")
else:
    st.error("❌ LA CARPETA 'modules' NO ESTÁ EN ESTA RUTA.")
    st.info("💡 Pista: Si la carpeta no aparece, es probable que tus archivos estén subidos dentro de una subcarpeta en GitHub.")

# 5. INTENTO DE IMPORTACIÓN MANUAL (PRUEBA DE FUEGO)
st.write("---")
st.write("🔥 **Prueba de Importación:**")

# Forzamos la ruta al sistema
if script_dir not in sys.path:
    sys.path.append(script_dir)

try:
    import modules
    st.success("1. Import 'modules' exitoso.")
    
    try:
        from modules import config
        st.success("2. Import 'modules.config' exitoso.")
    except ImportError as e:
        st.error(f"2. Falló import modules.config: {e}")
        
    try:
        from modules import auth
        st.success("3. Import 'modules.auth' exitoso.")
    except ImportError as e:
        st.error(f"3. Falló import modules.auth: {e}")
        st.warning("Si falla aquí, es probable que 'auth.py' tenga un import incorrecto dentro.")

except ImportError as e:
    st.error(f"1. Falló import 'modules': {e}")

st.write("---")
st.info("Si ves todos los checks verdes arriba, descomenta tu código original abajo.")

# ==========================================
# CÓDIGO ORIGINAL (DESCOMENTAR CUANDO FUNCIONE)
# ==========================================
# Una vez que el diagnóstico muestre todo verde, borra todo lo de arriba 
# y deja solo tu código normal.
#
# from modules import config, ui, auth, database, ...
# ... resto de tu app ...
