"""Token kullanimi ve maliyet takibi."""
from collections import defaultdict
from typing import Dict

class CostTracker:
    """Token ve maliyet istatistiklerini tutar."""

    def __init__(self) -> None:
        self.usage_by_model: Dict[str, int] = defaultdict(int)
        self.cost_by_model: Dict[str, float] = defaultdict(float)

    def add_usage(self, model: str, prompt_tokens: int, completion_tokens: int, cost: float) -> None:
        self.usage_by_model[model] += prompt_tokens + completion_tokens
        self.cost_by_model[model] += cost

    def get_total_usage(self) -> int:
        return sum(self.usage_by_model.values())

    def get_total_cost(self) -> float:
        return sum(self.cost_by_model.values())

    def get_usage_by_model(self) -> Dict[str, int]:
        return dict(self.usage_by_model)

    def reset(self) -> None:
        self.usage_by_model.clear()
        self.cost_by_model.clear()
