#!/usr/bin/env python3
"""
Script de entrada principal para el Sistema de Gestión de Activos (SGA)
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar y ejecutar la aplicación
from app import main

if __name__ == '__main__':
    main()
