from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from enum import Enum
import enum

db = SQLAlchemy()

# =============================================================================
# ENUMS - Definición de tipos de datos categóricos
# =============================================================================

class AssetStatus(enum.Enum):
    EN_BODEGA = "En Bodega"
    ACTIVO = "Activo"
    EN_REPARACION = "En Reparación"
    EN_PRESTAMO = "En Préstamo"
    DADO_DE_BAJA = "Dado de Baja"

class UserRole(enum.Enum):
    ADMIN = "Admin"
    TECNICO = "Técnico"
    CONTADOR = "Contador"
    AUDITOR = "Auditor"
    EMPLEADO = "Empleado"

class MaintenanceType(enum.Enum):
    PREVENTIVO = "Preventivo"
    CORRECTIVO = "Correctivo"
    MEJORA = "Mejora"
    DIAGNOSTICO = "Diagnóstico"

class AuditStatus(enum.Enum):
    EN_PROGRESO = "En Progreso"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"

class ScanResult(enum.Enum):
    OK = "OK"
    UBICACION_INCORRECTA = "Ubicación Incorrecta"
    NO_ENCONTRADO = "No Encontrado"
    ACTIVO_DESCONOCIDO = "Activo Desconocido"

# =============================================================================
# MODELOS PRINCIPALES
# =============================================================================

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    rol = db.Column(db.Enum(UserRole), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    activos_asignados = db.relationship('Activo', foreign_keys='Activo.usuario_asignado_id', backref='usuario_asignado')
    compras_solicitadas = db.relationship('Compra', backref='solicitante')
    mantenimientos_realizados = db.relationship('Mantenimiento', backref='tecnico')
    auditorias_realizadas = db.relationship('Auditoria', backref='auditor')
    historial_movimientos = db.relationship('HistorialMovimiento', backref='usuario')

    def to_dict(self):
        return {
            'id': self.id,
            'nombre_completo': self.nombre_completo,
            'email': self.email,
            'rol': self.rol.value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Ubicacion(db.Model):
    __tablename__ = 'ubicaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    parent_ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'))
    
    # Relaciones
    parent_ubicacion = db.relationship('Ubicacion', remote_side=[id], backref='sub_ubicaciones')
    activos = db.relationship('Activo', backref='ubicacion')
    auditorias = db.relationship('Auditoria', backref='ubicacion_auditada')

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'parent_ubicacion_id': self.parent_ubicacion_id,
            'parent_ubicacion': self.parent_ubicacion.nombre if self.parent_ubicacion else None
        }

