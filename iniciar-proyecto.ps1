# Script para iniciar el proyecto completo
# Ejecutar: .\iniciar-proyecto.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Sistema de Rutinas de Gimnasio" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar PostgreSQL
Write-Host "1. Verificando PostgreSQL..." -ForegroundColor Yellow
$pgService = Get-Service -Name postgresql* -ErrorAction SilentlyContinue
if ($pgService) {
    Write-Host "   ✓ PostgreSQL encontrado" -ForegroundColor Green
} else {
    Write-Host "   ⚠ PostgreSQL no encontrado. Asegúrate de tenerlo instalado y corriendo." -ForegroundColor Yellow
}

# Crear archivo .env del backend si no existe
Write-Host "2. Configurando backend..." -ForegroundColor Yellow
$backendEnv = "backend\.env"
if (-not (Test-Path $backendEnv)) {
    @"
DATABASE_URL=postgresql+psycopg2://postgres:umu192@localhost:5432/rutinas
"@ | Out-File -FilePath $backendEnv -Encoding UTF8
    Write-Host "   ✓ Archivo .env creado en backend" -ForegroundColor Green
} else {
    Write-Host "   ✓ Archivo .env ya existe" -ForegroundColor Green
}

# Crear archivo .env del frontend si no existe
Write-Host "3. Configurando frontend..." -ForegroundColor Yellow
$frontendEnv = "frontend\.env"
if (-not (Test-Path $frontendEnv)) {
    @"
VITE_API_URL=http://localhost:8000
"@ | Out-File -FilePath $frontendEnv -Encoding UTF8
    Write-Host "   ✓ Archivo .env creado en frontend" -ForegroundColor Green
} else {
    Write-Host "   ✓ Archivo .env ya existe" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTRUCCIONES PARA EJECUTAR:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "TERMINAL 1 - Backend:" -ForegroundColor Yellow
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  pip install -r requirements.txt" -ForegroundColor White
Write-Host "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "TERMINAL 2 - Frontend:" -ForegroundColor Yellow
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  npm install" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "URLs:" -ForegroundColor Cyan
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor Green
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host ""

