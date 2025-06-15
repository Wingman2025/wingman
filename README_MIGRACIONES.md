# 🔄 Guía de Migraciones - Wingman

Esta guía documenta los procesos y mejores prácticas para las migraciones de base de datos en el proyecto Wingman, especialmente para la Companion App Motivacional.

## 📋 Índice

1. [Entornos de Deployment](#entornos-de-deployment)
2. [Estructura de Migraciones](#estructura-de-migraciones)
3. [Proceso de Desarrollo](#proceso-de-desarrollo)
4. [Scripts de Diagnóstico](#scripts-de-diagnóstico)
5. [Deployment Automático](#deployment-automático)
6. [Comandos Estándar](#comandos-estándar)
7. [Mejores Prácticas](#mejores-prácticas)

## 🌍 Entornos de Deployment

### Desarrollo
- **URL**: `https://wingman-dev.up.railway.app/`
- **Base de datos**: PostgreSQL en Railway (desarrollo)
- **Propósito**: Testing y desarrollo de features

### Producción
- **URL**: `https://www.wingsalsa.com/`
- **Base de datos**: PostgreSQL en Railway (producción)
- **Proceso**: Merge desde desarrollo después de validación

### Flujo de Trabajo
```
Desarrollo Local → Railway Dev → Validación → Merge → Railway Prod
```

## 🏗️ Estructura de Migraciones

### Migración Principal: Companion App
**Archivo**: `migrations/versions/20250615_add_companion_app_tables.py`
**Revisión**: `20250615_companion`

#### Tablas Creadas:
1. **`goal_template`** - Plantillas de objetivos maestros
2. **`user_goal`** - Objetivos activos por usuario
3. **`badge`** - Sistema de logros/badges
4. **`user_badge`** - Badges desbloqueados por usuario

#### Columnas Añadidas a `session`:
- `duration_minutes` (Integer)
- `distance_km` (Float)
- `falls_count` (Integer)
- `jibes_count` (Integer)
- `jumps_count` (Integer)

### Cadena de Dependencias:
```
20250614_add_goal_fields → 20250615_seed_levels → 20250615_companion
```

## 🔄 Proceso de Desarrollo

### 1. Desarrollo Local

```bash
# Crear nueva migración
flask db migrate -m "descripcion_cambio"

# Aplicar migraciones localmente
flask db upgrade

# Verificar cambios
python diagnose_migrations.py
```

### 2. Testing en Desarrollo

```bash
# Push a rama de desarrollo
git push origin development

# Railway auto-deploya
# Verificar en: https://wingman-dev.up.railway.app/

# Ejecutar diagnóstico remoto
railway run python diagnose_migrations.py
```

### 3. Validación y Seed

```bash
# Ejecutar seed en desarrollo
railway run python seed_railway.py

# O usar endpoint temporal (si existe)
GET https://wingman-dev.up.railway.app/deploy-companion
```

### 4. Merge a Producción

```bash
# Después de validación exitosa
git checkout main
git merge development
git push origin main

# Railway auto-deploya a producción
# Verificar en: https://www.wingsalsa.com/
```

## 🔍 Scripts de Diagnóstico

### `diagnose_migrations.py`

**Propósito**: Verificar estado de migraciones y datos

```bash
# Local
python diagnose_migrations.py

# Railway (desarrollo)
railway run python diagnose_migrations.py

# Railway (producción)
railway run python diagnose_migrations.py --environment production
```

**Funciones**:
- ✅ Verificar estado de migraciones Alembic
- ✅ Listar tablas existentes
- ✅ Contar registros en cada tabla
- ✅ Detectar inconsistencias

## 🚀 Deployment Automático

### Configuración Railway

**Procfile**:
```
web: flask db upgrade && gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:application
```

### Variables de Entorno

#### Desarrollo
```bash
DATABASE_URL=postgresql://... (dev)
FLASK_ENV=development
RAILWAY_ENVIRONMENT=development
```

#### Producción
```bash
DATABASE_URL=postgresql://... (prod)
FLASK_ENV=production
RAILWAY_ENVIRONMENT=production
```

### Proceso Automático

1. **Git Push** → Railway detecta cambios
2. **Build** → Instala dependencias
3. **Migrate** → `flask db upgrade`
4. **Deploy** → `gunicorn` inicia app
5. **Verify** → Endpoints disponibles

## 🛠️ Comandos Estándar

### Migraciones

```bash
# Crear migración
flask db migrate -m "add_new_feature"

# Aplicar migraciones
flask db upgrade

# Ver historial
flask db history

# Ver migración actual
flask db current

# Revertir (solo en desarrollo)
flask db downgrade
```

### Railway CLI

```bash
# Login
railway login

# Seleccionar proyecto
railway link

# Ejecutar comandos
railway run flask db upgrade
railway run python seed_railway.py
railway run python diagnose_migrations.py

# Ver logs
railway logs

# Conectar a DB
railway connect postgresql
```

### Verificación de Estado

```bash
# Verificar tablas localmente
python -c "
from app import app, db
with app.app_context():
    print(db.engine.table_names())
"

# Verificar datos en Railway
railway run python -c "
from app import app
from models import GoalTemplate, Badge
with app.app_context():
    print(f'Plantillas: {GoalTemplate.query.count()}')
    print(f'Badges: {Badge.query.count()}')
"
```

## ✅ Mejores Prácticas

### 1. Migraciones

- **Nombres descriptivos**: `flask db migrate -m "add_companion_app_tables"`
- **Revisiones incrementales**: Una feature por migración
- **Testing local**: Siempre probar antes de push
- **Backup antes de prod**: Respaldar DB antes de merge

### 2. Seeds

- **Idempotencia**: Verificar existencia antes de crear
- **Datos mínimos**: Solo datos esenciales para funcionalidad
- **Versionado**: Mantener seeds en control de versiones
- **Separación por entorno**: Seeds diferentes para dev/prod si necesario

### 3. Deployment

- **Validación en dev**: Probar completamente antes de merge
- **Monitoreo**: Verificar logs durante deployment
- **Rollback plan**: Tener plan de reversión si falla
- **Documentación**: Actualizar docs con cada cambio

### 4. Base de Datos

- **Constraints**: Definir foreign keys y constraints apropiados
- **Índices**: Añadir índices para queries frecuentes
- **Tipos de datos**: Usar tipos apropiados (no over-engineer)
- **Naming**: Convenciones consistentes para tablas y columnas

## 📊 Modelo de Datos Actual

### Tablas Principales

```sql
-- Plantillas de objetivos
goal_template (id, title, description, category, difficulty_level, ...)

-- Objetivos activos por usuario  
user_goal (id, user_id, goal_template_id, title, target_value, current_progress, ...)

-- Sistema de badges
badge (id, name, description, icon, category, criteria, points_value, rarity)

-- Badges desbloqueados
user_badge (id, user_id, badge_id, unlocked_at)

-- Sesiones extendidas
session (id, user_id, ..., duration_minutes, distance_km, falls_count, jibes_count, jumps_count)
```

### Relaciones

```
User 1:N UserGoal N:1 GoalTemplate
User 1:N UserBadge N:1 Badge
User 1:N Session
```

## 🎯 Checklist de Deployment

### Pre-Deployment
- [ ] Migraciones probadas localmente
- [ ] Seeds ejecutados y verificados
- [ ] Tests pasando
- [ ] Documentación actualizada

### Deployment a Desarrollo
- [ ] Push a rama development
- [ ] Verificar auto-deployment en Railway
- [ ] Ejecutar diagnóstico remoto
- [ ] Probar endpoints principales
- [ ] Verificar datos poblados

### Deployment a Producción
- [ ] Validación completa en desarrollo
- [ ] Backup de base de datos de producción
- [ ] Merge a main
- [ ] Monitorear deployment
- [ ] Verificar funcionalidad en https://www.wingsalsa.com/
- [ ] Confirmar datos migrados correctamente

---

## 🎯 Conclusión

Este documento establece los procesos estándar para migraciones en el proyecto Wingman. Siguiendo estas prácticas se garantiza:

- **Deployments consistentes** entre entornos
- **Datos íntegros** en desarrollo y producción  
- **Procesos repetibles** y documentados
- **Rollbacks seguros** cuando sea necesario

**Estado Actual**: ✅ **PRODUCTION READY**

---

*Última actualización: 2025-06-15*
*Entornos: Desarrollo (wingman-dev.up.railway.app) → Producción (www.wingsalsa.com)*
