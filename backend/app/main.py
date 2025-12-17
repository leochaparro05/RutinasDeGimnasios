from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
import csv
from fpdf import FPDF

from . import crud
from .database import get_session, init_db
from .models import DiaSemana, Ejercicio, Rutina, Planificacion
from .schemas import (
    EjercicioCreate,
    EjercicioRead,
    EjercicioUpdate,
    EstadisticasResponse,
    RutinaCreate,
    RutinaListResponse,
    RutinaRead,
    RutinaUpdate,
    RutinaDuplicatePayload,
    PlanificacionCreate,
    PlanificacionRead,
    PlanificacionUpdate,
)
""" endpoints principales. """

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

"""Obtiene todas las rutinas con sus ejercicios relacionados para exportación."""
def _fetch_rutinas_completas(session: Session) -> list[Rutina]:
    statement = session.query(Rutina).all()  # type: ignore
    return statement

""" Exportar rutinas en formato csv o pdf """

@app.get("/api/rutinas/export")
def exportar_rutinas(
    formato: str = Query("csv", pattern="^(csv|pdf)$"),
    session: Session = Depends(get_session),
):
    rutinas = _fetch_rutinas_completas(session)

    if formato == "csv":
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            ["rutina_id", "nombre", "descripcion", "creado_en", "ejercicio", "dia", "series", "repeticiones", "peso", "notas", "orden"]
        )
        for r in rutinas:
            for ej in r.ejercicios:
                writer.writerow(
                    [
                        r.id,
                        r.nombre,
                        r.descripcion or "",
                        r.creado_en,
                        ej.nombre,
                        ej.dia_semana,
                        ej.series,
                        ej.repeticiones,
                        ej.peso or "",
                        ej.notas or "",
                        ej.orden or "",
                    ]
                )
            if not r.ejercicios:
                writer.writerow([r.id, r.nombre, r.descripcion or "", r.creado_en, "", "", "", "", "", "", ""])
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="rutinas.csv"'},
        )

    # PDF
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=12)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Rutinas de Gimnasio", ln=1)
        pdf.set_font("Arial", "", 11)

        for r in rutinas:
            pdf.set_text_color(30, 64, 175)
            pdf.cell(0, 8, f"Rutina: {r.nombre} (ID {r.id})", ln=1)
            pdf.set_text_color(51, 65, 85)
            if r.descripcion:
                pdf.multi_cell(0, 6, f"Desc: {r.descripcion}")
            pdf.set_text_color(15, 23, 42)
            if r.ejercicios:
                for ej in r.ejercicios:
                    linea = f"- {ej.dia_semana}: {ej.nombre} {ej.series}x{ej.repeticiones}"
                    if ej.peso:
                        linea += f" @ {ej.peso}kg"
                    if ej.orden:
                        linea += f" (orden {ej.orden})"
                    pdf.cell(0, 6, linea, ln=1)
                    if ej.notas:
                        pdf.set_text_color(100, 116, 139)
                        pdf.multi_cell(0, 5, f"  Notas: {ej.notas}")
                        pdf.set_text_color(15, 23, 42)
            else:
                pdf.cell(0, 6, "Sin ejercicios", ln=1)
            pdf.ln(4)

        pdf_output = pdf.output(dest="S")
        pdf_bytes = pdf_output if isinstance(pdf_output, (bytes, bytearray)) else pdf_output.encode(
            "latin-1", "ignore"
        )
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="rutinas.pdf"'},
        )
    except Exception as exc:  # fallback a CSV si falla el PDF
        print(f"[EXPORT PDF] Error generando PDF: {exc}")
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            ["rutina_id", "nombre", "descripcion", "creado_en", "ejercicio", "dia", "series", "repeticiones", "peso", "notas", "orden"]
        )
        for r in rutinas:
            for ej in r.ejercicios:
                writer.writerow(
                    [
                        r.id,
                        r.nombre,
                        r.descripcion or "",
                        r.creado_en,
                        ej.nombre,
                        ej.dia_semana,
                        ej.series,
                        ej.repeticiones,
                        ej.peso or "",
                        ej.notas or "",
                        ej.orden or "",
                    ]
                )
            if not r.ejercicios:
                writer.writerow([r.id, r.nombre, r.descripcion or "", r.creado_en, "", "", "", "", "", "", ""])
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="rutinas_fallback.csv"'},
        )


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

