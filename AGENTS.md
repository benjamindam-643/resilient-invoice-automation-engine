# AGENTS.md — Autonomous Agent Coordination & Multi-Worker Guidelines

This document specifies the operational rules for AI coding agents (Claude Code, OpenAI Codex, GitHub Copilot) operating across this repository in parallel.

## 1. Core Principles
- **Financial Determinism**: Do not replace geometric clustering or cross-footing rules with LLM prompt calls. Calculations must be bit-exact.
- **Fail-Closed Safety**: In the event of an ambiguous OCR scan, missing total, or malformed table structure, the pipeline MUST set `needs_review: True`.
- **Statutory Compliance**: Ensure tax checks reflect jurisdictional standards (e.g., Australia 10% GST, New Zealand 15% GST, European VAT).

## 2. Directory Layout & Roles
```text
src/
├── parser/          # Geometric word clustering, table detection, math validator
├── rules_engine/    # Duplicate detection hashing, statutory GST/VAT checker
└── pipeline/        # Ingestion coordinator & Microsoft Teams / Slack dispatcher
tests/               # 100% offline synthetic unit tests
```

## 3. Parallel Agent Orchestration
When dispatching multiple agents:
1. **Worker A (Parser/Geometry)**: Modifies only `src/parser/`. Tests: `tests/test_geometry.py`, `tests/test_math_validator.py`.
2. **Worker B (Rules/Compliance)**: Modifies only `src/rules_engine/`. Tests: `tests/test_rules_engine.py`.
3. **Worker C (Integration/Dispatch)**: Modifies only `src/pipeline/`. Tests: `tests/test_pipeline.py`.
4. Merge coordination must verify that `python -m unittest discover tests` returns 100% passing tests before pushing to main.
