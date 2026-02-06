import streamlit as st
import pandas as pd 
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import hashlib
import logging
import re
import json
import io
import os
import warnings
from pathlib import Path
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    layout="wide",
    page_title="AEROPOSTALE ERP | Control Total",
    page_icon="👔",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 1. ESTILOS CSS - MEJORADO Y COMPLETO
# ==============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700;800&display=swap');

.stApp {
    font-family: 'Montserrat', sans-serif;
    background-color: #0e1117;
    overflow: hidden;
}

.main-bg {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    z-index: -1;
}

/* Contenedor Ultra-Compacto */
.gallery-container {
    padding: 30px 5% 10px 5%;
    text-align: center;
    max-width: 1400px;
    margin: 0 auto;
}

.brand-title {
    color: white;
    font-size: 3.5rem;
    font-weight: 900;
    letter-spacing: 15px;
    margin-bottom: 10px;
    text-transform: uppercase;
    background: linear-gradient(45deg, #60A5FA, #F472B6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
    from { text-shadow: 0 0 10px rgba(96, 165, 250, 0.5); }
    to { text-shadow: 0 0 20px rgba(244, 114, 182, 0.8); }
}

.brand-subtitle {
    color: #94A3B8;
    font-size: 1rem;
    letter-spacing: 6px;
    margin-bottom: 40px;
    text-transform: uppercase;
    font-weight: 300;
}

/* Grid de módulos */
.modules-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    padding: 0 10px;
}

@media (max-width: 1024px) {
    .modules-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
    .modules-grid { grid-template-columns: 1fr; }
    .brand-title { font-size: 2.5rem; letter-spacing: 10px; }
}

/* Tarjetas Rectangulares Compactas */
.module-card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    height: 180px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 20px;
    position: relative;
    cursor: pointer;
    overflow: hidden;
}

.module-card:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
}

.module-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.7s;
}

.module-card:hover::before {
    left: 100%;
}

.card-icon {
    font-size: 2.8rem;
    margin-bottom: 15px;
    transition: transform 0.3s ease;
}

.module-card:hover .card-icon {
    transform: scale(1.2) rotate(5deg);
}

.card-title {
    color: white;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    text-align: center;
}

.card-description {
    color: #94A3B8;
    font-size: 0.85rem;
    text-align: center;
    margin-top: 8px;
    opacity: 0.8;
    line-height: 1.3;
}

/* Botones invisibles */
.stButton > button.module-btn {
    width: 100% !important;
    height: 180px !important;
    background-color: transparent !important;
    border: none !important;
    color: transparent !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    z-index: 10 !important;
    cursor: pointer !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a237e 0%, #283593 100%);
}

.sidebar-header {
    text-align: center;
    padding: 20px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-title {
    color: white;
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 5px;
}

.sidebar-subtitle {
    color: #94A3B8;
    font-size: 0.8rem;
}

/* Contenido interno */
.internal-header {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    padding: 2rem;
    border-left: 6px solid #60A5FA;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    margin-bottom: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.header-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: white;
    margin-bottom: 0.5rem;
    background: linear-gradient(45deg, #60A5FA, #F472B6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header-subtitle {
    font-size: 1rem;
    color: #94A3B8;
    font-weight: 400;
}

/* Tarjetas de estadísticas */
.stat-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    height: 100%;
}

.stat-card:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-3px);
}

.stat-icon {
    font-size: 2rem;
    margin-bottom: 1rem;
    color: #60A5FA;
}

.stat-title {
    font-size: 0.9rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.stat-value {
    font-size: 2rem;
    font-weight: 800;
    color: white;
    margin: 0.5rem 0;
}

.stat-change {
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    display: inline-block;
    background: rgba(34, 197, 94, 0.2);
    color: #4ADE80;
}

.stat-change.negative {
    background: rgba(239, 68, 68, 0.2);
    color: #F87171;
}

/* Grid para métricas */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

/* Tabs personalizados */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background-color: transparent;
}

.stTabs [data-baseweb="tab"] {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 0.8rem 1.5rem;
    font-weight: 600;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
    color: #94A3B8;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: rgba(255, 255, 255, 0.08);
    border-color: #60A5FA;
    color: white;
}

.stTabs [aria-selected="true"] {
    background-color: rgba(96, 165, 250, 0.2);
    color: #60A5FA;
    border-color: #60A5FA;
}

/* Botones */
.stButton > button {
    background: linear-gradient(45deg, #60A5FA, #8B5CF6) !important;
    color: white !important;
    border: none !important;
    padding: 0.8rem 2rem !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(96, 165, 250, 0.2) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(96, 165, 250, 0.3) !important;
}

/* DataFrames */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
    background: rgba(255, 255,255, 0.05) !important;
}

/* Scrollbar personalizado */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(45deg, #60A5FA, #8B5CF6);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(45deg, #8B5CF6, #F472B6);
}

