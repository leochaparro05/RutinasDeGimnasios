## Proyecto: Gestor de Rutinas de Gimnasio (FastAPI + React)

Documento de apoyo para repasar, continuar y defender el trabajo práctico.

Este documento irá creciendo a medida que agreguemos secciones. Esta versión cubre la arquitectura general y el resumen detallado del backend, adaptado al código actual del repo.

---

## Arquitectura general

- **Backend**: FastAPI + SQLModel + PostgreSQL. API REST con CRUD de rutinas/ejercicios, búsqueda, validaciones y exportación CSV/PDF.
- **Frontend**: React 18 + Vite. UI con pestañas para listar, buscar, crear, editar, ver estadísticas y calendario; consumo de la API con Axios. (Nota: en este proyecto no se usa React Router, se manejan pestañas en un único componente).
- **Comunicación**: HTTP/JSON; CORS abierto para desarrollo (configurado en FastAPI).

---

## Backend (resumen detallado)

Rutas relevantes: `backend/app/` (`main.py`, `database.py`, `models.py`, `schemas.py`, `crud.py`).

### 1) Configuración y base de datos
- `database.py`: carga `.env` con `python-dotenv`, define `DATABASE_URL` (por defecto `postgresql+psycopg2://postgres:umu192@localhost:5432/rutinas`), crea el `engine`, expone `init_db()` para crear tablas en startup y `get_session()` para inyectar sesiones por request.  
  Motivo: centralizar la conexión y asegurarse de que las tablas existan al arrancar.
- No hay `config.py` separado; la configuración se concentra en `database.py` y en variables de entorno.
- Archivos de apoyo: `env.example` como plantilla de `.env`; `test-backend.ps1` crea venv, instala deps, verifica `.env` y lanza uvicorn.

### 2) Modelos y validaciones (SQLModel)
- `models.py`:
  - Enum `DiaSemana` (Lunes-Domingo) usado para validar días.
  - `Rutina`: `id`, `nombre` único, `descripcion`, `creado_en`, relación 1:N con `Ejercicio`, borrado en cascada (`cascade all, delete-orphan`).
  - `Ejercicio`: `nombre`, `dia_semana`, `series`, `repeticiones`, `peso` opcional, `notas`, `orden` opcional, `rutina_id` FK.
  - `Planificacion`: `fecha` única + `rutina_id` para calendario.
  Motivo: representar el modelo solicitado y asegurar integridad referencial y borrado en cascada de ejercicios.

### 3) Esquemas (payloads Pydantic)
- `schemas.py` separa entrada/salida:
  - `RutinaCreate/Update/Read` y `EjercicioCreate/Update/Read`; `RutinaRead` incluye lista de ejercicios y `creado_en`.
  - Validaciones: series/reps > 0; peso > 0 si se envía; orden opcional.
  - `PlanificacionCreate/Update/Read` para el calendario.
  Motivo: controlar opcionales, validar datos de negocio y evitar exponer campos internos.

### 4) Endpoints principales (definidos en `main.py`)
- Salud: `GET /health`.
- Rutinas:
  - Listar con paginación y filtros: `GET /api/rutinas?limit&offset&dia_semana&ejercicio`.
  - Búsqueda parcial: `GET /api/rutinas/buscar?nombre=`.
  - Detalle: `GET /api/rutinas/{rutina_id}`.
  - Crear: `POST /api/rutinas` (opcionalmente con ejercicios iniciales).
  - Actualizar: `PUT /api/rutinas/{rutina_id}`.
  - Eliminar: `DELETE /api/rutinas/{rutina_id}` (borra ejercicios en cascada).
  - Duplicar: `POST /api/rutinas/{rutina_id}/duplicar` (clona ejercicios, genera nombre único).
  - Exportar CSV/PDF: `GET /api/rutinas/export?formato=csv|pdf` (nota: el archivo tiene dos definiciones del endpoint; prevalece la última).
