# Solución: Swagger no funciona

## 🔍 Diagnóstico Rápido

### Paso 1: Verificar que el servidor esté corriendo

Abre una terminal PowerShell y ejecuta:

```powershell
cd "C:\Users\Leo Chaparro\Desktop\RutinasDeGimnasio\backend"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Deberías ver algo como:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
✓ Base de datos inicializada correctamente
INFO:     Application startup complete.
```

---

### Paso 2: Verificar que el servidor responda

Abre tu navegador y visita:

- **http://localhost:8000** - Debería mostrar: `{"message":"API de Rutinas de Gimnasio está funcionando","docs":"/docs"}`
- **http://localhost:8000/health** - Debería mostrar: `{"status":"ok","message":"Servidor funcionando correctamente"}`
- **http://localhost:8000/docs** - Debería mostrar la interfaz de Swagger

---

## ❌ Problemas Comunes y Soluciones

### Problema 1: "Connection refused" o página no carga

**Causa:** El servidor no está corriendo o hay un error al iniciar.

**Solución:**
1. Verifica que no haya errores en la terminal donde ejecutaste `uvicorn`
2. Verifica que el puerto 8000 no esté ocupado:
   ```powershell
   netstat -ano | findstr :8000
   ```
3. Si el puerto está ocupado, cambia el puerto:
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

---

### Problema 2: Error de conexión a PostgreSQL

**Causa:** PostgreSQL no está corriendo o la base de datos no existe.

**Solución:**
1. Verifica que PostgreSQL esté corriendo:
   ```powershell
   Get-Service -Name postgresql*
   ```
2. Si no está corriendo, inícialo:
   ```powershell
   Start-Service -Name postgresql-x64-*  # Ajusta el nombre según tu instalación
   ```
3. Crea la base de datos `rutinas` en pgAdmin:
   - Abre pgAdmin 4
   - Conecta al servidor (usuario: `postgres`, contraseña: `umu192`)
   - Click derecho en "Databases" → "Create" → "Database"
   - Nombre: `rutinas`
   - Click en "Save"

---

### Problema 3: Error al importar módulos

**Causa:** El entorno virtual no está activado o faltan dependencias.

**Solución:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### Problema 4: Swagger muestra error 500 o "Internal Server Error"

**Causa:** Error en el código o en la inicialización de la base de datos.

**Solución:**
1. Revisa los logs en la terminal donde corre el servidor
2. Verifica que el archivo `.env` exista y tenga la configuración correcta:
   ```
   DATABASE_URL=postgresql+psycopg2://postgres:umu192@localhost:5432/rutinas
   ```
3. Verifica que la base de datos `rutinas` exista

---

### Problema 5: Swagger carga pero no muestra los endpoints

**Causa:** Puede ser un problema de caché del navegador.

**Solución:**
1. Presiona `Ctrl + Shift + R` para recargar sin caché
2. O abre en modo incógnito: `Ctrl + Shift + N`

---

## ✅ Script Automático de Prueba

Ejecuta este script para verificar todo automáticamente:

```powershell
cd "C:\Users\Leo Chaparro\Desktop\RutinasDeGimnasio\backend"
.\test-backend.ps1
```

---

## 📝 Comandos Rápidos

### Iniciar el servidor:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Verificar que funciona:
- Abre: http://localhost:8000/docs

### Ver logs en tiempo real:
- Los logs aparecen en la terminal donde ejecutaste `uvicorn`

---

## 🆘 Si nada funciona

1. **Detén el servidor** (Ctrl+C en la terminal)
2. **Verifica los logs** de error en la terminal
3. **Comparte el error** que aparece para poder ayudarte mejor

