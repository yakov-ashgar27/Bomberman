"""All on-screen text in English and Hebrew.

t(key, lang, **values) returns the string in *logical* order; the renderer
passes Hebrew through text.to_visual() before drawing it.
"""
from __future__ import annotations

LANGUAGES = ("en", "he")
LANGUAGE_NAMES = {"en": "English", "he": "עברית"}

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "subtitle": "Software Engineering Project",
        "menu_start": "Start Game",
        "menu_language": "Language: {name}",
        "menu_sound": "Sound: {state}",
        "menu_highscores": "High Scores",
        "menu_quit": "Quit",
        "sound_on": "On",
        "sound_off": "Off",
        "controls": "Arrows / WASD move   Space bomb   P pause   M sound",
        "menu_help": "Up / Down choose   Enter select   Left / Right change",
        "paused": "PAUSED",
        "paused_help": "P / Esc resume     Q quit to menu",
        "level_complete": "LEVEL {n} COMPLETE!",
        "game_over": "GAME OVER",
        "victory": "YOU WIN!",
        "score_line": "Score: {score}",
        "final_score": "Final score: {score}",
        "press_enter": "Press Enter",
        "new_highscore": "NEW HIGH SCORE!",
        "enter_name": "Enter your name:",
        "save_hint": "Enter - save",
        "highscores_title": "HIGH SCORES",
        "no_scores": "No scores yet - go play!",
        "back_hint": "Enter / Esc - back",
        "hud_level": "LEVEL {n}/{total}",
        "hud_score": "SCORE {score}",
        "hud_lives": "LIVES {lives}",
        "hud_enemies": "ENEMIES {n}",
        "hud_stats": "B{b} F{f} S{s}",
        "no_hebrew_font": "No Hebrew font found on this computer",
    },
    "he": {
        "subtitle": "פרויקט בהנדסת תוכנה",
        "menu_start": "התחל משחק",
        "menu_language": "שפה: {name}",
        "menu_sound": "צלילים: {state}",
        "menu_highscores": "טבלת שיאים",
        "menu_quit": "יציאה",
        "sound_on": "פועלים",
        "sound_off": "כבויים",
        "controls": "חיצים - תנועה   רווח - פצצה   P - עצירה   M - צלילים",
        "menu_help": "חיצים למעלה ולמטה - בחירה   Enter - אישור   ימין ושמאל - שינוי",
        "paused": "המשחק עצור",
        "paused_help": "P - המשך     Q - חזרה לתפריט",
        "level_complete": "שלב {n} הושלם!",
        "game_over": "המשחק נגמר",
        "victory": "ניצחת!",
        "score_line": "ניקוד: {score}",
        "final_score": "ניקוד סופי: {score}",
        "press_enter": "לחצו Enter",
        "new_highscore": "שיא חדש!",
        "enter_name": "הקלידו את שמכם:",
        "save_hint": "Enter - שמירה",
        "highscores_title": "טבלת שיאים",
        "no_scores": "עדיין אין שיאים - קדימה לשחק!",
        "back_hint": "Enter או Esc - חזרה",
        "hud_level": "שלב {n}/{total}",
        "hud_score": "ניקוד {score}",
        "hud_lives": "חיים {lives}",
        "hud_enemies": "אויבים {n}",
        "hud_stats": "B{b} F{f} S{s}",
        "no_hebrew_font": "לא נמצא גופן עברי במחשב הזה",
    },
}


def t(key: str, lang: str = "en", **values) -> str:
    table = STRINGS.get(lang, STRINGS["en"])
    template = table.get(key, STRINGS["en"][key])
    return template.format(**values)


def next_language(lang: str) -> str:
    i = LANGUAGES.index(lang) if lang in LANGUAGES else 0
    return LANGUAGES[(i + 1) % len(LANGUAGES)]
