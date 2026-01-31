from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge
import time

# Создаем кастомные метрики
REQUEST_COUNT = Counter(
    'scoring_service_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'scoring_service_request_duration_seconds',
    'Request latency in seconds',
    ['method', 'endpoint', 'status'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

SCORING_RESULTS = Counter(
    'scoring_service_results_total',
    'Scoring results distribution',
    ['result_range']
)

def instrument_app(app):
    """Инструментирование приложения метриками Prometheus"""
    
    # Базовый инструментатор
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        excluded_handlers=["/metrics", "/health"],
    )
    
    # Добавляем кастомные метрики
    @app.middleware("http")
    async def add_metrics(request, call_next):
        start_time = time.time()
        
        # Продолжаем обработку запроса
        response = await call_next(request)
        
        # Регистрируем метрики
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).observe(time.time() - start_time)
        
        return response
    
    instrumentator.instrument(app).expose(app)