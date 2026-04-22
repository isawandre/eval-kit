"""
Tests for the rubric pack loader and domain filter.
"""

import json
from pathlib import Path

import pytest

from eval_kit.models import Verdict, Tier
from eval_kit.rubrics import RubricPackLoader, RubricPack, RubricConfig, DomainFilter


PACK_DIR = Path(__file__).resolve().parent.parent / "rubric_packs" / "customer_support"


# ── loader tests ─────────────────────────────────────────────────
class TestRubricPackLoader:

    def test_load_customer_support_pack(self):
        pack = RubricPackLoader.load(PACK_DIR)
        assert isinstance(pack, RubricPack)
        assert pack.name == "customer_support"
        assert pack.version == "1.0.0"
        assert len(pack.rubrics) == 3

    def test_rubric_names(self):
        pack = RubricPackLoader.load(PACK_DIR)
        names = {r.name for r in pack.rubrics}
        assert names == {"escalation_detection", "resolution_quality", "empathy_score"}

    def test_weights_sum_to_one(self):
        pack = RubricPackLoader.load(PACK_DIR)
        total = sum(r.weight for r in pack.rubrics)
        assert abs(total - 1.0) < 0.01

    def test_thresholds_loaded(self):
        pack = RubricPackLoader.load(PACK_DIR)
        assert pack.pass_threshold == 0.75
        assert pack.warn_threshold == 0.45

    def test_scoring_modes(self):
        pack = RubricPackLoader.load(PACK_DIR)
        modes = {r.name: r.scoring_mode for r in pack.rubrics}
        assert modes["escalation_detection"] == "keyword_coverage"
        assert modes["resolution_quality"] == "composite"
        assert modes["empathy_score"] == "keyword_coverage"

    def test_missing_manifest_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="manifest.yaml"):
            RubricPackLoader.load(tmp_path)

    def test_validate_healthy_pack(self):
        pack = RubricPackLoader.load(PACK_DIR)
        warnings = RubricPackLoader.validate(pack)
        assert warnings == []


# ── domain filter tests ──────────────────────────────────────────
class TestDomainFilter:

    @pytest.fixture
    def cs_filter(self) -> DomainFilter:
        pack = RubricPackLoader.load(PACK_DIR)
        return DomainFilter(pack)

    def test_filter_metadata(self, cs_filter):
        assert cs_filter.name == "domain_customer_support"
        assert cs_filter.tier == Tier.DOMAIN

    def test_strong_response_scores_high(self, cs_filter):
        text = (
            "I'm sorry to hear about your experience — that must be frustrating. "
            "I understand your concern completely. Let me escalate this to a "
            "specialist on our dedicated team right away. I've gone ahead and "
            "applied a refund of $25 credited to your account. You should see a "
            "confirmation email within 24 hours. Thank you for your patience."
        )
        result = cs_filter.evaluate(text)
        assert result.score >= 0.70
        assert result.verdict in (Verdict.PASS, Verdict.WARN)
        assert "rubric_scores" in result.details

    def test_weak_response_scores_low(self, cs_filter):
        text = (
            "Per our policy, that is incorrect. There's nothing I can do. "
            "You should have read the terms. It's not our fault. "
            "Call back later if you want."
        )
        result = cs_filter.evaluate(text)
        assert result.score < 0.50
        assert result.verdict == Verdict.FAIL

    def test_empty_text(self, cs_filter):
        result = cs_filter.evaluate("")
        assert isinstance(result.score, float)
        assert result.score <= 0.5

    def test_rubric_details_present(self, cs_filter):
        result = cs_filter.evaluate("I understand. Let me transfer you to a manager.")
        details = result.details
        assert "rubric_scores" in details
        assert "rubric_details" in details
        assert "escalation_detection" in details["rubric_scores"]
        assert "empathy_score" in details["rubric_scores"]
        assert "resolution_quality" in details["rubric_scores"]

    def test_partial_match_still_reports_strengths(self, cs_filter):
        """Even a response that fails overall should show what WAS strong."""
        text = (
            "I'm sorry about that, I understand your frustration. "
            "Unfortunately we cannot help. That's not possible."
        )
        result = cs_filter.evaluate(text)
        scores = result.details["rubric_scores"]
        # empathy should score okay — positive signals present
        assert scores["empathy_score"] > 0.0
        # resolution should tank — negative signals dominate
        assert scores["resolution_quality"] < scores["empathy_score"]

    def test_pattern_match_rubric(self, cs_filter):
        """resolution_quality uses composite mode with patterns."""
        text = (
            "I've already processed a refund of $50. "
            "You'll receive a confirmation email within 2 business days."
        )
        result = cs_filter.evaluate(text)
        res_detail = result.details["rubric_details"]["resolution_quality"]
        # composite mode returns keyword + pattern sub-details
        assert "keyword" in res_detail or "pattern" in res_detail


# ── programmatic rubric config ──────────────────────────────────
class TestInlineRubricPack:
    """Build a pack in code without YAML files."""

    def test_inline_pack(self):
        pack = RubricPack(
            name="test_inline",
            version="0.0.1",
            description="unit test pack",
            gate="domain",
            pass_threshold=0.60,
            warn_threshold=0.30,
            rubrics=[
                RubricConfig(
                    name="has_greeting",
                    description="checks for a greeting",
                    weight=1.0,
                    scoring_mode="keyword_coverage",
                    positive_signals=["hello", "hi", "good morning"],
                    negative_signals=[],
                    expected_min_hits=1,
                    negative_penalty=0.0,
                ),
            ],
        )

        filt = DomainFilter(pack)

        result_pass = filt.evaluate("Hello! How can I help you today?")
        assert result_pass.score >= 0.60

        result_fail = filt.evaluate("The fiscal quarter ended in March.")
        assert result_fail.score < 0.60
