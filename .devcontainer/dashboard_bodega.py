import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, date
import time
import sqlite3
import json
import os
import hashlib
from pathlib import Path
import warnings
from scipy import stats
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.impute import SimpleImputer
from contextlib import contextmanager
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
warnings.filterwarnings('ignore')

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración de página
st.set_page_config(
    layout="wide",
    page_title="Sistema de KPIs - Equipo de Distribución",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# CSS personalizado mejorado
st.markdown("""
<style>
    .main { background-color: cool black; }
    .stApp { background-color: cool black; }
    .kpi-card {
        background: deepskyblue;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        padding: 18px;
        margin: 10px 0;
        border-left: 4px solid #2c3e50;
        transition: all 0.3s ease;
    }
    .kpi-card:hover { 
        box-shadow: 0 6px 16px rgba(0,0,0,0.12); 
        transform: translateY(-3px); 
    }
    .metric-value { 
        font-size: 2.8em !important; 
        font-weight: bold; 
        color: #2c3e50;
        line-height: 1.2;
    }
    .worker-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        color: #2c3e50;
        margin: 8px;
        min-height: 250px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #3498db;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .worker-header { 
        font-size: 1.3em; 
        margin-bottom: 10px; 
        color: #000000;
        font-weight: bold;
    }
    .worker-metric { 
        font-size: 1.1em; 
        margin: 5px 0; 
        color: #2c3e50;
    }
    .trend-up { color: #27ae60; }
    .trend-down { color: #e74c3c; }
    .header-title { 
        color: #000000;
        font-weight: 800;
        font-size: 2.5em;
        margin-bottom: 20px;
    }
    .section-title {
        border-left: 5px solid #3498db;
        padding-left: 10px;
        margin: 20px 0;
        color: #000000;
        font-size: 1.8em;
    }
    .comment-container {
        margin-top: 15px;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 5px;
        border-left: 3px solid #3498db;
    }
    .comment-title {
        font-weight: bold;
        margin-bottom: 5px;
        color: #2c3e50;
    }
    .comment-content {
        font-size: 0.9em;
        color: #2c3e50;
    }
    .metric-label {
        color: #2c3e50;
        font-size: 0.9em;
    }
    .password-container {
        background-color: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        max-width: 400px;
        margin: 100px auto;
    }
    .stats-container {
        flex-grow: 1;
    }
    .date-selector {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #17a2b8;
        margin: 10px 0;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #2980b9;
        color: white;
    }
    .stSelectbox, .stDateInput, .stNumberInput, .stTextArea {
        margin-bottom: 15px;
    }
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .jar-progress {
        background: #f0f0f0;
        border-radius: 20px;
        height: 30px;
        margin: 15px 0;
        overflow: hidden;
    }
    .jar-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        border-radius: 20px;
        transition: width 0.5s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    }
    .team-section {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .team-header {
        font-size: 1.5em;
        color: #2c3e50;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

# Clase Singleton para manejo de base de datos
class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.conn = None
        self.setup_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager para manejar conexiones a la base de datos"""
        try:
            if self.conn is None:
                self.conn = sqlite3.connect('kpi_data.db', check_same_thread=False)
                self.conn.row_factory = sqlite3.Row
            yield self.conn
        except sqlite3.Error as e:
            logger.error(f"Error de base de datos: {e}")
            raise
        finally:
            # No cerramos la conexión para mantenerla en el estado de la sesión
            pass
    
    def setup_database(self):
        """Configura la base de datos SQLite"""
        try:
            with self.get_connection() as conn:
                c = conn.cursor()
                
                # Crear tabla de datos diarios
                c.execute('''
                CREATE TABLE IF NOT EXISTS daily_kpis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL,
                    nombre TEXT NOT NULL,
                    actividad TEXT NOT NULL,
                    cantidad REAL NOT NULL,
                    meta REAL NOT NULL,
                    eficiencia REAL NOT NULL,
                    productividad REAL NOT NULL,
                    comentario TEXT,
                    meta_mensual REAL,
                    horas_trabajo REAL,
                    equipo TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(fecha, nombre)
                )
                ''')
                
                # Verificar si la columna 'equipo' existe y agregarla si no existe
                try:
                    c.execute("SELECT equipo FROM daily_kpis LIMIT 1")
                except sqlite3.OperationalError:
                    c.execute('ALTER TABLE daily_kpis ADD COLUMN equipo TEXT')
                
                # Crear tabla de configuración
                c.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                ''')
                
                # Crear tabla de usuarios
                c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # Crear tabla de trabajadores
                c.execute('''
                CREATE TABLE IF NOT EXISTS trabajadores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    equipo TEXT NOT NULL,
                    activo BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # Insertar usuario admin por defecto si no existe
                password_hash = hashlib.sha256("Wilo3161".encode()).hexdigest()
                c.execute('''
                INSERT OR IGNORE INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
                ''', ('admin', password_hash, 'admin'))
                
                # Insertar trabajadores por defecto si no existen
                trabajadores_default = [
                    ("Andrés Yépez", "Transferencias"),
                    ("Josué Imbacuán", "Transferencias"),
                    ("Luis Perugachi", "Transferencias"),
                    ("Diana García", "Arreglo"),
                    ("Simón Vera", "Guías"),
                    ("Jhonny Guadalupe", "Ventas"),
                    ("Victor Montenegro", "Ventas"),
                    ("Fernando Quishpe", "Ventas")
                ]
                
                for nombre, equipo in trabajadores_default:
                    c.execute('''
                    INSERT OR IGNORE INTO trabajadores (nombre, equipo)
                    VALUES (?, ?)
                    ''', (nombre, equipo))
                
                conn.commit()
                logger.info("Base de datos configurada correctamente")
                
        except sqlite3.Error as e:
            logger.error(f"Error al configurar la base de datos: {e}")
            raise

# Inicializar el gestor de base de datos
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

# Funciones de utilidad
def validar_fecha(fecha: str) -> bool:
    """Valida que una fecha tenga el formato correcto"""
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validar_numero_positivo(valor: Any) -> bool:
    """Valida que un valor sea un número positivo"""
    try:
        num = float(valor)
        return num >= 0
    except (ValueError, TypeError):
        return False

# Funciones de cálculo de KPIs
def calcular_kpi(cantidad: float, meta: float) -> float:
    """Calcula el porcentaje de KPI general"""
    return (cantidad / meta) * 100 if meta > 0 else 0

def kpi_transferencias(transferidas: float, meta: float = 1750) -> float:
    """Calcula el KPI para transferencias"""
    return calcular_kpi(transferidas, meta)

def kpi_arreglos(arregladas: float, meta: float = 150) -> float:
    """Calcula el KPI para arreglos"""
    return calcular_kpi(arregladas, meta)

def kpi_distribucion(distribuidas: float, recibidas: float) -> float:
    """Calcula el KPI para distribución"""
    return calcular_kpi(distribuidas, recibidas)

def kpi_guias(guias: float, meta: float = 120) -> float:
    """Calcula el KPI para guías"""
    return calcular_kpi(guias, meta)

def productividad_hora(cantidad: float, horas_trabajo: float) -> float:
    """Calcula la productividad por hora"""
    return cantidad / horas_trabajo if horas_trabajo > 0 else 0

# Funciones de acceso a datos
def obtener_trabajadores() -> pd.DataFrame:
    """Obtiene la lista de trabajadores desde la base de datos"""
    try:
        with st.session_state.db_manager.get_connection() as conn:
            df = pd.read_sql_query('SELECT nombre, equipo FROM trabajadores WHERE activo = 1 ORDER BY equipo, nombre', conn)
            return df
    except Exception as e:
        logger.error(f"Error al obtener trabajadores: {e}")
        # Si hay error, devolver lista por defecto
        return pd.DataFrame({
            'nombre': ["Andrés Yépez", "Josué Imbacuán", "Luis Perugachi", "Diana García", 
                      "Simón Vera", "Jhonny Guadalupe", "Victor Montenegro", "Fernando Quishpe"],
            'equipo': ["Transferencias", "Transferencias", "Transferencias", "Arreglo", 
                      "Guías", "Ventas", "Ventas", "Ventas"]
        })

def obtener_equipos() -> List[str]:
    """Obtiene la lista de equipos desde la base de datos"""
    try:
        with st.session_state.db_manager.get_connection() as conn:
            df = pd.read_sql_query('SELECT DISTINCT equipo FROM trabajadores WHERE activo = 1 ORDER BY equipo', conn)
            return df['equipo'].tolist()
    except Exception as e:
        logger.error(f"Error al obtener equipos: {e}")
        return ["Transferencias", "Arreglo", "Distribución", "Guías", "Ventas"]

def guardar_datos_db(fecha: str, datos: Dict[str, Dict]) -> bool:
    """Guarda los datos en la base de datos SQLite"""
    try:
        with st.session_state.db_manager.get_connection() as conn:
            c = conn.cursor()
            
            for nombre, info in datos.items():
                # Validar datos antes de guardar
                if not all([
                    validar_fecha(fecha),
                    validar_numero_positivo(info.get("cantidad", 0)),
                    validar_numero_positivo(info.get("meta", 0)),
                    validar_numero_positivo(info.get("horas_trabajo", 0))
                ]):
                    logger.warning(f"Datos inválidos para {nombre}, omitiendo guardado")
                    continue
                
                # Verificar si ya existe un registro para esta fecha y trabajador
                c.execute('SELECT id FROM daily_kpis WHERE fecha = ? AND nombre = ?', (fecha, nombre))
                existing = c.fetchone()
                
                if existing:
                    # Actualizar registro existente
                    c.execute('''
                    UPDATE daily_kpis 
                    SET actividad=?, cantidad=?, meta=?, eficiencia=?, 
                        productividad=?, comentario=?, meta_mensual=?, horas_trabajo=?, equipo=?
                    WHERE fecha=? AND nombre=?
                    ''', (
                        info.get("actividad", ""),
                        info.get("cantidad", 0),
                        info.get("meta", 0),
                        info.get("eficiencia", 0),
                        info.get("productividad", 0),
                        info.get("comentario", ""),
                        info.get("meta_mensual", 0),
                        info.get("horas_trabajo", 0),
                        info.get("equipo", ""),
                        fecha,
                        nombre
                    ))
                else:
                    # Insertar nuevo registro
                    c.execute('''
                    INSERT INTO daily_kpis 
                    (fecha, nombre, actividad, cantidad, meta, eficiencia, productividad, comentario, meta_mensual, horas_trabajo, equipo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        fecha,
                        nombre,
                        info.get("actividad", ""),
                        info.get("cantidad", 0),
                        info.get("meta", 0),
                        info.get("eficiencia", 0),
                        info.get("productividad", 0),
                        info.get("comentario", ""),
                        info.get("meta_mensual", 0),
                        info.get("horas_trabajo", 0),
                        info.get("equipo", "")
                    ))
            
            conn.commit()
            
            # Crear backup después de guardar
            crear_backup()
            
            # Limpiar caché de datos históricos
            if 'historico_data' in st.session_state:
                del st.session_state['historico_data']
                
            logger.info(f"Datos guardados correctamente para la fecha {fecha}")
            return True
            
    except Exception as e:
        logger.error(f"Error al guardar datos: {e}")
        return False

def cargar_historico_db(fecha_inicio: Optional[str] = None, 
                       fecha_fin: Optional[str] = None, 
                       trabajador: Optional[str] = None) -> pd.DataFrame:
    """Carga datos históricos desde la base de datos"""
    try:
        with st.session_state.db_manager.get_connection() as conn:
            query = '''
            SELECT fecha, nombre, actividad, cantidad, meta, eficiencia, productividad, 
                   comentario, meta_mensual, horas_trabajo, equipo
            FROM daily_kpis
            WHERE 1=1
            '''
            params = []
            
            if fecha_inicio:
                query += ' AND fecha >= ?'
                params.append(fecha_inicio)
            
            if fecha_fin:
                query += ' AND fecha <= ?'
                params.append(fecha_fin)
            
            if trabajador:
                query += ' AND nombre = ?'
                params.append(trabajador)
            
            query += ' ORDER BY fecha DESC, nombre'
            
            df = pd.read_sql_query(query, conn, params=params)
            
            if not df.empty:
                # Convertir fecha a datetime
                df['fecha'] = pd.to_datetime(df['fecha'])
                
                # Calcular columnas adicionales
                df['cumplimiento_meta'] = np.where(df['cantidad'] >= df['meta'], 'Sí', 'No')
                df['diferencia_meta'] = df['cantidad'] - df['meta']
                
            return df
            
    except Exception as e:
        logger.error(f"Error al cargar datos históricos: {e}")
        return pd.DataFrame()

def crear_backup() -> bool:
    """Crea una copia de seguridad de la base de datos"""
    try:
        # Crear directorio de backups si no existe
        Path("backups").mkdir(exist_ok=True)
        
        # Nombre del archivo de backup con fecha y hora
        backup_name = f"backups/kpi_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        # Copiar la base de datos
        with open('kpi_data.db', 'rb') as original:
            with open(backup_name, 'wb') as backup:
                backup.write(original.read())
                
        # Mantener solo los últimos 7 backups
        backups = sorted(Path("backups").glob("kpi_backup_*.db"), key=os.path.getmtime)
        for old_backup in backups[:-7]:
            try:
                old_backup.unlink()
            except Exception as e:
                logger.warning(f"No se pudo eliminar el backup antiguo {old_backup}: {e}")
                
        logger.info(f"Backup creado: {backup_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error al crear backup: {e}")
        return False

def restaurar_backup(backup_path: str) -> bool:
    """Restaura la base de datos desde un backup"""
    try:
        # Cerrar conexión actual si existe
        if hasattr(st.session_state.db_manager, 'conn') and st.session_state.db_manager.conn:
            st.session_state.db_manager.conn.close()
            st.session_state.db_manager.conn = None
        
        # Copiar el backup sobre la base de datos actual
        with open(backup_path, 'rb') as backup:
            with open('kpi_data.db', 'wb') as original:
                original.write(backup.read())
        
        # Reestablecer conexión
        st.session_state.db_manager = DatabaseManager()
        
        # Limpiar datos en caché
        if 'historico_data' in st.session_state:
            del st.session_state['historico_data']
            
        logger.info(f"Backup restaurado desde: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error al restaurar backup: {e}")
        return False

# Funciones de autenticación
def verificar_password() -> bool:
    """Verifica la contraseña del usuario"""
    if 'password_correct' not in st.session_state:
        st.session_state.password_correct = False
    
    if not st.session_state.password_correct:
        st.markdown("<div class='password-container'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: black;'>🔐 Acceso Restringido</h2>", unsafe_allow_html=True)
        password = st.text_input("Ingrese la contraseña:", type="password", key="password_input")
        
        if password:
            # Verificar contraseña usando hash
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            try:
                with st.session_state.db_manager.get_connection() as conn:
                    c = conn.cursor()
                    c.execute('SELECT username, role FROM users WHERE password_hash = ?', (password_hash,))
                    user = c.fetchone()
                    
                    if user:
                        st.session_state.password_correct = True
                        st.session_state.user = user[0]
                        st.session_state.role = user[1]
                        st.markdown("<div class='success-box'>✅ Contraseña correcta</div>", unsafe_allow_html=True)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.markdown("<div class='error-box'>❌ Contraseña incorrecta</div>", unsafe_allow_html=True)
            except Exception as e:
                logger.error(f"Error en verificación de contraseña: {e}")
                st.markdown("<div class='error-box'>❌ Error del sistema</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return False
    return True

# Funciones de visualización
def crear_grafico_interactivo(data: pd.DataFrame, x: str, y: str, title: str, 
                             xlabel: str, ylabel: str, tipo: str = 'bar') -> go.Figure:
    """Crea gráficos interactivos con Plotly"""
    try:
        if tipo == 'bar':
            fig = px.bar(data, x=x, y=y, title=title, labels={x: xlabel, y: ylabel})
        elif tipo == 'line':
            fig = px.line(data, x=x, y=y, title=title, labels={x: xlabel, y: ylabel})
        elif tipo == 'scatter':
            fig = px.scatter(data, x=x, y=y, title=title, labels={x: xlabel, y: ylabel})
        elif tipo == 'box':
            fig = px.box(data, x=x, y=y, title=title, labels={x: xlabel, y: ylabel})
        else:
            fig = px.bar(data, x=x, y=y, title=title, labels={x: xlabel, y: ylabel})
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#d6dfe9"),
            title_font_color="white"
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error al crear gráfico: {e}")
        # Devolver figura vacía en caso de error
        return go.Figure()

def crear_grafico_frasco(porcentaje: float, titulo: str) -> go.Figure:
    """Crea un gráfico de frasco de agua para mostrar el porcentaje de cumplimiento"""
    try:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = porcentaje,
            number = {'suffix': '%'},
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': titulo},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "gold"},
                'steps': [
                    {'range': [0, 50], 'color': "darkred"},
                    {'range': [50, 75], 'color': "darkorange"},
                    {'range': [75, 100], 'color': "forestgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error al crear gráfico de frasco: {e}")
        return go.Figure()

# Funciones de análisis
def analizar_tendencias(df: pd.DataFrame, metric: str) -> Union[Dict[str, Any], str]:
    """Analiza tendencias en los datos"""
    if df.empty or len(df) < 2:
        return "No hay suficientes datos para analizar tendencias"
    
    try:
        # Calcular media móvil
        df['media_movil'] = df[metric].rolling(window=7, min_periods=1).mean()
        
        # Calcular tendencia (regresión lineal simple)
        x = np.arange(len(df))
        y = df[metric].values
        coeficientes = np.polyfit(x, y, 1)
        tendencia = coeficientes[0] * x + coeficientes[1]
        
        # Determinar dirección de la tendencia
        if coeficientes[0] > 0.5:  # Umbral más alto para evitar fluctuaciones pequeñas
            direccion = "↑ Ascendente significativa"
        elif coeficientes[0] > 0:
            direccion = "↑ Ligeramente ascendente"
        elif coeficientes[0] < -0.5:
            direccion = "↓ Descendente significativa"
        elif coeficientes[0] < 0:
            direccion = "↓ Ligeramente descendente"
        else:
            direccion = "→ Estable"
        
        return {
            'tendencia': tendencia,
            'direccion': direccion,
            'pendiente': coeficientes[0],
            'r_cuadrado': np.corrcoef(x, y)[0, 1]**2
        }
    except Exception as e:
        logger.error(f"Error en análisis de tendencias: {e}")
        return "Error al analizar tendencias"

def predecir_valores_futuros(df: pd.DataFrame, columna: str, dias: int = 7) -> Optional[np.ndarray]:
    """Predice valores futuros usando regresión con validación"""
    if len(df) < 5:  # Mínimo de datos para predicción
        return None
    
    try:
        # Preparar datos
        X = np.arange(len(df)).reshape(-1, 1)
        y = df[columna].values
        
        # Dividir en train y test para validación
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Probar múltiples modelos
        modelos = {
            'Lineal': LinearRegression(),
            'Ridge': Ridge(alpha=1.0),
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        
        mejor_modelo = None
        mejor_mae = float('inf')
        
        for nombre, modelo in modelos.items():
            modelo.fit(X_train, y_train)
            predicciones = modelo.predict(X_test)
            mae = mean_absolute_error(y_test, predicciones)
            
            if mae < mejor_mae:
                mejor_mae = mae
                mejor_modelo = modelo
        
        # Predecir valores futuros con el mejor modelo
        X_futuro = np.arange(len(df), len(df) + dias).reshape(-1, 1)
        predicciones = mejor_modelo.predict(X_futuro)
        
        return predicciones
        
    except Exception as e:
        logger.error(f"Error en predicción: {e}")
        return None

def calcular_estadisticas_avanzadas(df: pd.DataFrame, columna: str) -> Dict[str, Any]:
    """Calcula estadísticas avanzadas para una columna"""
    if df.empty:
        return {}
    
    try:
        valores = df[columna].dropna()
        if len(valores) == 0:
            return {}
        
        return {
            'media': np.mean(valores),
            'mediana': np.median(valores),
            'desviacion_estandar': np.std(valores),
            'percentil_25': np.percentile(valores, 25),
            'percentil_75': np.percentile(valores, 75),
            'rango': np.ptp(valores),
            'asimetria': stats.skew(valores),
            'curtosis': stats.kurtosis(valores),
            'count': len(valores),
            'min': np.min(valores),
            'max': np.max(valores)
        }
    except Exception as e:
        logger.error(f"Error al calcular estadísticas: {e}")
        return {}

# Funciones principales de la aplicación
def mostrar_gestion_trabajadores():
    """Muestra la interfaz de gestión de trabajadores"""
    st.markdown("<h1 class='header-title'>👥 Gestión de Trabajadores</h1>", unsafe_allow_html=True)
    
    try:
        with st.session_state.db_manager.get_connection() as conn:
            c = conn.cursor()
            
            # Obtener lista actual de trabajadores
            c.execute('SELECT nombre, equipo, activo FROM trabajadores ORDER BY equipo, nombre')
            trabajadores = c.fetchall()
            
            st.markdown("<h2 class='section-title'>Trabajadores Actuales</h2>", unsafe_allow_html=True)
            
            if trabajadores:
                df_trabajadores = pd.DataFrame(trabajadores, columns=['Nombre', 'Equipo', 'Activo'])
                st.dataframe(df_trabajadores, use_container_width=True)
            else:
                st.info("No hay trabajadores registrados.")
            
            st.markdown("<h2 class='section-title'>Agregar Nuevo Trabajador</h2>", unsafe_allow_html=True)
            
            with st.form("form_nuevo_trabajador"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nuevo_nombre = st.text_input("Nombre del trabajador:")
                
                with col2:
                    equipos = obtener_equipos()
                    nuevo_equipo = st.selectbox("Equipo:", options=equipos)
                
                submitted = st.form_submit_button("Agregar Trabajador")
                
                if submitted:
                    if nuevo_nombre:
                        try:
                            c.execute('INSERT INTO trabajadores (nombre, equipo) VALUES (?, ?)', 
                                     (nuevo_nombre, nuevo_equipo))
                            conn.commit()
                            st.markdown("<div class='success-box'>✅ Trabajador agregado correctamente.</div>", unsafe_allow_html=True)
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.markdown("<div class='error-box'>❌ El trabajador ya existe.</div>", unsafe_allow_html=True)
                        except Exception as e:
                            logger.error(f"Error al agregar trabajador: {e}")
                            st.markdown("<div class='error-box'>❌ Error al agregar trabajador.</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='error-box'>❌ Debe ingresar un nombre.</div>", unsafe_allow_html=True)
            
            st.markdown("<h2 class='section-title'>Eliminar Trabajador</h2>", unsafe_allow_html=True)
            
            if trabajadores:
                trabajadores_activos = [t[0] for t in trabajadores if t[2]]
                
                if trabajadores_activos:
                    trabajador_eliminar = st.selectbox("Selecciona un trabajador para eliminar:", options=trabajadores_activos)
                    
                    if st.button("Eliminar Trabajador"):
                        try:
                            c.execute('UPDATE trabajadores SET activo = 0 WHERE nombre = ?', (trabajador_eliminar,))
                            conn.commit()
                            st.markdown("<div class='success-box'>✅ Trabajador eliminado correctamente.</div>", unsafe_allow_html=True)
                            st.rerun()
                        except Exception as e:
                            logger.error(f"Error al eliminar trabajador: {e}")
                            st.markdown("<div class='error-box'>❌ Error al eliminar trabajador.</div>", unsafe_allow_html=True)
                else:
                    st.info("No hay trabajadores activos para eliminar.")
            else:
                st.info("No hay trabajadores registrados.")
                
    except Exception as e:
        logger.error(f"Error en gestión de trabajadores: {e}")
        st.markdown("<div class='error-box'>❌ Error del sistema al gestionar trabajadores.</div>", unsafe_allow_html=True)

def ingresar_datos():
    """Muestra la interfaz para ingresar datos de KPIs"""
    st.markdown("<h1 class='header-title'>📥 Ingreso de Datos de KPIs</h1>", unsafe_allow_html=True)
    
    # Obtener trabajadores desde la base de datos
    df_trabajadores = obtener_trabajadores()
    trabajadores_por_equipo = {}
    
    for _, row in df_trabajadores.iterrows():
        equipo = row['equipo']
        if equipo not in trabajadores_por_equipo:
            trabajadores_por_equipo[equipo] = []
        trabajadores_por_equipo[equipo].append(row['nombre'])
    
    # Selector de fecha
    col_fecha, _ = st.columns([1, 2])
    with col_fecha:
        fecha_seleccionada = st.date_input(
            "Selecciona la fecha:",
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    periodo = st.radio("Selecciona el período:", ["Día", "Semana"], horizontal=True)
    
    # Inicializar variables de sesión para almacenar datos
    if 'datos_calculados' not in st.session_state:
        st.session_state.datos_calculados = None
    if 'fecha_guardar' not in st.session_state:
        st.session_state.fecha_guardar = None
    
    with st.form("form_datos"):
        # Meta mensual única para transferencias
        st.markdown("<h3 class='section-title'>Meta Mensual de Transferencias</h3>", unsafe_allow_html=True)
        meta_mensual_transferencias = st.number_input("Meta mensual para el equipo de transferencias:", min_value=0, value=150000, key="meta_mensual_transferencias")
        
        for equipo, miembros in trabajadores_por_equipo.items():
            st.markdown(f"<div class='team-section'><div class='team-header'>{equipo}</div></div>", unsafe_allow_html=True)
            
            for trabajador in miembros:
                st.subheader(trabajador)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if equipo == "Transferencias":
                        cantidad = st.number_input(f"Prendas transferidas por {trabajador}:", min_value=0, value=1800, key=f"{trabajador}_cantidad")
                        meta = st.number_input(f"Meta diaria para {trabajador}:", min_value=0, value=1750, key=f"{trabajador}_meta")
                    elif equipo == "Arreglo":
                        cantidad = st.number_input(f"Prendas arregladas por {trabajador}:", min_value=0, value=130, key=f"{trabajador}_cantidad")
                        meta = st.number_input(f"Meta diaria para {trabajador}:", min_value=0, value=150, key=f"{trabajador}_meta")
                    elif equipo == "Guías":
                        cantidad = st.number_input(f"Guías realizadas por {trabajador}:", min_value=0, value=110, key=f"{trabajador}_cantidad")
                        meta = st.number_input(f"Meta diaria para {trabajador}:", min_value=0, value=120, key=f"{trabajador}_meta")
                    elif equipo == "Ventas":
                        cantidad = st.number_input(f"Pedidos preparados por {trabajador}:", min_value=0, value=45, key=f"{trabajador}_cantidad")
                        meta = st.number_input(f"Meta diaria para {trabajador}:", min_value=0, value=40, key=f"{trabajador}_meta")
                    else:
                        cantidad = st.number_input(f"Cantidad realizada por {trabajador}:", min_value=0, value=100, key=f"{trabajador}_cantidad")
                        meta = st.number_input(f"Meta diaria para {trabajador}:", min_value=0, value=100, key=f"{trabajador}_meta")
                
                with col2:
                    horas = st.number_input(f"Horas trabajadas por {trabajador}:", min_value=0.0, value=8.0, key=f"{trabajador}_horas", step=0.5)
                    comentario = st.text_area(f"Comentario para {trabajador}:", key=f"{trabajador}_comentario")
        
        submitted = st.form_submit_button("Calcular KPIs")
        
        if submitted:
            datos_guardar = {}
            
            for equipo, miembros in trabajadores_por_equipo.items():
                for trabajador in miembros:
                    # Obtener valores del formulario
                    cantidad = st.session_state.get(f"{trabajador}_cantidad", 0)
                    meta = st.session_state.get(f"{trabajador}_meta", 0)
                    horas = st.session_state.get(f"{trabajador}_horas", 0)
                    comentario = st.session_state.get(f"{trabajador}_comentario", "")
                    
                    # Validar datos
                    if not all([validar_numero_positivo(cantidad), validar_numero_positivo(meta), validar_numero_positivo(horas)]):
                        st.markdown(f"<div class='error-box'>❌ Datos inválidos para {trabajador}. Verifique los valores ingresados.</div>", unsafe_allow_html=True)
                        continue
                    
                    # Calcular KPIs según el equipo
                    if equipo == "Transferencias":
                        eficiencia = kpi_transferencias(cantidad, meta)
                        actividad = "Transferencias"
                        meta_mensual = meta_mensual_transferencias
                    elif equipo == "Arreglo":
                        eficiencia = kpi_arreglos(cantidad, meta)
                        actividad = "Arreglos"
                        meta_mensual = 0
                    elif equipo == "Guías":
                        eficiencia = kpi_guias(cantidad, meta)
                        actividad = "Guías"
                        meta_mensual = 0
                    elif equipo == "Ventas":
                        eficiencia = kpi_transferencias(cantidad, meta)  # Reutilizamos la función para ventas
                        actividad = "Ventas"
                        meta_mensual = 0
                    else:
                        eficiencia = (cantidad / meta * 100) if meta > 0 else 0
                        actividad = "General"
                        meta_mensual = 0
                    
                    productividad = productividad_hora(cantidad, horas)
                    
                    datos_guardar[trabajador] = {
                        "actividad": actividad, 
                        "cantidad": cantidad, 
                        "meta": meta, 
                        "eficiencia": eficiencia, 
                        "productividad": productividad,
                        "comentario": comentario, 
                        "meta_mensual": meta_mensual,
                        "horas_trabajo": horas,
                        "equipo": equipo
                    }
            
            # Convertir la fecha seleccionada a string
            fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")
            
            # Almacenar datos en sesión para confirmación posterior
            st.session_state.datos_calculados = datos_guardar
            st.session_state.fecha_guardar = fecha_str
            
            # Mostrar resumen
            st.markdown("<h3 class='section-title'>📋 Resumen de KPIs Calculados</h3>", unsafe_allow_html=True)
            
            for equipo, miembros in trabajadores_por_equipo.items():
                st.markdown(f"**{equipo}:**")
                for trabajador in miembros:
                    if trabajador in datos_guardar:
                        datos = datos_guardar[trabajador]
                        st.markdown(f"- {trabajador}: {datos['cantidad']} unidades ({datos['eficiencia']:.1f}%)")
    
    # Botón de confirmación fuera del formulario
    if st.session_state.datos_calculados is not None and st.session_state.fecha_guardar is not None:
        if st.button("✅ Confirmar y Guardar Datos", key="confirmar_guardar"):
            if guardar_datos_db(st.session_state.fecha_guardar, st.session_state.datos_calculados):
                st.markdown("<div class='success-box'>✅ Datos guardados correctamente!</div>", unsafe_allow_html=True)
                # Limpiar datos de confirmación
                st.session_state.datos_calculados = None
                st.session_state.fecha_guardar = None
                time.sleep(2)
                st.rerun()
            else:
                st.markdown("<div class='error-box'>❌ Error al guardar los datos. Por favor, intente nuevamente.</div>", unsafe_allow_html=True)

def mostrar_dashboard():
    """Muestra el dashboard principal con KPIs"""
    st.markdown("<h1 class='header-title'>📊 Dashboard de KPIs Fashion Club</h1>", unsafe_allow_html=True)
    
    # Cargar datos históricos
    if 'historico_data' not in st.session_state:
        with st.spinner("Cargando datos históricos..."):
            st.session_state.historico_data = cargar_historico_db()
    
    df = st.session_state.historico_data
    
    if df.empty:
        st.markdown("<div class='warning-box'>⚠️ No hay datos históricos. Por favor, ingresa datos primero.</div>", unsafe_allow_html=True)
        return
    
    # Crear selector de fecha
    st.markdown("<div class='date-selector'>", unsafe_allow_html=True)
    st.markdown("<h3>Selecciona la fecha a visualizar:</h3>", unsafe_allow_html=True)
    
    # Obtener fechas únicas y ordenarlas
    if not df.empty and 'fecha' in df.columns:
        # Convertir a fecha y eliminar duplicados
        fechas_disponibles = sorted(df['fecha'].dt.date.unique(), reverse=True)
        
        if not fechas_disponibles:
            st.markdown("<div class='warning-box'>⚠️ No hay fechas disponibles para mostrar.</div>", unsafe_allow_html=True)
            return
        
        fecha_seleccionada = st.selectbox(
            "Fecha:",
            options=fechas_disponibles,
            index=0,
            label_visibility="collapsed"
        )
    else:
        st.markdown("<div class='warning-box'>⚠️ No hay datos disponibles.</div>", unsafe_allow_html=True)
        return
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Filtrar datos por fecha seleccionada
    df_reciente = df[df['fecha'].dt.date == fecha_seleccionada]
    
    if df_reciente.empty:
        st.markdown(f"<div class='warning-box'>⚠️ No hay datos disponibles para la fecha {fecha_seleccionada}.</div>", unsafe_allow_html=True)
        return
    
    st.markdown(f"<p style='color: white; font-size: 1.1em;'>Datos para la fecha: {fecha_seleccionada}</p>", unsafe_allow_html=True)
    
    st.markdown("<h2 class='section-title'>📈 KPIs Globales</h2>", unsafe_allow_html=True)
    
    # Cálculos globales
    total_cantidad = df_reciente['cantidad'].sum()
    total_meta = df_reciente['meta'].sum()
    total_horas = df_reciente['horas_trabajo'].sum()
    avg_eficiencia = (df_reciente['eficiencia'] * df_reciente['horas_trabajo']).sum() / total_horas if total_horas > 0 else 0
    avg_productividad = df_reciente['productividad'].mean()
    productividad_total = total_cantidad / total_horas if total_horas > 0 else 0
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        cumplimiento_meta = (total_cantidad / total_meta * 100) if total_meta > 0 else 0
        st.markdown(f"""
        <div class="kpi-card">
            <h3>✅ Total Producción</h3>
            <p class="metric-value">{total_cantidad:,.0f}</p>
            <p>Meta: {total_meta:,.0f} | <span class="{'trend-up' if cumplimiento_meta >= 100 else 'trend-down'}">{cumplimiento_meta:.1f}%</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi2:
        st.markdown(f"""
        <div class="kpi-card">
            <h3>🎯 Eficiencia Promedio</h3>
            <p class="metric-value">{avg_eficiencia:.1f}%</p>
            <p>Meta: 100% | <span class="{'trend-up' if avg_eficiencia >= 100 else 'trend-down'}">{avg_eficiencia - 100:.1f}%</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi3:
        st.markdown(f"""
        <div class="kpi-card">
            <h3>⚡ Productividad Promedio</h3>
            <p class="metric-value">{avg_productividad:.1f}</p>
            <p>unidades/hora</p>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi4:
        st.markdown(f"""
        <div class="kpi-card">
            <h3>⏱️ Productividad Total</h3>
            <p class="metric-value">{productividad_total:.1f}</p>
            <p>unidades/hora ({total_horas:.1f} h)</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h2 class='section-title'>📅 Cumplimiento de Metas Mensuales (Transferencias)</h2>", unsafe_allow_html=True)
    
    current_month = fecha_seleccionada.month
    current_year = fecha_seleccionada.year
    
    # Filtrar datos del mes actual para transferencias
    df_month = df[(df['fecha'].dt.month == current_month) & 
                  (df['fecha'].dt.year == current_year)]
    
    df_transferencias_month = df_month[df_month['equipo'] == 'Transferencias']
    
    # Obtener meta mensual de transferencias (usamos el último valor registrado)
    if not df_transferencias_month.empty:
        meta_mensual_transferencias = df_transferencias_month['meta_mensual'].iloc[0]
    else:
        # Si no hay datos, usar un valor por defecto
        meta_mensual_transferencias = 150000
    
    cum_transferencias = df_transferencias_month['cantidad'].sum()
    cumplimiento_transferencias = (cum_transferencias / meta_mensual_transferencias * 100) if meta_mensual_transferencias > 0 else 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <h3>Meta Mensual Transferencias</h3>
            <p class="metric-value">{cumplimiento_transferencias:.1f}%</p>
            <p>Acumulado: {cum_transferencias:,.0f} / Meta Mensual: {meta_mensual_transferencias:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Gráfico de frasco de agua para el cumplimiento
        fig = crear_grafico_frasco(cumplimiento_transferencias, "Cumplimiento Mensual Transferencias")
        st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de evolución mensual
    if not df_transferencias_month.empty:
        df_transferencias_daily = df_transferencias_month.groupby(df_transferencias_month['fecha'].dt.date)['cantidad'].sum().reset_index(name='cantidad')
        df_transferencias_daily['fecha'] = pd.to_datetime(df_transferencias_daily['fecha'])
        df_transferencias_daily = df_transferencias_daily.sort_values('fecha')
        df_transferencias_daily['cumulative'] = df_transferencias_daily['cantidad'].cumsum()
        
        fig = crear_grafico_interactivo(
            df_transferencias_daily, 
            'fecha', 
            'cumulative', 
            'Cumplimiento Mensual Transferencias', 
            'Día', 
            'Acumulado',
            'line'
        )
        
        # Añadir línea de meta
        fig.add_hline(y=meta_mensual_transferencias, line_dash="dash", line_color="red", annotation_text="Meta Mensual")
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para el gráfico de Transferencias.")
    
    st.markdown("<h2 class='section-title'>👥 Rendimiento por Equipos</h2>", unsafe_allow_html=True)
    
    # Obtener lista de equipos
    equipos = df_reciente['equipo'].unique()
    
    for equipo in equipos:
        df_equipo = df_reciente[df_reciente['equipo'] == equipo]
        
        st.markdown(f"<div class='team-section'><div class='team-header'>{equipo}</div></div>", unsafe_allow_html=True)
        
        # Calcular KPIs del equipo
        total_equipo = df_equipo['cantidad'].sum()
        meta_equipo = df_equipo['meta'].sum()
        horas_equipo = df_equipo['horas_trabajo'].sum()
        eficiencia_equipo = (df_equipo['eficiencia'] * df_equipo['horas_trabajo']).sum() / horas_equipo if horas_equipo > 0 else 0
        productividad_equipo = total_equipo / horas_equipo if horas_equipo > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>Producción</h3>
                <p class="metric-value">{total_equipo:,.0f}</p>
                <p>Meta: {meta_equipo:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>Eficiencia</h3>
                <p class="metric-value">{eficiencia_equipo:.1f}%</p>
                <p>Meta: 100%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>Productividad</h3>
                <p class="metric-value">{productividad_equipo:.1f}</p>
                <p>unidades/hora</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>Horas</h3>
                <p class="metric-value">{horas_equipo:.1f}</p>
                <p>horas trabajadas</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Mostrar trabajadores del equipo
        for _, row in df_equipo.iterrows():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                color = "#27ae60" if row['eficiencia'] >= 100 else "#e74c3c"
                card_content = f"""
                <div class="worker-card">
                    <div class="stats-container">
                        <div class="worker-header">{row['nombre']}</div>
                        <div class="worker-metric">📦 {row['actividad']}: <span style='font-weight:bold'>{row['cantidad']}</span></div>
                        <div class="worker-metric">🎯 Eficiencia: <span style='color:{color}; font-weight:bold'>{row['eficiencia']:.1f}%</span></div>
                        <div class="worker-metric">⏱️ Productividad: {row['productividad']:.1f}/hora</div>
                        <div class="worker-metric">⏰ Horas: {row['horas_trabajo']:.1f} h</div>
                    </div>
                </div>
                """
                st.markdown(card_content, unsafe_allow_html=True)
            
            with col2:
                comentario = row.get('comentario', None)
                if pd.notna(comentario) and str(comentario).strip() != "":
                    st.markdown(f"""
                    <div class="comment-container">
                        <div class="comment-title">💬 Comentario:</div>
                        <div class="comment-content">{comentario}</div>
                    </div>
                    """, unsafe_allow_html=True)

def mostrar_analisis_historico():
    """Muestra el análisis histórico de KPIs"""
    st.markdown("<h1 class='header-title'>📈 Análisis Histórico de KPIs</h1>", unsafe_allow_html=True)
    
    df = cargar_historico_db()
    
    if df.empty:
        st.markdown("<div class='warning-box'>⚠️ No hay datos históricos. Por favor, ingresa datos primero.</div>", unsafe_allow_html=True)
        return
    
    df['dia'] = df['fecha'].dt.date
    
    fecha_min = df['dia'].min()
    fecha_max = df['dia'].max()
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        fecha_inicio = st.date_input("Fecha de inicio:", value=fecha_min, min_value=fecha_min, max_value=fecha_max)
    
    with col2:
        fecha_fin = st.date_input("Fecha de fin:", value=fecha_max, min_value=fecha_min, max_value=fecha_max)
    
    with col3:
        trabajador = st.selectbox("Filtrar por trabajador:", options=["Todos"] + list(df['nombre'].unique()))
    
    if fecha_inicio > fecha_fin:
        st.markdown("<div class='error-box'>❌ La fecha de inicio no puede ser mayor que la fecha de fin.</div>", unsafe_allow_html=True)
        return
    
    # Aplicar filtros
    df_filtrado = df[(df['dia'] >= fecha_inicio) & (df['dia'] <= fecha_fin)]
    
    if trabajador != "Todos":
        df_filtrado = df_filtrado[df_filtrado['nombre'] == trabajador]
    
    if df_filtrado.empty:
        st.markdown("<div class='warning-box'>⚠️ No hay datos en el rango de fechas seleccionado.</div>", unsafe_allow_html=True)
        return
    
    st.markdown("<h2 class='section-title'>📋 Resumen Estadístico</h2>", unsafe_allow_html=True)
    
    # Mostrar resumen estadístico
    st.dataframe(df_filtrado.groupby('nombre').agg({
        'cantidad': ['count', 'mean', 'sum', 'max', 'min'],
        'eficiencia': ['mean', 'max', 'min'],
        'productividad': ['mean', 'max', 'min'],
        'horas_trabajo': ['sum', 'mean']
    }).round(2), use_container_width=True)
    
    st.markdown("<h2 class='section-title'>📊 Tendencias Históricas</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Eficiencia por Día", "Producción Acumulada", "Comparativa por Área", "Análisis Detallado", "Predicciones"])
    
    with tab1:
        df_eficiencia_dia = df_filtrado.groupby('dia')['eficiencia'].mean().reset_index()
        
        if not df_eficiencia_dia.empty:
            fig = crear_grafico_interactivo(
                df_eficiencia_dia, 
                'dia', 
                'eficiencia', 
                'Evolución de la Eficiencia Promedio Diaria', 
                'Fecha', 
                'Eficiencia Promedio (%)',
                'line'
            )
            
            # Añadir línea de meta
            fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Meta de eficiencia")
            
            # Analizar tendencia
            tendencia = analizar_tendencias(df_eficiencia_dia, 'eficiencia')
            if isinstance(tendencia, dict):
                fig.add_trace(go.Scatter(
                    x=df_eficiencia_dia['dia'], 
                    y=tendencia['tendencia'], 
                    mode='lines', 
                    name=f'Tendencia ({tendencia["direccion"]})',
                    line=dict(dash='dash', color='orange')
                ))
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar información de tendencia
            if isinstance(tendencia, dict):
                st.markdown(f"**Tendencia:** {tendencia['direccion']} (R²: {tendencia['r_cuadrado']:.3f})")
        else:
            st.info("No hay datos para el gráfico.")
    
    with tab2:
        df_produccion = df_filtrado.groupby(['dia', 'actividad'])['cantidad'].sum().reset_index()
        
        if not df_produccion.empty:
            fig = crear_grafico_interactivo(
                df_produccion, 
                'dia', 
                'cantidad', 
                'Producción Acumulada por Área', 
                'Fecha', 
                'Producción Acumulada',
                'line'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos para el gráfico.")
    
    with tab3:
        if not df_filtrado.empty:
            fig = crear_grafico_interactivo(
                df_filtrado, 
                'actividad', 
                'productividad', 
                'Distribución de Productividad por Área', 
                'Área', 
                'Productividad (unidades/hora)',
                'box'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos para el gráfico.")
    
    with tab4:
        st.markdown("<h3>📈 Análisis de Correlación</h3>", unsafe_allow_html=True)
        
        # Calcular matriz de correlación
        numeric_cols = df_filtrado.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = df_filtrado[numeric_cols].corr()
            
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                color_continuous_scale='RdBu_r',
                title='Matriz de Correlación'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay suficientes datos numéricos para calcular correlaciones.")
        
        st.markdown("<h3>📋 Datos Detallados</h3>", unsafe_allow_html=True)
        st.dataframe(df_filtrado, use_container_width=True)
    
    with tab5:
        st.markdown("<h3>🔮 Predicción de Tendencia</h3>", unsafe_allow_html=True)
        
        if not df_eficiencia_dia.empty and len(df_eficiencia_dia) > 5:
            # Preparar datos para predicción
            dias_prediccion = 7
            predicciones = predecir_valores_futuros(df_eficiencia_dia, 'eficiencia', dias_prediccion)
            
            if predicciones is not None:
                # Crear fechas futuras
                ultima_fecha = df_eficiencia_dia['dia'].max()
                fechas_futuras = [ultima_fecha + timedelta(days=i+1) for i in range(dias_prediccion)]
                
                # Crear gráfico
                fig = go.Figure()
                
                # Datos históricos
                fig.add_trace(go.Scatter(
                    x=df_eficiencia_dia['dia'], 
                    y=df_eficiencia_dia['eficiencia'],
                    mode='lines+markers',
                    name='Datos Históricos'
                ))
                
                # Predicciones
                fig.add_trace(go.Scatter(
                    x=fechas_futuras, 
                    y=predicciones,
                    mode='lines+markers',
                    name='Predicción',
                    line=dict(dash='dash', color='orange')
                ))
                
                # Línea de meta
                fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Meta de eficiencia")
                
                fig.update_layout(
                    title='Predicción de Eficiencia para los Próximos 7 Días',
                    xaxis_title='Fecha',
                    yaxis_title='Eficiencia Promedio (%)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="black")
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Mostrar valores de predicción
                st.markdown("<h4>Valores de Predicción:</h4>", unsafe_allow_html=True)
                for i, (fecha, pred) in enumerate(zip(fechas_futuras, predicciones)):
                    st.write(f"{fecha.strftime('%Y-%m-%d')}: {pred:.1f}%")
            else:
                st.info("Error al generar predicciones. Verifique los datos.")
        else:
            st.info("Se necesitan al menos 5 días de datos para realizar predicciones.")
    
    st.markdown("<h2 class='section-title'>💾 Exportar Datos</h2>", unsafe_allow_html=True)
    
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar datos históricos (CSV)",
        data=csv,
        file_name=f"kpis_historico_{fecha_inicio}_a_{fecha_fin}.csv",
        mime="text/csv",
        use_container_width=True
    )

def mostrar_administracion():
    """Muestra la interfaz de administración del sistema"""
    st.markdown("<h1 class='header-title'>⚙️ Administración del Sistema</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Backups", "Restaurar Backup", "Usuarios", "Configuración"])
    
    with tab1:
        st.markdown("<h3>📦 Gestión de Backups</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Crear Backup Ahora"):
                if crear_backup():
                    st.markdown("<div class='success-box'>✅ Backup creado correctamente.</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='error-box'>❌ Error al crear backup.</div>", unsafe_allow_html=True)
        
        with col2:
            # Listar backups disponibles
            backups = sorted(Path("backups").glob("kpi_backup_*.db"), key=os.path.getmtime, reverse=True)
            
            if backups:
                st.markdown("**Backups disponibles:**")
                for backup in backups[:5]:  # Mostrar solo los 5 más recientes
                    st.text(f"{backup.name} ({time.strftime('%Y-%m-%d %H:%M', time.gmtime(backup.stat().st_mtime))})")
            else:
                st.info("No hay backups disponibles.")
    
    with tab2:
        st.markdown("<h3>📥 Restaurar desde Backup</h3>", unsafe_allow_html=True)
        
        # Listar backups disponibles
        backups = sorted(Path("backups").glob("kpi_backup_*.db"), key=os.path.getmtime, reverse=True)
        
        if backups:
            backup_options = [f"{b.name} ({time.strftime('%Y-%m-%d %H:%M', time.gmtime(b.stat().st_mtime))})" for b in backups]
            backup_seleccionado = st.selectbox("Selecciona un backup para restaurar:", options=backup_options)
            
            if st.button("🔄 Restaurar Backup Seleccionado"):
                backup_path = backups[backup_options.index(backup_seleccionado)]
                if restaurar_backup(str(backup_path)):
                    st.markdown("<div class='success-box'>✅ Backup restaurado correctamente. La página se recargará.</div>", unsafe_allow_html=True)
                    time.sleep(2)
                    st.rerun()
                else:
                    st.markdown("<div class='error-box'>❌ Error al restaurar backup.</div>", unsafe_allow_html=True)
        else:
            st.info("No hay backups disponibles para restaurar.")
    
    with tab3:
        st.markdown("<h3>👥 Gestión de Usuarios</h3>", unsafe_allow_html=True)
        
        try:
            with st.session_state.db_manager.get_connection() as conn:
                c = conn.cursor()
                
                # Mostrar usuarios existentes
                c.execute('SELECT username, role, created_at FROM users')
                users = c.fetchall()
                
                if users:
                    st.markdown("**Usuarios existentes:**")
                    for user in users:
                        st.text(f"{user[0]} ({user[1]}) - Creado: {user[2]}")
                else:
                    st.info("No hay usuarios registrados.")
                
                # Formulario para agregar usuario
                st.markdown("---")
                st.markdown("<h4>➕ Agregar Nuevo Usuario</h4>", unsafe_allow_html=True)
                
                with st.form("form_nuevo_usuario"):
                    nuevo_usuario = st.text_input("Nombre de usuario:")
                    nueva_contrasena = st.text_input("Contraseña:", type="password")
                    rol_usuario = st.selectbox("Rol:", options=["user", "admin"])
                    
                    submitted = st.form_submit_button("Agregar Usuario")
                    
                    if submitted:
                        if nuevo_usuario and nueva_contrasena:
                            # Verificar si el usuario ya existe
                            c.execute('SELECT id FROM users WHERE username = ?', (nuevo_usuario,))
                            if c.fetchone():
                                st.markdown("<div class='error-box'>❌ El usuario ya existe.</div>", unsafe_allow_html=True)
                            else:
                                # Hashear contraseña y guardar usuario
                                password_hash = hashlib.sha256(nueva_contrasena.encode()).hexdigest()
                                c.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
                                         (nuevo_usuario, password_hash, rol_usuario))
                                conn.commit()
                                st.markdown("<div class='success-box'>✅ Usuario agregado correctamente.</div>", unsafe_allow_html=True)
                                st.rerun()
                        else:
                            st.markdown("<div class='error-box'>❌ Debe completar todos los campos.</div>", unsafe_allow_html=True)
        except Exception as e:
            logger.error(f"Error en gestión de usuarios: {e}")
            st.markdown("<div class='error-box'>❌ Error del sistema al gestionar usuarios.</div>", unsafe_allow_html=True)
    
    with tab4:
        st.markdown("<h3>⚙️ Configuración del Sistema</h3>", unsafe_allow_html=True)
        
        st.markdown("**Opciones de visualización:**")
        mostrar_graficos = st.checkbox("Mostrar gráficos interactivos", value=True)
        actualizacion_automatica = st.checkbox("Actualización automática de datos", value=True)
        
        if st.button("💾 Guardar Configuración"):
            try:
                with st.session_state.db_manager.get_connection() as conn:
                    c = conn.cursor()
                    c.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', 
                             ('mostrar_graficos', str(mostrar_graficos)))
                    c.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', 
                             ('actualizacion_automatica', str(actualizacion_automatica)))
                    conn.commit()
                    st.markdown("<div class='success-box'>✅ Configuración guardada correctamente.</div>", unsafe_allow_html=True)
            except Exception as e:
                logger.error(f"Error al guardar configuración: {e}")
                st.markdown("<div class='error-box'>❌ Error al guardar configuración.</div>", unsafe_allow_html=True)

def main():
    """Función principal de la aplicación"""
    st.sidebar.title("🔧 Menú de Navegación")
    
    # Mostrar información del usuario si está logueado
    if 'user' in st.session_state:
        st.sidebar.markdown(f"**Usuario:** {st.session_state.user}")
        st.sidebar.markdown(f"**Rol:** {st.session_state.role}")
        
        if st.sidebar.button("🚪 Cerrar Sesión"):
            st.session_state.password_correct = False
            st.session_state.pop('user', None)
            st.session_state.pop('role', None)
            st.rerun()
    
    opcion = st.sidebar.radio("Selecciona una opción:", 
                              ["Dashboard de KPIs", "Análisis Histórico", "Ingresar Datos", "Administración", "Gestión de Trabajadores"])
    
    if opcion == "Dashboard de KPIs":
        mostrar_dashboard()
    elif opcion == "Análisis Histórico":
        mostrar_analisis_historico()
    elif opcion == "Ingresar Datos":
        if verificar_password():
            ingresar_datos()
    elif opcion == "Administración":
        if verificar_password() and st.session_state.get('role') == 'admin':
            mostrar_administracion()
        else:
            st.markdown("<div class='error-box'>❌ No tiene permisos de administrador.</div>", unsafe_allow_html=True)
    elif opcion == "Gestión de Trabajadores":
        if verificar_password() and st.session_state.get('role') == 'admin':
            mostrar_gestion_trabajadores()
        else:
            st.markdown("<div class='error-box'>❌ No tiene permisos de administrador.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()