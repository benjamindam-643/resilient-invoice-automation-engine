# 2-Minute Screen Recording Demo Script: AI Coding Setup & Invoice Automation

This script guides a 2-3 minute loom/screen recording showcasing your AI coding workflow with Claude Code / Codex and the Resilient Invoice Automation Engine.

---

### Step 1: Introduction (0:00 - 0:30)
- **Visual**: Show your IDE (VS Code or Terminal) with `CLAUDE.md`, `AGENTS.md`, and the project architecture.
- **Voiceover**: 
  > "Hi there! In this quick 2-minute walkthrough, I'm showcasing our Resilient Invoice Automation Engine alongside our multi-agent AI coding workflow using Claude Code and Codex. 
  > In enterprise AP workflows, relying solely on LLMs for table math introduces dangerous hallucination risks. Here, we implemented a hybrid architecture: deterministic layout parsing and accounting invariants in Python, paired with AI-driven exception routing."

---

### Step 2: The Parallel AI Coding Workflow (0:30 - 1:15)
- **Visual**: Open terminal and show `git status` or run tests with `python -m unittest discover tests`.
- **Voiceover**: 
  > "For AI-assisted development, I maintain strict guidelines in `CLAUDE.md` and `AGENTS.md`. We instruct our agents to enforce hard invariants: 
  > 1. Word clustering by bounding box geometry without per-vendor templates.
  > 2. Zero-tolerance math verification where line item sums must strictly equal the subtotal, and subtotal + tax must match the total.
  > When running multiple coding agents in parallel, we scope each agent to its domain—Parser, Rules Engine, and Approval Dispatcher—preventing merge collisions."

---

### Step 3: Demonstrating Real Exception Handling (1:15 - 2:00)
- **Visual**: Run `python -m unittest tests/test_pipeline.py -v`.
- **Voiceover**: 
  > "Notice how our automated tests verify both clean receipts and edge cases:
  > When an invoice arrives with a subtotal mismatch or an anomalous GST calculation, our rules engine instantly triggers `needs_review: True` and constructs an Adaptive Card for Microsoft Teams. Approvers get an interactive card with 1-click Approve or Reject buttons, while clean invoices flow directly into downstream ERP/REST APIs."

---

### Step 4: Wrap-up & Project Handover (2:00 - 2:30)
- **Voiceover**:
  > "This architecture has proven 100% resilient across unseen receipt formats, completely eliminating silent financial errors. I'm ready to bring this exact rigor to your M365 / Azure / fleet management automation pipeline. Thanks for watching!"
