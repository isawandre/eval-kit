from __future__ import annotations

import re
from eval_kit.filters.base import BaseFilter
from eval_kit.models import FilterResult, Tier, Verdict
from eval_kit.rubrics.loader import RubricConfig, RubricPack


class DomainFilter(BaseFilter):
    """Evaluate text against a loaded rubric pack.

    Scores each rubric independently, then produces a weighted
    composite.  Details dict includes per-rubric breakdowns so
    callers can see exactly which domain criteria passed or failed.
    """

    def __init__(self, pack: RubricPack):
        self.pack = pack
        self.name = f"domain_{pack.name}"
        self.tier = Tier.DOMAIN

    # ── BaseFilter contract ─────────────────────────────────────
    def evaluate(self, text: str, config: dict | None = None) -> FilterResult:
        text_lower = text.lower()
        rubric_scores: dict[str, float] = {}
        rubric_details: dict[str, dict] = {}
        weighted_sum = 0.0
        weight_sum = 0.0

        for rubric in self.pack.rubrics:
            score, detail = self._score_rubric(rubric, text_lower)
            rubric_scores[rubric.name] = round(score, 3)
            rubric_details[rubric.name] = detail
            weighted_sum += score * rubric.weight
            weight_sum += rubric.weight

        composite = weighted_sum / weight_sum if weight_sum > 0 else 0.0

        if composite >= self.pack.pass_threshold:
            verdict = Verdict.PASS
        elif composite >= self.pack.warn_threshold:
            verdict = Verdict.WARN
        else:
            verdict = Verdict.FAIL

        return FilterResult(
            filter_name=self.name,
            tier=self.tier,
            verdict=verdict,
            score=round(composite, 3),
            details={
                "pack": self.pack.name,
                "pack_version": self.pack.version,
                "rubric_scores": rubric_scores,
                "rubric_details": rubric_details,
            },
        )

    # ── rubric dispatch ─────────────────────────────────────────
    def _score_rubric(
        self, rubric: RubricConfig, text_lower: str
    ) -> tuple[float, dict]:
        if rubric.scoring_mode == "keyword_coverage":
            return self._keyword_coverage(rubric, text_lower)
        if rubric.scoring_mode == "pattern_match":
            return self._pattern_match(rubric, text_lower)
        if rubric.scoring_mode == "composite":
            kw_score, kw_detail = self._keyword_coverage(rubric, text_lower)
            pm_score, pm_detail = self._pattern_match(rubric, text_lower)
            avg = (kw_score + pm_score) / 2.0
            return avg, {"keyword": kw_detail, "pattern": pm_detail}
        return 0.0, {"error": f"unknown mode: {rubric.scoring_mode}"}

    # ── keyword coverage scorer ─────────────────────────────────
    @staticmethod
    def _keyword_coverage(
        rubric: RubricConfig, text_lower: str
    ) -> tuple[float, dict]:
        pos_hits = [s for s in rubric.positive_signals if s.lower() in text_lower]
        neg_hits = [s for s in rubric.negative_signals if s.lower() in text_lower]

        hit_count = len(pos_hits)
        expected = max(rubric.expected_min_hits, 1)
        base = min(hit_count / expected, 1.0)
        penalty = len(neg_hits) * rubric.negative_penalty
        score = max(0.0, min(1.0, base - penalty))

        detail = {
            "positive_matched": pos_hits,
            "negative_matched": neg_hits,
            "hit_ratio": f"{hit_count}/{expected}",
            "penalty_applied": round(penalty, 3),
        }
        return score, detail

    # ── pattern match scorer ────────────────────────────────────
    @staticmethod
    def _pattern_match(
        rubric: RubricConfig, text_lower: str
    ) -> tuple[float, dict]:
        if not rubric.patterns:
            return 0.5, {"note": "no patterns defined, neutral score"}

        matched: list[str] = []
        for pattern in rubric.patterns:
            try:
                if re.search(pattern, text_lower):
                    matched.append(pattern)
            except re.error:
                continue

        score = min(len(matched) / len(rubric.patterns), 1.0)
        detail = {
            "patterns_matched": len(matched),
            "patterns_total": len(rubric.patterns),
            "matched": matched,
        }
        return score, detail
