# Backend - API de Rutinas de Gimnasio

API RESTful para gestionar rutinas de gimnasio y sus ejercicios con FastAPI y PostgreSQL.

## Requisitos previos
- Python 3.10+
- PostgreSQL en ejecución (usuario por defecto `postgres`, contraseña `umu192` según enunciado)

## Instalación
```bash
python -m venv venv
venv\\Scripts\\activate  # En Windows
pip install -r requirements.txt
```

## Configuración de Base de Datos
1) Define la variable de entorno `DATABASE_URL` con el string de conexión:
```
postgresql+psycopg2://USUARIO:CONTRASEÑA@HOST:PUERTO/NOMBRE_DB
```
Ejemplo usando las credenciales del enunciado:
```
postgresql+psycopg2://postgres:umu192@localhost:5432/rutinas
```
2) Crea la base de datos vacía en PostgreSQL (p.ej. `rutinas`).
3) Opcional: copia `env.example` a `.env` y ajusta el valor.

Las tablas se crean automáticamente al iniciar la app.

## Ejecución
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
La documentación interactiva está en `http://localhost:8000/docs`.

## Endpoints principales
- `GET /api/rutinas` listar rutinas
- `GET /api/rutinas/{id}` detalle
- `GET /api/rutinas/buscar?nombre=texto` búsqueda parcial (case-insensitive)
- `POST /api/rutinas` crear (con ejercicios opcionales)
- `PUT /api/rutinas/{id}` actualizar datos
- `DELETE /api/rutinas/{id}` eliminar (cascada sobre ejercicios)
- `POST /api/rutinas/{id}/ejercicios` agregar ejercicio a rutina
- `PUT /api/ejercicios/{id}` actualizar ejercicio
- `DELETE /api/ejercicios/{id}` eliminar ejercicio

## Estructura del proyecto
```
backend/
  app/
    main.py          # FastAPI y rutas
    database.py      # Conexión y sesión
    models.py        # Modelos SQLModel
    schemas.py       # Esquemas Pydantic
    crud.py          # Lógica CRUD
  requirements.txt
  env.example        # Ejemplo de configuración
```


