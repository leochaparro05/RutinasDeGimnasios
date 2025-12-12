# Frontend - Rutinas de Gimnasio

SPA en React + Vite para gestionar rutinas y ejercicios consumiendo el backend FastAPI.

## Requisitos previos
- Node.js 18+
- npm o yarn

## Instalación
```bash
cd frontend
npm install
```

## Configuración
Define la URL del backend mediante variable de entorno Vite:
```
VITE_API_URL=http://localhost:8000
```
Puedes crear un archivo `.env` en `frontend/` con esa línea.

## Ejecución
- Desarrollo: `npm run dev` (puerto 5173 por defecto)
- Producción: `npm run build` y luego `npm run preview`

## Tecnologías usadas
- React 18
- Vite 5
- Axios

## Estructura
```
frontend/
  src/
    App.jsx       # UI principal y lógica CRUD
    api.js        # Cliente Axios
    main.jsx      # Render raíz
    styles.css    # Estilos básicos
  vite.config.js
  package.json
  index.html
```


