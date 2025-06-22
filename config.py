import os
from pathlib import Path

class Config:
    """Configuración base de la aplicación SGA"""
    
    # Rutas base del proyecto
    BASE_DIR = Path(__file__).resolve().parent
    INSTANCE_PATH = BASE_DIR / 'instance'
    
    # Configuración de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{INSTANCE_PATH}/sga.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQL_DEBUG', 'False').lower() == 'true'
    
    # Configuración de archivos estáticos
    STATIC_FOLDER = BASE_DIR / 'static'
    TEMPLATE_FOLDER = BASE_DIR / 'templates'
    
    # Configuración de QR y etiquetas
    QR_CODE_SIZE = 10
    QR_CODE_BORDER = 4
    LABEL_BASE_URL = os.environ.get('LABEL_BASE_URL') or 'http://localhost:5000'
    
    # Configuración de archivos de carga
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # Configuración de paginación
    ITEMS_PER_PAGE = 25
    MAX_ITEMS_PER_PAGE = 100
    
    @staticmethod
    def init_app(app):
        """Inicialización específica de la aplicación"""
        # Crear carpetas necesarias
        Config.INSTANCE_PATH.mkdir(exist_ok=True)
        Config.UPLOAD_FOLDER.mkdir(exist_ok=True)

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
