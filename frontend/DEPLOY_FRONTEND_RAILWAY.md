# 🚀 Despliegue del Frontend React en Railway

Esta guía explica paso a paso cómo desplegar el **frontend React** de Wingman en Railway, tanto en **entorno de desarrollo (DEV)** como en **producción (PROD)**.

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
