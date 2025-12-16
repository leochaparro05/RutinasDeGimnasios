# Script para probar el backend
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Test del Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar que estamos en el directorio correcto
Write-Host "1. Verificando directorio..." -ForegroundColor Yellow
if (-not (Test-Path "app\main.py")) {
    Write-Host "   ✗ Error: No se encuentra app\main.py" -ForegroundColor Red
    Write-Host "   Ejecuta este script desde el directorio backend" -ForegroundColor Red
    exit 1
}
Write-Host "   ✓ Directorio correcto" -ForegroundColor Green
Write-Host ""

# 2. Verificar entorno virtual
Write-Host "2. Verificando entorno virtual..." -ForegroundColor Yellow
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "   ⚠ No se encuentra el entorno virtual" -ForegroundColor Yellow
    Write-Host "   Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "   ✓ Entorno virtual creado" -ForegroundColor Green
}
Write-Host "   ✓ Entorno virtual encontrado" -ForegroundColor Green
Write-Host ""

# 3. Activar entorno virtual e instalar dependencias
Write-Host "3. Instalando dependencias..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
Write-Host "   ✓ Dependencias instaladas" -ForegroundColor Green
Write-Host ""

# 4. Verificar archivo .env
Write-Host "4. Verificando configuración..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "   ⚠ No se encuentra .env, creando desde env.example..." -ForegroundColor Yellow
    Copy-Item env.example .env
    Write-Host "   ✓ Archivo .env creado" -ForegroundColor Green
} else {
    Write-Host "   ✓ Archivo .env encontrado" -ForegroundColor Green
}
Write-Host ""

# 5. Verificar conexión a PostgreSQL
Write-Host "5. Verificando PostgreSQL..." -ForegroundColor Yellow
$pgService = Get-Service -Name postgresql* -ErrorAction SilentlyContinue
if ($pgService) {
    Write-Host "   ✓ Servicio PostgreSQL encontrado" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Servicio PostgreSQL no encontrado" -ForegroundColor Yellow
    Write-Host "   Asegúrate de que PostgreSQL esté corriendo" -ForegroundColor Yellow
}
Write-Host ""

# 6. Intentar iniciar el servidor
Write-Host "6. Iniciando servidor..." -ForegroundColor Yellow
Write-Host "   El servidor se iniciará en: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   Swagger UI estará en: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Iniciar el servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000







