import { useEffect, useMemo, useState } from "react";
import {
  addEjercicio,
  createRutina,
  deleteEjercicio,
  deleteRutina,
  fetchRutinas,
  searchRutinas,
  updateEjercicio,
  updateRutina,
  duplicateRutina,
} from "./api";

// Días disponibles (para selects)
const dias = [
  "Lunes",
  "Martes",
  "Miércoles",
  "Jueves",
  "Viernes",
  "Sábado",
  "Domingo",
];

// Estado base para formularios de ejercicio
const inicialEjercicio = {
  nombre: "",
  dia_semana: "Lunes",
  series: 3,
  repeticiones: 10,
  peso: "",
  notas: "",
  orden: "",
};

function App() {
  // Estado global de la UI
  const [rutinas, setRutinas] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [total, setTotal] = useState(0);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const [formRutina, setFormRutina] = useState({ nombre: "", descripcion: "" });
  const [ejerciciosNuevos, setEjerciciosNuevos] = useState([inicialEjercicio]);
  const [ejercicioPorRutina, setEjercicioPorRutina] = useState({});
  const [editandoEjercicio, setEditandoEjercicio] = useState(null);
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const [filtroDia, setFiltroDia] = useState("");
  const [filtroEjercicio, setFiltroEjercicio] = useState("");

  // Agrupa ejercicios por día para mostrarlos ordenados
  const ejerciciosPorDia = (ejercicios) =>
    ejercicios.reduce((acc, ej) => {
      const key = ej.dia_semana;
      acc[key] = acc[key] || [];
      acc[key].push(ej);
      acc[key].sort((a, b) => (a.orden ?? 0) - (b.orden ?? 0));
      return acc;
    }, {});

  // Carga inicial de rutinas
  const cargarRutinas = async () => {
    setCargando(true);
    setError("");
    try {
      const offset = (page - 1) * pageSize;
      const resp = await fetchRutinas({
        limit: pageSize,
        offset,
        dia_semana: filtroDia || undefined,
        ejercicio: filtroEjercicio || undefined,
      });
      const items = resp?.data?.items ?? resp?.data ?? [];
      const totalResp = resp?.data?.total ?? items.length ?? 0;
      setRutinas(items);
      setTotal(totalResp);
    } catch (e) {
      setError("No se pudieron cargar las rutinas");
      setRutinas([]);
      setTotal(0);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    if (!busqueda) {
      cargarRutinas();
    }
  }, [page, filtroDia, filtroEjercicio]);

  useEffect(() => {
    cargarRutinas();
  }, []);

  // Búsqueda en vivo por nombre
  const buscar = async (texto) => {
    setBusqueda(texto);
    setPage(1);
    if (!texto) {
      cargarRutinas();
      return;
    }
    try {
      const resp = await searchRutinas(texto);
      const items = resp?.data ?? [];
      setRutinas(items);
      setTotal(items.length);
    } catch (e) {
      setError("Error al buscar rutinas");
      setRutinas([]);
      setTotal(0);
    }
  };

  // Handlers de formularios de ejercicios nuevos
  const manejarCambioEjercicioNuevo = (idx, campo, valor) => {
    setEjerciciosNuevos((prev) =>
      prev.map((ej, i) => (i === idx ? { ...ej, [campo]: valor } : ej))
    );
  };

  const agregarFilaEjercicio = () => setEjerciciosNuevos((prev) => [...prev, inicialEjercicio]);
  const eliminarFilaEjercicio = (idx) =>
    setEjerciciosNuevos((prev) => prev.filter((_, i) => i !== idx));

  // Crear rutina con ejercicios opcionales
  const submitRutina = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const ejercicios = ejerciciosNuevos
        .filter((ej) => ej.nombre.trim())
        .map((ej) => ({
          ...ej,
          peso: ej.peso ? Number(ej.peso) : null,
          series: Number(ej.series),
          repeticiones: Number(ej.repeticiones),
          orden: ej.orden ? Number(ej.orden) : null,
        }));
      await createRutina({ ...formRutina, ejercicios });
      setFormRutina({ nombre: "", descripcion: "" });
      setEjerciciosNuevos([inicialEjercicio]);
      await cargarRutinas();
    } catch (e) {
      setError(e.response?.data?.detail || "No se pudo crear la rutina");
    }
  };

  // Eliminar rutina
  const eliminarRutinaHandler = async (id) => {
    if (!confirm("¿Eliminar la rutina y sus ejercicios?")) return;
    try {
      await deleteRutina(id);
      await cargarRutinas();
    } catch (e) {
      setError("No se pudo eliminar");
    }
  };

  // Preparar formulario para agregar ejercicio a una rutina
  const prepararEjercicioRutina = (rutinaId) =>
    setEjercicioPorRutina((prev) => ({
      ...prev,
      [rutinaId]: { ...inicialEjercicio },
    }));

  // Agregar ejercicio a una rutina existente
  const agregarEjercicioRutina = async (rutinaId) => {
    const data = ejercicioPorRutina[rutinaId];
    if (!data?.nombre) return;
    try {
      await addEjercicio(rutinaId, {
        ...data,
        peso: data.peso ? Number(data.peso) : null,
        series: Number(data.series),
        repeticiones: Number(data.repeticiones),
        orden: data.orden ? Number(data.orden) : null,
      });
      await cargarRutinas();
      prepararEjercicioRutina(rutinaId);
    } catch (e) {
      setError("No se pudo agregar el ejercicio");
    }
  };

  // Preparar edición de un ejercicio
  const editarEjercicio = (ejercicio) => {
    setEditandoEjercicio(ejercicio.id);
    setEjercicioPorRutina((prev) => ({
      ...prev,
      [`edit-${ejercicio.id}`]: {
        ...ejercicio,
        peso: ejercicio.peso ?? "",
        orden: ejercicio.orden ?? "",
      },
    }));
  };

  // Guardar edición de un ejercicio
  const guardarEdicionEjercicio = async (ejercicioId) => {
    const data = ejercicioPorRutina[`edit-${ejercicioId}`];
    try {
      await updateEjercicio(ejercicioId, {
        ...data,
        peso: data.peso ? Number(data.peso) : null,
        series: Number(data.series),
        repeticiones: Number(data.repeticiones),
        orden: data.orden ? Number(data.orden) : null,
      });
      setEditandoEjercicio(null);
      await cargarRutinas();
    } catch (e) {
      setError("No se pudo actualizar el ejercicio");
    }
  };

  // Eliminar ejercicio
  const eliminarEjercicioHandler = async (id) => {
    if (!confirm("¿Eliminar ejercicio?")) return;
    try {
      await deleteEjercicio(id);
      await cargarRutinas();
    } catch (e) {
      setError("No se pudo eliminar el ejercicio");
    }
  };

  // Renombrar rutina (prompt simple)
  const actualizarRutinaNombre = async (rutina) => {
    const nuevo = prompt("Nuevo nombre:", rutina.nombre);
    if (!nuevo || nuevo === rutina.nombre) return;
    try {
      await updateRutina(rutina.id, { nombre: nuevo });
      await cargarRutinas();
    } catch (e) {
      setError(e.response?.data?.detail || "No se pudo actualizar la rutina");
    }
  };

  const duplicarRutinaHandler = async (rutina) => {
    const nuevo = prompt(
      "Nombre opcional para la copia (deja vacío para generar uno automáticamente):",
      `${rutina.nombre} (copia)`
    );
    try {
      await duplicateRutina(rutina.id, nuevo || undefined);
      await cargarRutinas();
    } catch (e) {
      setError(e.response?.data?.detail || "No se pudo duplicar la rutina");
    }
  };

  // Preprocesar rutinas para agrupar por día
  const rutinasConDias = useMemo(
    () =>
      rutinas.map((r) => ({
        ...r,
        ejerciciosPorDia: ejerciciosPorDia(r.ejercicios || []),
      })),
    [rutinas]
  );

  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const irPagina = (nueva) => {
    if (nueva < 1 || nueva > totalPages) return;
    setPage(nueva);
  };

  const limpiarFiltros = () => {
    setFiltroDia("");
    setFiltroEjercicio("");
    setPage(1);
  };

  return (
    <div className="container">
      <div className="header">
        <div>
          <h1 className="title">Rutinas de Gimnasio</h1>
          <p className="muted">CRUD + búsqueda en vivo</p>
        </div>
        <div className="grid" style={{ minWidth: 240, gap: 8 }}>
          <input
            placeholder="Buscar por nombre..."
            value={busqueda}
            onChange={(e) => buscar(e.target.value)}
          />
          <div className="row" style={{ gap: 8 }}>
            <select
              value={filtroDia}
              onChange={(e) => {
                setFiltroDia(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Todos los días</option>
              {dias.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
            <input
              placeholder="Filtro por ejercicio"
              value={filtroEjercicio}
              onChange={(e) => {
                setFiltroEjercicio(e.target.value);
                setPage(1);
              }}
            />
          </div>
          <button className="secondary" type="button" onClick={limpiarFiltros}>
            Limpiar filtros
          </button>
        </div>
      </div>

      {error && <p style={{ color: "#dc2626" }}>{error}</p>}

      <div className="grid grid-2" style={{ marginTop: 16 }}>
        {/* Columna: Crear rutina */}
        <div className="card">
          <h3 className="title">Crear rutina</h3>
          <form className="grid" onSubmit={submitRutina}>
            <div>
              <label>Nombre</label>
              <input
                required
                value={formRutina.nombre}
                onChange={(e) => setFormRutina({ ...formRutina, nombre: e.target.value })}
              />
            </div>
            <div>
              <label>Descripción</label>
              <textarea
                value={formRutina.descripcion}
                onChange={(e) => setFormRutina({ ...formRutina, descripcion: e.target.value })}
              />
            </div>
            <div className="grid" style={{ gap: 12 }}>
              <div className="space-between">
                <strong>Ejercicios (opcional)</strong>
                <button type="button" className="secondary" onClick={agregarFilaEjercicio}>
                  + Ejercicio
                </button>
              </div>
              {ejerciciosNuevos.map((ej, idx) => (
                <div key={idx} className="card" style={{ padding: 12 }}>
                  <div className="grid" style={{ gap: 8 }}>
                    <div>
                      <label>Nombre</label>
                      <input
                        value={ej.nombre}
                        onChange={(e) => manejarCambioEjercicioNuevo(idx, "nombre", e.target.value)}
                        placeholder="Sentadillas"
                        required
                      />
                    </div>
                    <div className="row">
                      <div style={{ flex: 1 }}>
                        <label>Día</label>
                        <select
                          value={ej.dia_semana}
                          onChange={(e) =>
                            manejarCambioEjercicioNuevo(idx, "dia_semana", e.target.value)
                          }
                        >
                          {dias.map((d) => (
                            <option key={d}>{d}</option>
                          ))}
                        </select>
                      </div>
                      <div style={{ flex: 1 }}>
                        <label>Orden</label>
                        <input
                          type="number"
                          value={ej.orden}
                          onChange={(e) =>
                            manejarCambioEjercicioNuevo(idx, "orden", e.target.value)
                          }
                          placeholder="1"
                        />
                      </div>
                    </div>
                    <div className="row">
                      <div style={{ flex: 1 }}>
                        <label>Series</label>
                        <input
                          type="number"
                          value={ej.series}
                          min="1"
                          onChange={(e) =>
                            manejarCambioEjercicioNuevo(idx, "series", e.target.value)
                          }
                          required
                        />
                      </div>
                      <div style={{ flex: 1 }}>
                        <label>Repeticiones</label>
                        <input
                          type="number"
                          value={ej.repeticiones}
                          min="1"
                          onChange={(e) =>
                            manejarCambioEjercicioNuevo(idx, "repeticiones", e.target.value)
                          }
                          required
                        />
                      </div>
                      <div style={{ flex: 1 }}>
                        <label>Peso (kg)</label>
                        <input
                          type="number"
                          value={ej.peso}
                          min="0"
                          onChange={(e) =>
                            manejarCambioEjercicioNuevo(idx, "peso", e.target.value)
                          }
                        />
                      </div>
                    </div>
                    <div>
                      <label>Notas</label>
                      <textarea
                        value={ej.notas}
                        onChange={(e) => manejarCambioEjercicioNuevo(idx, "notas", e.target.value)}
                      />
                    </div>
                    {ejerciciosNuevos.length > 1 && (
                      <button
                        type="button"
                        className="danger"
                        onClick={() => eliminarFilaEjercicio(idx)}
                      >
                        Quitar
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
            <button type="submit" disabled={cargando}>
              {cargando ? "Guardando..." : "Crear rutina"}
            </button>
          </form>
        </div>

        {/* Columna: Listado de rutinas */}
        <div className="card">
          <div className="space-between">
            <h3 className="title">Rutinas ({total})</h3>
            <button className="secondary" onClick={cargarRutinas}>
              Recargar
            </button>
          </div>
          {cargando && <p className="muted">Cargando...</p>}
          <div className="list">
            {rutinasConDias.map((rutina) => (
              <div key={rutina.id} className="card">
                <div className="space-between">
                  <div>
                    <h4 className="title">{rutina.nombre}</h4>
                    <p className="muted">{rutina.descripcion || "Sin descripción"}</p>
                  </div>
                  <div className="row">
                    <button className="secondary" onClick={() => duplicarRutinaHandler(rutina)}>
                      Duplicar
                    </button>
                    <button className="secondary" onClick={() => actualizarRutinaNombre(rutina)}>
                      Renombrar
                    </button>
                    <button className="danger" onClick={() => eliminarRutinaHandler(rutina.id)}>
                      Eliminar
                    </button>
                  </div>
                </div>
                <div className="grid" style={{ gap: 8 }}>
                  {Object.entries(rutina.ejerciciosPorDia).map(([dia, ejercicios]) => (
                    <div key={dia} className="card" style={{ background: "#f8fafc" }}>
                      <div className="space-between">
                        <span className="badge">{dia}</span>
                        <span className="muted">{ejercicios.length} ejercicios</span>
                      </div>
                      <div className="list">
                        {ejercicios.map((ej) => (
                          <div key={ej.id} className="card">
                            <div className="space-between">
                              <div>
                                <strong>{ej.nombre}</strong>
                                <p className="muted">
                                  {ej.series}x{ej.repeticiones} {ej.peso ? `- ${ej.peso} kg` : ""}
                                  {ej.orden ? ` - Orden ${ej.orden}` : ""}
                                </p>
                                {ej.notas && <p className="muted">{ej.notas}</p>}
                              </div>
                              <div className="row">
                                <button className="secondary" onClick={() => editarEjercicio(ej)}>
                                  Editar
                                </button>
                                <button
                                  className="danger"
                                  onClick={() => eliminarEjercicioHandler(ej.id)}
                                >
                                  Borrar
                                </button>
                              </div>
                            </div>
                            {editandoEjercicio === ej.id && (
                              <div className="grid" style={{ marginTop: 8 }}>
                                <div className="row">
                                  <div style={{ flex: 1 }}>
                                    <label>Nombre</label>
                                    <input
                                      value={ejercicioPorRutina[`edit-${ej.id}`]?.nombre || ""}
                                      onChange={(e) =>
                                        setEjercicioPorRutina((prev) => ({
                                          ...prev,
                                          [`edit-${ej.id}`]: {
                                            ...prev[`edit-${ej.id}`],
                                            nombre: e.target.value,
                                          },
                                        }))
                                      }
                                    />
                                  </div>
                                  <div style={{ flex: 1 }}>
                                    <label>Día</label>
                                    <select
                                      value={ejercicioPorRutina[`edit-${ej.id}`]?.dia_semana || "Lunes"}
                                      onChange={(e) =>
                                        setEjercicioPorRutina((prev) => ({
                                          ...prev,
                                          [`edit-${ej.id}`]: {
                                            ...prev[`edit-${ej.id}`],
                                            dia_semana: e.target.value,
                                          },
                                        }))
                                      }
                                    >
                                      {dias.map((d) => (
                                        <option key={d}>{d}</option>
                                      ))}
                                    </select>
                                  </div>
                                </div>
                                <div className="row">
                                  <div style={{ flex: 1 }}>
                                    <label>Series</label>
                                    <input
                                      type="number"
                                      value={ejercicioPorRutina[`edit-${ej.id}`]?.series || ""}
                                      onChange={(e) =>
                                        setEjercicioPorRutina((prev) => ({
                                          ...prev,
                                          [`edit-${ej.id}`]: {
                                            ...prev[`edit-${ej.id}`],
                                            series: e.target.value,
                                          },
                                        }))
                                      }
                                    />
                                  </div>
                                  <div style={{ flex: 1 }}>
                                    <label>Repeticiones</label>
                                    <input
                                      type="number"
                                      value={ejercicioPorRutina[`edit-${ej.id}`]?.repeticiones || ""}
                                      onChange={(e) =>
                                        setEjercicioPorRutina((prev) => ({
                                          ...prev,
                                          [`edit-${ej.id}`]: {
                                            ...prev[`edit-${ej.id}`],
                                            repeticiones: e.target.value,
                                          },
                                        }))
                                      }
                                    />
                                  </div>
                                  <div style={{ flex: 1 }}>
                                    <label>Peso</label>
                                    <input
                                      type="number"
                                      value={ejercicioPorRutina[`edit-${ej.id}`]?.peso || ""}
                                      onChange={(e) =>
                                        setEjercicioPorRutina((prev) => ({
                                          ...prev,
                                          [`edit-${ej.id}`]: {
                                            ...prev[`edit-${ej.id}`],
                                            peso: e.target.value,
                                          },
                                        }))
                                      }
                                    />
                                  </div>
                                </div>
                                <div className="row">
                                  <div style={{ flex: 1 }}>
                                    <label>Orden</label>
                                    <input
                                      type="number"
                                      value={ejercicioPorRutina[`edit-${ej.id}`]?.orden || ""}
                                      onChange={(e) =>
                                        setEjercicioPorRutina((prev) => ({
                                          ...prev,
                                          [`edit-${ej.id}`]: {
                                            ...prev[`edit-${ej.id}`],
                                            orden: e.target.value,
                                          },
                                        }))
                                      }
                                    />
                                  </div>
                                  <div style={{ flex: 1 }}>
                                    <label>Notas</label>
                                    <input
                                      value={ejercicioPorRutina[`edit-${ej.id}`]?.notas || ""}
                                      onChange={(e) =>
                                        setEjercicioPorRutina((prev) => ({
                                          ...prev,
                                          [`edit-${ej.id}`]: {
                                            ...prev[`edit-${ej.id}`],
                                            notas: e.target.value,
                                          },
                                        }))
                                      }
                                    />
                                  </div>
                                </div>
                                <div className="row">
                                  <button onClick={() => guardarEdicionEjercicio(ej.id)}>
                                    Guardar
                                  </button>
                                  <button
                                    className="secondary"
                                    type="button"
                                    onClick={() => setEditandoEjercicio(null)}
                                  >
                                    Cancelar
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                      <div className="card" style={{ marginTop: 8 }}>
                        <strong>Agregar ejercicio</strong>
                        <div className="grid" style={{ gap: 8 }}>
                          <input
                            placeholder="Nombre"
                            value={ejercicioPorRutina[rutina.id]?.nombre || ""}
                            onChange={(e) =>
                              setEjercicioPorRutina((prev) => ({
                                ...prev,
                                [rutina.id]: { ...(prev[rutina.id] || inicialEjercicio), nombre: e.target.value },
                              }))
                            }
                          />
                          <div className="row">
                            <select
                              value={ejercicioPorRutina[rutina.id]?.dia_semana || "Lunes"}
                              onChange={(e) =>
                                setEjercicioPorRutina((prev) => ({
                                  ...prev,
                                  [rutina.id]: {
                                    ...(prev[rutina.id] || inicialEjercicio),
                                    dia_semana: e.target.value,
                                  },
                                }))
                              }
                            >
                              {dias.map((d) => (
                                <option key={d}>{d}</option>
                              ))}
                            </select>
                            <input
                              type="number"
                              placeholder="Series"
                              value={ejercicioPorRutina[rutina.id]?.series || ""}
                              onChange={(e) =>
                                setEjercicioPorRutina((prev) => ({
                                  ...prev,
                                  [rutina.id]: {
                                    ...(prev[rutina.id] || inicialEjercicio),
                                    series: e.target.value,
                                  },
                                }))
                              }
                            />
                            <input
                              type="number"
                              placeholder="Reps"
                              value={ejercicioPorRutina[rutina.id]?.repeticiones || ""}
                              onChange={(e) =>
                                setEjercicioPorRutina((prev) => ({
                                  ...prev,
                                  [rutina.id]: {
                                    ...(prev[rutina.id] || inicialEjercicio),
                                    repeticiones: e.target.value,
                                  },
                                }))
                              }
                            />
                          </div>
                          <div className="row">
                            <input
                              type="number"
                              placeholder="Peso opcional"
                              value={ejercicioPorRutina[rutina.id]?.peso || ""}
                              onChange={(e) =>
                                setEjercicioPorRutina((prev) => ({
                                  ...prev,
                                  [rutina.id]: {
                                    ...(prev[rutina.id] || inicialEjercicio),
                                    peso: e.target.value,
                                  },
                                }))
                              }
                            />
                            <input
                              type="number"
                              placeholder="Orden"
                              value={ejercicioPorRutina[rutina.id]?.orden || ""}
                              onChange={(e) =>
                                setEjercicioPorRutina((prev) => ({
                                  ...prev,
                                  [rutina.id]: {
                                    ...(prev[rutina.id] || inicialEjercicio),
                                    orden: e.target.value,
                                  },
                                }))
                              }
                            />
                          </div>
                          <input
                            placeholder="Notas"
                            value={ejercicioPorRutina[rutina.id]?.notas || ""}
                            onChange={(e) =>
                              setEjercicioPorRutina((prev) => ({
                                ...prev,
                                [rutina.id]: {
                                  ...(prev[rutina.id] || inicialEjercicio),
                                  notas: e.target.value,
                                },
                              }))
                            }
                          />
                          <button type="button" onClick={() => agregarEjercicioRutina(rutina.id)}>
                            Añadir
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                  {Object.keys(rutina.ejerciciosPorDia).length === 0 && (
                    <p className="muted">Sin ejercicios aún.</p>
                  )}
                </div>
              </div>
            ))}
          </div>
          <div className="space-between" style={{ marginTop: 12 }}>
            <div className="muted">
              Página {page} de {totalPages} — mostrando {rutinas.length} de {total}
            </div>
            <div className="row">
              <button className="secondary" disabled={page === 1} onClick={() => irPagina(page - 1)}>
                ← Anterior
              </button>
              <button
                className="secondary"
                disabled={page >= totalPages}
                onClick={() => irPagina(page + 1)}
              >
                Siguiente →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;