"""Lista todas las planificaciones (rutinas programadas en fechas), con sus rutinas asociadas."""
@app.get("/api/planificaciones", response_model=list[PlanificacionRead])
def listar_planificaciones(session: Session = Depends(get_session)) -> list[PlanificacionRead]:
    return crud.listar_planificaciones(session)


@app.post("/api/planificaciones", response_model=PlanificacionRead, status_code=201)
def crear_planificacion(data: PlanificacionCreate, session: Session = Depends(get_session)) -> Planificacion:
    # Validar que la rutina exista
    if not crud.obtener_rutina(session, data.rutina_id):
        raise HTTPException(status_code=404, detail="Rutina no encontrada")
    existente = crud.obtener_plan_por_fecha(session, data.fecha)
    if existente:
        # Si ya existe para esa fecha, actualizar
        return crud.actualizar_planificacion(session, existente, PlanificacionUpdate(rutina_id=data.rutina_id))
    return crud.crear_planificacion(session, data)


"""Actualiza parcialmente una planificación: fecha y/o rutina asociada."""
@app.put("/api/planificaciones/{plan_id}", response_model=PlanificacionRead)
def actualizar_planificacion(
    plan_id: int, data: PlanificacionUpdate, session: Session = Depends(get_session)
) -> Planificacion:
    plan = session.get(Planificacion, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Planificación no encontrada")
    if data.rutina_id and not crud.obtener_rutina(session, data.rutina_id):
        raise HTTPException(status_code=404, detail="Rutina no encontrada")
    return crud.actualizar_planificacion(session, plan, data)

"""Elimina una planificación del calendario sin afectar la rutina original."""
@app.delete("/api/planificaciones/{plan_id}", status_code=204)
def eliminar_planificacion(plan_id: int, session: Session = Depends(get_session)) -> None:
    plan = session.get(Planificacion, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Planificación no encontrada")
    crud.eliminar_planificacion(session, plan)





@app.get("/api/rutinas/export")
def exportar_rutinas(
    formato: str = Query("csv", pattern="^(csv|pdf)$"),
    session: Session = Depends(get_session),
):
    rutinas = _fetch_rutinas_completas(session)

    if formato == "csv":
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            ["rutina_id", "nombre", "descripcion", "creado_en", "ejercicio", "dia", "series", "repeticiones", "peso", "notas", "orden"]
        )
        for r in rutinas:
            for ej in r.ejercicios:
                writer.writerow(
                    [
                        r.id,
                        r.nombre,
                        r.descripcion or "",
                        r.creado_en,
                        ej.nombre,
                        ej.dia_semana,
                        ej.series,
                        ej.repeticiones,
                        ej.peso or "",
                        ej.notas or "",
                        ej.orden or "",
                    ]
                )
            if not r.ejercicios:
                writer.writerow([r.id, r.nombre, r.descripcion or "", r.creado_en, "", "", "", "", "", "", ""])
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="rutinas.csv"'},
        )

    # PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Rutinas de Gimnasio", ln=1)
    pdf.set_font("Arial", "", 11)

    for r in rutinas:
        pdf.set_text_color(30, 64, 175)
        pdf.cell(0, 8, f"Rutina: {r.nombre} (ID {r.id})", ln=1)
        pdf.set_text_color(51, 65, 85)
        if r.descripcion:
            pdf.multi_cell(0, 6, f"Desc: {r.descripcion}")
        pdf.set_text_color(15, 23, 42)
        if r.ejercicios:
            for ej in r.ejercicios:
                linea = f"- {ej.dia_semana}: {ej.nombre} {ej.series}x{ej.repeticiones}"
                if ej.peso:
                    linea += f" @ {ej.peso}kg"
                if ej.orden:
                    linea += f" (orden {ej.orden})"
                pdf.cell(0, 6, linea, ln=1)
                if ej.notas:
                    pdf.set_text_color(100, 116, 139)
                    pdf.multi_cell(0, 5, f"  Notas: {ej.notas}")
                    pdf.set_text_color(15, 23, 42)
        else:
            pdf.cell(0, 6, "Sin ejercicios", ln=1)
        pdf.ln(4)

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="rutinas.pdf"'},
    )


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


