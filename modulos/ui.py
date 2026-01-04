import streamlit as st
def load_css():
    st.markdown("<style>.dashboard-header {background: linear-gradient(90deg, #004085 0%, #007BFF 100%); padding: 20px; border-radius: 8px; color: white;} .kpi-card {background: white; padding: 20px; border-radius: 8px; border-left: 5px solid #007BFF; box-shadow: 0 2px 4px rgba(0,0,0,0.05); color: #333;}</style>", unsafe_allow_html=True)
def render_header(title, subtitle=""):
    st.markdown(f"<div class='dashboard-header'><h1>{title}</h1><div>{subtitle}</div></div>", unsafe_allow_html=True)
