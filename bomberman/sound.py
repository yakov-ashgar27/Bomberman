"""Sound effects and music, synthesised in code - the game ships no audio files.

Two layers:
* synthesis (pure Python, testable): builds 16-bit mono WAV bytes from simple
  waveforms - square, triangle, sine and noise - with pitch slides and envelopes.
* SoundPlayer (pygame.mixer): loads those WAVs and plays them. If the computer
  has no audio device, the player quietly turns itself off instead of crashing.
"""
from __future__ import annotations

import io
import math
import random
import struct
import wave

from . import config

RATE = config.SAMPLE_RATE

# game events that make a sound (the event name is also the sound name)
SOUND_EVENTS = {"bomb_placed", "explosion", "powerup", "enemy_killed", "player_died",
                "level_complete", "victory", "game_over"}

# --------------------------------------------------------------- synthesis

def _osc(kind: str, phase: float, rng: random.Random) -> float:
    if kind == "square":
        return 1.0 if (phase % 1.0) < 0.5 else -1.0
    if kind == "triangle":
        p = phase % 1.0
        return 4 * p - 1 if p < 0.5 else 3 - 4 * p
    if kind == "noise":
        return rng.uniform(-1.0, 1.0)
    return math.sin(2 * math.pi * phase)  # sine


def tone(freq: float, duration: float, kind: str = "square", volume: float = 0.5,
         freq_end: float | None = None, attack: float = 0.005, release: float = 0.05,
         decay: float = 0.0, seed: int = 0) -> list[float]:
    """One note. freq_end slides the pitch; decay > 0 adds an exponential fade."""
    n = max(1, int(RATE * duration))
    freq_end = freq if freq_end is None else freq_end
    rng = random.Random(seed)
    out, phase = [], 0.0
    a, r = max(1, int(RATE * attack)), max(1, int(RATE * release))
    for i in range(n):
        t = i / n
        f = freq + (freq_end - freq) * t
        phase += f / RATE
        env = min(1.0, i / a, (n - i) / r)
        if decay:
            env *= math.exp(-decay * i / RATE)
        out.append(_osc(kind, phase, rng) * volume * env)
    return out


def silence(duration: float) -> list[float]:
    return [0.0] * int(RATE * duration)


def sequence(notes: list[tuple[float, float]], kind: str = "square", volume: float = 0.4) -> list[float]:
    """Notes played one after another. A frequency of 0 is a rest."""
    out: list[float] = []
    for freq, dur in notes:
        out += silence(dur) if freq <= 0 else tone(freq, dur, kind, volume)
    return out


def mix(*tracks: list[float]) -> list[float]:
    length = max(len(t) for t in tracks)
    return [sum(t[i] for t in tracks if i < len(t)) for i in range(length)]


def to_wav(samples: list[float]) -> bytes:
    """Clip to [-1, 1] and encode as a 16-bit mono WAV file."""
    frames = struct.pack(f"<{len(samples)}h",
                         *(int(max(-1.0, min(1.0, s)) * 32767) for s in samples))
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(frames)
    return buf.getvalue()


# Musical note frequencies (Hz)
C4, D4, E4, F4, G4, A4, B4 = 261.6, 293.7, 329.6, 349.2, 392.0, 440.0, 493.9
C5, D5, E5, G5, A5, C6 = 523.3, 587.3, 659.3, 784.0, 880.0, 1046.5
A2, C3, D3, E3, F3, G3 = 110.0, 130.8, 146.8, 164.8, 174.6, 196.0


def _music() -> list[float]:
    """An 8-bar chiptune loop: square-wave melody over a triangle bass line."""
    beat = 60 / 150 / 2  # eighth notes at 150 bpm
    melody = [E5, 0, G5, E5, D5, C5, D5, E5,   C5, 0, E5, C5, A4, G4, A4, C5,
              D5, 0, F4 * 2, D5, C5, B4, C5, D5, E5, D5, C5, B4, C5, 0, 0, 0] * 2
    bass = [A2 * 2, A2 * 2, E3, E3, F3, F3, C3 * 2, C3 * 2,
            D3, D3, A2 * 2, A2 * 2, G3, G3, E3, E3] * 4
    mel = sequence([(f, beat) for f in melody], "square", 0.10)
    bas = sequence([(f, beat) for f in bass], "triangle", 0.22)
    return mix(mel, bas)


def build_effects() -> dict[str, bytes]:
    """Every sound in the game, keyed by the event name that triggers it."""
    return {
        "bomb_placed": to_wav(tone(220, 0.08, "square", 0.35, freq_end=150)),
        "explosion": to_wav(mix(tone(0, 0.55, "noise", 0.55, decay=7, seed=1),
                                tone(90, 0.45, "sine", 0.6, freq_end=35, decay=5))),
        "powerup": to_wav(sequence([(C5, 0.06), (E5, 0.06), (G5, 0.06), (C6, 0.12)], "square", 0.3)),
        "enemy_killed": to_wav(tone(900, 0.18, "square", 0.3, freq_end=200)),
        "player_died": to_wav(sequence([(A4, 0.12), (F4, 0.12), (D4, 0.12), (A2 * 2, 0.35)],
                                       "triangle", 0.5)),
        "level_complete": to_wav(sequence([(C5, 0.1), (E5, 0.1), (G5, 0.1), (C6, 0.35)], "square", 0.3)),
        "victory": to_wav(sequence([(G4, 0.12), (C5, 0.12), (E5, 0.12), (G5, 0.24), (E5, 0.12),
                                    (G5, 0.5)], "square", 0.3)),
        "game_over": to_wav(sequence([(G4, 0.25), (E4, 0.25), (C4, 0.25), (G3, 0.6)], "triangle", 0.5)),
        "menu_move": to_wav(tone(660, 0.04, "square", 0.2)),
        "menu_select": to_wav(tone(880, 0.09, "square", 0.25, freq_end=1320)),
    }


def build_music() -> bytes:
    return to_wav(_music())


# ------------------------------------------------------------------ player

class SoundPlayer:
    """Plays the synthesised sounds through pygame.mixer. Safe without audio hardware."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.available = False
        self._sounds = {}
        self._music = None
        self._music_channel = None
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(RATE, -16, 1, 512)
            self._sounds = {name: pygame.mixer.Sound(file=io.BytesIO(data))
                            for name, data in build_effects().items()}
            for snd in self._sounds.values():
                snd.set_volume(config.SFX_VOLUME)
            self._music = pygame.mixer.Sound(file=io.BytesIO(build_music()))
            self._music.set_volume(config.MUSIC_VOLUME)
            self.available = True
        except Exception:  # no audio device, missing mixer, ... -> silent game
            self.available = False

    @property
    def active(self) -> bool:
        return self.enabled and self.available

    def play(self, name: str) -> None:
        if self.active and name in self._sounds:
            self._sounds[name].play()

    def start_music(self) -> None:
        if self.active and self._music is not None and not self._music_playing():
            self._music_channel = self._music.play(loops=-1)

    def stop_music(self) -> None:
        if self._music_channel is not None:
            self._music_channel.stop()
            self._music_channel = None

    def pause_music(self, paused: bool) -> None:
        if self._music_channel is not None:
            if paused:
                self._music_channel.pause()
            else:
                self._music_channel.unpause()

    def _music_playing(self) -> bool:
        return self._music_channel is not None and bool(self._music_channel.get_busy())

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        if not enabled:
            self.stop_music()
