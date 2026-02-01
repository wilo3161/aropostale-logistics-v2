"""
Este archivo convierte la carpeta en un paquete.
Importamos los módulos aquí para que estén disponibles como 'modules.config', etc.
"""
import os
import sys

# Forzar la visibilidad del directorio actual
sys.path.append(os.path.dirname(__file__))

try:
    from . import config
    from . import ui
    from . import auth
    from . import database
    from . import pdf_utils
    from . import reconciliation
    from . import wilo_ai
except ImportError as e:
    # Esto nos dirá exactamente cuál archivo falta
    print(f"Error interno en modules/__init__.py: {e}")