- Ejercicios:
  - Agregar a rutina: `POST /api/rutinas/{rutina_id}/ejercicios`.
  - Actualizar: `PUT /api/ejercicios/{ejercicio_id}`.
  - Eliminar: `DELETE /api/ejercicios/{ejercicio_id}`.
- Estadísticas: `GET /api/estadisticas` (totales, top rutinas por cantidad de ejercicios, días más entrenados).
- Calendario: CRUD de planificaciones en `/api/planificaciones`, con validación de rutina existente y fecha única (si existe, actualiza; si no, crea).

### 5) Lógica de negocio (resumen de `crud.py`)
- Listado con filtros: usa joins para filtrar por día y nombre de ejercicio, y retorna también el total paginado.
- Creación de rutina: valida unicidad de nombre (lanza `UniqueNameError` si colisiona); permite crear ejercicios iniciales respetando orden.
- Duplicado de rutina: genera nombre libre (`(copia)`, `(copia 2)`, etc.) y clona todos los ejercicios.
- Estadísticas: totales de rutinas/ejercicios, top 5 rutinas por cantidad de ejercicios y conteo de ejercicios por día de la semana.
- Planificaciones: fecha única; si se intenta crear con fecha existente, actualiza la rutina asignada en vez de duplicar registros.

### 6) Ejecución y pruebas rápidas
- Requisitos previos: Python 3.10+, PostgreSQL activo.
- Setup rápido (Windows):
  1. `python -m venv venv`
  2. `venv\Scripts\Activate.ps1`
  3. `pip install -r requirements.txt`
  4. Crear `backend/.env` (copiar `env.example`) y ajustar `DATABASE_URL`.
  5. `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Verificación: `GET /health`; documentación: `http://localhost:8000/docs`.

---

## Routers y endpoints

En este proyecto, las rutas están definidas directamente en `app/main.py` (no hay subcarpeta `routers/`). Aun así, cubren los mismos casos que el bloque original del PDF:

- Prefijo `/api/rutinas`:
  - `GET /api/rutinas`: lista rutinas con ejercicios, paginado, con filtros opcionales por día y nombre de ejercicio.
  - `GET /api/rutinas/buscar?nombre=`: búsqueda case-insensitive por nombre.
  - `GET /api/rutinas/{id}`: detalle de rutina.
  - `POST /api/rutinas`: crea rutina (con ejercicios opcionales); valida unicidad de nombre.
  - `PUT /api/rutinas/{id}`: actualiza nombre/descr. de rutina; los ejercicios se gestionan en endpoints separados (no se sincronizan en bloque).
  - `DELETE /api/rutinas/{id}`: elimina rutina y ejercicios (cascada).
  - `POST /api/rutinas/{id}/duplicar`: clona rutina y sus ejercicios, generando nombre único.
  - `GET /api/rutinas/export?formato=csv|pdf`: exporta rutinas + ejercicios; el archivo define el endpoint dos veces, prevalece la última definición.
- Ejercicios:
  - `POST /api/rutinas/{id}/ejercicios`: crea ejercicio ligado a una rutina.
  - `PUT /api/ejercicios/{id}`: actualiza ejercicio.
  - `DELETE /api/ejercicios/{id}`: elimina ejercicio.
- Estadísticas:
  - `GET /api/estadisticas`: totales, top por cantidad de ejercicios y ejercicios por día (no incluye promedio explícito, pero se reportan totales y top).
- Calendario:
  - `GET/POST/PUT/DELETE /api/planificaciones`: agenda por fecha única; si se crea con fecha existente, actualiza.

Notas de adaptación vs PDF:
- No existe `routers/routines.py` ni `routers/exercises.py`; toda la API se monta en `main.py`.
- La sincronización de ejercicios en bloque vía `PUT /rutinas/{id}` no está implementada; se maneja ejercicio a ejercicio con endpoints dedicados.

## App y CORS
- `main.py`: crea la instancia FastAPI, habilita CORS abierto para desarrollo (`allow_origins=["*"]`), registra rutas y ejecuta `init_db()` en `startup`. Expone `GET /health` como chequeo de vida.

