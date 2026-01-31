from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class LoanStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"

class Loan(BaseModel):
    amount: float = Field(ge=0, description="Сумма займа")
    loan_date: str = Field(..., description="Дата оформления в формате ДД.ММ.ГГГГ")
    is_closed: bool = Field(..., description="Флаг закрытия займа")

class ScoringRequest(BaseModel):
    income_amount: float = Field(ge=0, description="Уровень дохода")
    loans_history: List[Loan] = Field(default=[], description="История займов")

class ScoringResponse(BaseModel):
    result: float = Field(..., description="Одобренная сумма")