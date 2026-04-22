from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from eval_kit.filters import (
    FormatComplianceFilter,
    WordCountFilter,
    RedundancyFilter,
    CoherenceFilter,
    ReasoningDepthFilter,
    FactualDensityFilter,
    ToneConsistencyFilter,
)
from eval_kit.pipeline import Pipeline
from eval_kit.scoring import ScoringEngine
from eval_kit.reporters import ConsoleReporter, JSONReporter


# ── default pipeline ────────────────────────────────────────────
def _build_default_pipeline() -> Pipeline:
    return Pipeline(
        filters=[
            FormatComplianceFilter(),
            WordCountFilter(),
            RedundancyFilter(),
            CoherenceFilter(),
            ReasoningDepthFilter(),
            FactualDensityFilter(),
            ToneConsistencyFilter(),
        ]
    )


# ── input loaders ───────────────────────────────────────────────
def _load_texts(source: str | None, file: str | None) -> list[str]:
    """Return a list of texts from either --text or --file."""
    texts: list[str] = []

    if source:
        texts.append(source)

    if file:
        path = Path(file)
        if not path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            sys.exit(1)

        suffix = path.suffix.lower()

        if suffix == ".jsonl":
            with path.open() as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    # accept {"text": "..."} or {"response": "..."} or bare string
                    if isinstance(obj, str):
                        texts.append(obj)
                    elif isinstance(obj, dict):
                        texts.append(
                            obj.get("text") or obj.get("response") or json.dumps(obj)
                        )

        elif suffix == ".json":
            with path.open() as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, str):
                        texts.append(item)
                    elif isinstance(item, dict):
                        texts.append(
                            item.get("text") or item.get("response") or json.dumps(item)
                        )
            elif isinstance(data, dict):
                texts.append(
                    data.get("text") or data.get("response") or json.dumps(data)
                )

        else:
            # plain text — treat entire file as one response
            texts.append(path.read_text(encoding="utf-8"))

    if not texts:
        print("Nothing to evaluate. Pass --text or --file.", file=sys.stderr)
        sys.exit(1)

    return texts


# ── arg parser ──────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="eval-kit",
        description="Evaluate LLM outputs through a layered filter chain.",
    )

    input_group = p.add_mutually_exclusive_group()
    input_group.add_argument(
        "--text", "-t",
        type=str,
        help="Single text string to evaluate.",
    )
    input_group.add_argument(
        "--file", "-f",
        type=str,
        help="Path to .txt / .json / .jsonl of responses.",
    )

    p.add_argument(
        "--format",
        choices=["console", "json"],
        default="console",
        help="Output format (default: console).",
    )
    p.add_argument(
        "--pass-threshold",
        type=float,
        default=0.80,
        help="Weighted score >= this is PASS (default: 0.80).",
    )
    p.add_argument(
        "--warn-threshold",
        type=float,
        default=0.50,
        help="Weighted score >= this is WARN (default: 0.50).",
    )
    p.add_argument(
        "--out", "-o",
        type=str,
        default=None,
        help="Write output to file instead of stdout.",
    )
    p.add_argument(
        "--rubric-pack",
        type=str,
        default=None,
        help="Path to a rubric pack directory (must contain manifest.yaml).",
    )

    return p


# ── main ────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    texts = _load_texts(args.text, args.file)

    pipeline = _build_default_pipeline()
    
    if args.rubric_pack:
        from eval_kit.rubrics import RubricPackLoader, DomainFilter
        pack = RubricPackLoader.load(args.rubric_pack)
        domain = DomainFilter(pack)
        pipeline.add(domain)
    
    engine = ScoringEngine(
        pass_threshold=args.pass_threshold,
        warn_threshold=args.warn_threshold,
    )

    if args.format == "json":
        reporter = JSONReporter()
    else:
        reporter = ConsoleReporter()

    reports = pipeline.run_batch(texts)
    cards = engine.score_batch(reports)

    if len(reports) == 1:
        output = reporter.render(reports[0], cards[0])
    else:
        output = reporter.render_batch(reports, cards)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Results written to {args.out}")
    else:
        print(output)
