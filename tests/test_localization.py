"""Languages, right-to-left text and saved settings (FR-17)."""
import string

from bomberman import i18n
from bomberman.settings import Settings
from bomberman.text import has_rtl, to_visual


# ------------------------------------------------------------- translations
def _fields(template: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(template) if name}


def test_every_key_exists_in_every_language():
    keys = set(i18n.STRINGS["en"])
    for lang in i18n.LANGUAGES:
        assert set(i18n.STRINGS[lang]) == keys, lang


def test_placeholders_match_between_languages():
    for key, english in i18n.STRINGS["en"].items():
        for lang in i18n.LANGUAGES:
            assert _fields(i18n.STRINGS[lang][key]) == _fields(english), (lang, key)


def test_hebrew_strings_are_really_hebrew():
    hebrew = i18n.STRINGS["he"]
    assert has_rtl(hebrew["menu_start"]) and has_rtl(hebrew["game_over"])


def test_translate_and_format():
    assert i18n.t("hud_level", "en", n=2, total=5) == "LEVEL 2/5"
    assert i18n.t("hud_level", "he", n=2, total=5) == "שלב 2/5"


def test_unknown_language_falls_back_to_english():
    assert i18n.t("menu_quit", "fr") == "Quit"


def test_next_language_cycles():
    assert i18n.next_language("en") == "he"
    assert i18n.next_language("he") == "en"


# ------------------------------------------------------------ bidi / visual
def test_latin_text_is_unchanged():
    assert to_visual("Score: 120") == "Score: 120"


def test_pure_hebrew_is_reversed():
    assert to_visual("שלום") == "םולש"


def test_numbers_inside_hebrew_keep_their_order():
    # logical "level 2/5" -> visual: number on the left, word on the right
    assert to_visual("שלב 2/5") == "2/5 בלש"
    assert to_visual("ניקוד 001200") == "001200 דוקינ"


def test_english_word_inside_hebrew_sentence():
    assert to_visual("Enter - שמירה") == "הרימש - Enter"
    assert to_visual("לחצו Enter") == "Enter וצחל"


def test_trailing_punctuation_goes_to_the_left():
    assert to_visual("ניצחת!") == "!תחצינ"


def test_brackets_are_mirrored():
    assert to_visual("(שלום)") == "(םולש)"


# ------------------------------------------------------------------ settings
def test_settings_defaults_when_missing(tmp_path):
    s = Settings.load(tmp_path / "none.json")
    assert (s.language, s.sound) == ("en", True)


def test_settings_round_trip(tmp_path):
    path = tmp_path / "settings.json"
    Settings(language="he", sound=False).save(path)
    loaded = Settings.load(path)
    assert (loaded.language, loaded.sound) == ("he", False)


def test_settings_ignore_bad_values(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text('{"language": "klingon", "sound": "loud"}', encoding="utf-8")
    loaded = Settings.load(path)
    assert (loaded.language, loaded.sound) == ("en", True)
    path.write_text("not json", encoding="utf-8")
    assert Settings.load(path).language == "en"
