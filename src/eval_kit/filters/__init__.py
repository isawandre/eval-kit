from __future__ import annotations

"""
Public filter exports.

Canonical class names live in their module files.
Short aliases (FormatFilter, LengthFilter …) match the CLI.
Both conventions are importable.
"""

from eval_kit.filters.base import BaseFilter
from eval_kit.filters.surface import (
    WordCountFilter,
    ProfanityFilter,
    FormatComplianceFilter,
    ReadabilityFilter,
)
from eval_kit.filters.structural import (
    CoherenceFilter,
    InstructionFollowingFilter,
)
from eval_kit.filters.substance import (
    ReasoningDepthFilter,
    FactualDensityFilter,
)
from eval_kit.filters.polish import (
    ToneConsistencyFilter,
    RedundancyFilter,
)

# ── short aliases (used by CLI & quick-start examples) ───────────
FormatFilter    = FormatComplianceFilter
LengthFilter    = WordCountFilter
RepetitionFilter = RedundancyFilter
FactualityFilter = FactualDensityFilter
ToneFilter       = ToneConsistencyFilter

__all__ = [
    # base
    "BaseFilter",
    # canonical
    "WordCountFilter",
    "ProfanityFilter",
    "FormatComplianceFilter",
    "ReadabilityFilter",
    "CoherenceFilter",
    "InstructionFollowingFilter",
    "ReasoningDepthFilter",
    "FactualDensityFilter",
    "ToneConsistencyFilter",
    "RedundancyFilter",
    # aliases
    "FormatFilter",
    "LengthFilter",
    "RepetitionFilter",
    "FactualityFilter",
    "ToneFilter",
]
