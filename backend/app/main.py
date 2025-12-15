from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud
from .database import get_session, init_db
from .models import DiaSemana, Ejercicio, Rutina
from .schemas import (
    EjercicioCreate,
    EjercicioRead,
    EjercicioUpdate,
    RutinaCreate,
    RutinaDuplicatePayload,
    RutinaListResponse,
    RutinaRead,
    RutinaUpdate,
    EstadisticasResponse,
)

# Configuración base de la aplicación FastAPI
app = FastAPI(title="API de Rutinas de Gimnasio", version="1.0.0")

# CORS abierto para facilitar pruebas desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Se ejecuta al arrancar: crea tablas si no existen."""
    init_db()


@app.get("/")
def root():
    """Endpoint raíz de verificación rápida."""
    return {"message": "API de Rutinas de Gimnasio está funcionando", "docs": "/docs"}


@app.get("/health")
def health_check():
    """Endpoint de salud para monitoreo."""
    return {"status": "ok", "message": "Servidor funcionando correctamente"}


# Rutinas
@app.get("/api/rutinas", response_model=RutinaListResponse)
def listar_rutinas(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    dia_semana: DiaSemana | None = Query(None),
    ejercicio: str | None = Query(None, min_length=1),
    session: Session = Depends(get_session),
) -> RutinaListResponse:
    """Listar rutinas con paginación (limit/offset) y filtros opcionales."""
    items, total = crud.listar_rutinas(
        session,
        limit=limit,
        offset=offset,
        dia_semana=dia_semana,
        ejercicio_nombre=ejercicio,
    )
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@app.get("/api/rutinas/buscar", response_model=list[RutinaRead])
def buscar_rutinas(
    nombre: str = Query(..., min_length=1),
    session: Session = Depends(get_session),
) -> list[Rutina]:
    """Búsqueda parcial por nombre (case-insensitive)."""
    return crud.buscar_rutinas(session, nombre)


@app.get("/api/rutinas/{rutina_id}", response_model=RutinaRead)
def obtener_rutina(rutina_id: int, session: Session = Depends(get_session)) -> Rutina:
    """Obtener detalle de una rutina por ID."""
    rutina = crud.obtener_rutina(session, rutina_id)
    if not rutina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rutina no encontrada")
    return rutina


@app.post("/api/rutinas", response_model=RutinaRead, status_code=status.HTTP_201_CREATED)
def crear_rutina(rutina: RutinaCreate, session: Session = Depends(get_session)) -> Rutina:
    """Crear rutina (con ejercicios opcionales)."""
    try:
        return crud.crear_rutina(session, rutina)
    except crud.UniqueNameError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una rutina con ese nombre"
        )


@app.put("/api/rutinas/{rutina_id}", response_model=RutinaRead)
def actualizar_rutina(
    rutina_id: int, data: RutinaUpdate, session: Session = Depends(get_session)
) -> Rutina:
    """Actualizar nombre/descripcion de rutina."""
    rutina = crud.obtener_rutina(session, rutina_id)
    if not rutina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rutina no encontrada")
    try:
        return crud.actualizar_rutina(session, rutina, data)
    except crud.UniqueNameError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una rutina con ese nombre"
        )


@app.post("/api/rutinas/{rutina_id}/duplicar", response_model=RutinaRead, status_code=201)
def duplicar_rutina(
    rutina_id: int, data: RutinaDuplicatePayload | None = None, session: Session = Depends(get_session)
) -> Rutina:
    """Duplicar una rutina y sus ejercicios; permite opcionalmente renombrarla."""
    return crud.duplicar_rutina(session, rutina_id, nuevo_nombre=data.nombre if data else None)


@app.get("/api/estadisticas", response_model=EstadisticasResponse)
def obtener_estadisticas(session: Session = Depends(get_session)) -> EstadisticasResponse:
    """Estadísticas básicas: totales, top rutinas y días más entrenados."""
    return crud.obtener_estadisticas(session)


@app.delete("/api/rutinas/{rutina_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_rutina(rutina_id: int, session: Session = Depends(get_session)) -> None:
    """Eliminar rutina y sus ejercicios (cascada)."""
    rutina = crud.obtener_rutina(session, rutina_id)
    if not rutina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rutina no encontrada")
    crud.eliminar_rutina(session, rutina)


# Ejercicios
@app.post(
    "/api/rutinas/{rutina_id}/ejercicios",
    response_model=EjercicioRead,
    status_code=status.HTTP_201_CREATED,
)
def agregar_ejercicio(
    rutina_id: int, data: EjercicioCreate, session: Session = Depends(get_session)
) -> Ejercicio:
    """Agregar ejercicio a una rutina existente."""
    rutina = crud.obtener_rutina(session, rutina_id)
    if not rutina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rutina no encontrada")
    return crud.crear_ejercicio(session, rutina_id, data)


@app.put("/api/ejercicios/{ejercicio_id}", response_model=EjercicioRead)
def actualizar_ejercicio(
    ejercicio_id: int, data: EjercicioUpdate, session: Session = Depends(get_session)
) -> Ejercicio:
    """Actualizar un ejercicio existente."""
    ejercicio = session.get(Ejercicio, ejercicio_id)
    if not ejercicio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ejercicio no encontrado")
    return crud.actualizar_ejercicio(session, ejercicio, data)


@app.delete("/api/ejercicios/{ejercicio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ejercicio(ejercicio_id: int, session: Session = Depends(get_session)) -> None:
    """Eliminar un ejercicio por ID."""
    ejercicio = session.get(Ejercicio, ejercicio_id)
    if not ejercicio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ejercicio no encontrado")
    crud.eliminar_ejercicio(session, ejercicio)


