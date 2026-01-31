import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

from app.main import app
from app.models import ScoringRequest, Loan

client = TestClient(app)

def test_health_check():
    """Тест эндпоинта здоровья"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_scoring_with_loans():
    """Тест расчета с историей займов"""
    request_data = {
        "income_amount": 10000,
        "loans_history": [
            {
                "amount": 10000,
                "loan_date": "22.10.2025",
                "is_closed": True
            }
        ]
    }
    
    response = client.post("/scoring", json=request_data)
    assert response.status_code == 200
    assert response.json() == {"result": 30000}

def test_scoring_no_loans_high_income():
    """Тест расчета без займов с высоким доходом"""
    request_data = {
        "income_amount": 60000,
        "loans_history": []
    }
    
    response = client.post("/scoring", json=request_data)
    assert response.status_code == 200
    assert response.json() == {"result": 20000}

def test_scoring_no_loans_medium_income():
    """Тест расчета без займов со средним доходом"""
    request_data = {
        "income_amount": 40000,
        "loans_history": []
    }
    
    response = client.post("/scoring", json=request_data)
    assert response.status_code == 200
    assert response.json() == {"result": 10000}

def test_scoring_no_loans_low_income():
    """Тест расчета без займов с низким доходом"""
    request_data = {
        "income_amount": 20000,
        "loans_history": []
    }
    
    response = client.post("/scoring", json=request_data)
    assert response.status_code == 200
    assert response.json() == {"result": 0}

def test_scoring_invalid_data():
    """Тест с некорректными данными"""
    request_data = {
        "income_amount": -100,  # Отрицательный доход
        "loans_history": []
    }
    
    response = client.post("/scoring", json=request_data)
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_cache_functionality():
    """Тест работы кэширования"""
    with patch('app.main.redis_client') as mock_redis:
        # Настраиваем mock
        mock_redis.get_cached_result.return_value = None
        mock_redis.generate_cache_key.return_value = "test_key"
        
        request_data = {
            "income_amount": 60000,
            "loans_history": []
        }
        
        # Первый запрос - нет в кэше
        response = client.post("/scoring", json=request_data)
        assert response.status_code == 200
        
        # Второй запрос - должен быть в кэше
        mock_redis.get_cached_result.return_value = 20000.0
        response = client.post("/scoring", json=request_data)
        assert response.status_code == 200
        
        # Проверяем, что метод кэширования вызывался
        assert mock_redis.cache_result.called

def test_metrics_endpoint():
    """Тест доступности метрик Prometheus"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "scoring_service_requests_total" in response.text