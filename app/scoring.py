from typing import List
from models import Loan

def calculate_score(income_amount: float, loans_history: List[Loan]) -> float:
    """
    Логика расчета одобренной суммы по правилам:
    1. Если есть история займов → 30000₽
    2. Если нет истории и доход > 50000 → 20000₽
    3. Если нет истории и доход > 30000 → 10000₽
    4. Иначе → 0₽
    """
    if loans_history:
        return 30000.0
    elif not loans_history and income_amount > 50000:
        return 20000.0
    elif not loans_history and income_amount > 30000:
        return 10000.0
    else:
        return 0.0