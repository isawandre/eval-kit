from __future__ import annotations

from dataclasses import dataclass, field

from eval_kit.models import EvalReport, Verdict


@dataclass
class ScoreCard:
    """Aggregate scoring output for one EvalReport."""

    response_id: str
    weighted_score: float          # 0.0 – 1.0
    overall_verdict: Verdict
    filter_scores: dict[str, float] = field(default_factory=dict)
    breakdown: dict[str, Verdict] = field(default_factory=dict)


class ScoringEngine:
    """
    Converts an EvalReport into a single weighted score + overall verdict.

    weights : {filter_name: float}  – relative importance (auto-normalized)
    pass_threshold : score >= this → PASS
    warn_threshold : score >= this → WARN  (below = FAIL)
    """

    def __init__(
        self,
        weights: dict[str, float] | None = None,
        pass_threshold: float = 0.80,
        warn_threshold: float = 0.50,
    ):
        self._raw_weights = weights or {}
        self.pass_threshold = pass_threshold
        self.warn_threshold = warn_threshold

    # ── helpers ───────────────────────────────────────────────────
    def _normalize(self, names: list[str]) -> dict[str, float]:
        raw = {n: self._raw_weights.get(n, 1.0) for n in names}
        total = sum(raw.values()) or 1.0
        return {n: v / total for n, v in raw.items()}

    def _verdict_from_score(self, score: float) -> Verdict:
        if score >= self.pass_threshold:
            return Verdict.PASS
        if score >= self.warn_threshold:
            return Verdict.WARN
        return Verdict.FAIL

    # ── core ─────────────────────────────────────────────────────
    def score(self, report: EvalReport) -> ScoreCard:
        names = [r.filter_name for r in report.results]
        norm = self._normalize(names)

        filter_scores: dict[str, float] = {}
        breakdown: dict[str, Verdict] = {}
        weighted_sum = 0.0

        for r in report.results:
            filter_scores[r.filter_name] = r.score
            breakdown[r.filter_name] = r.verdict
            weighted_sum += r.score * norm[r.filter_name]

        return ScoreCard(
            response_id=report.response_id,
            weighted_score=round(weighted_sum, 4),
            overall_verdict=self._verdict_from_score(weighted_sum),
            filter_scores=filter_scores,
            breakdown=breakdown,
        )

    def score_batch(self, reports: list[EvalReport]) -> list[ScoreCard]:
        return [self.score(r) for r in reports]