## Dependencias y documentación
- `requirements.txt`: FastAPI, Uvicorn, SQLModel, psycopg2-binary, python-dotenv, fpdf2.
- `backend/README.md`: requisitos, instalación, `.env`, creación de DB, comando de ejecución (`uvicorn app.main:app --reload --port 8000`), endpoints y estructura del proyecto.

---

## Frontend (resumen detallado)

Rutas relevantes: `frontend/src/` (`App.jsx`, `api.js`, `styles.css`, `main.jsx`).

### 1) Bootstrap y dependencias
- Vite + React 18.
- Dependencias añadidas: `axios` (HTTP). En este proyecto no se usa `react-router-dom` ni `react-hot-toast`; la navegación se resuelve con pestañas internas en `App.jsx`.

### 2) Cliente API
- `api.js`: instancia Axios con `baseURL` desde `VITE_API_URL` (fallback `http://localhost:8000`). Expone helpers para rutinas, ejercicios, estadísticas, planificaciones y exportación:
  - Rutinas: `fetchRutinas`, `searchRutinas`, `createRutina`, `updateRutina`, `deleteRutina`, `duplicateRutina`.
  - Ejercicios: `addEjercicio`, `updateEjercicio`, `deleteEjercicio`.
  - Estadísticas: `fetchStats`.
  - Calendario: `fetchPlanificaciones`, `createPlanificacion`, `updatePlanificacion`, `deletePlanificacion`.
  - Exportación: `exportRutinas(formato="csv"|"pdf")` (usa `responseType: "blob"`).

### 3) Layout y estructura de vistas
- `App.jsx`: componente único que maneja pestañas (no hay rutas SPA):
  - Tabs: `listar`, `crear`, `estadisticas`, `calendario`.
  - Estado global: rutinas, filtros, búsqueda, paginación, ejercicios en edición, estadísticas, planificaciones, drag & drop, errores y cargando.
- `main.jsx`: punto de entrada que renderiza `<App />` y aplica `styles.css`.
- `styles.css`: estilos base (cards, grids, badges, botones, tabs, fondos con gradiente).

### 4) Vistas y funcionalidades (dentro de `App.jsx`)
- Listar:
  - Búsqueda en vivo por nombre; filtros por día y texto de ejercicio; paginación 10/pg.
  - Acciones por rutina: duplicar, renombrar (prompt), eliminar (confirm).
  - Ejercicios agrupados por día; drag & drop para reordenar (persiste `orden`).
  - CRUD de ejercicios en la tarjeta (agregar, editar inline, borrar).
  - Exportar CSV/PDF (llama al endpoint de exportación y descarga blob).
- Crear:
  - Formulario de rutina con ejercicios opcionales; convierte números antes de enviar; usa `POST /api/rutinas`.
- Estadísticas:
  - Muestra totales de rutinas/ejercicios, top por ejercicios y días más entrenados; botón “Refrescar”.
- Calendario:
  - Semana actual (7 días desde hoy); asignar rutina por fecha; si ya existe, se actualiza; permite eliminar asignación.

### 5) Estilos
- `styles.css` ya contiene un layout pulido con tarjetas, grids, tabs y botones con gradientes. No se usan otros frameworks de estilos.

---

## README frontend
- `frontend/README.md`: especifica requisitos (Node 18+), instalación (`npm install`), `.env` con `VITE_API_URL`, comandos de desarrollo/producción (`npm run dev`, `npm run build`, `npm run preview`), estructura del proyecto y breve descripción de las vistas.

---

## Cómo ejecutar

Backend:
1. `cd backend`
2. `python -m venv venv` y activar (`venv\Scripts\Activate.ps1` en Windows)
3. `pip install -r requirements.txt`
4. Crear la base vacía en PostgreSQL (en el repo se usa `rutinas`; el PDF sugería `gym_routines`)
5. `.env` con `DATABASE_URL=postgresql+psycopg2://postgres:umu192@localhost:5432/rutinas` (ajusta usuario/clave/DB según tu entorno)
6. `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
7. Swagger: `http://localhost:8000/docs`

