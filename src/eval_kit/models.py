from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class Verdict(Enum):
    PASS = "pass"
    PARTIAL = "partial"
    WARN = "warn"
    FAIL = "fail"


class Tier(Enum):
    SURFACE = 1
    STRUCTURAL = 2
    SUBSTANCE = 3
    POLISH = 4
    DOMAIN = 5


@dataclass
class FilterResult:
    filter_name: str
    verdict: Verdict
    score: float  # 0.0 to 1.0
    tier: Tier = Tier.SURFACE
    message: str = ""
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)
    
    @property
    def passed(self) -> bool:
        return self.verdict in (Verdict.PASS, Verdict.PARTIAL)


@dataclass
class PipelineReport:
    input_text: str
    results: list[FilterResult] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @property
    def composite_score(self) -> float:
        if not self.results:
            return 0.0
        weights = {Tier.SURFACE: 1.0, Tier.STRUCTURAL: 1.5, 
                   Tier.SUBSTANCE: 2.5, Tier.POLISH: 1.0}
        total_weight = 0.0
        weighted_sum = 0.0
        for r in self.results:
            w = weights.get(r.tier, 1.0)
            weighted_sum += r.score * w
            total_weight += w
        return round(weighted_sum / total_weight, 4)

    @property
    def overall_verdict(self) -> Verdict:
        if any(r.verdict == Verdict.FAIL for r in self.results):
            return Verdict.FAIL
        if any(r.verdict == Verdict.PARTIAL for r in self.results):
            return Verdict.PARTIAL
        return Verdict.PASS

    @property
    def strength_map(self) -> dict[str, list[str]]:
        return {r.filter_name: r.strengths for r in self.results if r.strengths}

    @property
    def weakness_map(self) -> dict[str, list[str]]:
        return {r.filter_name: r.weaknesses for r in self.results if r.weaknesses}


@dataclass
class EvalReport:
    """Evaluation report from running a pipeline on a text."""
    response_id: str
    response_text: str
    results: list[FilterResult] = field(default_factory=list)
    timestamp: str = ""
    metadata: dict = field(default_factory=dict)
