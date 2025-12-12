# Comandos para Ejecutar el Proyecto

## 🔵 PASO 1: Activar PostgreSQL

Abre **pgAdmin** o ejecuta PostgreSQL desde el servicio de Windows:

```powershell
# Verificar que PostgreSQL esté corriendo
Get-Service -Name postgresql*

# Si no está corriendo, iniciarlo (requiere permisos de administrador)
Start-Service -Name postgresql-x64-*  # Ajusta el nombre según tu instalación
```

**O manualmente:**
- Abre **pgAdmin 4**
- Conecta al servidor (usuario: `postgres`, contraseña: `umu192`)
- Crea una base de datos llamada `rutinas` (si no existe)

---

## 🟢 PASO 2: Configurar y Ejecutar el BACKEND

Abre una **terminal PowerShell** y ejecuta:

```powershell
# 1. Ir al directorio del backend
cd "C:\Users\Leo Chaparro\Desktop\RutinasDeGimnasio\backend"

# 2. Activar el entorno virtual (si ya existe)
.\venv\Scripts\Activate.ps1

# Si no existe el venv, créalo primero:
# python -m venv venv
# .\venv\Scripts\Activate.ps1

# 3. Instalar dependencias (solo la primera vez)
pip install -r requirements.txt

# 4. Crear archivo .env con la configuración de la base de datos
# (Copia el contenido de env.example a .env)
Copy-Item env.example .env

# 5. Ejecutar el servidor FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**✅ El backend estará corriendo en:** `http://localhost:8000`
**📚 Documentación API:** `http://localhost:8000/docs`

---

## 🟡 PASO 3: Configurar y Ejecutar el FRONTEND

Abre **otra terminal PowerShell** (deja el backend corriendo) y ejecuta:

```powershell
# 1. Ir al directorio del frontend
cd "C:\Users\Leo Chaparro\Desktop\RutinasDeGimnasio\frontend"

# 2. Instalar dependencias (solo la primera vez)
npm install

# 3. Crear archivo .env con la URL del backend
echo "VITE_API_URL=http://localhost:8000" > .env

# 4. Ejecutar el servidor de desarrollo
npm run dev
```

**✅ El frontend estará corriendo en:** `http://localhost:5173`

---

## 📝 Resumen de Comandos Rápidos

### Terminal 1 - Backend:
```powershell
cd "C:\Users\Leo Chaparro\Desktop\RutinasDeGimnasio\backend"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend:
```powershell
cd "C:\Users\Leo Chaparro\Desktop\RutinasDeGimnasio\frontend"
npm run dev
```

---

## ⚠️ Notas Importantes:

1. **PostgreSQL debe estar corriendo** antes de iniciar el backend
2. **La base de datos `rutinas` debe existir** (se crea automáticamente si usas el código, pero verifica)
3. **Mantén ambas terminales abiertas** mientras trabajas
4. **El backend se reinicia automáticamente** cuando cambias código (gracias a `--reload`)
5. **El frontend también se recarga** automáticamente cuando cambias código

---

## 🐛 Solución de Problemas:

### Error: "No se puede conectar a PostgreSQL"
- Verifica que PostgreSQL esté corriendo
- Verifica usuario: `postgres`, contraseña: `umu192`
- Verifica que la base de datos `rutinas` exista

### Error: "ModuleNotFoundError"
- Asegúrate de tener el venv activado
- Ejecuta: `pip install -r requirements.txt`

### Error: "npm no se reconoce"
- Instala Node.js desde: https://nodejs.org/

### Error: "Puerto 8000 en uso"
- Cambia el puerto: `uvicorn app.main:app --reload --port 8001`
- Actualiza `VITE_API_URL` en el frontend

