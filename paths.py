from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"
LORE_DIR = BASE_DIR / "lore"
CHAPTERS_DIR = BASE_DIR / "chapters"
BRIEFS_DIR = BASE_DIR / "briefs"
EDIT_LOGS_DIR = BASE_DIR / "edit_logs"
EVAL_LOGS_DIR = BASE_DIR / "eval_logs"

# Framework files
CRAFT_PATH = PROMPTS_DIR / "CRAFT.md"
ANTI_SLOP_PATH = PROMPTS_DIR / "ANTI-SLOP.md"
ANTI_PATTERNS_PATH = PROMPTS_DIR / "ANTI-PATTERNS.md"
PROGRAM_PATH = PROMPTS_DIR / "program.md"

# Novel files
SEED_PATH = LORE_DIR / "seed.txt"
WORLD_PATH = LORE_DIR / "world.md"
CHARACTERS_PATH = LORE_DIR / "characters.md"
OUTLINE_PATH = LORE_DIR / "outline.md"
CANON_PATH = LORE_DIR / "canon.md"
VOICE_PATH = LORE_DIR / "voice.md"
MYSTERY_PATH = LORE_DIR / "MYSTERY.md"
STATE_PATH = LORE_DIR / "state.json"
RESULTS_PATH = LORE_DIR / "results.tsv"
