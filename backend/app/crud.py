from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlmodel import select

from .models import Ejercicio, Rutina
from .schemas import EjercicioCreate, EjercicioUpdate, RutinaCreate, RutinaUpdate


class UniqueNameError(Exception):
    """Se lanza cuando el nombre de rutina ya existe."""


def listar_rutinas(session: Session, limit: int, offset: int) -> Tuple[List[Rutina], int]:
    """Devuelve rutinas con paginación y el total para UI."""
    statement = select(Rutina).order_by(Rutina.creado_en.desc()).offset(offset).limit(limit)
    items = session.exec(statement).all()
    total = session.exec(select(func.count()).select_from(Rutina)).one()
    return items, total


def obtener_rutina(session: Session, rutina_id: int) -> Optional[Rutina]:
    """Busca una rutina por ID."""
    return session.get(Rutina, rutina_id)


def buscar_rutinas(session: Session, nombre: str) -> List[Rutina]:
    """Búsqueda parcial, case-insensitive, por nombre."""
    pattern = f"%{nombre}%"
    statement = select(Rutina).where(Rutina.nombre.ilike(pattern)).order_by(Rutina.nombre)
    return session.exec(statement).all()


def crear_rutina(session: Session, rutina_data: RutinaCreate) -> Rutina:
    """Crea una rutina y opcionalmente sus ejercicios iniciales."""
    rutina = Rutina(nombre=rutina_data.nombre, descripcion=rutina_data.descripcion)
    session.add(rutina)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise UniqueNameError from exc
    session.refresh(rutina)

    # Crear ejercicios iniciales respetando el orden dado
    for idx, ejercicio in enumerate(rutina_data.ejercicios):
        crear_ejercicio(session, rutina.id, ejercicio, orden_default=idx)
    session.refresh(rutina)
    return rutina


def actualizar_rutina(session: Session, rutina: Rutina, data: RutinaUpdate) -> Rutina:
    """Actualiza nombre/descripcion de una rutina."""
    if data.nombre is not None:
        rutina.nombre = data.nombre
    if data.descripcion is not None:
        rutina.descripcion = data.descripcion
    try:
        session.add(rutina)
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise UniqueNameError from exc
    session.refresh(rutina)
    return rutina


def eliminar_rutina(session: Session, rutina: Rutina) -> None:
    """Elimina rutina y ejercicios (cascada configurada en el modelo)."""
    session.delete(rutina)
    session.commit()


def crear_ejercicio(
    session: Session, rutina_id: int, data: EjercicioCreate, orden_default: int | None = None
) -> Ejercicio:
    """Crea un ejercicio ligado a una rutina."""
    ejercicio = Ejercicio(
        rutina_id=rutina_id,
        nombre=data.nombre,
        dia_semana=data.dia_semana,
        series=data.series,
        repeticiones=data.repeticiones,
        peso=data.peso,
        notas=data.notas,
        orden=data.orden if data.orden is not None else orden_default,
    )
    session.add(ejercicio)
    session.commit()
    session.refresh(ejercicio)
    return ejercicio


def actualizar_ejercicio(session: Session, ejercicio: Ejercicio, data: EjercicioUpdate) -> Ejercicio:
    """Actualiza campos de un ejercicio existente."""
    if data.nombre is not None:
        ejercicio.nombre = data.nombre
    if data.dia_semana is not None:
        ejercicio.dia_semana = data.dia_semana
    if data.series is not None:
        ejercicio.series = data.series
    if data.repeticiones is not None:
        ejercicio.repeticiones = data.repeticiones
    if data.peso is not None:
        ejercicio.peso = data.peso
    if data.notas is not None:
        ejercicio.notas = data.notas
    if data.orden is not None:
        ejercicio.orden = data.orden

    session.add(ejercicio)
    session.commit()
    session.refresh(ejercicio)
    return ejercicio


def eliminar_ejercicio(session: Session, ejercicio: Ejercicio) -> None:
    """Borra un ejercicio."""
    session.delete(ejercicio)
    session.commit()


