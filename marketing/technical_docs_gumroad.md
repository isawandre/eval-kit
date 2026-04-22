# eval-kit: Technical Documentation Rubric Pack

**Price:** $29

*If your AI writes docs nobody can follow, nobody will use your product.*

Your AI-generated API docs say "just call the endpoint and pass your credentials." That's not documentation. That's a Stack Overflow comment from 2014.

This rubric pack ensures AI-generated technical content is actually useful to developers.

**What's inside:**

- **Accuracy** — Catches deprecated syntax (componentWillMount, document.write), security anti-patterns (chmod 777, verify=False), version mismatches, incorrect defaults, and unsupported absolute claims.
- **Completeness** — Checks for prerequisites, parameter documentation with types, return value specs, error handling coverage, and edge case acknowledgment.
- **Code Examples** — Scores formatted code blocks, language specification, inline comments, expected output display, import inclusion, and copy-paste runnability.
- **Readability** — Evaluates header structure, paragraph length, list usage, jargon definitions, transition signals, and TL;DR/quick-start sections.
- **Versioning** — Checks for specific version references, changelog pointers, deprecation notices, migration guidance, and compatibility matrices.
- **API Reference** — Validates endpoint format with HTTP methods, request/response schemas, authentication details, rate limit disclosure, and curl examples.

**Also includes:**
- 2 benchmark scenarios (comprehensive API doc vs. lazy one-liner) with expected scores
- Drop-in usage: `eval-kit --pack technical_docs --file generated_docs.jsonl`

**Who needs this:**
- DevTool companies using AI to generate or assist documentation
- API platforms auto-generating endpoint references
- Technical writing teams auditing AI draft quality
- Any team where "the AI wrote the docs" needs to mean "the docs are actually good" 
