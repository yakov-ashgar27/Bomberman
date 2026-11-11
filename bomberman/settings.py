"""Player settings (language, sound) saved between runs as JSON."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .i18n import LANGUAGES


@dataclass
class Settings:
    language: str = "en"
    sound: bool = True

    @classmethod
    def load(cls, path: str | Path) -> "Settings":
        """Missing or broken files fall back to defaults instead of crashing."""
        try:
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return cls()
        if not isinstance(raw, dict):
            return cls()
        settings = cls()
        if raw.get("language") in LANGUAGES:
            settings.language = raw["language"]
        if isinstance(raw.get("sound"), bool):
            settings.sound = raw["sound"]
        return settings

    def save(self, path: str | Path) -> bool:
        try:
            Path(path).write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
            return True
        except OSError:
            return False
