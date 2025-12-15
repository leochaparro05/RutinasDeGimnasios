from datetime import datetime, date
from enum import Enum
from typing import List, Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel
from sqlalchemy import Date


class DiaSemana(str, Enum):
    """Enum restringido a los días válidos."""

    lunes = "Lunes"
    martes = "Martes"
    miercoles = "Miércoles"
    jueves = "Jueves"
    viernes = "Viernes"
    sabado = "Sábado"
    domingo = "Domingo"


class Ejercicio(SQLModel, table=True):
    """Tabla de ejercicios asociados a una rutina."""

    __tablename__ = "ejercicios"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)
    dia_semana: DiaSemana
    series: int
    repeticiones: int
    peso: Optional[float] = None
    notas: Optional[str] = None
    orden: Optional[int] = None
    rutina_id: int = Field(foreign_key="rutinas.id")

    # Relación inversa hacia la rutina
    rutina: Optional["Rutina"] = Relationship(back_populates="ejercicios")


class Rutina(SQLModel, table=True):
    """Tabla principal de rutinas."""

    __tablename__ = "rutinas"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True)
    descripcion: Optional[str] = None
    creado_en: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.utcnow)
    )

    # Relación 1:N con ejercicios, con borrado en cascada
    ejercicios: List[Ejercicio] = Relationship(
        back_populates="rutina",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Planificacion(SQLModel, table=True):
    """Asignación de una rutina a una fecha específica (calendario)."""

    __tablename__ = "planificaciones"

    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: date = Field(sa_column=Column(Date, index=True, unique=True))
    rutina_id: int = Field(foreign_key="rutinas.id")

    rutina: Optional[Rutina] = Relationship()


