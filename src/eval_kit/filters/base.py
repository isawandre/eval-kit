from __future__ import annotations

from abc import ABC, abstractmethod
from eval_kit.models import FilterResult, Tier, Verdict


class BaseFilter(ABC):
    """
    Contract:
    - evaluate() must ALWAYS return a FilterResult
    - evaluate() must NEVER raise an exception
    - populate strengths AND weaknesses regardless of verdict
    - each filter operates independently, no dependency on other filters
    """

    name: str = "unnamed_filter"
    tier: Tier = Tier.SURFACE

    @abstractmethod
    def evaluate(self, text: str, config: dict | None = None) -> FilterResult:
        ...

    def safe_evaluate(self, text: str, config: dict | None = None) -> FilterResult:
        try:
            return self.evaluate(text, config)
        except Exception as e:
            return FilterResult(
                filter_name=self.name,
                tier=self.tier,
                verdict=Verdict.FAIL,
                score=0.0,
                strengths=[],
                weaknesses=[f"Filter crashed: {str(e)}"],
                details={"error": str(e)}
            )
