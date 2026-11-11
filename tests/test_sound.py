"""Sound synthesis (FR-16). Runs without pygame or speakers."""
import io
import sys
import wave

from bomberman import config, sound
from bomberman.sound import SOUND_EVENTS


def _read(wav_bytes):
    with wave.open(io.BytesIO(wav_bytes)) as w:
        return w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()


def test_tone_has_requested_length_and_volume():
    samples = sound.tone(440, 0.1, "square", volume=0.5)
    assert len(samples) == int(config.SAMPLE_RATE * 0.1)
    assert max(abs(s) for s in samples) <= 0.5 + 1e-9


def test_every_waveform_stays_in_range():
    for kind in ("square", "triangle", "sine", "noise"):
        samples = sound.tone(300, 0.05, kind, volume=1.0)
        assert all(-1.0 <= s <= 1.0 for s in samples), kind


def test_envelope_fades_in_and_out():
    samples = sound.tone(440, 0.2, "square", volume=1.0)
    assert abs(samples[0]) < 0.05 and abs(samples[-1]) < 0.05


def test_wav_encoding_is_valid_and_clipped():
    data = sound.to_wav([0.0, 2.0, -2.0, 0.5])
    assert _read(data) == (1, 2, config.SAMPLE_RATE, 4)


def test_every_game_event_has_a_sound():
    effects = sound.build_effects()
    assert SOUND_EVENTS <= set(effects)
    for name, data in effects.items():
        channels, width, rate, frames = _read(data)
        assert (channels, width, rate) == (1, 2, config.SAMPLE_RATE), name
        assert 0 < frames / rate < 2.0, name  # short effects


def test_music_loop_is_several_seconds():
    _, _, rate, frames = _read(sound.build_music())
    assert 5 < frames / rate < 20


def test_player_without_audio_is_silent_not_crashing(monkeypatch):
    monkeypatch.setitem(sys.modules, "pygame", None)  # "import pygame" now fails
    player = sound.SoundPlayer(enabled=True)
    assert not player.available and not player.active
    player.play("explosion")
    player.start_music()
    player.pause_music(True)
    player.stop_music()
