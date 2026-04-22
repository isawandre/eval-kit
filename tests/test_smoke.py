"""
Smoke tests — verify the full pipeline runs end-to-end
without crashing and returns sane types.
"""

from eval_kit.filters import (
    FormatComplianceFilter,
    WordCountFilter,
    RedundancyFilter,
    CoherenceFilter,
    ReasoningDepthFilter,
    FactualDensityFilter,
    ToneConsistencyFilter,
)
from eval_kit.models import EvalReport, Verdict
from eval_kit.pipeline import Pipeline
from eval_kit.scoring import ScoreCard, ScoringEngine
from eval_kit.reporters import ConsoleReporter, JSONReporter


SAMPLE_GOOD = (
    "The quarterly revenue increased by 14% compared to the previous period. "
    "This growth was driven primarily by expansion in the APAC region, where "
    "new enterprise contracts accounted for roughly 60% of net new ARR. "
    "Customer churn remained stable at 4.2%, and NPS improved from 38 to 45."
)

SAMPLE_BAD = "yeah idk lol"

ALL_FILTERS = [
    FormatComplianceFilter(),
    WordCountFilter(),
    RedundancyFilter(),
    CoherenceFilter(),
    ReasoningDepthFilter(),
    FactualDensityFilter(),
    ToneConsistencyFilter(),
]


def _run(text: str) -> tuple[EvalReport, ScoreCard]:
    pipe = Pipeline(filters=ALL_FILTERS)
    report = pipe.run(text)
    card = ScoringEngine().score(report)
    return report, card


# ── type checks ──────────────────────────────────────────────────
def test_report_types():
    report, card = _run(SAMPLE_GOOD)
    assert isinstance(report, EvalReport)
    assert isinstance(card, ScoreCard)
    assert isinstance(card.weighted_score, float)
    assert card.overall_verdict in (Verdict.PASS, Verdict.WARN, Verdict.FAIL)


def test_all_filters_present():
    report, _ = _run(SAMPLE_GOOD)
    names = {r.filter_name for r in report.results}
    expected = {f.name for f in ALL_FILTERS}
    assert names == expected


# ── score sanity ─────────────────────────────────────────────────
def test_good_text_scores_higher():
    _, good_card = _run(SAMPLE_GOOD)
    _, bad_card = _run(SAMPLE_BAD)
    assert good_card.weighted_score > bad_card.weighted_score


def test_scores_bounded():
    _, card = _run(SAMPLE_GOOD)
    assert 0.0 <= card.weighted_score <= 1.0
    for s in card.filter_scores.values():
        assert 0.0 <= s <= 1.0


# ── reporters don't crash ───────────────────────────────────────
def test_console_reporter():
    report, card = _run(SAMPLE_GOOD)
    output = ConsoleReporter().render(report, card)
    assert isinstance(output, str)
    assert len(output) > 50


def test_json_reporter():
    report, card = _run(SAMPLE_GOOD)
    output = JSONReporter().render(report, card)
    import json
    parsed = json.loads(output)
    assert "response_id" in parsed
    assert "weighted_score" in parsed
    assert "filters" in parsed


# ── batch ────────────────────────────────────────────────────────
def test_batch_run():
    pipe = Pipeline(filters=ALL_FILTERS)
    reports = pipe.run_batch([SAMPLE_GOOD, SAMPLE_BAD])
    cards = ScoringEngine().score_batch(reports)
    assert len(reports) == 2
    assert len(cards) == 2

    con = ConsoleReporter().render_batch(reports, cards)
    assert SAMPLE_GOOD[:20] not in con or len(con) > 100  # just checking it ran

    j = JSONReporter().render_batch(reports, cards)
    import json
    arr = json.loads(j)
    assert isinstance(arr, list)
    assert len(arr) == 2


# ── crash resilience ─────────────────────────────────────────────
def test_empty_string():
    report, card = _run("")
    assert isinstance(card.weighted_score, float)


def test_unicode_input():
    report, card = _run("日本語テスト 🚀 émojis и кириллица")
    assert isinstance(card.weighted_score, float)
