"""Personal directory: maps personnel names to email addresses."""

import json
import logging
import os

logger = logging.getLogger(__name__)

PERSONAL_PATH = "data/personal_directory.json"


def load_directory() -> dict[str, str]:
    """Load the name→email mapping. Returns empty dict if file doesn't exist."""
    if not os.path.exists(PERSONAL_PATH):
        return {}
    try:
        with open(PERSONAL_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Error loading personal directory: %s", e)
        return {}


def save_directory(directory: dict[str, str]) -> bool:
    """Save the name→email mapping to disk."""
    try:
        os.makedirs(os.path.dirname(PERSONAL_PATH), exist_ok=True)
        with open(PERSONAL_PATH, "w", encoding="utf-8") as f:
            json.dump(directory, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error("Error saving personal directory: %s", e)
        return False


def get_emails_for(names: list[str]) -> list[str]:
    """Return email addresses for the given names. Names without email are skipped."""
    directory = load_directory()
    return [directory[name] for name in names if name in directory and directory[name].strip()]
