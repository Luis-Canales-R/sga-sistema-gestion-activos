from flask import Blueprint, request, jsonify, current_app, send_file
from sqlalchemy import and_, or_
from datetime import datetime, date
import qrcode
from io import BytesIO

from models import (
    db, Activo, Usuario, Ubicacion, 
    AssetStatus, UserRole
)

# Crear el Blueprint para la API
api = Blueprint('api', __name__, url_prefix='/api')

def paginate_query(query, page=1, per_page=None):
    """Función auxiliar para paginación"""
    if per_page is None:
        per_page = current_app.config['ITEMS_PER_PAGE']
    
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return {
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
        'per_page': per_page,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next
    }

@api.route('/activos', methods=['GET'])
def get_activos():
    """Obtiene lista de activos con filtros y paginación"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        search = request.args.get('search', '').strip()
        status = request.args.get('status')
        
        query = Activo.query
        
        if search:
            search_filter = or_(
                Activo.codigo_activo.ilike(f'%{search}%'),
                Activo.nombre_activo.ilike(f'%{search}%'),
                Activo.marca.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        if status:
            query = query.filter(Activo.status == AssetStatus(status))
        
        query = query.order_by(Activo.codigo_activo)
        return jsonify(paginate_query(query, page, per_page))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/activos', methods=['POST'])
def create_activo():
    """Crea un nuevo activo"""
    try:
        data = request.get_json()
        
        # Verificar que el código no exista
        if Activo.query.filter_by(codigo_activo=data['codigo_activo']).first():
            return jsonify({'error': 'El código de activo ya existe'}), 409
        
        # Crear nuevo activo
        activo = Activo(
            codigo_activo=data['codigo_activo'],
            nombre_activo=data['nombre_activo'],
            descripcion=data.get('descripcion'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            numero_serie=data.get('numero_serie'),
            status=AssetStatus(data.get('status', 'En Bodega')),
            fecha_adquisicion=datetime.strptime(data['fecha_adquisicion'], '%Y-%m-%d').date(),
            costo_adquisicion=float(data['costo_adquisicion']),
            vida_util_meses=int(data.get('vida_util_meses', 36)),
            valor_residual=float(data.get('valor_residual', 0)),
            ubicacion_id=data.get('ubicacion_id'),
            usuario_asignado_id=data.get('usuario_asignado_id')
        )
        
        # Generar URL del QR
        activo.qr_url = f"{current_app.config['LABEL_BASE_URL']}/activo/{activo.codigo_activo}"
        
        db.session.add(activo)
        db.session.commit()
        
        return jsonify(activo.to_dict(include_relations=True)), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/activos/<int:activo_id>/qr', methods=['GET'])
def get_activo_qr(activo_id):
    """Genera y devuelve el código QR de un activo"""
    try:
        activo = Activo.query.get_or_404(activo_id)
        
        qr_url = activo.qr_url or f"{current_app.config['LABEL_BASE_URL']}/activo/{activo.codigo_activo}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = BytesIO()
        img.save(img_buffer, 'PNG')
        img_buffer.seek(0)
        
        return send_file(img_buffer, mimetype='image/png')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/ubicaciones', methods=['GET'])
def get_ubicaciones():
    """Obtiene lista de ubicaciones"""
    try:
        ubicaciones = Ubicacion.query.order_by(Ubicacion.nombre).all()
        return jsonify([ubicacion.to_dict() for ubicacion in ubicaciones])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/usuarios', methods=['GET'])
def get_usuarios():
    """Obtiene lista de usuarios"""
    try:
        usuarios = Usuario.query.order_by(Usuario.nombre_completo).all()
        return jsonify({'items': [usuario.to_dict() for usuario in usuarios]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/reportes/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Obtiene estadísticas para el dashboard"""
    try:
        stats = {
            'total_activos': Activo.query.count(),
            'activos_por_status': {},
            'activos_sin_ubicacion': Activo.query.filter_by(ubicacion_id=None).count(),
            'activos_sin_asignar': Activo.query.filter_by(usuario_asignado_id=None).count(),
            'auditorias_pendientes': 0
        }
        
        # Activos por status
        for status in AssetStatus:
            count = Activo.query.filter_by(status=status).count()
            stats['activos_por_status'][status.value] = count
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/buscar', methods=['GET'])
def buscar_global():
    """Búsqueda global en el sistema"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Se requiere un término de búsqueda'}), 400
        
        # Buscar activos
        activos = Activo.query.filter(
            or_(
                Activo.codigo_activo.ilike(f'%{query}%'),
                Activo.nombre_activo.ilike(f'%{query}%'),
                Activo.marca.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        return jsonify({
            'activos': [activo.to_dict() for activo in activos]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
