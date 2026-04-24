#!/usr/bin/env python3
"""Generate remaining chapters + foreshadowing ledger."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

WRITER_MODEL = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")

from llm import call_llm

def call_writer(prompt, max_tokens=16000):
    system_prompt = (
        "You are a novel architect continuing an outline. Write in the same format "
        "as the preceding chapters. Every chapter needs: POV, Location, Save the Cat beat, "
        "% mark, Emotional arc, Try-fail cycle, Beats, Plants, Payoffs, Character movement, "
        "The lie, Word count target."
    )
    return call_llm(
        prompt,
        system_prompt=system_prompt,
        model=WRITER_MODEL,
        max_tokens=max_tokens,
        temperature=0.8,
        include_reasoning=False
    )

outline_path = BASE_DIR / "outline.md"
if not outline_path.exists():
    print("ERROR: outline.md not found. Run gen_outline.py first.", file=sys.stderr)
    sys.exit(1)

part1 = outline_path.read_text()
mystery = (BASE_DIR / "MYSTERY.md").read_text()

# Determine where we left off
import re
matches = re.findall(r'###\s*Ch(?:apter)?\s*(\d+)', part1)
if matches:
    last_ch = int(matches[-1])
else:
    last_ch = 0

if last_ch >= 24:
    print(f"Outline already seems complete (up to Ch {last_ch}). Skipping part 2.")
    sys.exit(0)

prompt = f"""Continue the chapter outline for this novel. 
The outline currently ends at Chapter {last_ch}. 
Complete the remaining chapters to reach a total of 24, then write the Foreshadowing Ledger.

THE OUTLINE SO FAR:
{part1}

THE CENTRAL MYSTERY (for reference):
{mystery}

REMAINING STRUCTURE NEEDED:
Complete chapters {last_ch+1} through 24 following the Act III and climax requirements 
implied by the seed and the preceding chapters.

Then write:

## Foreshadowing Ledger

| # | Thread | Planted (Ch) | Reinforced (Ch) | Payoff (Ch) | Type |
|---|--------|-------------|-----------------|-------------|------|

Include at LEAST 15 threads. Types: object, dialogue, action, symbolic, structural.
Plant-to-payoff distance must be at least 3 chapters.

REMEMBER:
- The climax must be mechanically resolvable using established world rules and magic costs.
- The Stability Trap: allow for genuine change and irreversible loss.
- At least one quiet chapter in the back half.
- Final Image should mirror Chapter 1's Opening Image but show transformation.
"""

print(f"Calling writer model to continue from Chapter {last_ch}...", file=sys.stderr)
result = call_writer(prompt)

# Append to outline.md
with open(outline_path, "a") as f:
    f.write("\n\n" + result)

print(result)
