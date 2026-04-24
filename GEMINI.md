# GEMINI.md

## Project Overview
**autonovel** is an autonomous framework for high-fidelity fiction production. Inspired by the "modify-evaluate-keep/discard" loop of scientific research, it applies similar rigor to creative writing. The system generates a novel across five co-evolving layers: Voice, World, Characters, Outline, and Prose, all maintained for consistency via a cross-cutting `canon.md` database.

- **Technology Stack:** Python 3.12+, `uv` (package management), Anthropic Claude (Opus for judging, Sonnet for drafting), fal.ai (Nano Banana 2 for art), ElevenLabs (audiobook), and Tectonic (LaTeX typesetting).
- **Core Philosophy:** "You're not writing the novel; you're programming the system that writes the novel."

## Orchestration & Workflow
The project is organized into four distinct phases, managed by `run_pipeline.py`.

### 1. Foundation
- **Goal:** Build the world bible, character registry, chapter outline, and voice fingerprint.
- **Process:** Iterative loops until `foundation_score > 7.5` and `lore_score > 7.0` (evaluated by `evaluate.py`).
- **Key Tools:** `gen_world.py`, `gen_characters.py`, `gen_outline.py`, `gen_canon.py`, `voice_fingerprint.py`.

### 2. Drafting
- **Goal:** Write all chapters sequentially.
- **Process:** Each chapter is drafted, evaluated against anti-pattern rules, and kept only if `score > 6.0`.
- **Key Tools:** `draft_chapter.py`, `run_drafts.py`.

### 3. Revision
- **Goal:** Structural and prose-level refinement.
- **Process:** 
    - **Automated Cycles:** Mechanical slop detection, adversarial cuts (removing AI over-explanation), and 4-persona reader panel reviews.
    - **Opus Review Loop:** Dual-persona review (Literary Critic + Professor of Fiction) via Claude Opus for high-level structural feedback.
- **Key Tools:** `adversarial_edit.py`, `apply_cuts.py`, `reader_panel.py`, `review.py`, `gen_revision.py`.

### 4. Export
- **Goal:** Final deliverables.
- **Process:** LaTeX typesetting (EB Garamond), cover/ornament generation, and ElevenLabs audiobook production.
- **Key Tools:** `typeset/build_tex.py`, `gen_art.py`, `gen_audiobook.py`, `gen_cover_print.py`.

## Key Commands
- **Setup:** `uv sync`
- **Full Pipeline (Fresh Start):** `uv run python run_pipeline.py --from-scratch`
- **Run Specific Phase:** `uv run python run_pipeline.py --phase [foundation|drafting|revision|export]`
- **Evaluate Foundation/Chapter:** `uv run python evaluate.py [--phase=foundation | --chapter=N | --full]`
- **Generate Audiobook:** `uv run python gen_audiobook.py`

## Development Conventions
- **Code Style:** Functional Python scripts utilizing `httpx` for API calls and `argparse` for CLI interfaces.
- **Agent Instructions:** Found in `program.md`.
- **Quality Standards:** Strictly follows `CRAFT.md` (narrative theory), `ANTI-SLOP.md` (word-level AI tells), and `ANTI-PATTERNS.md` (structural AI tics).
- **Validation:** Every change is validated by `evaluate.py`. The "Judge" (Claude Opus) is intentionally different/harsher than the "Writer" (Claude Sonnet).
- **State Management:** `state.json` tracks the current pipeline progress, scores, and "propagation debts" (needed updates across layers).
- **Git Protocol:** The orchestrator automatically commits "keep" results with scores and resets on "discards."

## Directory Structure
- `chapters/`: The generated prose.
- `typeset/`: LaTeX templates and build scripts.
- `briefs/`: Generated revision instructions for `gen_revision.py`.
- `edit_logs/` & `eval_logs/`: Performance metrics and feedback JSONs.
- `landing/`: Web templates for the finished book.
