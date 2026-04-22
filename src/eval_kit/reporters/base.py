from __future__ import annotations

from abc import ABC, abstractmethod

from eval_kit.models import EvalReport
from eval_kit.scoring import ScoreCard


class BaseReporter(ABC):
    """All reporters conform to this interface."""

    @abstractmethod
    def render(self, report: EvalReport, score_card: ScoreCard) -> str:
        ...

    @abstractmethod
    def render_batch(
        self,
        reports: list[EvalReport],
        score_cards: list[ScoreCard],
    ) -> str:
        ...
