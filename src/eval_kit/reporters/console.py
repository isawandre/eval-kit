from __future__ import annotations

from eval_kit.models import EvalReport, Verdict
from eval_kit.reporters.base import BaseReporter
from eval_kit.scoring import ScoreCard

_ICONS = {
    Verdict.PASS: "✅",
    Verdict.PARTIAL: "⚠️",
    Verdict.WARN: "⚠️",
    Verdict.FAIL: "❌",
}


class ConsoleReporter(BaseReporter):
    """Pretty-prints results to terminal."""

    def render(self, report: EvalReport, score_card: ScoreCard) -> str:
        lines: list[str] = []
        lines.append(f"{'─' * 60}")
        lines.append(f"  Response : {score_card.response_id}")
        lines.append(
            f"  Score    : {score_card.weighted_score:.2%}  "
            f"{_ICONS[score_card.overall_verdict]} {score_card.overall_verdict.value.upper()}"
        )
        lines.append(f"{'─' * 60}")

        for r in report.results:
            icon = _ICONS[r.verdict]
            lines.append(
                f"  {icon}  {r.filter_name:<28} "
                f"{r.score:.2f}  │ {r.message}"
            )

        lines.append(f"{'─' * 60}\n")
        return "\n".join(lines)

    def render_batch(
        self,
        reports: list[EvalReport],
        score_cards: list[ScoreCard],
    ) -> str:
        parts = [
            self.render(r, s) for r, s in zip(reports, score_cards)
        ]
        return "\n".join(parts)
