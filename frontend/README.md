# Wingman Frontend - React SPA

Frontend moderno para la aplicación Wingman Companion App Motivacional, construido con React, Vite, Tailwind CSS y React Query.

## 🚀 Stack Tecnológico

- **React 18** - Framework principal
- **Vite** - Build tool y dev server
- **Tailwind CSS** - Styling y diseño responsivo
- **React Query** - State management y cache de API
- **React Router** - Navegación SPA
- **Axios** - Cliente HTTP con interceptors
- **Lucide React** - Iconografía moderna

## 🏗️ Arquitectura

```
src/
├── components/          # Componentes React principales
│   ├── Dashboard.jsx   # Vista principal con estadísticas
│   ├── Goals.jsx       # Gestión de objetivos
│   ├── Badges.jsx      # Sistema de logros
│   └── Navigation.jsx  # Navegación con iconos
├── services/
│   └── api.js          # Cliente API con configuración CORS
├── App.jsx             # Router principal
└── main.jsx            # Entry point con QueryClient
```

## 🔧 Desarrollo Local

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview
```

## 🚀 Despliegue en Railway

### Configuración Automática

El proyecto está configurado para despliegue automático en Railway con:

- **`railway.toml`** - Configuración de build y deploy
- **`.env.production`** - Variables de entorno para producción
- **`package.json`** - Script `start` optimizado para Railway

### Variables de Entorno

```bash
# Producción (Railway)
VITE_API_BASE_URL=https://wingman-dev.up.railway.app
NODE_ENV=production
```

### Pasos para Desplegar

1. **Crear nuevo proyecto en Railway**
   ```bash
   railway login
   railway init
   ```

2. **Configurar variables de entorno**
   - `VITE_API_BASE_URL`: URL del backend Flask
   - `NODE_ENV`: production

3. **Deploy automático**
   ```bash
   git push origin main
   ```

Railway detectará automáticamente el proyecto Node.js y ejecutará:
- `npm install` (dependencias)
- `npm run build` (build de producción)
- `npm start` (servidor de preview)

## 🔗 Integración Backend

### CORS Configurado

El backend Flask debe tener CORS configurado para permitir:
- `http://localhost:3000` (desarrollo)
- `https://*.up.railway.app` (Railway)

### Endpoints API

```javascript
// Goals
GET /api/user_goals
POST /api/create_goal
PATCH /api/update_goal_progress
GET /api/goal_templates

// Badges
GET /api/user_badges
GET /api/badges
POST /api/unlock_badge

// Stats
GET /api/motivational_stats
```

## 🎨 Componentes Principales

### Dashboard
- Estadísticas de objetivos y badges
- Progreso visual con barras
- Logros recientes

### Goals
- Crear objetivos desde templates
- Actualizar progreso (+1, +5)
- Estados de completado

### Badges
- Categorías y niveles de rareza
- Estados bloqueado/desbloqueado
- Efectos visuales

## 📱 Responsive Design

- **Mobile First** con Tailwind CSS
- **Breakpoints**: sm, md, lg, xl
- **Componentes adaptativos** para todas las pantallas

## 🔒 Autenticación

- **Cookies de sesión Flask** con `withCredentials: true`
- **Interceptors Axios** para manejo automático
- **Redirección** en caso de no autenticación

## 🚀 Performance

- **Code splitting** automático con Vite
- **React Query cache** para optimización de API
- **Lazy loading** de componentes
- **Source maps** para debugging

## 📋 Próximos Pasos

- [ ] Implementar autenticación completa
- [ ] Añadir notificaciones push
- [ ] Optimizar para PWA
- [ ] Tests unitarios con Vitest
- [ ] Storybook para componentes
