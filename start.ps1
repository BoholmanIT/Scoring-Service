Write-Host "Запуск Scoring Service на Windows..." -ForegroundColor Green

# Проверка Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker не установлен!" -ForegroundColor Red
    exit 1
}

# Проверка Docker Compose
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "Docker Compose не установлен!" -ForegroundColor Red
    exit 1
}

# Остановка предыдущих контейнеров
Write-Host "Останавливаем предыдущие контейнеры..." -ForegroundColor Yellow
docker-compose down

# Сборка и запуск
Write-Host "Собираем и запускаем контейнеры..." -ForegroundColor Yellow
docker-compose up --build -d

# Ожидание запуска
Write-Host "Ожидаем запуск сервисов (30 секунд)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Проверка сервисов
Write-Host "`nПроверка сервисов:" -ForegroundColor Green
Write-Host "1. FastAPI: http://localhost:8000/docs"
Write-Host "2. Grafana: http://localhost:3000 (admin/admin)"
Write-Host "3. Prometheus: http://localhost:9090"
Write-Host "4. Health-check: http://localhost:8000/health"
Write-Host "`nДля просмотра логов выполните: docker-compose logs -f" -ForegroundColor Cyan