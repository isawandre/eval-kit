from __future__ import annotations

import re
from eval_kit.models import FilterResult, Tier, Verdict
from eval_kit.filters.base import BaseFilter


class CoherenceFilter(BaseFilter):
    name = "coherence"
    tier = Tier.STRUCTURAL

    # transition words that signal logical flow
    TRANSITION_MARKERS = {
        "however", "therefore", "furthermore", "moreover",
        "additionally", "consequently", "nevertheless",
        "although", "because", "since", "thus", "hence",
        "meanwhile", "specifically", "for example",
        "in contrast", "on the other hand", "as a result",
        "in addition", "first", "second", "third", "finally",
        "next", "then", "also", "similarly", "likewise"
    }

    def evaluate(self, text: str, config: dict | None = None) -> FilterResult:
        config = config or {}
        min_transitions_per_500_words = config.get("min_transitions_per_500", 3)
        
        words = text.lower().split()
        word_count = len(words)
        strengths = []
        weaknesses = []

        # count transition usage
        text_lower = text.lower()
        found_transitions = []
        for marker in self.TRANSITION_MARKERS:
            if marker in text_lower:
                found_transitions.append(marker)

        # normalize to per-500-word rate
        if word_count > 0:
            rate = (len(found_transitions) / word_count) * 500
        else:
            rate = 0

        # paragraph structure check
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        avg_para_len = 0
        if paragraphs:
            avg_para_len = word_count / len(paragraphs)

        # repetition check — crude but useful
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip().lower() for s in sentences if len(s.strip()) > 10]
        unique_starts = set()
        repetitive_starts = 0
        for s in sentences:
            first_three = " ".join(s.split()[:3])
            if first_three in unique_starts:
                repetitive_starts += 1
            unique_starts.add(first_three)

        # scoring
        score_components = []

        # transition score (40% weight)
        if rate >= min_transitions_per_500_words:
            score_components.append(1.0)
            strengths.append(f"Good transition usage ({len(found_transitions)} markers found)")
        elif rate >= min_transitions_per_500_words * 0.5:
            score_components.append(0.6)
            weaknesses.append("Below average transition word usage")
        else:
            score_components.append(0.2)
            weaknesses.append("Very few logical connectors between ideas")

        # paragraph structure score (30% weight)
        if len(paragraphs) >= 2 and 40 < avg_para_len < 200:
            score_components.append(1.0)
            strengths.append(f"Well-structured paragraphs (avg {int(avg_para_len)} words)")
        elif len(paragraphs) >= 2:
            score_components.append(0.6)
            weaknesses.append(f"Paragraph length imbalance (avg {int(avg_para_len)} words)")
        else:
            score_components.append(0.3)
            weaknesses.append("Text lacks paragraph breaks")

        # repetition score (30% weight)
        if len(sentences) > 0:
            rep_ratio = repetitive_starts / len(sentences)
        else:
            rep_ratio = 0
        
        if rep_ratio < 0.1:
            score_components.append(1.0)
            strengths.append("Varied sentence openings")
        elif rep_ratio < 0.25:
            score_components.append(0.6)
            weaknesses.append("Some repetitive sentence beginnings")
        else:
            score_components.append(0.2)
            weaknesses.append(f"Highly repetitive openings ({int(rep_ratio*100)}% repeated)")

        weights = [0.4, 0.3, 0.3]
        score = sum(s * w for s, w in zip(score_components, weights))

        if score >= 0.75:
            verdict = Verdict.PASS
        elif score >= 0.45:
            verdict = Verdict.PARTIAL
        else:
            verdict = Verdict.FAIL

        return FilterResult(
            filter_name=self.name,
            tier=self.tier,
            verdict=verdict,
            score=round(score, 4),
            strengths=strengths,
            weaknesses=weaknesses,
            details={
                "transitions_found": found_transitions,
                "transition_rate_per_500": round(rate, 2),
                "paragraph_count": len(paragraphs),
                "avg_paragraph_length": round(avg_para_len, 1),
                "repetitive_start_ratio": round(rep_ratio, 3)
            }
        )


class InstructionFollowingFilter(BaseFilter):
    name = "instruction_following"
    tier = Tier.STRUCTURAL

    def evaluate(self, text: str, config: dict | None = None) -> FilterResult:
        config = config or {}
        required_elements = config.get("required_elements", [])
        banned_elements = config.get("banned_elements", [])
        
        strengths = []
        weaknesses = []
        text_lower = text.lower()

        hits = 0
        misses = []
        for element in required_elements:
            if element.lower() in text_lower:
                hits += 1
            else:
                misses.append(element)

        violations = []
        for element in banned_elements:
            if element.lower() in text_lower:
                violations.append(element)

        total_checks = len(required_elements) + len(banned_elements)

        if total_checks == 0:
            return FilterResult(
                filter_name=self.name,
                tier=self.tier,
                verdict=Verdict.PASS,
                score=1.0,
                strengths=["No specific instruction constraints defined"],
                weaknesses=[],
                details={"note": "no constraints provided in config"}
            )

        passed_checks = hits + (len(banned_elements) - len(violations))
        score = passed_checks / total_checks

        if misses:
            weaknesses.append(f"Missing required elements: {', '.join(misses)}")
        if hits > 0:
            strengths.append(f"Included {hits}/{len(required_elements)} required elements")
        if violations:
            weaknesses.append(f"Contains banned elements: {', '.join(violations)}")
        if not violations and banned_elements:
            strengths.append("Avoided all banned elements")

        if score >= 0.8:
            verdict = Verdict.PASS
        elif score >= 0.5:
            verdict = Verdict.PARTIAL
        else:
            verdict = Verdict.FAIL

        return FilterResult(
            filter_name=self.name,
            tier=self.tier,
            verdict=verdict,
            score=round(score, 4),
            strengths=strengths,
            weaknesses=weaknesses,
            details={
                "required_hits": hits,
                "required_total": len(required_elements),
                "missing": misses,
                "violations": violations
            }
        )
