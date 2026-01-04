import pandas as pd
import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import matplotlib.pyplot as plt

class LogisticsReconciler:
    def __init__(self):
        self.df_facturas = None
        self.df_manifiesto = None
        self.guides_facturadas = []
        self.guides_anuladas = []
        self.guides_sobrantes_factura = []
        self.kpis = {}

    def _clean_guide(self, series):
        """Limpia y extrae el número de guía usando Regex."""
        # Busca LC seguido de números o solo 6+ dígitos
        pattern = r'(LC\d+|\d{6,})'
        return series.astype(str).str.strip().str.upper().str.extract(pattern, expand=False)

    def _find_col(self, df, keywords):
        """Busca una columna que coincida con keywords."""
        for col in df.columns:
            if any(k in str(col).upper() for k in keywords):
                return col
        return None

    def process_files(self, factura_file, manifiesto_file):
        try:
            self.df_facturas = pd.read_excel(factura_file)
            self.df_manifiesto = pd.read_excel(manifiesto_file)
            
            # Identificar columnas de guías
            col_fac = self._find_col(self.df_facturas, ['GUIA', 'TRACKING', 'REMISION', 'REFERENCIA'])
            col_man = self._find_col(self.df_manifiesto, ['GUIA', 'TRACKING', 'REMISION', 'REFERENCIA'])
            
            if not col_fac or not col_man:
                st.error("No se encontraron columnas de Guía/Tracking en los archivos.")
                return False

            # Limpieza
            self.df_facturas['CLEAN_GUIDE'] = self._clean_guide(self.df_facturas[col_fac])
            self.df_manifiesto['CLEAN_GUIDE'] = self._clean_guide(self.df_manifiesto[col_man])
            
            # Filtrar vacíos
            fac_set = set(self.df_facturas['CLEAN_GUIDE'].dropna())
            man_set = set(self.df_manifiesto['CLEAN_GUIDE'].dropna())
            
            # Lógica de Conjuntos
            self.guides_facturadas = list(fac_set & man_set) # Intersección (OK)
            self.guides_anuladas = list(man_set - fac_set)   # En manifiesto, no en factura (Anulada/Perdida)
            self.guides_sobrantes_factura = list(fac_set - man_set) # En factura, no en manifiesto (Error cobro)
            
            # Calcular KPIs financieros (Busca columna de Valor/Subtotal)
            val_col = self._find_col(self.df_facturas, ['SUBTOTAL', 'VALOR', 'MONTO', 'PRECIO'])
            total_val = 0
            val_ok = 0
            
            if val_col:
                # Limpiar moneda
                self.df_facturas[val_col] = pd.to_numeric(
                    self.df_facturas[val_col].astype(str).str.replace(',', '.').str.replace(r'[^\d.]', '', regex=True),
                    errors='coerce'
                ).fillna(0)
                
                total_val = self.df_facturas[val_col].sum()
                val_ok = self.df_facturas[self.df_facturas['CLEAN_GUIDE'].isin(self.guides_facturadas)][val_col].sum()
            
            self.kpis = {
                'total_facturadas': len(self.guides_facturadas),
                'total_anuladas': len(self.guides_anuladas),
                'total_sobrantes': len(self.guides_sobrantes_factura),
                'monto_total': total_val,
                'monto_conciliado': val_ok,
                'monto_pendiente': total_val - val_ok
            }
            return True
            
        except Exception as e:
            st.error(f"Error procesando reconciliación: {e}")
            return False

    def generate_pdf_report(self):
        """Genera reporte PDF con ReportLab."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Título
        elements.append(Paragraph("Reporte de Conciliación Logística", styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Tabla KPIs
        data = [
            ['Concepto', 'Cantidad', 'Monto Estimado'],
            ['Guías Conciliadas (OK)', str(self.kpis['total_facturadas']), f"${self.kpis['monto_conciliado']:,.2f}"],
            ['Guías Faltantes en Factura', str(self.kpis['total_anuladas']), "N/A"],
            ['Guías Sobrantes en Factura', str(self.kpis['total_sobrantes']), f"${self.kpis['monto_pendiente']:,.2f}"]
        ]
        
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        
        # Gráfico (Matplotlib a Imagen)
        fig, ax = plt.subplots(figsize=(6, 4))
        labels = ['Conciliadas', 'Anuladas', 'Sobrantes']
        sizes = [self.kpis['total_facturadas'], self.kpis['total_anuladas'], self.kpis['total_sobrantes']]
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        elements.append(Spacer(1, 20))
        elements.append(ReportLabImage(img_buf, width=400, height=300))
        plt.close(fig)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
