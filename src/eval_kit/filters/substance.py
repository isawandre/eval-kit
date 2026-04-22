from __future__ import annotations

import re
from collections import Counter
from eval_kit.models import FilterResult, Tier, Verdict
from eval_kit.filters.base import BaseFilter


class ReasoningDepthFilter(BaseFilter):
    name = "reasoning_depth"
    tier = Tier.SUBSTANCE

    REASONING_INDICATORS = [
        "because", "due to", "as a result", "this means",
        "the reason", "caused by", "leads to", "implies",
        "suggests that", "evidence", "therefore", "thus",
        "it follows", "given that", "assuming", "if we consider",
        "on one hand", "on the other hand", "weighing",
        "the tradeoff", "compared to", "in contrast",
        "alternatively", "pros and cons", "the risk",
        "the benefit", "specifically", "for instance",
        "for example", "such as", "illustrated by",
        "to put it concretely", "in practice", "consider the case"
    ]

    def evaluate(self, text: str, config: dict | None = None) -> FilterResult:
        config = config or {}
        min_indicators = config.get("min_indicators", 5)
        
        text_lower = text.lower()
        words = text_lower.split()
        word_count = len(words)
        strengths = []
        weaknesses = []

        found_indicators = []
        for indicator in self.REASONING_INDICATORS:
            count = text_lower.count(indicator)
            if count > 0:
                found_indicators.append((indicator, count))

        unique_indicators = len(found_indicators)
        total_usage = sum(c for _, c in found_indicators)

        # causal chain detection — looks for sequential reasoning
        causal_pairs = [
            ("because", "therefore"),
            ("if", "then"),
            ("given", "thus"),
            ("since", "consequently"),
            ("although", "however")
        ]
        chains_found = 0
        for a, b in causal_pairs:
            if a in text_lower and b in text_lower:
                chains_found += 1

        # scoring
        score_parts = []

        # indicator density (50%)
        if unique_indicators >= min_indicators:
            score_parts.append(1.0)
            strengths.append(f"Rich reasoning language ({unique_indicators} unique indicators)")
        elif unique_indicators >= min_indicators * 0.5:
            score_parts.append(0.6)
            weaknesses.append(f"Moderate reasoning depth ({unique_indicators} indicators)")
        else:
            score_parts.append(0.2)
            weaknesses.append(f"Shallow reasoning — only {unique_indicators} indicators found")

        # causal chains (30%)
        if chains_found >= 2:
            score_parts.append(1.0)
            strengths.append(f"Contains {chains_found} causal reasoning chains")
        elif chains_found >= 1:
            score_parts.append(0.6)
            strengths.append("At least one causal chain present")
        else:
            score_parts.append(0.2)
            weaknesses.append("No clear causal reasoning chains detected")

        # word count sanity — deeper reasoning needs more words (20%)
        if word_count >= 200:
            score_parts.append(1.0)
            strengths.append("Sufficient length for substantive analysis")
        elif word_count >= 100:
            score_parts.append(0.6)
        else:
            score_parts.append(0.2)
            weaknesses.append("Too short for meaningful reasoning assessment")

        weights = [0.5, 0.3, 0.2]
        score = sum(s * w for s, w in zip(score_parts, weights))

        if score >= 0.7:
            verdict = Verdict.PASS
        elif score >= 0.4:
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
                "unique_indicators": unique_indicators,
                "total_indicator_usage": total_usage,
                "causal_chains": chains_found,
                "top_indicators": sorted(found_indicators, 
                                         key=lambda x: x[1], 
                                         reverse=True)[:5]
            }
        )


class FactualDensityFilter(BaseFilter):
    name = "factual_density"
    tier = Tier.SUBSTANCE

    def evaluate(self, text: str, config: dict | None = None) -> FilterResult:
        config = config or {}
        
        strengths = []
        weaknesses = []

        # detect numeric claims
        numbers = re.findall(r'\b\d+[\d,.]*%?\b', text)
        
        # detect quoted sources or citations
        quotes = re.findall(r'"[^"]{10,}"', text)
        citations = re.findall(
            r'(?:according to|cited by|reported by|per|source:|ref:)',
            text.lower()
        )

        # detect named entities (crude — capitalized multi-word phrases)
        named_entities = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)+', text)

        # detect hedging vs certainty
        hedge_words = ["maybe", "perhaps", "possibly", "might", "could be",
                       "it seems", "arguably", "supposedly"]
        certainty_words = ["clearly", "obviously", "definitely", "certainly",
                          "proven", "established", "demonstrated", "confirmed"]
        
        text_lower = text.lower()
        hedges = sum(1 for h in hedge_words if h in text_lower)
        certainties = sum(1 for c in certainty_words if c in text_lower)

        words = text.split()
        word_count = len(words)

        # scoring
        score_parts = []

        # numeric specificity (35%)
        num_density = len(numbers) / max(word_count / 100, 1)
        if num_density >= 2:
            score_parts.append(1.0)
            strengths.append(f"Good numeric specificity ({len(numbers)} data points)")
        elif num_density >= 0.5:
            score_parts.append(0.6)
            strengths.append(f"Some numeric references ({len(numbers)} found)")
        else:
            score_parts.append(0.3)
            weaknesses.append("Low factual specificity — few numbers or data points")

        # source signals (35%)
        source_signals = len(quotes) + len(citations) + len(named_entities)
        if source_signals >= 3:
            score_parts.append(1.0)
            strengths.append(f"References external sources or entities ({source_signals} signals)")
        elif source_signals >= 1:
            score_parts.append(0.6)
            strengths.append("Some source references present")
        else:
            score_parts.append(0.2)
            weaknesses.append("No citations, quotes, or named references detected")

        # hedge-to-certainty balance (30%)
        total_modifiers = hedges + certainties
        if total_modifiers == 0:
            score_parts.append(0.5)
            weaknesses.append("No confidence modifiers detected")
        elif hedges > certainties * 2:
            score_parts.append(0.3)
            weaknesses.append("Excessively hedged — lacks confident claims")
        elif certainties > hedges * 3:
            score_parts.append(0.4)
            weaknesses.append("Overconfident — lacks appropriate qualifiers")
        else:
            score_parts.append(1.0)
            strengths.append("Good balance of confidence and qualification")

        weights = [0.35, 0.35, 0.3]
        score = sum(s * w for s, w in zip(score_parts, weights))

        if score >= 0.7:
            verdict = Verdict.PASS
        elif score >= 0.4:
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
                "numbers_found": len(numbers),
                "quotes_found": len(quotes),
                "citation_signals": len(citations),
                "named_entities": len(named_entities),
                "hedge_count": hedges,
                "certainty_count": certainties
            }
        )
