# Backend - API de Rutinas de Gimnasio

API RESTful en FastAPI + SQLModel + PostgreSQL para gestionar rutinas, ejercicios, filtros, duplicados, calendario y exportaciones.

## Requisitos previos
- Python 3.10+ (probado con 3.12.4)
- PostgreSQL en ejecución

## Instalación
```bash
# Crear y activar entorno virtual (Windows)
python -m venv venv
venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración de Base de Datos
- String de conexión (formato):
```
postgresql+psycopg2://USUARIO:CONTRASEÑA@HOST:PUERTO/NOMBRE_DB
```
- Ejemplo (según enunciado):
```
postgresql+psycopg2://postgres:umu192@localhost:5432/rutinas
```
- Variable de entorno necesaria: `DATABASE_URL`
- Ejemplo de archivo `.env` (copia `env.example`):
```
DATABASE_URL=postgresql+psycopg2://postgres:umu192@localhost:5432/rutinas
```
- Crear la base de datos vacía en PostgreSQL (p.ej. `rutinas`). No hay migraciones; las tablas se crean al iniciar (`init_db()` en startup).

## Ejecución
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Swagger/OpenAPI: `http://localhost:8000/docs`
- Puerto por defecto: 8000

## Endpoints principales
- Rutinas y ejercicios:
  - `GET /api/rutinas?limit&offset&dia_semana&ejercicio` (paginado + filtros)
  - `GET /api/rutinas/buscar?nombre=texto`
  - `GET /api/rutinas/{id}`
  - `POST /api/rutinas`
  - `PUT /api/rutinas/{id}`
  - `DELETE /api/rutinas/{id}`
  - `POST /api/rutinas/{id}/ejercicios`
  - `PUT /api/ejercicios/{id}`
  - `DELETE /api/ejercicios/{id}`
  - `POST /api/rutinas/{id}/duplicar`
- Estadísticas:
  - `GET /api/estadisticas`
- Exportación:
  - `GET /api/rutinas/export?formato=csv|pdf`
- Calendario:
  - `GET /api/planificaciones`
  - `POST /api/planificaciones`
  - `PUT /api/planificaciones/{plan_id}`
  - `DELETE /api/planificaciones/{plan_id}`

## Estructura del proyecto
```
backend/
  app/
    main.py        # Rutas y configuración FastAPI
    database.py    # Conexión y sesión SQLModel
    models.py      # Modelos SQLModel (rutinas, ejercicios, planificaciones)
    schemas.py     # Esquemas Pydantic
    crud.py        # Lógica de negocio CRUD/consultas
  requirements.txt
  env.example      # Ejemplo de .env con DATABASE_URL
```


