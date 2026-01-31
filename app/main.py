from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
import json
from typing import Dict

from app.models import ScoringRequest, ScoringResponse
from app.redis_client import redis_client
from app.scoring import calculate_score
from app.metrics import instrument_app
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    print("Starting Scoring Service...")
    yield
    # Shutdown
    print("Shutting down Scoring Service...")

app = FastAPI(
    title="Scoring Service",
    description="Сервис для расчета одобренной суммы кредита",
    version="1.0.0",
    lifespan=lifespan
)

# Инструментируем приложение метриками
instrument_app(app)

@app.get("/health")
async def health_check():
    """Эндпоинт для проверки здоровья сервиса"""
    return {"status": "healthy"}

@app.post("/scoring", response_model=ScoringResponse)
async def scoring_endpoint(request: ScoringRequest):
    """
    Эндпоинт для расчета скоринга клиента.
    
    - Проверяет кэш в Redis
    - Если нет в кэше - рассчитывает сумму
    - Сохраняет результат в Redis
    """
    try:
        # Генерируем ключ для кэша
        request_data = request.model_dump()
        cache_key = redis_client.generate_cache_key(request_data)
        
        # Проверяем кэш
        cached_result = redis_client.get_cached_result(cache_key)
        if cached_result is not None:
            return ScoringResponse(result=cached_result)
        
        # Рассчитываем сумму
        result = calculate_score(
            income_amount=request.income_amount,
            loans_history=request.loans_history
        )
        
        # Сохраняем в кэш
        redis_client.cache_result(cache_key, result)
        
        # Регистрируем результат для метрик
        from .metrics import SCORING_RESULTS
        if result == 0:
            SCORING_RESULTS.labels(result_range="0").inc()
        elif result == 10000:
            SCORING_RESULTS.labels(result_range="10000").inc()
        elif result == 20000:
            SCORING_RESULTS.labels(result_range="20000").inc()
        elif result == 30000:
            SCORING_RESULTS.labels(result_range="30000").inc()
        
        return ScoringResponse(result=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )