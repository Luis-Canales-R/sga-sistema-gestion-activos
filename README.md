# 🏷️ Sistema de Gestión de Activos (SGA)

<div align="center">

![SGA Logo](https://img.shields.io/badge/SGA-v1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Flask](https://img.shields.io/badge/Flask-3.0+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Sistema completo de gestión de activos empresariales con generación de etiquetas QR, auditorías en tiempo real e interface móvil optimizada.**

</div>

## ⚡ Instalación Rápida

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/sga-sistema-gestion-activos.git
cd sga-sistema-gestion-activos

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env

# 5. Inicializar base de datos
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"

# 6. Ejecutar aplicación
python run.py
```

## 🎯 Acceso al Sistema

Una vez ejecutando:

```
🏠 Dashboard:          http://localhost:5000/
👨‍💼 Panel Admin:        http://localhost:5000/admin
📱 Interface Móvil:    http://localhost:5000/mobile
🔍 Scanner QR:         http://localhost:5000/mobile/scan
🏷️ Etiquetas:          http://localhost:5000/print-labels
🔌 API:                http://localhost:5000/api/
```

## ✨ Características

- ✅ **Gestión completa de activos** con códigos QR automáticos
- ✅ **Generador de etiquetas profesionales** (múltiples tamaños)
- ✅ **Dashboard inteligente** con estadísticas en tiempo real
- ✅ **Interface móvil PWA** con scanner QR
- ✅ **Sistema de auditorías** por ubicación
- ✅ **API RESTful completa**
- ✅ **Migración desde sistemas legacy**

## 🛠️ Stack Tecnológico

- **Backend**: Flask 3.0+, SQLAlchemy
- **Frontend**: Bootstrap 5, Chart.js
- **QR/Labels**: qrcode + Pillow
- **Mobile**: PWA con ZXing scanner
- **Database**: SQLite/PostgreSQL
- **Deploy**: Docker ready

## 📚 Documentación

Para documentación completa, ver la [Wiki del proyecto](../../wiki).

## 🤝 Contribuir

Las contribuciones son bienvenidas. Ver [CONTRIBUTING.md](CONTRIBUTING.md) para detalles.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.
