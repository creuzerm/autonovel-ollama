#!/usr/bin/env python3
"""Generate outline.md from seed + world + characters + mystery + craft."""
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
        "You are a novel architect with deep knowledge of Save the Cat beats, "
        "Sanderson's plotting principles, Dan Harmon's Story Circle, and MICE Quotient. "
        "You build outlines that an author can draft from without inventing structure "
        "on the fly. Every chapter has beats, emotional arc, and try-fail cycle type. "
        "You never use AI slop words. You write in clean, direct prose."
    )
    return call_llm(
        prompt,
        system_prompt=system_prompt,
        model=WRITER_MODEL,
        max_tokens=max_tokens,
        temperature=0.5
    )

seed = (BASE_DIR / "seed.txt").read_text()
world = (BASE_DIR / "world.md").read_text()
characters = (BASE_DIR / "characters.md").read_text()
mystery = (BASE_DIR / "MYSTERY.md").read_text()
craft = (BASE_DIR / "CRAFT.md").read_text()

# Voice Part 2 only
voice = (BASE_DIR / "voice.md").read_text()
voice_lines = voice.split('\n')
try:
    part2_start = next(i for i, l in enumerate(voice_lines) if 'Part 2' in l)
    voice_part2 = '\n'.join(voice_lines[part2_start:])
except StopIteration:
    voice_part2 = voice

prompt = f"""Build a complete chapter outline for this fantasy novel. Target: 22-26 chapters,
~80,000 words total (~3,000-4,000 words per chapter).

SEED CONCEPT:
{seed}

THE CENTRAL MYSTERY (author's eyes only -- reader discovers gradually):
{mystery}

WORLD BIBLE:
{world}

CHARACTER REGISTRY:
{characters}

VOICE (tone and register):
{voice_part2}

CRAFT REFERENCE (structures to follow):
{craft}

BUILD THE OUTLINE WITH:

## Act Structure
Map out Act I (0-23%), Act II Part 1 (23-50%), Act II Part 2 (50-77%), Act III (77-100%).
State the percentage marks for the key novel beats (Catalyst, Midpoint, etc).

## Chapter-by-Chapter Outline

For EACH chapter, provide:
### Ch N: [Title]
- **POV:** (primary character, third-person limited)
- **Location:** Specific locations from the world bible
- **Save the Cat beat:** Which beat this chapter serves
- **% mark:** Where this falls in the novel
- **Emotional arc:** Starting emotion → ending emotion
- **Try-fail cycle:** Yes-but / No-and / No-but / Yes-and
- **Beats:** 3-5 specific scene beats that must happen
- **Plants:** Foreshadowing elements planted in this chapter
- **Payoffs:** Foreshadowing elements that pay off here
- **Character movement:** What changes for the protagonist (or other characters) by chapter's end
- **The lie:** How the protagonist's Lie (from character registry) is reinforced or challenged
- **~Word count target:** for pacing

## Foreshadowing Ledger

A table tracking every planted thread:
| Thread | Planted (Ch) | Reinforced (Ch) | Payoff (Ch) | Type |

Include at LEAST 15 threads. Types: object, dialogue, action, symbolic, structural.

KEY PLOT ARCHITECTURE:

Act I (Ch 1-6ish): Establish the protagonist's world, their trade, the setting, and their family/social circle.
Plant the mystery early. Catalyst: The event from the seed that forces the protagonist out of their status quo.

Act II Part 1 (Ch 7-12ish): Investigation/Action. The protagonist engages with the new world/problem. 
Initial successes and failures. Meeting allies and antagonists.
Midpoint: A major revelation or event that changes the stakes and shifts the protagonist from reactive to active.

Act II Part 2 (Ch 13-18ish): Pressure mounts. The antagonists move decisively.
Personal stakes collide with cosmic ones. The protagonist's Lie becomes increasingly unsustainable.
All Is Lost: The lowest point where the protagonist faces the full consequence of their Lie and the looming cosmic threat.

Act III (Ch 19-24ish): The protagonist understands the true question. 
Must choose how to answer based on their Need.
The climax plays out using the world's established rules and magic costs.
The resolution shows the aftermath of their choice and the new status quo.

CONSTRAINTS:
- The climax must be mechanically resolvable using established world rules and magic costs.
- The investigation should feel like a mystery plot overlaid on a character-driven arc.
- The Stability Trap: allow for genuine change and irreversible loss.
- At least 3 chapters should be "quiet" -- character-focused, low-action, emotionally rich.
- Vary the try-fail types: 60%+ should be "yes-but" or "no-and".
- The foreshadowing ledger must have plant-to-payoff distances of at least 3 chapters.
"""

print("Calling writer model...", file=sys.stderr)
result = call_writer(prompt)
(BASE_DIR / "outline.md").write_text(result)
print(result)
