# Освободить порты
$ports = 8001, 3000, 9090, 6379
foreach ($port in $ports) {
    Write-Host "Проверяем порт $port" -ForegroundColor Gray
    $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | 
               Select-Object -First 1 -ExpandProperty OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "Завершаем процесс $process на порту $port" -ForegroundColor Yellow
        taskkill /PID $process /F 2>$null
    }
}

# Полностью перезапустить Docker
Write-Host "Полный перезапуск Docker..." -ForegroundColor Green

# Закрыть Docker Desktop
Get-Process "Docker Desktop" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 3

# Остановить службы Docker
Stop-Service -Name "com.docker.service" -Force -ErrorAction SilentlyContinue
Stop-Service -Name "Docker Desktop Service" -Force -ErrorAction SilentlyContinue

# Запустить Docker Desktop
Write-Host "Запускаем Docker Desktop..." -ForegroundColor Green
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Ждем и проверяем запуск
$maxAttempts = 10
$attempt = 0
$dockerReady = $false

while ($attempt -lt $maxAttempts -and -not $dockerReady) {
    $attempt++
    Write-Host "Попытка $attempt/$maxAttempts проверяем Docker..." -ForegroundColor Gray
    
    try {
        docker version 2>$null | Out-Null
        $dockerReady = $true
        Write-Host "✓ Docker запущен" -ForegroundColor Green
    } catch {
        Write-Host "✗ Docker еще не готов, ждем..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
}

if (-not $dockerReady) {
    Write-Host "Не удалось запустить Docker!" -ForegroundColor Red
    exit 1
}

# Запустить проект
Write-Host "Запускаем проект..." -ForegroundColor Green
docker-compose down
docker-compose up --build -d

Write-Host "`nГотово! Проверьте:" -ForegroundColor Cyan
Write-Host "http://localhost:8000/health" -ForegroundColor Yellow