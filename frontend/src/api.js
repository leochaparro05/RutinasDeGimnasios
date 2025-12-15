import axios from "axios";

// Cliente Axios con baseURL configurable por Vite (variable de entorno)
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

// Endpoints de rutinas
export const fetchRutinas = ({ limit = 10, offset = 0, dia_semana, ejercicio } = {}) =>
  api.get("/api/rutinas", { params: { limit, offset, dia_semana, ejercicio } });
export const searchRutinas = (nombre) => api.get("/api/rutinas/buscar", { params: { nombre } });
export const createRutina = (data) => api.post("/api/rutinas", data);
export const updateRutina = (id, data) => api.put(`/api/rutinas/${id}`, data);
export const deleteRutina = (id) => api.delete(`/api/rutinas/${id}`);
export const duplicateRutina = (id, nombre) =>
  api.post(`/api/rutinas/${id}/duplicar`, nombre ? { nombre } : {});
export const fetchStats = () => api.get("/api/estadisticas");

// Endpoints de ejercicios
export const addEjercicio = (rutinaId, data) =>
  api.post(`/api/rutinas/${rutinaId}/ejercicios`, data);
export const updateEjercicio = (id, data) => api.put(`/api/ejercicios/${id}`, data);
export const deleteEjercicio = (id) => api.delete(`/api/ejercicios/${id}`);

export default api;

