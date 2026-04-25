#!/usr/bin/env python3
"""
Generate MYSTERY.md based on the seed concept.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from paths import BASE_DIR, SEED_PATH, MYSTERY_PATH
load_dotenv(BASE_DIR / ".env")

WRITER_MODEL = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")

from llm import call_llm

def call_writer(prompt, max_tokens=4000):
    system_prompt = (
        "You are a master of suspense and mystery in fiction. You design secrets "
        "that are logically consistent with the world's rules but completely "
        "recontextualize the reader's understanding when revealed. "
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

prompt = f"""Design the central mystery for this fantasy novel. 
This is the secret the reader will gradually uncover, leading to a major climax.

SEED CONCEPT:
{seed}

REQUIREMENTS:
- A central question that can be asked in one sentence.
- An answer that recontextualizes the entire story.
- High stakes: the answer must change the protagonist's world.
- Logical consistency: it must be hinted at (foreshadowed) throughout the book.
- Moral ambiguity: there should be no easy "right" answer once the secret is out.
- A physical manifestation: the mystery should involve something tangible in the world.

OUTPUT FORMAT:
# THE CENTRAL MYSTERY
### Author's Eyes Only

## The Question
One sentence.

## The Secret
A detailed explanation of the truth.

## Recontextualization
How this changes the reader's understanding of earlier events.

## Foreshadowing Hints
3-5 specific things to plant in early chapters.

## The Choice
The impossible choice the protagonist must make once they know the truth.
"""

print("Calling writer model...", file=sys.stderr)
result = call_writer(prompt)
MYSTERY_PATH.write_text(result, encoding='utf-8')
print(result)
print(result)
