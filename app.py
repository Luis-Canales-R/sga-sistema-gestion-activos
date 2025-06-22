import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_migrate import Migrate
from pathlib import Path

from config import config
from models import db, Activo, Usuario, Ubicacion, AssetStatus, UserRole
from api import api

def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Registrar blueprints
    app.register_blueprint(api)
    
    # =================================================================
    # RUTAS PRINCIPALES DE LA APLICACIÓN WEB
    # =================================================================
    
    @app.route('/')
    def index():
        """Página principal - Dashboard"""
        return render_template('dashboard.html')
    
    @app.route('/admin')
    def admin_panel():
        """Panel de administración"""
        return render_template('admin/panel.html')
    
    @app.route('/admin/activos')
    def admin_activos():
        """Gestión de activos"""
        return render_template('admin/activos.html')
    
    @app.route('/mobile')
    def mobile_interface():
        """Interface móvil para campo"""
        return render_template('mobile/interface.html')
    
    @app.route('/mobile/scan')
    def mobile_scan():
        """Scanner QR móvil"""
        return render_template('mobile/scanner.html')
    
    @app.route('/activo/<codigo_activo>')
    def view_activo(codigo_activo):
        """Vista pública de activo (desde QR)"""
        activo = Activo.query.filter_by(codigo_activo=codigo_activo).first_or_404()
        return render_template('public/activo_detail.html', activo=activo)
    
    @app.cli.command()
    def init_db():
        """Inicializar base de datos"""
        db.create_all()
        print('Base de datos inicializada.')
    
    @app.cli.command()
    def create_sample_data():
        """Crear datos de ejemplo para desarrollo"""
        from datetime import date
        
        # Usuario administrador
        admin = Usuario(
            nombre_completo='Administrador del Sistema',
            email='admin@empresa.com',
            rol=UserRole.ADMIN
        )
        db.session.add(admin)
        
        # Ubicación de ejemplo
        ubicacion = Ubicacion(
            nombre='Oficina Principal',
            descripcion='Oficina principal de la empresa'
        )
        db.session.add(ubicacion)
        db.session.flush()
        
        # Activo de ejemplo
        activo = Activo(
            codigo_activo='LAP-001',
            nombre_activo='Laptop Dell Inspiron',
            descripcion='Laptop para desarrollo',
            marca='Dell',
            modelo='Inspiron 15 3000',
            numero_serie='DL123456789',
            status=AssetStatus.ACTIVO,
            fecha_adquisicion=date(2024, 1, 15),
            costo_adquisicion=1200.00,
            ubicacion_id=ubicacion.id,
            usuario_asignado_id=admin.id
        )
        activo.qr_url = f"{app.config['LABEL_BASE_URL']}/activo/{activo.codigo_activo}"
        db.session.add(activo)
        
        db.session.commit()
        print('Datos de ejemplo creados exitosamente.')
    
    @app.context_processor
    def inject_global_vars():
        """Inyecta variables globales en todos los templates"""
        return {
            'asset_statuses': [status.value for status in AssetStatus],
            'user_roles': [role.value for role in UserRole],
            'app_name': 'Sistema de Gestión de Activos',
            'app_version': '1.0.0'
        }
    
    return app

def main():
    """Función principal para ejecutar la aplicación"""
    app = create_app()
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    
    # Ejecutar aplicación
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )

if __name__ == '__main__':
    main()
