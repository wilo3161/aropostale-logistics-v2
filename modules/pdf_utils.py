import os
import io
import tempfile
import requests
import qrcode
from fpdf import FPDF
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def generar_qr_imagen(url: str) -> Image.Image:
    """Genera una imagen PIL de un código QR."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=5,
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def generar_pdf_guia(store_name: str, brand: str, url: str, sender_name: str, sender_address: str, sender_phone: str, tracking_number: str, store_info: dict) -> bytes:
    """Genera el PDF de la guía de envío."""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_margins(10, 10, 10)
        pdf.set_auto_page_break(True, 15)
        
        # --- Encabezado ---
        pdf.set_fill_color(0, 45, 98) # Azul Aeropostale
        pdf.rect(0, 0, 210, 35, style='F')
        
        # Logo (Usamos URLs estables o placeholders si fallan)
        logos_urls = {
            "Fashion": "https://raw.githubusercontent.com/wilo3161/kpi-system/main/images/Fashion.jpg",
            "Tempo": "https://raw.githubusercontent.com/wilo3161/kpi-system/main/images/Tempo.jpg"
        }
        logo_url = logos_urls.get(brand)
        
        if logo_url:
            try:
                response = requests.get(logo_url, timeout=5)
                if response.status_code == 200:
                    logo_img = Image.open(io.BytesIO(response.content))
                    # Convertir a RGB para asegurar compatibilidad con FPDF
                    if logo_img.mode != 'RGB':
                        logo_img = logo_img.convert('RGB')
                        
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                        logo_img.save(tmp.name, format='JPEG')
                        pdf.image(tmp.name, x=10, y=1, w=30)
                        os.unlink(tmp.name)
            except Exception as e:
                logger.error(f"No se pudo cargar logo: {e}")

        # Títulos
        pdf.set_text_color(255, 0, 0) # Rojo
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_xy(0, 5)
        pdf.cell(210, 10, "AEROPOSTALE", 0, 1, "C")

        pdf.set_text_color(255, 255, 255) # Blanco
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_xy(0, 18)
        pdf.cell(210, 10, "CENTRO DE DISTRIBUCIÓN FASHION CLUB", 0, 1, "C")
        
        # --- Cuerpo ---
        pdf.set_text_color(0, 0, 0)
        pdf.set_y(45)
        y_start = pdf.get_y()
        
        # Remitente
        pdf.set_font("Arial", "B", 14)
        pdf.cell(90, 8, "REMITENTE:", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(90, 6, f"{sender_name}\n{sender_address}\nTelf: {sender_phone}")
        pdf.ln(5)
        
        # Destinatario
        pdf.set_font("Arial", "B", 14)
        pdf.cell(90, 8, "DESTINATARIO:", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.cell(90, 6, f"Rastreo: {tracking_number}", 0, 1)
        pdf.set_font("Helvetica", "B", 16)
        pdf.multi_cell(90, 8, store_name)
        
        pdf.set_font("Arial", "", 12)
        if store_info.get('address'):
            pdf.multi_cell(90, 6, store_info['address'])
        if store_info.get('phone'):
            pdf.cell(90, 6, f"Telf: {store_info['phone']}", 0, 1)

        # Código QR (A la derecha)
        if url:
            qr_img = generar_qr_imagen(url)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                qr_img.save(tmp.name)
                # Posicionar a la derecha del contenido
                pdf.image(tmp.name, x=130, y=y_start, w=60)
                os.unlink(tmp.name)

        return pdf.output(dest="S").encode("latin1")
        
    except Exception as e:
        logger.error(f"Error generando PDF Guía: {e}")
        return b""

def generar_pdf_etiqueta(datos: dict) -> bytes:
    """Genera etiqueta de producto grande para cajas."""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_margins(10, 10, 10)
        
        # Encabezado
        pdf.set_fill_color(10, 16, 153)
        pdf.rect(0, 0, 210, 35, style='F')
        
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_xy(0, 5)
        pdf.cell(210, 10, "AEROPOSTALE", 0, 1, "C")
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_xy(0, 18)
        pdf.cell(210, 10, "PRICE CLUB GUAYAQUIL", 0, 1, "C")
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_y(45)
        
        # Datos
        campos = [
            ("REFERENCIA", datos['referencia']),
            ("TIPO", datos['tipo'].upper()),
            ("CANTIDAD", str(datos['cantidad'])),
            ("CAJA", str(datos['caja']))
        ]
        
        for titulo, valor in campos:
            pdf.set_font("Helvetica", "", 16)
            pdf.cell(50, 10, titulo, 0, 0)
            pdf.set_font("Helvetica", "B", 22)
            if titulo == "TIPO":
                pdf.set_text_color(10, 16, 153)
            pdf.cell(0, 10, valor, 0, 1)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)

        # Imagen del producto si existe
        if datos.get('imagen_path') and os.path.exists(datos['imagen_path']):
            y_img = pdf.get_y()
            pdf.image(datos['imagen_path'], x=120, y=45, w=70)
        
        # Piso (Grande al final)
        pdf.ln(10)
        pdf.set_font("Helvetica", "B", 70)
        pdf.cell(0, 30, f"PISO {datos['piso']}", 0, 1, "C")
        
        return pdf.output(dest="S").encode("latin1")
    except Exception as e:
        logger.error(f"Error generando PDF Etiqueta: {e}")
        return None
