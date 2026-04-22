from __future__ import annotations

import re
from eval_kit.models import FilterResult, Tier, Verdict
from eval_kit.filters.base import BaseFilter


class ToneConsistencyFilter(BaseFilter):
    name = "tone_consistency"
    tier = Tier.POLISH

    FORMAL_MARKERS = [
        "furthermore", "consequently", "regarding",
        "pursuant", "hereby", "aforementioned",
        "thus", "hence", "whereas", "notwithstanding"
    ]

    INFORMAL_MARKERS = [
        "gonna", "wanna", "kinda", "lol", "btw",
        "ngl", "tbh", "imo", "yeah", "nope",
        "dude", "bro", "chill", "vibe", "lowkey"
    ]

    def evaluate(self, text: str, config: dict | None = None) -> FilterResult:
        config = config or {}
        expected_tone = config.get("expected_tone", "neutral")
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        strengths = []
        weaknesses = []

        formal_hits = [m for m in self.FORMAL_MARKERS if m in text_lower]
        informal_hits = [m for m in self.INFORMAL_MARKERS if m in text_lower]

        # tone mixing score
        if formal_hits and informal_hits:
            mix_severity = min(len(formal_hits), len(informal_hits))
            tone_consistency = max(0.2, 1.0 - (mix_severity * 0.2))
            weaknesses.append(
                f"Tone mixing: formal ({', '.join(formal_hits[:3])}) "
                f"and informal ({', '.join(informal_hits[:3])}) in same text"
            )
        else:
            tone_consistency = 1.0
            if formal_hits:
                strengths.append("Consistent formal tone")
            elif informal_hits:
                strengths.append("Consistent informal tone")
            else:
                strengths.append("Neutral consistent tone")

        # check against expected tone
        tone_match = 1.0
        if expected_tone == "formal" and informal_hits:
            tone_match = max(0.3, 1.0 - (len(informal_hits) * 0.15))
            weaknesses.append(f"Expected formal tone but found informal markers")
        elif expected_tone == "informal" and formal_hits and not informal_hits:
            tone_match = 0.6
            weaknesses.append("Expected informal tone but text reads formal")
        elif expected_tone == "formal" and formal_hits:
            strengths.append("Matches expected formal tone")
        elif expected_tone == "informal" and informal_hits:
            strengths.append("Matches expected informal tone")

        score = (tone_consistency * 0.6) + (tone_match * 0.4)

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
                "formal_markers": formal_hits,
                "informal_markers": informal_hits,
                "expected_tone": expected_tone,
                "consistency_score": round(tone_consistency, 3),
                "tone_match_score": round(tone_match, 3)
            }
        )


class RedundancyFilter(BaseFilter):
    name = "redundancy"
    tier = Tier.POLISH

    def evaluate(self, text: str, config: dict | None = None) -> FilterResult:
        config = config or {}
        max_repeat_ratio = config.get("max_repeat_ratio", 0.15)
        
        strengths = []
        weaknesses = []

        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip().lower() for s in sentences if len(s.strip()) > 15]

        if len(sentences) < 3:
            return FilterResult(
                filter_name=self.name,
                tier=self.tier,
                verdict=Verdict.PASS,
                score=0.8,
                strengths=["Too few sentences to assess redundancy"],
                weaknesses=[],
                details={"sentence_count": len(sentences)}
            )

        # check for near-duplicate sentences
        duplicates = 0
        seen = []
        for s in sentences:
            s_words = set(s.split())
            for prev in seen:
                prev_words = set(prev.split())
                if len(s_words) == 0 or len(prev_words) == 0:
                    continue
                overlap = len(s_words & prev_words) / max(len(s_words), len(prev_words))
                if overlap > 0.8:
                    duplicates += 1
                    break
            seen.append(s)

        # check phrase-level repetition
        # extract 3-grams
        words = text.lower().split()
        trigrams = [" ".join(words[i:i+3]) for i in range(len(words)-2)]
        trigram_counts = Counter(trigrams)
        repeated_trigrams = {k: v for k, v in trigram_counts.items() if v >= 3}

        dup_ratio = duplicates / len(sentences) if sentences else 0
        trigram_ratio = len(repeated_trigrams) / max(len(trigrams), 1)

        # scoring
        score_parts = []

        # sentence duplication (60%)
        if dup_ratio <= 0.05:
            score_parts.append(1.0)
            strengths.append("No redundant sentences detected")
        elif dup_ratio <= max_repeat_ratio:
            score_parts.append(0.6)
            weaknesses.append(f"{duplicates} near-duplicate sentences found")
        else:
            score_parts.append(0.2)
            weaknesses.append(f"High redundancy: {duplicates}/{len(sentences)} sentences are near-duplicates")

        # phrase repetition (40%)
        if trigram_ratio < 0.02:
            score_parts.append(1.0)
            strengths.append("Varied phrasing throughout")
        elif trigram_ratio < 0.05:
            score_parts.append(0.6)
            weaknesses.append(f"Some repeated phrases: {list(repeated_trigrams.keys())[:3]}")
        else:
            score_parts.append(0.2)
            weaknesses.append(f"Excessive phrase repetition ({len(repeated_trigrams)} repeated trigrams)")

        score = score_parts[0] * 0.6 + score_parts[1] * 0.4

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
                "duplicate_sentences": duplicates,
                "total_sentences": len(sentences),
                "duplicate_ratio": round(dup_ratio, 3),
                "repeated_trigrams": dict(list(repeated_trigrams.items())[:5]),
                "trigram_ratio": round(trigram_ratio, 4)
            }
        )
