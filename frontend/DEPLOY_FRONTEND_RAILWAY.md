# 🚀 Frontend Deployment Guide for Railway

This guide explains how to deploy the Wingman React frontend to Railway, covering both **development (DEV)** and **production (PROD)** environments. It also documents the purpose and relationship of all configuration files.

## 📁 Configuration Files Overview

| File | Purpose | Relationship |
|------|---------|--------------|
| `Dockerfile` | Defines the container build process using Nginx as the web server | Used when `builder = "DOCKERFILE"` in railway.toml |
| `nginx.conf` | Nginx server configuration for routing, proxying, and serving static files | Used by the Dockerfile to configure Nginx |
| `nixpacks.toml` | Alternative build configuration for Nixpacks (simpler than Docker) | Used when `builder = "nixpacks"` in railway.toml |
| `railway.toml` | Railway-specific deployment configuration | Controls the deployment process on Railway |
| `.env.production` | Environment variables for production builds | Used during the build process |

### Detailed Configuration Files

#### 1. `Dockerfile`
Defines how to build the container image:
- Uses Node.js to build the React app
- Uses Nginx to serve the built static files
- Handles environment variables at runtime
- Configures proper ports and routing

#### 2. `nginx.conf`
Nginx web server configuration that:
- Serves static files from `/usr/share/nginx/html`
- Proxies API requests to the backend service
- Handles client-side routing with SPA fallback
- Configures compression and caching
- Sets security headers

#### 3. `nixpacks.toml`
Alternative build configuration that specifies:
- Required system packages (Node.js)
- Build commands (`npm ci`, `npm run build`)
- Start command (`npx serve -s dist`)
- Environment variables

#### 4. `railway.toml`
Railway-specific settings that:
- Specifies the build method (Dockerfile or Nixpacks)
- Defines environment variables
- Configures deployment behavior
- Can override build and start commands

#### 5. `.env.production`
Contains production environment variables that are baked into the build:
- `VITE_API_BASE_URL` - Backend API URL
- `NODE_ENV` - Environment mode (production)

---
## Deployment Guide

This guide explains how to deploy the **React frontend** to Railway, for both **development (DEV)** and **production (PROD)** environments.

---
## 1. Prerrequisitos

| Herramienta | Versión recomendada |
|-------------|---------------------|
| Node.js     | 18.x o superior     |
| npm         | 8.x o superior      |
| Railway CLI | 3.x o superior      |
| Git         | Acceso al repo      |

---
## 2. Configuración de Archivos

### 2.1 Estructura relevante
```
frontend/
├── railway.toml          # Configuración Railway Nixpacks
├── .env.production       # Variables de entorno para producción
├── package.json          # Scripts de build & start
└── src/                  # Código fuente React
```

### 2.2 `railway.toml`
Este archivo ya está configurado para usar **Nixpacks** y exponer la aplicación en el puerto **3000**.

```
[build]
builder = "nixpacks"

[deploy]
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10

[env]
NODE_ENV = "production"
VITE_API_BASE_URL = "https://wingman-dev.up.railway.app"
```
> 🔄 **Reemplaza** `VITE_API_BASE_URL` por la URL del backend de PRODUCCIÓN cuando pases a prod.

### 2.3 `.env.production`
```
VITE_API_BASE_URL=https://wingman-dev.up.railway.app
NODE_ENV=production
```
---
## 3. Despliegue en DEV

1. Inicia sesión y crea servicio:
   ```bash
   cd frontend/
   railway login
   railway init  # Selecciona «New Project»
   ```
2. En el dashboard de Railway:
   - Abre **Variables** y añade:
     - `VITE_API_BASE_URL` → `https://wingman-dev.up.railway.app`
     - `NODE_ENV` → `production`
3. Genera el dominio público:
   - Sección **Networking → Generate Service Domain**
   - Puerto a exponer: **3000**
   - Se generará algo como `https://supportive-ambition-dev.up.railway.app`.
4. Push al repositorio:
   ```bash
   git add .
   git commit -m "Deploy frontend to Railway DEV"
   git push origin main   # o la rama relevante
   ```
   Railway ejecutará automáticamente:
   - `npm install`
   - `npm run build`
   - `npm start` (`vite preview` en puerto $PORT)
5. Verifica el build visitando la URL generada.

---
## 4. Actualizar Backend (CORS)

Asegúrate de que el backend Flask incluya en CORS:
```
https://supportive-ambition-dev.up.railway.app
```
> Ya se agregó en `backend/app.py`, junto con `https://*.up.railway.app` para flexibilidad.

---
## 5. Migración a Producción

1. Crea **nueva instancia** Railway (o renombra la actual):
   ```bash
   railway init  # dentro de frontend/ seleccionar New Project "wingman-frontend-prod"
   ```
2. Variables de entorno:
   - `VITE_API_BASE_URL` → `https://wingman-dev.up.railway.app` (cambiar a backend de prod p.ej. `https://api.wingsalsa.com`)
3. Genera dominio personalizado o usa tu propio dominio (p.ej. `https://app.wingsalsa.com`).
4. Añade el nuevo dominio a CORS backend (`https://www.wingsalsa.com` o el que corresponda).
5. **Push / Deploy**.

---
## 6. Troubleshooting

| Problema | Solución |
|----------|----------|
| `CORS error` | Confirma que la URL del frontend está en la lista de `origins` CORS del backend y que `supports_credentials=True`. |
| `404 /api` | Asegúrate de que `VITE_API_BASE_URL` apunta correctamente al backend y que los endpoints incluyan `/api/*`. |
| `Invalid source map` | Deshabilita `sourcemap` en `vite.config.js` en prod si no lo necesitas. |

---
## 7. Referencias rápidas

- **Railway CLI docs:** <https://docs.railway.app/develop/cli>
- **Vite preview docs:** <https://vitejs.dev/guide/build.html#vite-preview>
- **Flask-CORS:** <https://flask-cors.readthedocs.io/en/latest/>

---
### © Wingman 2025 / Jorge
