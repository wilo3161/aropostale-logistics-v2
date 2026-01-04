from fpdf import FPDF
import qrcode
import tempfile
import os
import time

def generate_shipping_guide(store, brand, url, sender, tracking):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 45, 98)
    pdf.rect(0, 0, 210, 35, style='F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 24)
    pdf.set_xy(0, 5)
    pdf.cell(210, 10, "AEROPOSTALE", 0, 1, "C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(50)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Rastreo: {tracking}", ln=True)
    pdf.cell(0, 10, f"Destino: {store}", ln=True)
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        img.save(tmp.name)
        pdf.image(tmp.name, x=150, y=40, w=50)
        os.unlink(tmp.name)
    return pdf.output(dest="S").encode("latin1")
