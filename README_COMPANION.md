# 🚀 Wingman Companion App Motivacional

## 📋 Descripción General

La **Companion App Motivacional** es una extensión del sistema Wingman que añade funcionalidades de gamificación, seguimiento de objetivos y motivación para usuarios de wingfoil. El sistema permite a los usuarios establecer metas personalizadas, seguir su progreso y desbloquear logros (badges) basados en su rendimiento.

## 🎯 Características Principales

### ✅ Sistema de Objetivos
- **Plantillas predefinidas**: Objetivos comunes categorizados por técnica, resistencia, consistencia y progresión
- **Objetivos personalizados**: Los usuarios pueden crear metas específicas adaptadas a sus necesidades
- **Seguimiento de progreso**: Actualización en tiempo real del avance hacia los objetivos
- **Estados dinámicos**: Activo, completado, pausado, expirado

### 🏆 Sistema de Badges (Logros)
- **Categorías diversas**: Hitos, técnica, resistencia, motivación, especiales
- **Niveles de rareza**: Común, raro, épico, legendario
- **Criterios automáticos**: Lógica para desbloqueo basada en actividad del usuario
- **Sistema de puntos**: Recompensas cuantificables por logros

### 📊 Tracking Motivacional Avanzado
- **Métricas detalladas**: Duración de vuelo, caídas, velocidad, trucos
- **Estados emocionales**: Niveles de motivación y energía por sesión
- **Análisis de progreso**: Estadísticas y tendencias de rendimiento
- **Contexto de sesión**: Condiciones, ubicación, tipo de entrenamiento

## 🏗️ Arquitectura Técnica

### Modelo de Datos

#### Nuevas Entidades
- **`GoalTemplate`**: Plantillas maestras de objetivos reutilizables
- **`UserGoal`**: Objetivos activos específicos por usuario
- **`Badge`**: Definición de logros y criterios de desbloqueo
- **`UserBadge`**: Relación usuario-badge con contexto de desbloqueo

#### Extensiones
- **`Session`**: Ampliada con 15+ campos nuevos para tracking motivacional detallado
- **`User`**: Mantiene compatibilidad con relaciones existentes

### API REST Endpoints

#### Gestión de Objetivos
```
GET    /api/goal_templates     # Plantillas disponibles
GET    /api/user_goals         # Objetivos activos del usuario
POST   /api/create_goal        # Crear nuevo objetivo
PATCH  /api/update_goal_progress # Actualizar progreso
```

#### Sistema de Badges
```
GET    /api/badges             # Badges disponibles y desbloqueados
POST   /api/unlock_badge       # Desbloquear logro específico
```

#### Estadísticas
```
GET    /api/session_stats      # Métricas motivacionales agregadas
```

### Stack Tecnológico

- **Backend**: Flask + SQLAlchemy
- **Base de Datos**: PostgreSQL (Railway en producción)
- **Migraciones**: Alembic/Flask-Migrate
- **Autenticación**: Sesiones Flask existentes
- **Formato de Datos**: JSON REST API

## 🗃️ Estructura de Base de Datos

### Tablas Principales

#### `goal_template`
Plantillas maestras de objetivos con categorización, dificultad y valores por defecto.

#### `user_goal`
Objetivos activos vinculados a usuarios con progreso, fechas y estado.

#### `badge`
Definición de logros con criterios, puntos y niveles de rareza.

#### `user_badge`
Relación many-to-many entre usuarios y badges desbloqueados.

#### `session` (extendida)
Tracking detallado con métricas de vuelo, motivación y contexto de entrenamiento.

## 🌱 Datos Iniciales (Seeds)

### Plantillas de Objetivos
- **Técnica**: Dominar el Jibe, Primeros Saltos, Waterstart Consistente
- **Resistencia**: Sesión de 2 Horas, Vuelo Continuo 30min
- **Progresión**: Subir de Nivel, Navegar en Viento Fuerte
- **Consistencia**: Racha de 7 Días, 20 Sesiones en un Mes

### Badges Iniciales
- **Hitos**: Primera Sesión, Adicto al Wingfoil
- **Técnica**: Primer Waterstart, Primer Jibe, Maestro del Jibe, Saltador
- **Consistencia**: Guerrero del Fin de Semana, Racha de Fuego
- **Especiales**: Madrugador, Guerrero de Viento, Explorador
- **Motivación**: Energía Positiva, Objetivo Cumplido, Coleccionista

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.8+
- PostgreSQL (local) o Railway (producción)
- Flask + SQLAlchemy
- Alembic para migraciones

