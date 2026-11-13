"""Bomberman launcher - opens the game like an app, with no console window.

The desktop / Start-menu shortcut runs this file with pythonw.exe.
On the first run it installs pygame if it is missing (a console window shows
the progress), and any startup error is shown in a message box and saved to
bomberman_error.log next to this file.
"""
import importlib
import os
import site
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


def show_error(text: str) -> None:
    (ROOT / "bomberman_error.log").write_text(text, encoding="utf-8")
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, text[-1500:], "Bomberman", 0x10)
    else:
        print(text, file=sys.stderr)


def ensure_pygame() -> None:
    try:
        import pygame  # noqa: F401
        return
    except ImportError:
        pass
    python = Path(sys.executable).with_name("python.exe" if sys.platform == "win32" else "python3")
    if not python.exists():
        python = Path(sys.executable)
    flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
    subprocess.run([str(python), "-m", "pip", "install", "--user", "-r", str(ROOT / "requirements.txt")],
                   creationflags=flags, check=True)
    site.addsitedir(site.getusersitepackages())
    importlib.invalidate_caches()


def main() -> None:
    try:
        ensure_pygame()
        from bomberman.app import App
        App().run()
    except SystemExit:
        raise
    except BaseException:
        show_error("Bomberman could not start:\n\n" + traceback.format_exc())


if __name__ == "__main__":
    main()
