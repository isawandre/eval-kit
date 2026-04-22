from __future__ import annotations

import re
from eval_kit.models import FilterResult, Tier, Verdict
from eval_kit.filters.base import BaseFilter


class WordCountFilter(BaseFilter):
    name = "word_count"
    tier = Tier.SURFACE

    def evaluate(self, text: str, config: dict | None = None) -> FilterResult:
        config = config or {}
        min_words = config.get("min_words", 50)
        max_words = config.get("max_words", 5000)
        
        words = text.split()
        count = len(words)
        strengths = []
        weaknesses = []

        if count < min_words:
            verdict = Verdict.FAIL
            score = count / min_words
            weaknesses.append(f"Only {count} words — minimum is {min_words}")
        elif count > max_words:
            verdict = Verdict.PARTIAL
            score = max(0.5, 1.0 - ((count - max_words) / max_words))
            weaknesses.append(f"{count} words exceeds {max_words} cap")
            strengths.append("Substantial content produced")
        else:
            verdict = Verdict.PASS
            score = 1.0
            strengths.append(f"Word count ({count}) within acceptable range")

        return FilterResult(
            filter_name=self.name,
            tier=self.tier,
            verdict=verdict,
            score=round(score, 4),
            strengths=strengths,
            weaknesses=weaknesses,
            details={"word_count": count, "min": min_words, "max": max_words}
        )


class ProfanityFilter(BaseFilter):
    name = "profanity_check"
    tier = Tier.SURFACE

    # baseline list — config can override
    DEFAULT_TERMS = {
        "fuck", "shit", "damn", "bitch", "ass",
        "bastard", "crap", "dick", "piss"
    }

    def evaluate(self, text: str, config: dict | None = None) -> FilterResult:
        config = config or {}
        blocked = set(config.get("blocked_terms", self.DEFAULT_TERMS))
        context_aware = config.get("context_aware", False)
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        found = [w for w in words if w in blocked]
        unique_found = set(found)
        
        strengths = []
        weaknesses = []

        if not found:
            verdict = Verdict.PASS
            score = 1.0
            strengths.append("No flagged language detected")
        elif len(unique_found) <= 2 and len(found) <= 3:
            verdict = Verdict.PARTIAL
            score = 0.6
            weaknesses.append(f"Minor profanity detected: {', '.join(unique_found)}")
            strengths.append("Limited to mild usage")
        else:
            verdict = Verdict.FAIL
            score = max(0.1, 1.0 - (len(found) * 0.1))
            weaknesses.append(f"Heavy profanity: {', '.join(unique_found)} ({len(found)} instances)")

        return FilterResult(
            filter_name=self.name,
            tier=self.tier,
            verdict=verdict,
            score=round(score, 4),
            strengths=strengths,
            weaknesses=weaknesses,
            details={"flagged_terms": list(unique_found), "total_hits": len(found)}
        )


class FormatComplianceFilter(BaseFilter):
    name = "format_compliance"
    tier = Tier.SURFACE

    def evaluate(self, text: str, config: dict | None = None) -> FilterResult:
        config = config or {}
        expected_format = config.get("expected_format", "prose")
        
        strengths = []
        weaknesses = []
        checks_passed = 0
        total_checks = 0

        if expected_format == "prose":
            total_checks = 3
            
            # check: has paragraphs
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            if len(paragraphs) >= 2:
                checks_passed += 1
                strengths.append(f"Contains {len(paragraphs)} paragraphs")
            else:
                weaknesses.append("Text appears to be a single block")

            # check: sentences end with punctuation
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            if len(sentences) >= 3:
                checks_passed += 1
                strengths.append("Multiple complete sentences detected")
            else:
                weaknesses.append("Few complete sentences found")

            # check: not just bullet points
            bullet_lines = len(re.findall(r'^\s*[-•*]\s', text, re.MULTILINE))
            total_lines = len([l for l in text.split("\n") if l.strip()])
            if total_lines > 0 and (bullet_lines / total_lines) < 0.5:
                checks_passed += 1
                strengths.append("Prose format maintained")
            else:
                weaknesses.append("Output is mostly bullet points, expected prose")

        elif expected_format == "json":
            total_checks = 1
            try:
                import json
                json.loads(text)
                checks_passed = 1
                strengths.append("Valid JSON structure")
            except (json.JSONDecodeError, ValueError):
                weaknesses.append("Invalid JSON")

        elif expected_format == "markdown":
            total_checks = 2
            if re.search(r'^#{1,6}\s', text, re.MULTILINE):
                checks_passed += 1
                strengths.append("Contains markdown headers")
            else:
                weaknesses.append("No markdown headers found")
            if re.search(r'\*\*.*?\*\*|__.*?__', text):
                checks_passed += 1
                strengths.append("Uses markdown formatting")
            else:
                weaknesses.append("No bold/emphasis formatting found")

        else:
            total_checks = 1
            checks_passed = 1
            strengths.append("No specific format requirement")

        score = checks_passed / total_checks if total_checks > 0 else 1.0

        if score >= 0.8:
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
            details={"expected_format": expected_format, 
                     "checks_passed": checks_passed, 
                     "total_checks": total_checks}
        )


class ReadabilityFilter(BaseFilter):
    name = "readability"
    tier = Tier.SURFACE

    def __init__(
        self,
        target_grade: float = 10.0,
        tolerance: float = 4.0,
    ):
        self.target_grade = target_grade
        self.tolerance = tolerance

    def evaluate(self, text: str, config: dict | None = None) -> FilterResult:
        config = config or {}
        target = config.get("target_grade", self.target_grade)
        tolerance = config.get("tolerance", self.tolerance)

        if not text.strip():
            return FilterResult(
                filter_name=self.name,
                verdict=Verdict.FAIL,
                score=0.0,
                tier=self.tier,
                details={"flesch_kincaid_grade": 0.0, "target": target},
            )

        # Simple approximation: count syllables for Flesch-Kincaid
        def count_syllables(word: str) -> int:
            word = word.lower()
            count = 0
            vowels = "aeiouy"
            previous_was_vowel = False
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not previous_was_vowel:
                    count += 1
                previous_was_vowel = is_vowel
            if word.endswith("e"):
                count -= 1
            if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
                count += 1
            return max(1, count)

        words = text.split()
        word_count = len(words)
        sentence_count = max(1, len(re.split(r'[.!?]+', text)) - 1)
        
        syllable_count = sum(count_syllables(w) for w in words if w.isalpha())

        # Flesch-Kincaid Grade Level formula
        if word_count > 0 and sentence_count > 0:
            grade = (0.39 * (word_count / sentence_count) + 
                    11.8 * (syllable_count / word_count) - 15.59)
            grade = max(0, grade)
        else:
            grade = 0

        deviation = abs(grade - target)

        if deviation <= tolerance:
            score = 1.0 - (deviation / tolerance) * 0.3
            verdict = Verdict.PASS
        elif deviation <= tolerance * 2:
            score = 0.4 + (1.0 - deviation / (tolerance * 2)) * 0.3
            verdict = Verdict.PARTIAL
        else:
            score = max(0.05, 0.4 - (deviation - tolerance * 2) * 0.05)
            verdict = Verdict.FAIL

        return FilterResult(
            filter_name=self.name,
            tier=self.tier,
            verdict=verdict,
            score=round(score, 4),
            details={
                "flesch_kincaid_grade": round(grade, 2),
                "target_grade": target,
                "deviation": round(deviation, 2),
            },
        )
