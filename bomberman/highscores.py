"""Persistent top-N high score table stored as JSON."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from . import config


@dataclass
class ScoreEntry:
    name: str
    score: int


def clean_name(name: str) -> str:
    name = "".join(ch for ch in name if ch.isprintable()).strip()
    return name[: config.MAX_NAME_LENGTH] or "PLAYER"


class HighScoreTable:
    def __init__(self, path: str | Path, max_entries: int = config.MAX_HIGHSCORES):
        self.path = Path(path)
        self.max_entries = max_entries
        self.entries: list[ScoreEntry] = self._load()

    def _load(self) -> list[ScoreEntry]:
        """Missing or corrupted files give an empty table instead of a crash."""
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            entries = [ScoreEntry(clean_name(str(e["name"])), int(e["score"])) for e in raw]
        except (OSError, ValueError, TypeError, KeyError):
            return []
        entries.sort(key=lambda e: e.score, reverse=True)
        return entries[: self.max_entries]

    def qualifies(self, score: int) -> bool:
        if score <= 0:
            return False
        if len(self.entries) < self.max_entries:
            return True
        return score > self.entries[-1].score

    def add(self, name: str, score: int) -> int | None:
        """Insert a score. Returns its 1-based rank, or None if it didn't make the table."""
        if not self.qualifies(score):
            return None
        entry = ScoreEntry(clean_name(name), int(score))
        # insert after equal scores so older entries keep their place
        index = next((i for i, e in enumerate(self.entries) if e.score < entry.score),
                     len(self.entries))
        self.entries.insert(index, entry)
        del self.entries[self.max_entries:]
        self.save()
        return index + 1

    def save(self) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps([asdict(e) for e in self.entries], indent=2),
                                 encoding="utf-8")
            return True
        except OSError:
            return False
