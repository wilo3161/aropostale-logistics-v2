import streamlit as st
from supabase import create_client, Client
from modules import config
import logging
import pandas as pd

logger = logging.getLogger(__name__)

@st.cache_resource
def init_supabase() -> Client:
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        st.error("⚠️ Faltan credenciales de Supabase.")
        return None
    try:
        return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    except Exception as e:
        logger.error(f"Error inicializando Supabase: {e}")
        return None

def fetch_data(table_name, select_query="*", order_by=None, filters=None):
    client = init_supabase()
    if not client: return pd.DataFrame()
    try:
        query = client.from_(table_name).select(select_query)
        if filters:
            for k, v in filters.items():
                query = query.eq(k, v)
        if order_by:
            query = query.order(order_by[0], desc=order_by[1])
        response = query.execute()
        # >>> AÑADIR AL FINAL DE modules/database.py

def obtener_distribuciones_semana(fecha_inicio_semana: str):
    """Obtiene distribuciones de la semana."""
    client = init_supabase()
    try:
        res = client.from_('distribuciones_semanales').select('*').eq('semana', fecha_inicio_semana).execute()
        if res.data:
            return res.data[0]
        return {'tempo_distribuciones': 0, 'luis_distribuciones': 0}
    except Exception as e:
        return {'tempo_distribuciones': 0, 'luis_distribuciones': 0}

def guardar_distribuciones_semanales(fecha, tempo, luis, meta):
    """Guarda/Actualiza distribuciones."""
    client = init_supabase()
    data = {
        'semana': fecha,
        'tempo_distribuciones': tempo,
        'luis_distribuciones': luis,
        'meta_semanal': meta
    }
    try:
        # Intentar upsert (insertar o actualizar)
        client.from_('distribuciones_semanales').upsert(data, on_conflict='semana').execute()
        return True
    except Exception as e:
        return False
        data = response.data if hasattr(response, 'data') else []
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        logger.error(f"Error fetching {table_name}: {e}")
        return pd.DataFrame()
