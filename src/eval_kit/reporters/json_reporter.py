from __future__ import annotations

import json
from typing import Any

from eval_kit.models import EvalReport
from eval_kit.reporters.base import BaseReporter
from eval_kit.scoring import ScoreCard


class JSONReporter(BaseReporter):
    """Serializes results to JSON (for logging, dashboards, CI pipelines)."""

    def __init__(self, indent: int = 2):
        self._indent = indent

    def _card_to_dict(self, report: EvalReport, sc: ScoreCard) -> dict[str, Any]:
        return {
            "response_id": sc.response_id,
            "weighted_score": sc.weighted_score,
            "overall_verdict": sc.overall_verdict.value,
            "timestamp": report.timestamp,
            "filters": [
                {
                    "name": r.filter_name,
                    "verdict": r.verdict.value,
                    "score": r.score,
                    "message": r.message,
                    "details": r.details,
                }
                for r in report.results
            ],
            "metadata": report.metadata,
        }

    def render(self, report: EvalReport, score_card: ScoreCard) -> str:
        return json.dumps(
            self._card_to_dict(report, score_card),
            indent=self._indent,
        )

    def render_batch(
        self,
        reports: list[EvalReport],
        score_cards: list[ScoreCard],
    ) -> str:
        payload = [
            self._card_to_dict(r, s)
            for r, s in zip(reports, score_cards)
        ]
        return json.dumps(payload, indent=self._indent)
