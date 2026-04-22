from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from eval_kit.filters.base import BaseFilter
from eval_kit.models import EvalReport, FilterResult, Verdict


class Pipeline:
    """Chains filters, runs them against a response, returns an EvalReport."""

    def __init__(self, filters: list[BaseFilter] | None = None):
        self._filters: list[BaseFilter] = filters or []

    # ── builder helpers ──────────────────────────────────────────
    def add(self, f: BaseFilter) -> "Pipeline":
        self._filters.append(f)
        return self                       # allows chaining: p.add(A()).add(B())

    def add_many(self, fs: list[BaseFilter]) -> "Pipeline":
        self._filters.extend(fs)
        return self

    # ── core run ─────────────────────────────────────────────────
    def run(
        self,
        text: str,
        *,
        response_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> EvalReport:
        response_id = response_id or uuid.uuid4().hex[:12]
        results: list[FilterResult] = []

        for f in self._filters:
            try:
                result = f.evaluate(text)
            except Exception as exc:
                result = FilterResult(
                    filter_name=f.name,
                    verdict=Verdict.FAIL,
                    score=0.0,
                    message=f"Filter crashed: {exc}",
                    details={"error": str(exc)},
                )
            results.append(result)

        return EvalReport(
            response_id=response_id,
            response_text=text,
            results=results,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )

    # ── batch convenience ────────────────────────────────────────
    def run_batch(
        self,
        texts: list[str],
        *,
        metadata: Optional[dict] = None,
    ) -> list[EvalReport]:
        return [
            self.run(t, metadata=metadata)
            for t in texts
        ]
