from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from .models import DiaSemana


class EjercicioBase(BaseModel):
    """Campos comunes para crear/leer ejercicios."""

    nombre: str
    dia_semana: DiaSemana
    series: int
    repeticiones: int
    peso: Optional[float] = None
    notas: Optional[str] = None
    orden: Optional[int] = None

    # Validaciones básicas de negocio
    @validator("series", "repeticiones")
    def validar_positivos(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Debe ser mayor que cero")
        return value

    @validator("peso")
    def validar_peso(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and value <= 0:
            raise ValueError("El peso debe ser mayor que cero")
        return value


class EjercicioCreate(EjercicioBase):
    """Payload para creación de ejercicios."""


class EjercicioUpdate(BaseModel):
    """Payload para actualización parcial de ejercicios."""

    nombre: Optional[str] = None
    dia_semana: Optional[DiaSemana] = None
    series: Optional[int] = None
    repeticiones: Optional[int] = None
    peso: Optional[float] = None
    notas: Optional[str] = None
    orden: Optional[int] = None

    @validator("series", "repeticiones")
    def validar_positivos(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value <= 0:
            raise ValueError("Debe ser mayor que cero")
        return value

    @validator("peso")
    def validar_peso(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and value <= 0:
            raise ValueError("El peso debe ser mayor que cero")
        return value


class EjercicioRead(EjercicioBase):
    """Respuesta al cliente con IDs incluidos."""

    id: int
    rutina_id: int

    class Config:
        orm_mode = True


class RutinaBase(BaseModel):
    """Campos comunes de una rutina."""

    nombre: str = Field(..., min_length=1)
    descripcion: Optional[str] = None


class RutinaCreate(RutinaBase):
    """Payload de creación; puede incluir ejercicios iniciales."""

    ejercicios: List[EjercicioCreate] = []


class RutinaUpdate(BaseModel):
    """Payload de actualización parcial de rutina."""

    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    ejercicios: Optional[List[EjercicioCreate]] = None


class RutinaRead(RutinaBase):
    """Respuesta de detalle de rutina con ejercicios."""

    id: int
    creado_en: datetime
    ejercicios: List[EjercicioRead] = []

    class Config:
        orm_mode = True


class RutinaListResponse(BaseModel):
    """Respuesta paginada del listado de rutinas."""

    items: List[RutinaRead]
    total: int
    limit: int
    offset: int