Frontend:
1. `cd frontend`
2. `npm install`
3. `.env` con `VITE_API_URL=http://localhost:8000`
4. `npm run dev` (puerto 5173 por defecto)

---

## Guion para explicar en la mesa
1. Arquitectura: React (cliente) ↔ FastAPI (API) ↔ PostgreSQL (DB). CORS abierto para desarrollo.
2. Modelo: `Rutina` 1:N `Ejercicio`; enum de días; validaciones de positivos y unicidad; cascada al borrar ejercicios.
3. Flujos (adaptados al código actual):
   - Alta: formulario en pestaña “Crear” → `POST /api/rutinas` con ejercicios anidados opcionales.
   - Listado/búsqueda: `GET /api/rutinas` con filtros, `GET /api/rutinas/buscar`; tarjetas con acciones (duplicar, renombrar, eliminar) y CRUD de ejercicios inline.
   - Detalle/visualización: se muestra dentro de la pestaña “Listar”; ejercicios agrupados por día y orden; permite editar/borrar ejercicios ahí mismo.
   - Edición de rutina: `PUT /api/rutinas/{id}` (solo nombre/descr.); los ejercicios se editan vía endpoints dedicados (`PUT /api/ejercicios/{id}`); no hay sincronización masiva de ejercicios en un único PUT.
   - Baja: `DELETE /api/rutinas/{id}` con confirmación en frontend; ejercicios se borran en cascada.
   - Calendario: asigna rutinas a fechas (`/api/planificaciones`); si la fecha existe, se actualiza la rutina.
   - Exportar: botones CSV/PDF llaman a `/api/rutinas/export`.
4. Configuración: `.env` backend para la DB; `.env` frontend para la URL de la API.
5. Ejecución: comandos de arranque (venv + uvicorn, npm run dev).
6. Validaciones y UX: validaciones en servidor (Pydantic + SQLModel), validaciones básicas en cliente (números a enteros, requeridos); manejo de errores y estados de carga en la UI.

---

## Próximos pasos (para continuar)
- Pulir estilos: la UI ya usa `styles.css` con cards y gradientes; se puede refinar responsividad y estados hover/focus.
- Añadir feedback de éxito/fracaso (toasts): hoy se muestran errores simples; se podría integrar `react-hot-toast` o similar.
- Ya implementado en este proyecto: paginación, filtros por día y por texto de ejercicio, drag & drop de orden de ejercicios, export CSV/PDF, calendario.
- Pendiente/no implementado: autenticación.
- Probar flujos completos: alta, listado/búsqueda, edición (rutina y ejercicios), borrado, duplicado, export, estadísticas y calendario.

---

# Guía para defender en la mesa (en criollo)

## Qué contar de entrada
- Arquitectura: FastAPI + SQLModel + PostgreSQL (backend) y React/Vite (frontend). Responsabilidades separadas: datos/lógica vs interfaz. CORS abierto para desarrollo.
- Modelo de datos: Rutina 1:N Ejercicios, enum de días, validaciones en servidor y checks básicos en cliente.
- Documentación: Swagger en `/docs` y README con pasos de ejecución; script `test-backend.ps1` ayuda a levantar rápido.

## Decisiones clave (y por qué)
- **FastAPI + SQLModel**: tipado, validaciones y OpenAPI automático; SQLModel une modelos y Pydantic. Sin migraciones (no Alembic) para rapidez en el TP; `create_all` crea tablas al arrancar.
- **PostgreSQL**: requerido; cadena en `.env` para no hardcodear credenciales.
- **Relación 1:N (Rutina-Ejercicio)**: cascada para no dejar ejercicios huérfanos; enum de días evita valores inválidos.
- **Validaciones**: nombre único de rutina (excepción `UniqueNameError`), series/reps > 0, peso opcional > 0; el cliente convierte números antes de enviar.
- **Búsqueda**: `GET /api/rutinas/buscar?nombre=` case-insensitive y parcial.
- **Edición**: el backend permite editar rutina y editar ejercicios por endpoints separados; no hay sincronización masiva de ejercicios en un solo PUT (a diferencia del PDF original).
- **Frontend**: React + Vite por velocidad; navegación por pestañas en `App.jsx` (no React Router ni Chakra en este proyecto). Drag & drop para ordenar ejercicios, calendario semanal, exportación CSV/PDF, y CRUD inline de ejercicios.
- **Estado vacío/UX**: se muestran mensajes y estados de carga; faltan toasts pero el flujo básico está cubierto con mensajes simples.

