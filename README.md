# eval-kit

**LLM output evaluation toolkit with pluggable rubric packs.**

Score any LLM-generated text against domain-specific rubrics. Get letter grades, detailed breakdowns, and actionable feedback -- all from the terminal.

## Quick Start

    cd eval-kit
    pip install -e .
    eval-kit list
    eval-kit score --pack hr_compliance --text "Our policy requires..."
    eval-kit score --pack sales_enablement --input pitch.txt
    eval-kit benchmark --pack hr_compliance

## Available Packs

| Pack | Dimensions | Use Case |
|------|-----------|----------|
| hr_compliance | 6 | HR policy, legal citations, bias, PII |
| sales_enablement | 6 | Pitch quality, objection handling, CTA |
| technical_docs | 6 | Accuracy, clarity, code examples |
| customer_support | 6 | Empathy, resolution, escalation |
| content_marketing | 6 | SEO, engagement, brand voice |
| legal_contract | 6 | Clause coverage, liability, compliance |
| medical_clinical | 6 | Safety, evidence, patient communication |
| financial_advisory | 6 | Regulation, risk disclosure, suitability |
| education_course | 6 | Pedagogy, accessibility, assessment |

## How It Works

1. Rubric Packs -- YAML-defined evaluation dimensions with weighted criteria
2. Scoring Engine -- matches positive/negative signals, computes weighted scores
3. Reporter -- rich terminal output with letter grades or exportable markdown
4. Benchmarks -- JSONL test suites to validate rubric accuracy

## License

MIT
