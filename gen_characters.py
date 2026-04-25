#!/usr/bin/env python3
"""
One-shot characters.md generator for foundation phase.
Reads seed.txt + voice.md + world.md + CRAFT.md, calls writer model.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from paths import BASE_DIR, SEED_PATH, WORLD_PATH, VOICE_PATH, CHARACTERS_PATH
load_dotenv(BASE_DIR / ".env")

WRITER_MODEL = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")

from llm import call_llm

def call_writer(prompt, max_tokens=16000):
    system_prompt = (
        "You are a character designer for literary fiction with deep knowledge of "
        "wound/want/need/lie frameworks, Sanderson's three sliders, and dialogue "
        "distinctiveness. You create characters who feel like real people with "
        "contradictions, secrets, and speech patterns you can hear. "
        "You never use AI slop words. You write in clean, direct prose."
    )
    return call_llm(
        prompt,
        system_prompt=system_prompt,
        model=WRITER_MODEL,
        max_tokens=max_tokens,
        temperature=0.8,
        include_reasoning=False
    )

seed = SEED_PATH.read_text(encoding='utf-8')
world = WORLD_PATH.read_text(encoding='utf-8')

# Voice Part 2 only
voice = VOICE_PATH.read_text(encoding='utf-8')
voice_lines = voice.split('\n')
try:
    part2_start = next(i for i, l in enumerate(voice_lines) if 'Part 2' in l)
    voice_part2 = '\n'.join(voice_lines[part2_start:])
except StopIteration:
    voice_part2 = voice

prompt = f"""Build a complete character registry for this fantasy novel. This is CHARACTERS.MD --
the definitive reference for WHO exists in this story, what drives them, how they speak,
and what secrets they carry.

SEED CONCEPT:
{seed}

WORLD BIBLE (the world these characters inhabit):
{world}

VOICE IDENTITY (the novel's tone):
{voice_part2}

CHARACTER CRAFT REQUIREMENTS (from CRAFT.md):

### The Three Sliders (Sanderson)
Every character has three independent dials (0-10):
  PROACTIVITY -- Do they drive the plot or react to it?
  LIKABILITY  -- Does the reader empathize with them?
  COMPETENCE  -- Are they good at what they do?
Rule: compelling = HIGH on at least TWO, or HIGH on one with clear growth.

### Wound / Want / Need / Lie Framework
A causal chain:
  GHOST (backstory event) -> WOUND (ongoing damage) -> LIE (false belief to cope)
    -> WANT (external goal driven by Lie) -> NEED (internal truth, opposes Lie)
Rules: Want and Need must be IN TENSION. Lie statable in one sentence.
  Truth is its direct opposite.

### Dialogue Distinctiveness (8 dimensions)
1. Vocabulary level  2. Sentence length  3. Contractions/formality
4. Verbal tics  5. Question vs statement ratio  6. Interruption patterns
7. Metaphor domain  8. Directness vs indirectness
Test: Remove dialogue tags. Can you tell who's speaking?

BUILD THE REGISTRY WITH AT LEAST THESE CHARACTERS:

1. **The Protagonist** (The primary POV character)
   - Must fit the Seed Concept's protagonist description.
   - Full wound/want/need/lie chain
   - Three sliders with justification
   - Arc type (positive/negative/flat)
   - Detailed speech pattern (8 dimensions)
   - Physical habits and tells
   - At least 2 secrets
   - Key relationships mapped

2. **The Primary Antagonist**
   - Not necessarily a villain, but someone whose goals directly conflict with the protagonist's.
   - Represent the institutional or systemic pressure mentioned in the seed.
   - Their own wound/want/need/lie (they should be understandable).

3. **A Mentor or Predecessor Figure**
   - Someone who represents the history of the protagonist's trade or the archive.
   - Could be present, or present only through their legacy/writings.

4. **A Personal Foil or Ally**
   - Someone close to the protagonist who represents a different way of dealing with the world's cost/magic.

5. **2-3 Additional Characters**
   - Family members, rivals, or inhabitants of the world who add depth and perspective.

FOR EACH CHARACTER INCLUDE:
- Name, age, role
- Ghost/Wound/Want/Need/Lie chain (for major characters)
- Three sliders (proactivity/likability/competence) with numbers and justification
- Arc type and arc trajectory
- Speech pattern (all 8 dimensions, with example lines)
- Physical appearance (specific, not generic)
- Physical habits and unconscious tells
- Secrets (what the reader doesn't learn immediately)
- Key relationships (mapped to other characters)
- Thematic role (what question does this character embody?)

IMPORTANT:
- Characters must INTERCONNECT. Their wants should conflict with each other.
- Every secret should be something that would CHANGE the story if revealed.
- Speech patterns must be distinct enough to pass the no-tags test.
- Give characters habits that come from the world's unique magic or environment.
- Target ~3000-4000 words. Dense character work, not padding.
"""

print("Calling writer model...", file=sys.stderr)
result = call_writer(prompt)
CHARACTERS_PATH.write_text(result, encoding='utf-8')
print(result)
print(result)