### Configuración Local

1. **Aplicar migraciones**
```bash
python -m flask db upgrade
```

2. **Crear tablas manualmente (si es necesario)**
```python
from app import app
from models import db
with app.app_context():
    db.create_all()
```

3. **Ejecutar seed de datos iniciales**
```bash
# Opción 1: Script optimizado para Railway
python seed_railway.py

# Opción 2: Script original
python run_seed.py

# Opción 3: Script independiente
python seed_companion_data.py
```

### Deployment en Railway

#### Estado Actual 
- **Migraciones**: Aplicadas exitosamente en Railway
- **Tablas**: Creadas correctamente (`goal_template`, `badge`, `user_goal`, `user_badge`)
- **Pendiente**: Ejecutar seed de datos iniciales

#### Pasos para Deployment

1. **Verificar tablas en Railway**
   - Las tablas ya están creadas pero vacías
   - Verificar en Railway Dashboard > Data > PostgreSQL

2. **Ejecutar seed en Railway**
```bash
# Opción A: Railway CLI (recomendado)
railway run python seed_railway.py

# Opción B: Endpoint temporal (una vez desplegado)
GET https://tu-app.railway.app/deploy-companion
```

3. **Verificar datos**
```bash
# Verificar que los datos se crearon correctamente
railway run python -c "
from app import app
from models import GoalTemplate, Badge
with app.app_context():
    print(f'Plantillas: {GoalTemplate.query.count()}')
    print(f'Badges: {Badge.query.count()}')
"
```

#### Scripts de Deployment Disponibles

| Script | Propósito | Uso |
|--------|-----------|-----|
| `seed_railway.py` | **Recomendado** - Optimizado para Railway | `python seed_railway.py` |
| `run_seed.py` | Seed con contexto Flask completo | `python run_seed.py` |
| `seed_companion_data.py` | Seed independiente | `python seed_companion_data.py` |
| `/deploy-companion` | Endpoint web temporal | `GET /deploy-companion` |

## 🧪 Testing y Validación

### Endpoints de Prueba
- **Plantillas**: `GET /api/goal_templates`
- **Badges**: `GET /api/badges`
- **Objetivos**: `GET /api/user_goals` (requiere autenticación)

### Script de Pruebas
Ejecutar `test_api.ps1` para validación completa de endpoints.

## 🔄 Integración con Sistema Existente

### Compatibilidad
- **Sin breaking changes**: Mantiene funcionalidad existente intacta
- **Extensión progresiva**: Añade capacidades sin afectar código legacy
- **Autenticación unificada**: Usa sistema de sesiones Flask existente

### Puntos de Integración
- **Dashboard**: Widgets de progreso y badges en interfaz principal
- **Sesiones**: Tracking automático de métricas motivacionales
- **Perfil de Usuario**: Visualización de logros y estadísticas

## 📈 Próximos Pasos

### Fase 3: Frontend Motivacional
- **Dashboard responsivo**: Visualización de objetivos y progreso
- **Gamificación visual**: Animaciones y feedback de logros
- **Notificaciones**: Alertas de progreso y nuevos badges
- **Analytics**: Gráficos de tendencias y estadísticas

### Mejoras Futuras
- **IA Motivacional**: Recomendaciones personalizadas de objetivos
- **Social Features**: Competencias y rankings entre usuarios
- **Integración IoT**: Datos automáticos de sensores y wearables
- **Notificaciones Push**: Recordatorios y celebraciones de logros

## 🔧 Mantenimiento

### Monitoreo
- **Logs de API**: Seguimiento de uso de endpoints
- **Métricas de Engagement**: Análisis de adopción de funcionalidades
- **Performance**: Optimización de queries de estadísticas

### Escalabilidad
- **Índices de BD**: Optimización para consultas frecuentes
- **Caching**: Redis para datos de badges y plantillas
- **API Rate Limiting**: Protección contra abuso

---

## 📞 Soporte Técnico

Para dudas sobre implementación, consultar:
- **Documentación API**: Endpoints en `companion_api.py`
- **Modelos de Datos**: Esquemas en `models.py`
- **Scripts de Utilidad**: `run_seed.py`, `test_api.ps1`

**Estado**:  **Funcional y listo para desarrollo frontend**
