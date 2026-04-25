#!/usr/bin/env python3
"""
Generate voice.md Part 2 based on seed, world, and characters.
Discovers the tone, rhythm, and vocabulary for the novel.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from paths import BASE_DIR, SEED_PATH, WORLD_PATH, CHARACTERS_PATH, VOICE_PATH
load_dotenv(BASE_DIR / ".env")

WRITER_MODEL = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")

from llm import call_llm

def call_writer(prompt, max_tokens=8000):
    system_prompt = (
        "You are a master of prose style and literary voice. You understand how "
        "diction, syntax, and rhythm create a unique 'feel' for a story. "
        "You never use AI slop. You write in clean, direct prose."
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
characters = CHARACTERS_PATH.read_text(encoding='utf-8')
voice_template = VOICE_PATH.read_text(encoding='utf-8')

prompt = f"""Discover and define the unique voice for this fantasy novel. 

SEED CONCEPT:
{seed}

WORLD BIBLE:
{world}

CHARACTER REGISTRY:
{characters}

TASK:
1. Propose 3 potential voice identities that would fit this story.
2. Select the most compelling one.
3. Fill in 'Part 2: Voice Identity' for the voice.md file.

The voice should NOT be generic fantasy. It should be shaped by the world's 
specific elements (e.g., the salt, the crystalline dust, the archives, the "echo-drag").

OUTPUT FORMAT (Part 2 of voice.md):

## Part 2: Voice Identity (Generated)

### Tone
Describe the tone (e.g., "Dense and mythic, like stone tablets being read aloud.").

### Sentence Rhythm
Describe the rhythmic tendencies (e.g., "Short, jagged sentences for action; long, winding clauses for the geode's interior.").

### Vocabulary Register
The word-hoard for this world. What specific domains of language are used? 
(e.g., "Geological terms, archival jargon, sensory words for salt and stone.")

### POV and Tense
e.g., "Third person limited, past tense."

### Dialogue Conventions
How do characters sound? Do they use contractions? Are tags used?

### Exemplar Passages
Write 3-5 paragraphs (diverse scenes) that ARE the voice. 
This is the tuning fork for the whole novel.

### Anti-Exemplars
3-5 paragraphs showing what this voice is NOT. 
(e.g., "This is too modern," "This is too flowery," "This is too generic AI-like.")
"""

print("Calling writer model...", file=sys.stderr)
result = call_writer(prompt)

# Append/Update voice.md
voice_lines = voice_template.split('\n')
try:
    part2_start = next(i for i, l in enumerate(voice_lines) if 'Part 2' in l)
    new_voice = '\n'.join(voice_lines[:part2_start]) + '\n' + result
except StopIteration:
    new_voice = voice_template + '\n\n' + result

VOICE_PATH.write_text(new_voice, encoding='utf-8')
print(result)
print(result)
