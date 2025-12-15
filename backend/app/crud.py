from typing import List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlmodel import select

from .models import DiaSemana, Ejercicio, Rutina, Planificacion
from .schemas import (
    EjercicioCreate,
    EjercicioUpdate,
    PlanificacionCreate,
    PlanificacionUpdate,
    RutinaCreate,
    RutinaUpdate,
)


class UniqueNameError(Exception):
    """Se lanza cuando el nombre de rutina ya existe."""


def listar_rutinas(
    session: Session,
    limit: int,
    offset: int,
    dia_semana: Optional[DiaSemana] = None,
    ejercicio_nombre: Optional[str] = None,
) -> Tuple[List[Rutina], int]:
    """Devuelve rutinas con paginación y el total para UI, con filtros opcionales."""

    stmt = select(Rutina)
    # Si hay filtros por ejercicio/día, hacemos join con ejercicios
    if dia_semana or ejercicio_nombre:
        stmt = stmt.join(Ejercicio)
        if dia_semana:
            stmt = stmt.where(Ejercicio.dia_semana == dia_semana)
        if ejercicio_nombre:
            stmt = stmt.where(Ejercicio.nombre.ilike(f"%{ejercicio_nombre}%"))
        stmt = stmt.distinct()

    stmt = stmt.order_by(Rutina.creado_en.desc()).offset(offset).limit(limit)
    items = session.exec(stmt).all()

    # Conteo total respetando filtros
    count_stmt = select(func.count(func.distinct(Rutina.id)))
    if dia_semana or ejercicio_nombre:
        count_stmt = count_stmt.join(Ejercicio)
        if dia_semana:
            count_stmt = count_stmt.where(Ejercicio.dia_semana == dia_semana)
        if ejercicio_nombre:
            count_stmt = count_stmt.where(Ejercicio.nombre.ilike(f"%{ejercicio_nombre}%"))

    total = session.exec(count_stmt).one()
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


def _generar_nombre_copia(session: Session, nombre_base: str) -> str:
    """
    Genera un nombre único para la copia.
    Ej: "Piernas" -> "Piernas (copia)" -> "Piernas (copia 2)" ...
    """
    candidato = f"{nombre_base} (copia)"
    contador = 2
    while session.exec(select(Rutina).where(Rutina.nombre == candidato)).first():
        candidato = f"{nombre_base} (copia {contador})"
        contador += 1
    return candidato


def duplicar_rutina(session: Session, rutina_id: int, nuevo_nombre: Optional[str]) -> Rutina:
    """Duplica una rutina y todos sus ejercicios."""
    original = session.get(Rutina, rutina_id)
    if not original:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")  # type: ignore

    nombre_copia = nuevo_nombre or _generar_nombre_copia(session, original.nombre)
    copia = Rutina(nombre=nombre_copia, descripcion=original.descripcion)
    session.add(copia)
    session.commit()
    session.refresh(copia)

    # Copiar ejercicios asociados
    for ej in original.ejercicios:
        nuevo_ej = Ejercicio(
            rutina_id=copia.id,
            nombre=ej.nombre,
            dia_semana=ej.dia_semana,
            series=ej.series,
            repeticiones=ej.repeticiones,
            peso=ej.peso,
            notas=ej.notas,
            orden=ej.orden,
        )
        session.add(nuevo_ej)
    session.commit()
    session.refresh(copia)
    return copia


def obtener_estadisticas(session: Session) -> dict:
    """Calcula estadísticas básicas de uso de rutinas/ejercicios."""
    total_rutinas = session.exec(select(func.count()).select_from(Rutina)).one()
    total_ejercicios = session.exec(select(func.count()).select_from(Ejercicio)).one()

    # Top rutinas por cantidad de ejercicios (máximo 5)
    top_stmt = (
        select(Rutina.id, Rutina.nombre, func.count(Ejercicio.id).label("ejercicios"))
        .join(Ejercicio, Ejercicio.rutina_id == Rutina.id)
        .group_by(Rutina.id, Rutina.nombre)
        .order_by(func.count(Ejercicio.id).desc(), Rutina.nombre)
        .limit(5)
    )
    top_rutinas = [
        {"id": r.id, "nombre": r.nombre, "ejercicios": r.ejercicios} for r in session.exec(top_stmt)
    ]

    # Días más entrenados (conteo de ejercicios por día)
    dias_stmt = (
        select(Ejercicio.dia_semana, func.count(Ejercicio.id).label("ejercicios"))
        .group_by(Ejercicio.dia_semana)
        .order_by(func.count(Ejercicio.id).desc())
    )
    dias_mas_entrenados = [
        {"dia_semana": r.dia_semana, "ejercicios": r.ejercicios} for r in session.exec(dias_stmt)
    ]

    return {
        "total_rutinas": total_rutinas,
        "total_ejercicios": total_ejercicios,
        "top_rutinas": top_rutinas,
        "dias_mas_entrenados": dias_mas_entrenados,
    }


# Planificaciones (calendario)
def listar_planificaciones(session: Session) -> List[Planificacion]:
    return session.exec(select(Planificacion).order_by(Planificacion.fecha)).all()


def obtener_plan_por_fecha(session: Session, fecha) -> Optional[Planificacion]:
    stmt = select(Planificacion).where(Planificacion.fecha == fecha)
    return session.exec(stmt).first()


def crear_planificacion(session: Session, data: PlanificacionCreate) -> Planificacion:
    plan = Planificacion(fecha=data.fecha, rutina_id=data.rutina_id)
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


def actualizar_planificacion(session: Session, plan: Planificacion, data: PlanificacionUpdate) -> Planificacion:
    if data.fecha is not None:
        plan.fecha = data.fecha
    if data.rutina_id is not None:
        plan.rutina_id = data.rutina_id
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


def eliminar_planificacion(session: Session, plan: Planificacion) -> None:
    session.delete(plan)
    session.commit()