/* Notificaciones */
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    background: rgba(34, 197, 94, 0.9);
    color: white;
    border-radius: 8px;
    z-index: 1000;
    animation: slideIn 0.3s ease;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Footer */
.app-footer {
    text-align: center;
    padding: 2rem;
    margin-top: 3rem;
    color: #64748B;
    font-size: 0.9rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Botón flotante */
.floating-btn {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(45deg, #60A5FA, #8B5CF6);
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    box-shadow: 0 8px 25px rgba(96, 165, 250, 0.3);
    transition: all 0.3s ease;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: center;
}

.floating-btn:hover {
    transform: scale(1.1) rotate(90deg);
    box-shadow: 0 12px 30px rgba(96, 165, 250, 0.4);
}
</style>

<div class="main-bg"></div>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. FUNCIONES DE APOYO
# ==============================================================================

def create_card(icon, title, description, key_target):
    """Crea una tarjeta de módulo interactiva"""
    st.markdown(f"""
    <div class="module-card">
        <div class="card-icon">{icon}</div>
        <div class="card-title">{title}</div>
        <div class="card-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Botón invisible que cubre toda la tarjeta
    if st.button(f"Entrar {title}", key=f"btn_{key_target}", help=f"Acceder a {title}"):
        st.session_state.current_page = key_target
        st.rerun()

def show_sidebar():
    """Muestra la barra lateral de navegación"""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-title">AERO ERP</div>
            <div class="sidebar-subtitle"> • Wilson Pérez</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏠 INICIO PRINCIPAL", use_container_width=True, type="primary"):
            st.session_state.current_page = "Inicio"
            st.rerun()
        
        st.divider()
        
        st.markdown("**📋 Módulos:**")
        
        # Menú de navegación rápida
        modules = [
            ("Dashboard KPIs", "Dashboard KPIs"),
            ("Reconciliación V8", "Reconciliación V8"),
            ("Email Wilo AI", "Email Wilo AI"),
            ("Dashboard Transferencias", "Dashboard Transferencias"),
            ("Trabajadores", "Trabajadores"),
            ("Generar Guías", "Generar Guías"),
            ("Inventario", "inventario"),
            ("Reportes", "reportes")
        ]
        
        for name, key in modules:
            if st.button(f"📌 {name}", key=f"sidebar_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()
        
        st.divider()
        
        if st.button("⚙️ Configuración", use_container_width=True):
            st.session_state.current_page = "configuracion"
            st.rerun()
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.current_page = "Inicio"
            st.rerun()

# ==============================================================================
# 3. FUNCIONES AUXILIARES GLOBALES
# ==============================================================================

import unicodedata
from typing import Dict, List, Optional, Any, Union

def normalizar_texto_wilo(texto):
    """Normaliza texto para comparación"""
    if pd.isna(texto) or texto == '': 
        return ''
    texto = str(texto)
    try:
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    except: 
        pass
    texto = re.sub(r'[^A-Za-z0-9\s]', ' ', texto.upper())
    return re.sub(r'\s+', ' ', texto).strip()

def procesar_subtotal_wilo(valor):
    """Procesa valores monetarios"""
    if pd.isna(valor): 
        return 0.0
    try:
        if isinstance(valor, (int, float)): 
            return float(valor)
        valor_str = str(valor).strip()
        valor_str = re.sub(r'[^\d.,-]', '', valor_str)
        if ',' in valor_str and '.' in valor_str:
            if valor_str.rfind(',') > valor_str.rfind('.'): 
                valor_str = valor_str.replace('.', '').replace(',', '.')
            else: 
                valor_str = valor_str.replace(',', '')
        elif ',' in valor_str: 
            valor_str = valor_str.replace(',', '.')
        return float(valor_str) if valor_str else 0.0
    except: 
        return 0.0

def hash_password(pw: str) -> str:
    """Genera hash SHA256 de contraseña"""
    return hashlib.sha256(pw.encode()).hexdigest()

def validar_fecha(fecha: str) -> bool:
    """Valida formato de fecha"""
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        return True
    except ValueError: 
        return False

# ==============================================================================
# 4. SIMULACIÓN DE BASE DE DATOS LOCAL
# ==============================================================================

class LocalDatabase:
    def __init__(self):
        self.data = {
            'users': [
                {'id': 1, 'username': 'admin', 'role': 'admin', 'password_hash': hash_password('admin123')},
                {'id': 2, 'username': 'user', 'role': 'user', 'password_hash': hash_password('user123')},
                {'id': 3, 'username': 'wilson', 'role': 'admin', 'password_hash': hash_password('admin123')}
            ],
            'kpis': self._generate_kpis_data(),
            'guias': [],
            'trabajadores': [],
            'distribuciones': [
                {'id': 1, 'transporte': 'Tempo', 'guías': 45, 'estado': 'En ruta'},
                {'id': 2, 'transporte': 'Luis Perugachi', 'guías': 32, 'estado': 'Entregado'}
            ]
        }
    
    def _generate_kpis_data(self):
        """Genera datos de KPIs de ejemplo"""
        kpis = []
        today = datetime.now()
        for i in range(30):
            date = today - timedelta(days=i)
            kpis.append({
                'id': i,
                'fecha': date.strftime('%Y-%m-%d'),
                'produccion': np.random.randint(800, 1500),
                'eficiencia': np.random.uniform(85, 98),
                'alertas': np.random.randint(0, 5),
                'costos': np.random.uniform(5000, 15000)
            })
        return kpis
    
    def query(self, table, filters=None):
        """Consulta datos de una tabla"""
        if table not in self.data:
            return []
        
        results = self.data[table]
        if filters:
            for key, value in filters.items():
                results = [item for item in results if item.get(key) == value]
        return results
    
    def insert(self, table, data):
        """Inserta datos en una tabla"""
        if table not in self.data:
            self.data[table] = []
        
        if isinstance(data, dict):
            data['id'] = len(self.data[table]) + 1
            self.data[table].append(data)
        elif isinstance(data, list):
            for item in data:
                item['id'] = len(self.data[table]) + 1
                self.data[table].append(item)
        return True
    
    def authenticate(self, username, password):
        """Autentica un usuario"""
        users = self.query('users', {'username': username})
        if not users:
            return None
        
        user = users[0]
        if user['password_hash'] == hash_password(password):
            return user
        return None

# Instancia global de base de datos local
local_db = LocalDatabase()

# Variables Globales
ADMIN_PASSWORD = "admin123"
USER_PASSWORD = "user123"

# ==============================================================================
# 5. MÓDULO DASHBOARD KPIs
# ==============================================================================

def mostrar_dashboard_kpis():
    """Dashboard principal de KPIs"""
    st.markdown("""
    <div class='internal-header'>
        <h1 class='header-title'>📊 DASHBOARD DE KPIs</h1>
        <div class='header-subtitle'>Métricas en tiempo real del Centro de Distribución</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtros
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    with col_filtro1:
        fecha_inicio = st.date_input("📅 Fecha Inicio", datetime.now() - timedelta(days=30))
    with col_filtro2:
        fecha_fin = st.date_input("📅 Fecha Fin", datetime.now())
    with col_filtro3:
        departamento = st.selectbox("🏭 Departamento", ["Todos", "Logística", "Almacén", "Ventas", "Administración"])
    
    st.divider()
    
    # Métricas principales
    st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='stat-card'>
            <div class='stat-icon'>📦</div>
            <div class='stat-title'>Productividad</div>
            <div class='stat-value'>1,247</div>
            <div class='stat-change'>+12.5%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='stat-card'>
            <div class='stat-icon'>⚡</div>
            <div class='stat-title'>Eficiencia</div>
            <div class='stat-value'>94.2%</div>
            <div class='stat-change'>+0.8%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='stat-card'>
            <div class='stat-icon'>💰</div>
            <div class='stat-title'>Ingresos</div>
            <div class='stat-value'>$45,230</div>
            <div class='stat-change'>+8.3%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='stat-card'>
            <div class='stat-icon'>👥</div>
            <div class='stat-title'>Personal Activo</div>
            <div class='stat-value'>42</div>
            <div class='stat-change'>+2</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Gráficos
    col_grafico1, col_grafico2 = st.columns(2)
    
    with col_grafico1:
        # Gráfico de líneas: Productividad diaria
        fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
        productividad = np.random.normal(1000, 200, len(fechas)).cumsum()
        
        fig1 = px.line(
            x=fechas, y=productividad,
            title="📈 Productividad Diaria",
            labels={'x': 'Fecha', 'y': 'Unidades Procesadas'},
            line_shape='spline'
        )
        fig1.update_traces(line=dict(color='#60A5FA', width=3))
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_grafico2:
        # Gráfico de barras: Distribución por departamento
        departamentos = ['Logística', 'Almacén', 'Ventas', 'Administración', 'Calidad']
        valores = np.random.randint(100, 1000, len(departamentos))
        
        fig2 = px.bar(
            x=departamentos, y=valores,
            title="🏭 Productividad por Departamento",
            color=departamentos,
            color_discrete_sequence=['#60A5FA', '#8B5CF6', '#F472B6', '#34D399', '#FBBF24']
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    st.divider()
    
    # Tabla de detalle
    st.subheader("📋 Detalle de Métricas")
    
    data = {
        'Métrica': ['Productividad CD', 'Eficiencia Operativa', 'Costos Logísticos', 
                   'Tiempo Promedio', 'Exactitud Inventario', 'Satisfacción Cliente'],
        'Valor Actual': ['1,247 unidades', '94.2%', '$12,450', '2.3 horas', '98.7%', '4.8/5.0'],
        'Meta': ['1,500 unidades', '95.0%', '$10,000', '2.0 horas', '99.0%', '5.0/5.0'],
        'Tendencia': ['↗️ Mejorando', '↗️ Mejorando', '↘️ Aumentando', '↘️ Aumentando', '→ Estable', '↗️ Mejorando'],
        'Responsable': ['W. Pérez', 'L. Perugachi', 'A. Cadena', 'J. Imbacuán', 'D. García', 'J. Suárez']
    }
    
    df_metricas = pd.DataFrame(data)
    st.dataframe(df_metricas, use_container_width=True)

# ==============================================================================
# 6. MÓDULO RECONCILIACIÓN V8
# ==============================================================================

def identificar_tipo_tienda_v8(nombre):
    """
    Lógica V8.0 para clasificación de tiendas.
    Incluye regla específica para JOFRE SANTANA y manejo de Piezas.
    """
    if pd.isna(nombre) or nombre == '': 
        return "DESCONOCIDO"
    nombre_norm = normalizar_texto_wilo(nombre)
    
    # 1. Regla Específica Solicitada
    if 'JOFRE' in nombre_norm and 'SANTANA' in nombre_norm:
        return "VENTAS AL POR MAYOR"
    
    # 2. Tiendas Físicas (Patrones)
    patrones_fisicas = ['LOCAL', 'MALL', 'PLAZA', 'SHOPPING', 'CENTRO', 'COMERCIAL', 'CC', 
                       'TIENDA', 'PASEO', 'PORTAL', 'DORADO', 'CITY', 'CEIBOS', 'QUITO', 
                       'GUAYAQUIL', 'AMBATO', 'MANTA', 'MACHALA', 'RIOCENTRO', 'AEROPOSTALE']
    
    if any(p in nombre_norm for p in patrones_fisicas):
        return "TIENDA FÍSICA"
        
    # 3. Nombres Propios (Venta Web)
    palabras = nombre_norm.split()
    if len(palabras) > 0 and len(palabras) <= 3:
        return "VENTA WEB"
        
    return "TIENDA FÍSICA" # Default

def mostrar_reconciliacion_v8():
    """Módulo de reconciliación financiera"""
    st.markdown("""
    <div class='internal-header'>
        <h1 class='header-title'>💰 RECONCILIACIÓN FINANCIERA</h1>
        <div class='header-subtitle'>Conciliación de facturas y manifiestos</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📤 Cargar Archivos", "⚙️ Configurar", "📊 Resultados"])
    
    with tab1:
        st.subheader("Subir Archivos para Reconciliación")
        
        col_archivo1, col_archivo2 = st.columns(2)
        
        with col_archivo1:
            st.markdown("### 📄 Manifiesto")
            f_manifiesto = st.file_uploader(
                "Subir archivo Excel/CSV",
                type=['xlsx', 'xls', 'csv'],
                key="manifiesto_file",
                help="Archivo con columnas: Guía, Destinatario, Valor, Piezas"
            )
        
        with col_archivo2:
            st.markdown("### 🧾 Facturas")
            f_facturas = st.file_uploader(
                "Subir archivo Excel/CSV",
                type=['xlsx', 'xls', 'csv'],
                key="facturas_file",
                help="Archivo con columnas: Guía, Valor Facturado"
            )
        
        st.divider()
        
        # Opciones de procesamiento
        col_op1, col_op2, col_op3 = st.columns(3)
        
        with col_op1:
            usar_demo = st.checkbox("Usar datos de demostración", value=True)
        
        with col_op2:
            auto_clasificar = st.checkbox("Clasificación automática", value=True)
        
        with col_op3:
            generar_informes = st.checkbox("Generar informes PDF", value=True)
    
    with tab2:
        st.subheader("Configuración de Columnas")
        
        if usar_demo:
            st.info("📊 **Usando datos de demostración** - Configure las columnas para su estructura")
            
            # Datos de ejemplo para demostración
            np.random.seed(42)
            num_rows = 50
            
            # Datos de manifiesto de ejemplo
            df_m = pd.DataFrame({
                'GUIA': [f'GUA-{i:04d}' for i in range(1001, 1001 + num_rows)],
                'DESTINATARIO': np.random.choice([
                    'JOFRE SANTANA IMPORT', 
                    'MALL DEL SOL AEROPOSTALE',
                    'SAN MARINO TIENDA',
                    'CARLOS PEREZ',
                    'MARIA GONZALEZ',
                    'CENTRO COMERCIAL QUITO',
                    'PLAZA DE LAS AMERICAS'
                ], num_rows),
                'PIEZAS': np.random.randint(1, 20, num_rows),
                'VALOR_DECLARADO': np.random.uniform(50, 500, num_rows).round(2)
            })
            
            # Datos de facturas de ejemplo
            df_f = pd.DataFrame({
                'GUIA_FACTURA': [f'GUA-{i:04d}' for i in range(1001, 1001 + int(num_rows * 0.8))],
                'VALOR_COBRADO': np.random.uniform(45, 550, int(num_rows * 0.8)).round(2)
            })
            
            col_conf1, col_conf2 = st.columns(2)
            
            with col_conf1:
                st.markdown("**Manifiesto**")
                col_guia_m = st.selectbox("Columna Guía", df_m.columns.tolist(), index=0)
                col_dest_m = st.selectbox("Columna Destinatario", df_m.columns.tolist(), index=1)
                col_valor_m = st.selectbox("Columna Valor", df_m.columns.tolist(), index=3)
                col_piezas_m = st.selectbox("Columna Piezas", df_m.columns.tolist(), index=2)
            
            with col_conf2:
                st.markdown("**Facturas**")
                col_guia_f = st.selectbox("Columna Guía Factura", df_f.columns.tolist(), index=0)
                col_valor_f = st.selectbox("Columna Valor Facturado", df_f.columns.tolist(), index=1)
    
    with tab3:
        st.subheader("Resultados de la Reconciliación")
        
        if st.button("🚀 Ejecutar Reconciliación", type="primary", use_container_width=True):
            with st.spinner("🔄 Procesando datos..."):
                time.sleep(2)
                
                # Procesamiento
                df_m['GUIA_CLEAN'] = df_m[col_guia_m].astype(str).str.strip().str.upper()
                df_f['GUIA_CLEAN'] = df_f[col_guia_f].astype(str).str.strip().str.upper()
                
                # Merge
                df_final = pd.merge(df_m, df_f, on='GUIA_CLEAN', how='left', suffixes=('_MAN', '_FAC'))
                
                # Lógica V8
                df_final['DESTINATARIO_NORM'] = df_final[col_dest_m].fillna('DESCONOCIDO')
                df_final['TIPO_TIENDA'] = df_final['DESTINATARIO_NORM'].apply(identificar_tipo_tienda_v8)
                
                # Manejo de Piezas y Valores
                df_final['PIEZAS_CALC'] = pd.to_numeric(df_final[col_piezas_m], errors='coerce').fillna(1)
                df_final['VALOR_REAL'] = df_final[col_valor_f].apply(procesar_subtotal_wilo).fillna(0)
                df_final['VALOR_MANIFIESTO'] = df_final[col_valor_m].apply(procesar_subtotal_wilo).fillna(0)
                
                total_facturado = df_final['VALOR_REAL'].sum()
                total_piezas = df_final['PIEZAS_CALC'].sum()
                con_factura = df_final[df_final['VALOR_REAL'] > 0].shape[0]
                sin_factura = df_final[df_final['VALOR_REAL'] == 0].shape[0]
                
                # Métricas
                col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                
                with col_res1:
                    st.metric("Guías Procesadas", len(df_final))
                
                with col_res2:
                    porcentaje = (con_factura/len(df_final))*100 if len(df_final) > 0 else 0
                    st.metric("Conciliadas", con_factura, f"{porcentaje:.1f}%")
                
                with col_res3:
                    st.metric("Valor Total", f"${total_facturado:,.2f}")
                
                with col_res4:
                    diferencia = total_facturado - df_final['VALOR_MANIFIESTO'].sum()
                    st.metric("Diferencia", f"${diferencia:,.2f}", delta_color="inverse")
                
                st.divider()
                
                # Gráfico de conciliación
                fig = go.Figure(data=[
                    go.Bar(name='Conciliadas', x=['Resultado'], y=[con_factura], marker_color='#34D399'),
                    go.Bar(name='Pendientes', x=['Resultado'], y=[sin_factura], marker_color='#F87171')
                ])
                
                fig.update_layout(
                    title="Estado de Conciliación",
                    barmode='stack',
                    height=300,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                
                st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# 7. MÓDULO AUDITORÍA DE CORREOS
# ==============================================================================

class WiloEmailEngine:
    """Motor de análisis de correos (versión simplificada para demostración)"""
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
    
    def get_latest_news(self, limit=10):
        """Obtiene correos recientes (datos de demostración)"""
        # Datos de demostración
        return [
            {
                'fecha': '2024-01-15 09:30',
                'remitente': 'cliente@empresa.com',
                'asunto': 'Faltante en pedido #12345',
                'tipo': '📦 FALTANTE',
                'urgencia': 'ALTA',
                'pedido': '#12345'
            },
            {
                'fecha': '2024-01-15 10:15',
                'remitente': 'tienda@mall.com',
                'asunto': 'Sobrante en entrega',
                'tipo': '👔 SOBRANTE',
                'urgencia': 'MEDIA',
                'pedido': '#12346'
            },
            {
                'fecha': '2024-01-15 11:45',
                'remitente': 'soporte@aeropostale.com',
                'asunto': 'Re: Etiquetas dañadas',
                'tipo': '⚠️ DAÑO',
                'urgencia': 'ALTA',
                'pedido': '#12347'
            }
        ]

def mostrar_auditoria_correos():
    """Módulo de auditoría de correos"""
    st.markdown("""
    <div class='internal-header'>
        <h1 class='header-title'>📧 AUDITORÍA DE CORREOS</h1>
        <div class='header-subtitle'>Análisis inteligente de novedades por email</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🔐 Credenciales")
        email_user = st.text_input("Correo", "wperez@fashionclub.com.ec")
        email_pass = st.text_input("Contraseña", type="password", value="demo123")
        imap_server = "mail.fashionclub.com.ec"
    
    col_btn1, col_btn2 = st.columns([3, 1])
    
    with col_btn1:
        st.info(f"**Servidor:** {imap_server} | **Usuario:** {email_user}")
    
    with col_btn2:
        iniciar_auditoria = st.button("🔍 Iniciar Auditoría", type="primary", use_container_width=True)
    
    if iniciar_auditoria:
        with st.spinner("🔍 Analizando bandeja de entrada..."):
            time.sleep(3)
            
            # Usar el motor de correos
            engine = WiloEmailEngine(imap_server, email_user, email_pass)
            datos_auditoria = engine.get_latest_news()
            
            df_auditoria = pd.DataFrame(datos_auditoria)
            
            # Métricas
            st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
            
            col_met1, col_met2, col_met3 = st.columns(3)
            
            with col_met1:
                st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-icon'>📧</div>
                    <div class='stat-title'>Correos Analizados</div>
                    <div class='stat-value'>{len(df_auditoria)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_met2:
                altas = len(df_auditoria[df_auditoria['urgencia'] == 'ALTA'])
                st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-icon'>🚨</div>
                    <div class='stat-title'>Urgencias Altas</div>
                    <div class='stat-value'>{altas}</div>
                    <div class='stat-change {'negative' if altas > 2 else ''}'>{'Revisar' if altas > 2 else 'OK'}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_met3:
                faltantes = len(df_auditoria[df_auditoria['tipo'].str.contains('FALTANTE')])
                st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-icon'>📦</div>
                    <div class='stat-title'>Faltantes</div>
                    <div class='stat-value'>{faltantes}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # Tabla de resultados
            st.subheader("📋 Resultados del Análisis")
            st.dataframe(df_auditoria, use_container_width=True)

# ==============================================================================
# 8. MÓDULO DASHBOARD DE TRANSFERENCIAS
# ==============================================================================

def mostrar_dashboard_transferencias():
    """Dashboard de logística y transferencias"""
    st.markdown("""
    <div class='internal-header'>
        <h1 class='header-title'>📦 DASHBOARD LOGÍSTICO</h1>
        <div class='header-subtitle'>Control de transferencias y distribución</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Subir archivo de transferencias
    archivo_transferencias = st.file_uploader(
        "📂 Subir archivo de transferencias (Excel)",
        type=['xlsx'],
        key="transferencias_file"
    )
    
    if archivo_transferencias or st.checkbox("Usar datos de demostración", value=True):
        # Datos de demostración
        categorias = ['Tiendas', 'Price Club', 'Ventas Mayor', 'Tienda Web', 'Fallas', 'Fundas']
        unidades = [1250, 850, 320, 180, 75, 450]
        
        col_log1, col_log2 = st.columns([2, 1])
        
        with col_log1:
            # Gráfico de distribución
            fig = px.pie(
                values=unidades,
                names=categorias,
                title="Distribución por Categoría",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_log2:
            st.subheader("📊 Resumen")
            for cat, uni in zip(categorias, unidades):
                porcentaje = (uni/sum(unidades))*100 if sum(unidades) > 0 else 0
                st.metric(cat, f"{uni:,}", delta=f"{porcentaje:.1f}%")
        
        st.divider()
        
        # Tabla detallada
        st.subheader("📋 Detalle de Transferencias")
        
        data_detalle = {
            'Secuencial': [f'TRF-{i:04d}' for i in range(1001, 1021)],
            'Destino': ['Mall del Sol', 'Price Club', 'Ventas Mayor', 'Tienda Web'] * 5,
            'Categoría': ['Tiendas', 'Price Club', 'Ventas Mayor', 'Tienda Web'] * 5,
            'Unidades': np.random.randint(10, 500, 20),
            'Estado': ['Completada', 'En tránsito', 'Pendiente'] * 7,
            'Fecha': [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(20)]
        }
        
        df_detalle = pd.DataFrame(data_detalle)
        st.dataframe(df_detalle, use_container_width=True)

# ==============================================================================
# 9. MÓDULO GESTIÓN DE TRABAJADORES
# ==============================================================================

def mostrar_gestion_trabajadores():
    """Gestión de personal"""
    st.markdown("""
    <div class='internal-header'>
        <h1 class='header-title'>👥 GESTIÓN DE EQUIPO</h1>
        <div class='header-subtitle'>Administración del personal del Centro de Distribución</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab_equipo1, tab_equipo2, tab_equipo3 = st.tabs(["🏢 Estructura", "➕ Agregar", "📊 Estadísticas"])
    
    with tab_equipo1:
        # Estructura organizacional
        estructura = {
            'Liderazgo': ['Wilson Pérez - Jefe Logística', 'Andrés Cadena - Jefe Inventarios'],
            'Transferencias': ['César Yépez - Transferencias Fashion', 'Luis Perugachi - Pivote Price', 'Josué Imbacuán - Transferencias Tempo'],
            'Distribución': ['Jessica Suárez - Distribución Aero', 'Norma Paredes - Distribución Price', 'Jhonny Villa - Empaque'],
            'Ventas Mayor': ['Jhonny Guadalupe - Bodega Packing', 'Rocio Cadena - Picking'],
            'Calidad': ['Diana García - Reproceso']
        }
        
        for departamento, personal in estructura.items():
            with st.expander(f"📌 {departamento} ({len(personal)} personas)", expanded=True):
                for persona in personal:
                    st.write(f"• {persona}")
    
    with tab_equipo2:
        # Formulario para agregar personal
        with st.form("form_personal"):
            col_per1, col_per2 = st.columns(2)
            
            with col_per1:
                nombre = st.text_input("Nombre completo")
                cargo = st.selectbox("Cargo", ["Operador", "Supervisor", "Coordinador", "Gerente"])
            
            with col_per2:
                departamento = st.selectbox("Departamento", ["Logística", "Almacén", "Ventas", "Administración"])
                fecha_ingreso = st.date_input("Fecha de ingreso")
            
            if st.form_submit_button("➕ Agregar Personal", type="primary"):
                st.success(f"✅ {nombre} agregado al equipo")
    
    with tab_equipo3:
        # Estadísticas del equipo
        col_est1, col_est2, col_est3 = st.columns(3)
        
        with col_est1:
            st.metric("Total Personal", "42")
        
        with col_est2:
            st.metric("Activos", "40", "+2")
        
        with col_est3:
            st.metric("Rotación", "4.8%", "-0.5%")

# ==============================================================================
# 10. MÓDULO GENERACIÓN DE GUÍAS
# ==============================================================================

def mostrar_generacion_guias():
    """Generador de guías de envío"""
    st.markdown("""
    <div class='internal-header'>
        <h1 class='header-title'>🚚 GENERADOR DE GUÍAS</h1>
        <div class='header-subtitle'>Sistema de envíos con seguimiento QR</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_guia"):
        col_guia1, col_guia2 = st.columns(2)
        
        with col_guia1:
            st.subheader("🏢 Información Remitente")
            remitente = st.selectbox("Remitente", ["Wilson Pérez", "Luis Perugachi", "Andrés Cadena"])
            marca = st.radio("Marca", ["Fashion Club", "Tempo"], horizontal=True)
        
        with col_guia2:
            st.subheader("🏪 Información Destinatario")
            destinatario = st.text_input("Nombre destinatario")
            telefono = st.text_input("Teléfono")
            direccion = st.text_area("Dirección completa")
        
        col_guia3, col_guia4 = st.columns(2)
        
        with col_guia3:
            tienda_destino = st.selectbox("Tienda destino", ["Mall del Sol", "Price Club", "Tienda Web", "Ventas Mayor"])
        
        with col_guia4:
            url_seguimiento = st.text_input("URL seguimiento", "https://aeropostale.com.ec/seguimiento/")
        
        generar = st.form_submit_button("📄 Generar Guía PDF", type="primary")
    
    if generar:
        with st.spinner("🔄 Generando guía..."):
            time.sleep(2)
            
            st.success("✅ Guía generada exitosamente")
            
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.markdown("### 📋 Resumen de Guía")
                st.write(f"**Número:** GFC-{np.random.randint(1000, 9999)}")
                st.write(f"**Remitente:** {remitente}")
                st.write(f"**Destinatario:** {destinatario}")
                st.write(f"**Tienda:** {tienda_destino}")
            
            with col_res2:
                st.markdown("### 📍 Información de Envío")
                st.write(f"**Dirección:** {direccion}")
                st.write(f"**Teléfono:** {telefono}")
                st.write(f"**Seguimiento:** {url_seguimiento}")

# ==============================================================================
# 11. MÓDULOS ADICIONALES
# ==============================================================================

def mostrar_inventario():
    """Control de inventario"""
    st.markdown("""
    <div class='internal-header'>
        <h1 class='header-title'>📋 CONTROL DE INVENTARIO</h1>
        <div class='header-subtitle'>Gestión de stock en tiempo real</div>
    </div>
    """, unsafe_allow_html=True)
    st.info("Módulo en desarrollo...")

def mostrar_reportes():
    """Generador de reportes"""
    st.markdown("""
    <div class='internal-header'>
        <h1 class='header-title'>📈 REPORTES AVANZADOS</h1>
        <div class='header-subtitle'>Análisis y estadísticas ejecutivas</div>
    </div>
    """, unsafe_allow_html=True)
    st.info("Módulo en desarrollo...")

def mostrar_configuracion():
    """Configuración del sistema"""
    st.markdown("""
    <div class='internal-header'>
        <h1 class='header-title'>⚙️ CONFIGURACIÓN</h1>
        <div class='header-subtitle'>Personalización del sistema ERP</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab_conf1, tab_conf2, tab_conf3 = st.tabs(["General", "Usuarios", "Seguridad"])
    
    with tab_conf1:
        st.subheader("Configuración General")
        empresa = st.text_input("Nombre Empresa", "AEROPOSTALE Ecuador")
        moneda = st.selectbox("Moneda", ["USD", "EUR", "PEN"])
        idioma = st.selectbox("Idioma", ["Español", "Inglés"])
        
        if st.button("💾 Guardar Configuración", type="primary"):
            st.success("✅ Configuración guardada")
    
    with tab_conf2:
        st.subheader("Gestión de Usuarios")
        st.info("Funcionalidad en desarrollo...")
    
    with tab_conf3:
        st.subheader("Seguridad del Sistema")
        st.info("Funcionalidad en desarrollo...")

# ==============================================================================
# 12. NAVEGACIÓN PRINCIPAL
# ==============================================================================

def mostrar_pantalla_inicio():
    """Página de inicio principal"""
    st.markdown("""
    <div class="gallery-container">
        <div class="brand-title">AEROPOSTALE</div>
        <div class="brand-subtitle">Centro de Distribución Ecuador | ERP </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Grid de módulos
    st.markdown('<div class="modules-grid">', unsafe_allow_html=True)
    
    # Definir módulos con sus propiedades
    modulos = [
        ("📊", "Dashboard KPIs", "Dashboard en tiempo real", "Dashboard KPIs"),
        ("💰", "Reconciliación V8", "Reconciliación financiera", "Reconciliación V8"),
        ("📧", "Email Wilo AI", "Auditoría de correos", "Email Wilo AI"),
        ("📦", "Dashboard Transferencias", "Logística y transferencias", "Dashboard Transferencias"),
        ("👥", "Trabajadores", "Gestión de personal", "Trabajadores"),
        ("🚚", "Generar Guías", "Generar guías con QR", "Generar Guías"),
        ("📋", "Inventario", "Control de stock", "inventario"),
        ("📈", "Reportes", "Análisis ejecutivo", "reportes"),
        ("⚙️", "Configuración", "Sistema y preferencias", "configuracion")
    ]
    
    # Crear 3 columnas
    cols = st.columns(3)
    
    for idx, (icon, title, desc, key) in enumerate(modulos):
        with cols[idx % 3]:
            create_card(icon, title, desc, key)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="app-footer">
        <p>Sistema ERP • Desarrollado por Wilson Pérez • Logística & Sistemas</p>
        <p style="font-size: 0.8rem; color: #64748B; margin-top: 10px;">
            © 2026 AEROPOSTALE Ecuador • Todos los derechos reservados
        </p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Función principal de la aplicación"""
    # Inicializar estado de sesión
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Inicio"
    
    # Mostrar sidebar solo si no estamos en la página de inicio
    if st.session_state.current_page != "Inicio":
        show_sidebar()
    
    # Navegación entre páginas
    if st.session_state.current_page == "Inicio":
        mostrar_pantalla_inicio()
    elif st.session_state.current_page == "Dashboard KPIs":
        mostrar_dashboard_kpis()
    elif st.session_state.current_page == "Reconciliación V8":
        mostrar_reconciliacion_v8()
    elif st.session_state.current_page == "Email Wilo AI":
        mostrar_auditoria_correos()
    elif st.session_state.current_page == "Dashboard Transferencias":
        mostrar_dashboard_transferencias()
    elif st.session_state.current_page == "Trabajadores":
        mostrar_gestion_trabajadores()
    elif st.session_state.current_page == "Generar Guías":
        mostrar_generacion_guias()
    elif st.session_state.current_page == "inventario":
        mostrar_inventario()
    elif st.session_state.current_page == "reportes":
        mostrar_reportes()
    elif st.session_state.current_page == "configuracion":
        mostrar_configuracion()
    else:
        st.error("Página no encontrada")
        st.session_state.current_page = "Inicio"
        st.rerun()
    
    # Botón flotante para volver al inicio
    if st.session_state.current_page != "Inicio":
        st.markdown("""
        <style>
        .stButton > button {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 100;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("🏠", help="Volver al inicio", key="floating_home"):
            st.session_state.current_page = "Inicio"
            st.rerun()

if __name__ == "__main__":
    main()
