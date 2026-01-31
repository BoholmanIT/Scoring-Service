from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from fastapi.routing import APIRoute
import time
from typing import Callable

# Создаем метрики
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

class PrometheusMiddleware:
    """Middleware для сбора метрик"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        # Перехват запроса для сбора метрик
        async def send_wrapper(response):
            if response['type'] == 'http.response.start':
                # Регистрируем метрики
                method = scope['method']
                endpoint = scope['path']
                status = response['status']
                
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()
                
                REQUEST_LATENCY.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).observe(time.time() - start_time)
            
            await send(response)
        
        await self.app(scope, receive, send_wrapper)

def instrument_app(app):
    """Инструментирование приложения метриками Prometheus"""
    
    # Добавляем middleware
    app.add_middleware(PrometheusMiddleware)
    
    # Добавляем эндпоинт для метрик
    @app.get("/metrics")
    async def metrics():
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )