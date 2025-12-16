# Frontend - Rutinas de Gimnasio

SPA en React + Vite que consume la API FastAPI: CRUD de rutinas/ejercicios, búsqueda, filtros, duplicado, drag & drop, estadísticas, calendario y exportacion de rutinas en csv o pdf.

## Requisitos previos
- Node.js 18+
- npm o yarn

## Instalación
```bash
cd frontend
npm install
```

## Configuración
- URL del backend (Vite env):
```
VITE_API_URL=http://localhost:8000
```
- Crear `.env` en `frontend/` con esa línea o exportarla en la sesión antes de `npm run dev`.

## Ejecución
- Desarrollo: `npm run dev` (puerto 5173 por defecto)
- Producción: `npm run build`
- Previsualizar build: `npm run preview`

## Tecnologías utilizadas
- React 18
- Vite 5
- Axios

## Estructura del proyecto
```
frontend/
  src/
    App.jsx     # UI principal: tabs (Listar/Crear/Estadísticas/Calendario), filtros, drag & drop
    api.js      # Cliente Axios y funciones de exportación/planificación
    main.jsx    # Render raíz
    styles.css  # Estilos y temas
  vite.config.js
  package.json
  index.html
```


