# 🔄 Guía de Migraciones - Wingman

## ⚡ TL;DR (lo esencial)

| Paso | Entorno | Comando / Acción |
|------|---------|------------------|
| 1 | Desarrollo | `flask --app backend.app db migrate && flask --app backend.app db upgrade` |

> **NOTA:** Si usas PowerShell, exporta la variable así antes de cualquier comando:
> ```powershell
> $env:FLASK_APP = "backend.app"
> ```
> O usa la opción `--app backend.app` en todos los comandos Flask.

- Si usas una app factory: `flask --app "backend.app:create_app()" db upgrade`
| 2 | Dev / Staging | `railway run python seed_railway.py` |
| 3 | Merge a Prod | `git checkout main && git merge development && git push` |
| 4 | Producción | Railway ejecuta automáticamente `flask db upgrade` |
| 5 | Seed maestros (una sola vez) | `curl -X POST https://www.wingsalsa.com/seed-master-data -H "X-Seed-Secret: <TU_SEED_SECRET>"` |
| 6 | Seguridad final | Eliminar el bloque del endpoint `/seed-master-data` en `backend/app.py` y hacer push |

Checklist rápido:
- [ ] Migraciones en dev ok
- [ ] Seed dev ok
- [ ] Merge a main
- [ ] Seed maestros en prod
- [ ] Endpoint `/seed-master-data` eliminado
- [ ] Verificación final en https://www.wingsalsa.com/

---

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


- `flight_duration` (Integer)
- `upwind_distance` (Float)
- `falls_count` (Integer)
- `max_speed` (Float)
- `avg_speed` (Float)
- `tricks_attempted` (Integer)
- `tricks_landed` (Integer)
- `water_time` (Integer)
- `preparation_time` (Integer)
- `session_type` (String)
- `motivation_level` (Integer)
- `energy_level_before` (Integer)
- `energy_level_after` (Integer)
- `goals_worked_on` (Text)
- `personal_bests` (Text)
 
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
# Ejecutar seed en desarrollo o staging
railway run python seed_railway.py
# O para datos maestros generales (en cualquier entorno):
railway run python seed_master_data.py
```

> **Nota:** El seed de datos maestros en producción se puede ejecutar mediante un endpoint temporal protegido:
>
> ```
> POST https://<tu-dominio>/seed-master-data
> Header: X-Seed-Secret: <TU_SEED_SECRET>
> ```
>
> Ejemplo con curl:
>
> ```bash
> curl -X POST https://www.wingsalsa.com/seed-master-data -H "X-Seed-Secret: mi_clave_supersecreta"
> ```
>
- Define la clave secreta en la variable de entorno `SEED_MASTER_SECRET` en Railway.
- El endpoint solo está disponible si `ENABLE_SEED_MASTER_ENDPOINT=1`.
- Asegúrate de deshabilitar esa variable tras ejecutarlo en producción para máxima seguridad.

---

### 🚨 Instrucciones para habilitar temporalmente el endpoint de seed

1. Define `ENABLE_SEED_MASTER_ENDPOINT=1` en las variables de entorno de tu despliegue.
2. Ejecuta el seed mediante el endpoint protegido.
3. Elimina o cambia a `0` la variable `ENABLE_SEED_MASTER_ENDPOINT` para deshabilitarlo nuevamente.

#### Checklist seguro para seed en producción
- [ ] Ejecutar el seed usando el endpoint temporal protegido
- [ ] Deshabilitar la variable `ENABLE_SEED_MASTER_ENDPOINT` tras su uso


### 4. Merge a Producción

```bash
# Después de validación exitosa
git checkout main
# Mergea tus cambios y haz push a producción
```

#### 🚀 Flujo de migraciones en producción (Railway)
- Cuando haces merge/push a la rama de producción (main), Railway ejecuta automáticamente `flask db upgrade` (según el Procfile).
- **No es necesario aplicar migraciones manualmente**: Railway detecta y aplica todas las migraciones pendientes en el entorno de producción.
- Solo ejecuta manualmente migraciones en casos excepcionales (errores, rollback, etc.).

#### Checklist actualizado
- [ ] Validar migraciones y seed en desarrollo/staging
- [ ] Ejecutar `seed_master_data.py` si necesitas poblar datos maestros
- [ ] Eliminar endpoints temporales antes de producción
- [ ] Hacer merge a main y push
- [ ] Railway aplicará automáticamente las migraciones en producción
- [ ] Validar datos y endpoints en https://www.wingsalsa.com/

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
web: flask db upgrade && gunicorn -w 4 -b 0.0.0.0:$PORT backend.wsgi:application
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
from backend.app import app
from backend.models.legacy import db
with app.app_context():
    print(db.engine.table_names())
"

# Verificar datos en Railway
railway run python -c "
from backend.app import app
from backend.models.legacy import GoalTemplate, Badge
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
