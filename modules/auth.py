import streamlit as st
from modules import config

def login_form(target_role="user"):
    st.markdown("### 🔐 Acceso Requerido")
    with st.form("login_form"):
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar")
        if submitted:
            if target_role == "admin" and password == config.ADMIN_PASSWORD:
                st.session_state.user_type = "admin"
                st.success("Acceso Admin concedido")
                st.rerun()
            elif target_role == "user" and (password == config.USER_PASSWORD or password == config.ADMIN_PASSWORD):
                st.session_state.user_type = "user"
                st.success("Acceso Usuario concedido")
                st.rerun()
            else:
                st.error("Contraseña incorrecta")

def require_auth(role="user"):
    if 'user_type' not in st.session_state or not st.session_state.user_type:
        login_form(role)
        st.stop()
    if role == "admin" and st.session_state.user_type != "admin":
        st.error("⛔ Se requieren privilegios de Administrador.")
        st.stop()
