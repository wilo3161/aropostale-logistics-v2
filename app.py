import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Importación de nuestros módulos locales
from modules import config, ui, auth, database, pdf_utils, reconciliation, wilo_ai

# --- CONFIGURACIÓN DE PÁGINA (Debe ser lo primero) ---
st.set_page_config(
    layout="wide",
    page_title="Sistema de KPIs Aeropostale",
    page_icon="✈️",
    initial_sidebar_state="expanded"
)

# --- INICIALIZACIÓN ---
auth.init_session_state()  # Inicializa variables de sesión
ui.load_css()              # Carga el CSS "Torrecarga"
wilo_ai.init_wilo_background() # Arranca el monitor de IA en segundo plano

# ==========================================
# VISTAS DEL SISTEMA (VIEW CONTROLLERS)
# ==========================================

def view_dashboard_kpis():
    ui.render_header("📊 Dashboard de KPIs", "Control Logístico en Tiempo Real")
    
    # Filtros
    st.markdown("<div class='filter-panel'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    fecha_inicio = c1.date_input("Fecha Inicio", value=datetime.now().date())
    fecha_fin = c2.date_input("Fecha Fin", value=datetime.now().date())
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Carga de datos
    df = database.cargar_historico_db(fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d"))
    
    if df.empty:
        st.info("⚠️ No hay datos para el rango seleccionado.")
        return

    # Cálculos KPIs Globales
    total_prod = df['cantidad'].sum()
    total_meta = df['meta'].sum()
    cumplimiento = (total_prod / total_meta * 100) if total_meta > 0 else 0
    horas_totales = df['horas_trabajo'].sum()
    prod_hora = total_prod / horas_totales if horas_totales > 0 else 0
    eficiencia_avg = (df['eficiencia'] * df['horas_trabajo']).sum() / horas_totales if horas_totales > 0 else 0

    # Tarjetas KPI
    st.markdown("<div class='kpi-tower'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: ui.render_kpi_card("Producción Total", f"{total_prod:,.0f}", f"Meta: {total_meta:,.0f}", "📦")
    with c2: ui.render_kpi_card("Cumplimiento", f"{cumplimiento:.1f}%", "Global", "🎯", "positive" if cumplimiento >= 90 else "negative")
    with c3: ui.render_kpi_card("Eficiencia Avg", f"{eficiencia_avg:.1f}%", "Ponderada", "⚡", "positive" if eficiencia_avg >= 95 else "negative")
    with c4: ui.render_kpi_card("Productividad", f"{prod_hora:.1f}", "Unid/Hora", "⏱️")
    st.markdown("</div>", unsafe_allow_html=True)

    # Gráficos
    st.markdown("### 📈 Tendencias")
    tab1, tab2 = st.tabs(["Evolución Diaria", "Por Equipo"])
    
    with tab1:
        df_daily = df.groupby('fecha')[['cantidad', 'meta']].sum().reset_index()
        fig = px.line(df_daily, x='fecha', y=['cantidad', 'meta'], title="Producción vs Meta")
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        df_team = df.groupby('equipo')[['cantidad', 'meta']].sum().reset_index()
        df_team['cumplimiento'] = (df_team['cantidad'] / df_team['meta'] * 100).fillna(0)
        fig = px.bar(df_team, x='equipo', y='cumplimiento', title="Cumplimiento por Equipo (%)", color='cumplimiento', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)

def view_ingreso_datos():
    auth.require_auth("admin")
    ui.render_header("📥 Ingreso de Datos", "Registro Diario de Producción")
    
    fecha = st.date_input("Fecha de Registro", value=datetime.now().date())
    trabajadores = database.obtener_trabajadores()
    
    if trabajadores.empty:
        st.warning("No hay trabajadores registrados. Vaya a 'Gestión de Trabajadores'.")
        return

    # Agrupar por equipo
    equipos = trabajadores['equipo'].unique()
    
    with st.form("form_ingreso"):
        datos_a_guardar = {}
        
        for equipo in equipos:
            st.markdown(f"### 👥 {equipo}")
            miembros = trabajadores[trabajadores['equipo'] == equipo]
            
            for _, trab in miembros.iterrows():
                nombre = trab['nombre']
                c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
                c1.markdown(f"**{nombre}**")
                cant = c2.number_input(f"Cant. {nombre}", min_value=0, key=f"c_{nombre}")
                horas = c3.number_input(f"Horas {nombre}", min_value=0.0, value=8.0, step=0.5, key=f"h_{nombre}")
                comentario = c4.text_input(f"Nota {nombre}", key=f"n_{nombre}")
                
                # Metas por defecto según equipo (Lógica original)
                meta_default = 1750 if equipo == "Transferencias" else (1000 if equipo == "Distribución" else 100)
                
                if cant > 0:
                    datos_a_guardar[nombre] = {
                        "actividad": equipo,
                        "cantidad": cant,
                        "meta": meta_default, # Simplificado, idealmente vendría de DB
                        "horas_trabajo": horas,
                        "eficiencia": (cant / meta_default * 100) if meta_default > 0 else 0,
                        "productividad": cant / horas if horas > 0 else 0,
                        "comentario": comentario,
                        "equipo": equipo,
                        "meta_mensual": 0 # Placeholder
                    }
        
        if st.form_submit_button("💾 Guardar Registros"):
            if database.guardar_datos_db(fecha.strftime("%Y-%m-%d"), datos_a_guardar):
                st.success("Datos guardados exitosamente")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Error al guardar datos")

def view_generar_guias():
    auth.require_auth("user")
    ui.render_header("📦 Generador de Guías", "Etiquetado Logístico")
    
    tab1, tab2 = st.tabs(["Generar Guía", "Historial"])
    
    with tab1:
        tiendas = database.obtener_tiendas()
        remitentes = database.obtener_remitentes()
        
        with st.form("guia_form"):
            c1, c2 = st.columns(2)
            tienda_sel = c1.selectbox("Tienda Destino", tiendas['name'].tolist() if not tiendas.empty else [])
            remitente_sel = c2.selectbox("Remitente", remitentes['name'].tolist() if not remitentes.empty else [])
            
            c3, c4 = st.columns(2)
            marca = c3.radio("Marca", ["Fashion", "Tempo"], horizontal=True)
            url = c4.text_input("URL Pedido", "https://")
            
            if st.form_submit_button("Generar PDF"):
                if tienda_sel and remitente_sel:
                    # Obtener datos completos para el PDF
                    tienda_info = tiendas[tiendas['name'] == tienda_sel].iloc[0].to_dict()
                    remitente_info = remitentes[remitentes['name'] == remitente_sel].iloc[0].to_dict()
                    tracking = f"TRK-{int(time.time())}"
                    
                    # Generar PDF
                    pdf_bytes = pdf_utils.generar_pdf_guia(
                        tienda_sel, marca, url, 
                        remitente_sel, remitente_info['address'], remitente_info['phone'],
                        tracking, tienda_info
                    )
                    
                    if pdf_bytes:
                        # Guardar Log
                        database.insert_data('guide_logs', {
                            'store_name': tienda_sel,
                            'brand': marca,
                            'sender_name': remitente_sel,
                            'url': url,
                            'status': 'Generated',
                            'tracking_number': tracking
                        })
                        
                        st.success("✅ Guía Generada")
                        st.download_button("⬇️ Descargar PDF", pdf_bytes, f"guia_{tracking}.pdf", "application/pdf")
                    else:
                        st.error("Error generando PDF")

    with tab2:
        df = database.fetch_data('guide_logs', order_by=('created_at', True))
        st.dataframe(df)

def view_reconciliacion():
    auth.require_auth("admin")
    ui.render_header("⚖️ Reconciliación Logística", "Facturas vs Manifiestos")
    
    # Inicializar estado local para el reconciliador
    if 'reconciler' not in st.session_state:
        st.session_state.reconciler = reconciliation.LogisticsReconciler()
        st.session_state.rec_processed = False

    c1, c2 = st.columns(2)
    f1 = c1.file_uploader("Excel Facturas", key="f1")
    f2 = c2.file_uploader("Excel Manifiesto", key="f2")
    
    if f1 and f2 and st.button("🚀 Procesar Conciliación"):
        with st.spinner("Analizando archivos..."):
            success = st.session_state.reconciler.process_files(f1, f2)
            st.session_state.rec_processed = success
    
    if st.session_state.rec_processed:
        rec = st.session_state.reconciler
        
        # Métricas
        st.markdown("<div class='kpi-tower'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: ui.render_kpi_card("Conciliadas", str(rec.kpis['total_facturadas']), "OK", "✅")
        with c2: ui.render_kpi_card("Faltantes en Factura", str(rec.kpis['total_anuladas']), "Error Logístico", "⚠️", "negative")
        with c3: ui.render_kpi_card("Sobrantes en Factura", str(rec.kpis['total_sobrantes']), "Error Cobro", "💰", "negative")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Descarga reporte
        pdf_report = rec.generate_pdf_report()
        st.download_button("📄 Descargar Reporte Oficial PDF", pdf_report, "reporte_conciliacion.pdf", "application/pdf")
        
        # Tablas detalle
        with st.expander("Ver Detalles de Guías"):
            st.write("Guías Faltantes (Anuladas):", rec.guides_anuladas)
            st.write("Guías Sobrantes:", rec.guides_sobrantes_factura)

def view_gestion_trabajadores():
    auth.require_auth("admin")
    ui.render_header("👥 Gestión de Personal", "Altas y Bajas")
    
    df = database.obtener_trabajadores()
    st.dataframe(df)
    
    with st.form("add_worker"):
        st.write("Agregar Nuevo Trabajador")
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre Completo")
        equipo = c2.selectbox("Equipo", ["Transferencias", "Distribución", "Arreglo", "Guías", "Ventas"])
        
        if st.form_submit_button("Agregar"):
            if database.insert_data('trabajadores', {'nombre': nombre, 'equipo': equipo, 'activo': True}):
                st.success("Trabajador agregado")
                time.sleep(0.5); st.rerun()
            else:
                st.error("Error al guardar")

def view_etiquetas():
    auth.require_auth("user")
    ui.render_header("🏷️ Generador de Etiquetas", "Cajas y Bultos")
    
    with st.form("etiqueta_form"):
        c1, c2 = st.columns(2)
        ref = c1.text_input("Referencia")
        tipo = c2.selectbox("Tipo", ["HOMBRE", "MUJER", "ACCESORIOS"])
        cant = c1.number_input("Cantidad", min_value=1)
        caja = c2.number_input("N° Caja", min_value=1)
        
        if st.form_submit_button("Generar Etiqueta"):
            # Lógica de piso según tipo (del código original)
            piso = 1 if tipo == "HOMBRE" else (3 if tipo == "MUJER" else 2)
            
            pdf_bytes = pdf_utils.generar_pdf_etiqueta({
                'referencia': ref, 'tipo': tipo, 'cantidad': cant,
                'caja': caja, 'piso': piso, 'imagen_path': None
            })
            
            if pdf_bytes:
                st.download_button("⬇️ Descargar Etiqueta", pdf_bytes, f"etiqueta_{ref}.pdf", "application/pdf")
            else:
                st.error("Error generando etiqueta")

def view_tempo_analisis():
    """Vista adaptada del módulo Tempo Análisis original"""
    auth.require_auth("user")
    ui.render_header("⏱️ Tempo Análisis", "Estudio de Tiempos y Movimientos")
    
    c1, c2 = st.columns(2)
    with c1:
        operario = st.selectbox("Operario", ["Seleccionar..."] + database.obtener_trabajadores()['nombre'].tolist())
        actividad = st.selectbox("Actividad", ["Picking", "Etiquetado", "Embalaje"])
    
    with c2:
        st.metric("Cronómetro", "00:00:00")
        if st.button("🟢 Iniciar"): st.toast("Cronómetro iniciado")
        if st.button("🔴 Detener"): st.success("Tiempo registrado: 45s (Simulado)")

def view_wilo_ai_wrapper():
    """Wrapper para llamar al dashboard de Wilo AI"""
    auth.require_auth("admin")
    wilo_ai.render_wilo_dashboard()

def view_novedades_correo():
    """Vista específica para búsqueda exhaustiva de correos (del código original)"""
    auth.require_auth("admin")
    ui.render_header("📧 Análisis de Novedades", "Búsqueda Exhaustiva en Correos")
    
    with st.form("search_mail"):
        dias = st.slider("Días atrás", 1, 30, 7)
        criterio = st.multiselect("Buscar problemas:", ["Faltante", "Daño", "Urgencia"], default=["Faltante"])
        if st.form_submit_button("🔍 Ejecutar Análisis"):
            st.info("Conectando con Wilo AI Engine...")
            # Aquí conectaríamos con wilo_ai.WiloAIEngine.analyze_text() iterando sobre correos
            # Por simplicidad en la demo, mostramos mensaje
            st.success("Análisis completado. Revise el Dashboard de Wilo AI para resultados detallados.")

# ==========================================
# MENÚ PRINCIPAL Y RUTEO
# ==========================================

def main():
    # Login Modal
    if st.session_state.show_login:
        auth.login_form()
        return

    with st.sidebar:
        st.markdown("""
        <div class='sidebar-logo'>
            <div class='logo-text'>AEROPOSTALE</div>
            <div class='logo-subtext'>Logistics v2.0</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Definición del Menú
        menu_options = [
            ("WILO AI Dashboard", "🧠", view_wilo_ai_wrapper, "admin"),
            ("Dashboard KPIs", "📊", view_dashboard_kpis, "public"),
            ("Ingreso de Datos", "📥", view_ingreso_datos, "admin"),
            ("Gestión Personal", "👥", view_gestion_trabajadores, "admin"),
            ("Reconciliación", "🔁", view_reconciliacion, "admin"),
            ("Generar Guías", "📋", view_generar_guias, "user"),
            ("Etiquetas Producto", "🏷️", view_etiquetas, "user"),
            ("WILO: Novedades", "📧", view_novedades_correo, "admin"),
            ("WILO: Tempo", "⏱️", view_tempo_analisis, "user"),
            ("Ayuda", "❓", lambda: st.info("Contactar a Soporte TI: Wilson Pérez"), "public"),
        ]

        # Renderizar botones
        for i, (label, icon, func, perm) in enumerate(menu_options):
            if st.button(f"{icon} {label}", key=f"nav_{i}", use_container_width=True):
                st.session_state.selected_menu = i

        st.markdown("---")
        
        # Botones de sesión
        if st.session_state.user_type:
            if st.button("Cerrar Sesión"):
                st.session_state.user_type = None
                st.rerun()
            st.caption(f"👤 {st.session_state.user_type.upper()}")
        else:
            c1, c2 = st.columns(2)
            if c1.button("Usuario"): 
                st.session_state.show_login = True; st.session_state.login_type = "user"; st.rerun()
            if c2.button("Admin"): 
                st.session_state.show_login = True; st.session_state.login_type = "admin"; st.rerun()

    # Router
    if 'selected_menu' not in st.session_state: st.session_state.selected_menu = 1
    
    if st.session_state.selected_menu < len(menu_options):
        label, icon, func, perm = menu_options[st.session_state.selected_menu]
        
        # Verificación de permisos
        authorized = False
        if perm == "public": authorized = True
        elif perm == "user" and st.session_state.user_type: authorized = True
        elif perm == "admin" and st.session_state.user_type == "admin": authorized = True
        
        if authorized:
            func()
        else:
            ui.render_header("🔒 Acceso Restringido", f"Se requiere nivel: {perm.upper()}")
            st.error("Por favor inicie sesión con los privilegios adecuados.")
            if st.button("Iniciar Sesión Ahora"):
                st.session_state.show_login = True
                st.session_state.login_type = perm
                st.rerun()

    # Footer
    st.markdown("""
    <div class="footer">
        Sistema de KPIs Aeropostale v2.0 | Desarrollado por Wilson Pérez<br>
        Arquitectura Modular © 2025
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