---

(Si quieres añadir más detalle de prueba paso a paso o capturas, dime y lo sumo.) 

---

## Flujos que tenés que poder relatar (según el código actual)
- **Alta**: formulario en pestaña “Crear” valida básicos y convierte números; hace `POST /api/rutinas` con ejercicios opcionales en un viaje.
- **Edición**: rutina se edita con `PUT /api/rutinas/{id}` (nombre/descr.); ejercicios se editan individualmente con `PUT /api/ejercicios/{id}`. No hay PUT masivo que sincronice/elimine ejercicios omitidos (difiere del PDF original).
- **Baja**: `DELETE /api/rutinas/{id}` borra rutina y, por cascada, ejercicios.
- **Búsqueda**: input que llama a `/api/rutinas/buscar`; si está vacío, recarga la lista completa paginada.
- **Detalle**: se muestra dentro de “Listar”; agrupa ejercicios por día y orden; se ve descripción y acciones; `creado_en` no se exhibe en UI actualmente (está disponible en la API).
- **Errores/feedback**: se manejan mensajes de error simples en el estado; no hay toasts implementados (a diferencia del PDF). Inputs con estilo claro en `styles.css`.

## Cómo justificar las decisiones
- **Simplicidad vs. robustez**: sin Alembic para migraciones; `create_all` basta para el TP. Si escala, se agrega migraciones.
- **Validaciones en ambos lados**: cliente valida lo básico y convierte a números; servidor refuerza (Pydantic/SQLModel) y retorna mensajes claros.
- **CORS abierto en dev**: facilita pruebas con Vite; en producción se limitarían orígenes.
- **Frontend sin router ni theming avanzado**: tabs internas simplifican; no hay modo claro/oscuro dinámico ni cambio de logos por tema (a diferencia del PDF con Chakra). UX se resuelve con estilos propios en `styles.css`.

## Qué decir si preguntan “qué falta”
- Migraciones (Alembic), tests automáticos, autenticación/roles.
- Ya implementado aquí: paginación, filtros por día y por ejercicio, drag & drop de orden, export CSV/PDF, calendario.
- Podría añadirse: CI/CD, manejo de versiones de API, toasts de feedback, theming claro/oscuro, exponer `creado_en` en la UI de detalle.

---

## Mini guion rápido (3-4 minutos) — adaptado a este proyecto
1) Arquitectura: FastAPI + SQLModel + PostgreSQL / React + Vite (sin Chakra ni router; tabs internas).  
2) Modelo: Rutina 1:N Ejercicio, enum de días, cascade delete, unicidad de nombre.  
3) Endpoints clave: CRUD + búsqueda; edición de ejercicios es por endpoints dedicados (no PUT masivo).  
4) Front: listar/buscar con filtros y paginación, detalle por día/orden, formularios crear y editar, drag & drop, export, stats y calendario; sin toasts ni modo oscuro.  
5) Cómo correr: backend (venv, requirements, `.env`, uvicorn), frontend (npm install, `VITE_API_URL`, `npm run dev`).  
6) Export y stats: CSV/PDF desde frontend (botones) y endpoint dedicado; stats con totales/top/días (no se calcula promedio explícito).  
7) Qué mejoraría si hay tiempo: migraciones, tests, auth, toasts, theming, CI/CD.

## Frases cortas para responder (ajustadas al código)
- “Validé nombre único y números positivos; no se pisan rutinas ni se cargan ejercicios con valores inválidos.”
- “Los ejercicios se editan con su propio endpoint; no hay PUT masivo de sincronización (a diferencia del PDF).”
- “Búsqueda case-insensitive con contains; el cliente consulta en vivo.”
- “CORS abierto solo en dev; en prod lo restringiría.”
- “Exporta CSV/PDF y tiene stats (totales, top por ejercicios, días más entrenados).”
- “Hay paginación, filtros y drag & drop de orden en la vista de rutinas; calendario semanal para asignar rutinas.”

