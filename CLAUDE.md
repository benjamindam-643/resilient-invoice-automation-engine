# CLAUDE.md — Resilient Invoice Automation Engine

This repository contains an enterprise-grade, deterministic invoice processing and verification engine designed for zero-hallucination accounts payable automation.

## Architecture Guidelines
- **Zero-LLM Core Parsing**: Layout parsing, text clustering, table boundary detection, and cross-footing are 100% deterministic (Python 3.11).
- **Hard Accounting Invariants**: Never let an unverified financial discrepancy pass without setting `needs_review: True`.
- **Statutory Rules Engine**: Validates duplicate fingerprints via composite SHA-256 hashes, verifies country-specific tax calculations (e.g. 10% / 15% GST), and enforces spending caps before dispatching.
- **Human-in-the-Loop Dispatch**: Routes anomalous invoices to Microsoft Teams Adaptive Cards or Slack webhooks for human approval.

## Testing & Quality Assurance
Run all unit tests:
```bash
python -m unittest discover tests
```

To run a specific test suite:
```bash
python -m unittest tests/test_geometry.py
python -m unittest tests/test_math_validator.py
python -m unittest tests/test_rules_engine.py
python -m unittest tests/test_pipeline.py
```

## Multi-Agent Coding Conventions
- When running parallel coding agents (Claude Code, Codex, Copilot), always isolate workspace git worktrees or branches.
- Adhere to strict type annotations (`typing`, `dataclasses`).
- Every new parsing heuristic or rule must come with a deterministic unit test containing synthetic OCR fixtures.
