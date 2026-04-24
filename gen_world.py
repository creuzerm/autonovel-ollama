#!/usr/bin/env python3
"""
One-shot world.md generator for foundation phase.
Reads seed.txt + voice.md, calls the writer model, outputs world.md content.
"""
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
        "You are a fantasy worldbuilder with deep knowledge of Sanderson's Laws, "
        "Le Guin's prose philosophy, and TTRPG-quality lore design. "
        "You write world bibles that are specific, interconnected, and imply depth "
        "beyond what's stated. You never use AI slop words (delve, tapestry, myriad, etc). "
        "You write in clean, direct prose. Every rule has a cost. Every cultural detail "
        "implies a history. Every location has a sensory signature."
    )
    return call_llm(
        prompt,
        system_prompt=system_prompt,
        model=WRITER_MODEL,
        max_tokens=max_tokens,
        temperature=0.7
    )

seed = (BASE_DIR / "seed.txt").read_text()
voice = (BASE_DIR / "voice.md").read_text()
craft = (BASE_DIR / "CRAFT.md").read_text()

# Extract voice Part 2 only (the novel-specific voice)
voice_lines = voice.split('\n')
try:
    part2_start = next(i for i, l in enumerate(voice_lines) if 'Part 2' in l)
    voice_part2 = '\n'.join(voice_lines[part2_start:])
except StopIteration:
    voice_part2 = voice # Fallback if Part 2 not found

prompt = f"""Build a complete world bible for this fantasy novel. This is the WORLD.MD file -- 
the definitive reference for everything that EXISTS in this world. A writer should be able 
to resolve any worldbuilding question from this document alone.

SEED CONCEPT:
{seed}

VOICE IDENTITY (the tone and register of this novel):
{voice_part2}

CRAFT REQUIREMENTS (from CRAFT.md -- follow these):
- Magic system needs HARD RULES with COSTS and LIMITATIONS per Sanderson's Second Law
- Limitations >= powers in narrative prominence
- Trace implications of magic through society, economy, law, religion
- At least 2-3 societal implications of magic explored in depth
- History must create PRESENT-DAY TENSIONS that drive the plot (not just backdrop)
- Geography must be specific and sensory (not generic fantasy)
- Iceberg principle: imply more than you state
- Interconnection: pulling one thread should move everything

STRUCTURE THE DOCUMENT WITH THESE SECTIONS:

## Cosmology & History
A timeline of major events. Focus on events that create PRESENT-DAY tensions.
Include the founding myth, key turning points, and recent events that matter to the plot.

## Magic System
### Hard Rules
Specific, testable rules. What is possible, what is impossible.
Include COSTS and LIMITATIONS prominently. How do users access this power?
What are the physical or spiritual consequences of use?

### Soft Magic / Perceptions
How do characters perceive the magic? What are the mysterious or unexplained 
elements that remain beyond the reach of formal study?

### Societal Implications
How does this magic/speculative element shape: governance, commerce, education, 
class structure, crime, family life, childhood, aging, disability?

## Geography
The physical layout of the primary setting (city, region, etc). 
Sensory signatures for major locations. How does the environment interact 
with the magic or the central conflict?

## Factions & Politics
Who holds power, who wants it, who's being crushed by it.
At least 3-4 factions with opposing interests.

## Bestiary / Flora / Natural World
What's unique about the natural world in this setting? 
Include at least one unique creature or plant that has economic or magical importance.

## Cultural Details
Customs, taboos, festivals, food, clothing, coming-of-age rituals.
Things that make daily life feel SPECIFIC to this world.

## Internal Consistency Rules
Hard constraints a writer must not violate. The "physics" of this world.
What's possible and what's not.

IMPORTANT:
- Be SPECIFIC. Name things, describe them, give them sensory signatures.
- Every rule should have a COST or LIMITATION stated alongside it.
- Include 2-3 facts per section that are unexplained, hinting at deeper systems 
  (iceberg depth).
- Facts should INTERCONNECT: the magic should shape the politics, the geography 
  should shape the culture, the history should explain current faction conflicts.
- Write in clean, direct prose. No AI slop. No "rich tapestry." No "delving."
- The world should feel grounded and LIVED-IN, not imagined. Think: what does 
  breakfast smell like? What do children play? How do old people complain?
- Target ~3000-4000 words. Dense, not padded.
"""

print("Calling writer model...", file=sys.stderr)
result = call_writer(prompt)
(BASE_DIR / "world.md").write_text(result)
print(result)
