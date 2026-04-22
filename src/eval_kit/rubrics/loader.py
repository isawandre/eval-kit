from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RubricConfig:
    """Single rubric definition loaded from YAML."""

    name: str
    description: str
    weight: float
    scoring_mode: str                        # keyword_coverage | pattern_match | composite
    positive_signals: list[str] = field(default_factory=list)
    negative_signals: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    expected_min_hits: int = 2
    negative_penalty: float = 0.25
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RubricPack:
    """Loaded rubric pack ready for scoring."""

    name: str
    version: str
    description: str
    gate: str
    pass_threshold: float
    warn_threshold: float
    rubrics: list[RubricConfig]
    source_path: Path | None = None


class RubricPackLoader:
    """Load a rubric pack directory into a ``RubricPack``."""

    # ── public API ──────────────────────────────────────────────
    @staticmethod
    def load(pack_path: str | Path) -> RubricPack:
        yaml = _require_yaml()

        pack_dir = Path(pack_path).resolve()
        manifest_file = pack_dir / "manifest.yaml"

        if not manifest_file.exists():
            raise FileNotFoundError(
                f"No manifest.yaml in {pack_dir}"
            )

        with manifest_file.open(encoding="utf-8") as fh:
            manifest: dict = yaml.safe_load(fh)

        thresholds = manifest.get("thresholds", {})

        rubrics: list[RubricConfig] = []
        for entry in manifest.get("rubrics", []):
            rubric_file = pack_dir / entry["file"]
            if not rubric_file.exists():
                raise FileNotFoundError(
                    f"Rubric file missing: {rubric_file}"
                )

            with rubric_file.open(encoding="utf-8") as fh:
                raw: dict = yaml.safe_load(fh)

            scoring = raw.get("scoring", {})

            rubrics.append(
                RubricConfig(
                    name=raw["name"],
                    description=raw.get("description", ""),
                    weight=float(entry.get("weight", 1.0)),
                    scoring_mode=scoring.get("mode", "keyword_coverage"),
                    positive_signals=scoring.get("positive_signals", []),
                    negative_signals=scoring.get("negative_signals", []),
                    patterns=scoring.get("patterns", []),
                    expected_min_hits=int(scoring.get("expected_min_hits", 2)),
                    negative_penalty=float(scoring.get("negative_penalty", 0.25)),
                    metadata=raw.get("metadata", {}),
                )
            )

        return RubricPack(
            name=manifest["name"],
            version=manifest.get("version", "0.0.0"),
            description=manifest.get("description", ""),
            gate=manifest.get("gate", "domain"),
            pass_threshold=float(thresholds.get("pass", 0.80)),
            warn_threshold=float(thresholds.get("warn", 0.50)),
            rubrics=rubrics,
            source_path=pack_dir,
        )

    # ── validation helper ────────────────────────────────────────
    @staticmethod
    def validate(pack: RubricPack) -> list[str]:
        """Return a list of warnings (empty = healthy)."""
        warnings: list[str] = []

        if not pack.rubrics:
            warnings.append("Pack has zero rubrics.")

        total_weight = sum(r.weight for r in pack.rubrics)
        if abs(total_weight - 1.0) > 0.01:
            warnings.append(
                f"Rubric weights sum to {total_weight:.2f}, expected ~1.0."
            )

        for r in pack.rubrics:
            if r.scoring_mode == "pattern_match" and not r.patterns:
                warnings.append(
                    f"Rubric '{r.name}' uses pattern_match but has no patterns."
                )
            if r.scoring_mode == "keyword_coverage" and not r.positive_signals:
                warnings.append(
                    f"Rubric '{r.name}' uses keyword_coverage but has no positive_signals."
                )
            # quick regex syntax check
            for p in r.patterns:
                try:
                    re.compile(p)
                except re.error as exc:
                    warnings.append(
                        f"Rubric '{r.name}' has invalid regex '{p}': {exc}"
                    )

        return warnings


# ── private helpers ─────────────────────────────────────────────
def _require_yaml():
    try:
        import yaml
        return yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required for rubric packs. "
            "Install it with: pip install eval-kit[rubrics]"
        ) from None