class Compra(db.Model):
    __tablename__ = 'compras'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.String(100))
    proveedor = db.Column(db.String(255))
    fecha_compra = db.Column(db.Date, nullable=False)
    solicitado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    activos = db.relationship('Activo', backref='compra')

    def to_dict(self):
        return {
            'id': self.id,
            'numero_factura': self.numero_factura,
            'proveedor': self.proveedor,
            'fecha_compra': self.fecha_compra.isoformat() if self.fecha_compra else None,
            'solicitado_por_id': self.solicitado_por_id,
            'solicitante': self.solicitante.nombre_completo if self.solicitante else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Activo(db.Model):
    __tablename__ = 'activos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_activo = db.Column(db.String(50), unique=True, nullable=False)
    nombre_activo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    numero_serie = db.Column(db.String(100), unique=True)
    status = db.Column(db.Enum(AssetStatus), default=AssetStatus.EN_BODEGA)
    fecha_adquisicion = db.Column(db.Date, nullable=False)
    costo_adquisicion = db.Column(db.Numeric(10, 2), nullable=False)
    vida_util_meses = db.Column(db.Integer, nullable=False, default=36)
    valor_residual = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    qr_url = db.Column(db.String(500))  # Campo optimización propuesta
    
    # Foreign Keys
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'))
    usuario_asignado_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    compra_id = db.Column(db.Integer, db.ForeignKey('compras.id'))
    ultima_auditoria_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Campos de auditoría
    ultima_auditoria_fecha = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    ultimo_auditor = db.relationship('Usuario', foreign_keys=[ultima_auditoria_por_id])
    mantenimientos = db.relationship('Mantenimiento', backref='activo', cascade='all, delete-orphan')
    historial = db.relationship('HistorialMovimiento', backref='activo', cascade='all, delete-orphan')
    auditoria_detalles = db.relationship('AuditoriaDetalle', backref='activo')

    def to_dict(self, include_relations=False):
        base_dict = {
            'id': self.id,
            'codigo_activo': self.codigo_activo,
            'nombre_activo': self.nombre_activo,
            'descripcion': self.descripcion,
            'marca': self.marca,
            'modelo': self.modelo,
            'numero_serie': self.numero_serie,
            'status': self.status.value,
            'fecha_adquisicion': self.fecha_adquisicion.isoformat() if self.fecha_adquisicion else None,
            'costo_adquisicion': float(self.costo_adquisicion) if self.costo_adquisicion else None,
            'vida_util_meses': self.vida_util_meses,
            'valor_residual': float(self.valor_residual) if self.valor_residual else None,
            'qr_url': self.qr_url,
            'ubicacion_id': self.ubicacion_id,
            'usuario_asignado_id': self.usuario_asignado_id,
            'compra_id': self.compra_id,
            'ultima_auditoria_fecha': self.ultima_auditoria_fecha.isoformat() if self.ultima_auditoria_fecha else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_relations:
            base_dict.update({
                'ubicacion': self.ubicacion.to_dict() if self.ubicacion else None,
                'usuario_asignado': self.usuario_asignado.to_dict() if self.usuario_asignado else None,
                'compra': self.compra.to_dict() if self.compra else None,
                'ultimo_auditor': self.ultimo_auditor.to_dict() if self.ultimo_auditor else None
            })
            
        return base_dict

class Mantenimiento(db.Model):
    __tablename__ = 'mantenimientos'
    
    id = db.Column(db.Integer, primary_key=True)
    activo_id = db.Column(db.Integer, db.ForeignKey('activos.id'), nullable=False)
    fecha_mantenimiento = db.Column(db.Date, nullable=False)
    tipo_mantenimiento = db.Column(db.Enum(MaintenanceType), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    costo = db.Column(db.Numeric(10, 2), default=0)
    realizado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'activo_id': self.activo_id,
            'fecha_mantenimiento': self.fecha_mantenimiento.isoformat() if self.fecha_mantenimiento else None,
            'tipo_mantenimiento': self.tipo_mantenimiento.value,
            'descripcion': self.descripcion,
            'costo': float(self.costo) if self.costo else 0,
            'realizado_por_id': self.realizado_por_id,
            'tecnico': self.tecnico.nombre_completo if self.tecnico else None
        }

class HistorialMovimiento(db.Model):
    __tablename__ = 'historial_movimientos'
    
    id = db.Column(db.Integer, primary_key=True)
    activo_id = db.Column(db.Integer, db.ForeignKey('activos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow)
    campo_modificado = db.Column(db.String(100))
    valor_anterior = db.Column(db.Text)
    valor_nuevo = db.Column(db.Text)
    nota = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'activo_id': self.activo_id,
            'usuario_id': self.usuario_id,
            'fecha_cambio': self.fecha_cambio.isoformat() if self.fecha_cambio else None,
            'campo_modificado': self.campo_modificado,
            'valor_anterior': self.valor_anterior,
            'valor_nuevo': self.valor_nuevo,
            'nota': self.nota,
            'usuario': self.usuario.nombre_completo if self.usuario else None
        }

class Auditoria(db.Model):
    __tablename__ = 'auditorias'
    
    id = db.Column(db.Integer, primary_key=True)
    ubicacion_auditada_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=False)
    auditor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime)
    status = db.Column(db.Enum(AuditStatus), default=AuditStatus.EN_PROGRESO)
    resumen = db.Column(db.Text)
    
    # Relaciones
    detalles = db.relationship('AuditoriaDetalle', backref='auditoria', cascade='all, delete-orphan')

    def to_dict(self, include_detalles=False):
        base_dict = {
            'id': self.id,
            'ubicacion_auditada_id': self.ubicacion_auditada_id,
            'auditor_id': self.auditor_id,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'status': self.status.value,
            'resumen': self.resumen,
            'ubicacion': self.ubicacion_auditada.nombre if self.ubicacion_auditada else None,
            'auditor': self.auditor.nombre_completo if self.auditor else None
        }
        
        if include_detalles:
            base_dict['detalles'] = [detalle.to_dict() for detalle in self.detalles]
            
        return base_dict

class AuditoriaDetalle(db.Model):
    __tablename__ = 'auditoria_detalles'
    
    id = db.Column(db.Integer, primary_key=True)
    auditoria_id = db.Column(db.Integer, db.ForeignKey('auditorias.id'), nullable=False)
    activo_id = db.Column(db.Integer, db.ForeignKey('activos.id'), nullable=False)
    resultado = db.Column(db.Enum(ScanResult), nullable=False)
    timestamp_scan = db.Column(db.DateTime, default=datetime.utcnow)
    nota = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'auditoria_id': self.auditoria_id,
            'activo_id': self.activo_id,
            'resultado': self.resultado.value,
            'timestamp_scan': self.timestamp_scan.isoformat() if self.timestamp_scan else None,
            'nota': self.nota,
            'activo': self.activo.codigo_activo if self.activo else None
        }
