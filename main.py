"""
Punto de entrada de ConvertMD.
"""

import sys
import os

# Asegurar que el directorio raíz esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui import run_app

if __name__ == "__main__":
    run_app()