## Checklist antes de la mesa
- Backend: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` con DB creada y `.env` apuntando a Postgres.
- Frontend: `npm run dev` con `VITE_API_URL=http://localhost:8000`.
- Probar un flujo completo: crear → ver → editar (agregar/quitar ejercicio) → buscar → borrar → duplicar → exportar → ver stats → asignar en calendario.
- Tener a mano el comando de conexión DB y el `.env` de ejemplo (sin credenciales reales).

---

## Decisiones y comparaciones (para justificar) — Backend
- **FastAPI + SQLModel** vs Django/Flask/ORM raw: se eligió FastAPI por tipado, validaciones y OpenAPI automático; SQLModel simplifica modelos + esquemas. Django era más pesado para el TP; Flask requería más código manual.
- **Sin Alembic**: se priorizó velocidad con `create_all`. Si el proyecto crece, se agregan migraciones.
- **Enum de días** vs texto libre: evita typos y facilita estadísticas por día.
- **Cascade delete** vs soft delete: mantiene la base limpia sin históricos; evita ejercicios huérfanos. Con soft delete habría que filtrar activos y mantener consistencia extra.
- **Validaciones en servidor**: unicidad de nombre (via `UniqueNameError`), series/reps > 0, peso opcional > 0. Se podrían reforzar con constraints únicos a nivel DB si escala.
- **CORS abierto solo en dev**: facilita pruebas con Vite; en producción se limitarían dominios.
- **Export CSV/PDF**: CSV por interoperabilidad; PDF para lectura amigable. Se usa `fpdf2`; alternativa sería HTML + WeasyPrint u otra librería más pesada.
- **Stats con queries agregadas**: en este código ya se usan `COUNT/GROUP BY` (totales, top, días). Si creciera, podría cachearse o materializar vistas para rendimiento.

### Frontend
- **React + Vite** vs CRA: Vite es más rápido en dev/build.
- **Chakra/UI frameworks**: en este proyecto no se usa Chakra ni MUI/Ant; se optó por estilos propios en `styles.css` para mantener liviano. (El PDF original mencionaba Chakra).
- **State con hooks locales**: no se usa Redux/Context porque el estado es acotado (lista, loading, error, filtros, ejercicios en edición). Si creciera, se podría llevar a un store global.
- **Sin React Router**: se usan pestañas internas en `App.jsx` para CRUD y vistas; alternativa sería router y vistas separadas.
- **Sin toasts**: feedback simple por estado/errores; se podría añadir `react-hot-toast` si se requiere.
- **Export desde frontend**: descarga blob con filename correcto para CSV/PDF, sin dependencias extra.

### Datos y modelo
- **Rutina 1:N Ejercicio**: refleja el negocio; evita tablas intermedias innecesarias.
- **Campos numéricos positivos**: series/reps > 0; peso opcional (> 0 si se envía); evita datos basura.
- **Orden en ejercicio**: entero opcional para ordenar; se puede reordenar con drag & drop en la UI.

### Qué haría distinto con más tiempo
- Agregar **migraciones Alembic**, **tests** (Pytest y RTL), **auth/roles**, **toasts** y **theming** (claro/oscuro).
- Router de vistas (en vez de tabs) si crecieran las secciones.
- Índice único a nivel DB y constraints reforzadas; handlers globales de errores y logs estructurados.
- CI/CD y despliegue con CORS restringido en producción.

### Riesgos/limitaciones actuales
- Sin autenticación ni permisos.
- Sin migraciones: cambios de modelo requieren recrear/ajustar la DB manualmente.
- Stats: calculadas con agregaciones simples; con muchos registros podría requerir caching/materialización.
- Export sin paginación: volúmenes grandes tardarán más (usa todo el dataset).

