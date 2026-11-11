"""Generate the Bomberman Hebrew slide deck (deck.json + slides/*.html) for the Claude Slides artifact.

Run: python generate_slides.py   - then python render_pdf.py to build a local PDF preview.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent  # writes deck.json and slides/ next to this script
(OUT / "slides").mkdir(parents=True, exist_ok=True)

RLE, PDF = "‫", "‬"


def R(s: str) -> str:
    """Embed Hebrew text right-to-left so mixed Hebrew/Latin reads correctly."""
    return f"{RLE}{s}{PDF}"


DARK = "#141A2E"
DARK2 = "#1E2742"
LIGHT = "#F6F1E7"
CARD = "#FFFDF8"
INK = "#1F2438"
BODY = "#3E4560"
SOFT_D = "#B9C1D9"
ORANGE = "#FF8A1F"
ORANGE_TXT = "#B04E06"
YELLOW = "#FFD447"
LINE = "#E4DCCB"
FONT = "font-family:'Rubik', Arial, sans-serif"
MONO = "font-family:'JetBrains Mono', 'Courier New', monospace"

TOTAL = 13


def light_section(sid, body, page, notes, transition="fade"):
    return (
        f'<section id="{sid}" data-transition="{transition}" style="background:{LIGHT};color:{BODY};{FONT};'
        f'padding:128px 128px 160px;display:flex;flex-direction:column;gap:40px">\n'
        f"{body}\n{footer(page, dark=False)}\n<aside>{notes}</aside>\n</section>\n"
    )


def dark_section(sid, body, page, notes, transition="fade"):
    return (
        f'<section id="{sid}" data-transition="{transition}" style="background:{DARK};color:{SOFT_D};{FONT};'
        f'padding:128px 128px 160px;display:flex;flex-direction:column;gap:40px">\n'
        f"{body}\n{footer(page, dark=True)}\n<aside>{notes}</aside>\n</section>\n"
    )


def footer(page, dark):
    c = "#7F89A8" if dark else "#7A7466"
    return (
        f'<p style="position:absolute;left:128px;bottom:64px;width:1200px;font-size:24px;color:{c};text-align:left">{page} / {TOTAL}</p>\n'
        f'<p style="position:absolute;right:128px;bottom:64px;width:900px;font-size:24px;color:{c};text-align:right">{R("פרויקט Bomberman בהנדסת תוכנה")}</p>'
    )


def heading(eyebrow, title, dark=False):
    eb = ORANGE if dark else ORANGE_TXT
    tc = LIGHT if dark else INK
    return (
        f'<div style="display:flex;flex-direction:column;gap:16px">\n'
        f'<p style="font-size:28px;font-weight:600;color:{eb};text-align:right">{R(eyebrow)}</p>\n'
        f'<h2 style="font-size:72px;font-weight:700;line-height:1.1;color:{tc};text-align:right">{R(title)}</h2>\n'
        f"</div>"
    )


slides = {}

# 1 ── cover ────────────────────────────────────────────────────────────────
bomb_svg = f"""<svg aria-label="איור של פצצה עם פתיל בוער מעל משבצות של מבוך" width="560" height="560" viewBox="0 0 560 560">
<rect x="0" y="400" width="112" height="112" rx="10" fill="#2A3352"/>
<rect x="112" y="400" width="112" height="112" rx="10" fill="#C2622F"/>
<rect x="224" y="400" width="112" height="112" rx="10" fill="#2A3352"/>
<rect x="336" y="400" width="112" height="112" rx="10" fill="#C2622F"/>
<rect x="448" y="400" width="112" height="112" rx="10" fill="#2A3352"/>
<circle cx="260" cy="270" r="170" fill="#0B0F1C" stroke="#3A4466" stroke-width="8"/>
<circle cx="200" cy="210" r="42" fill="#2E3758"/>
<rect x="318" y="96" width="70" height="56" rx="10" fill="#3A4466" transform="rotate(35 353 124)"/>
<path d="M372 104 C 410 60, 440 70, 452 40" fill="none" stroke="#D9C79A" stroke-width="10" stroke-linecap="round"/>
<polygon points="458,4 470,30 498,24 478,46 494,70 466,62 452,88 446,60 418,58 440,40" fill="{ORANGE}"/>
<circle cx="458" cy="44" r="12" fill="{YELLOW}"/>
</svg>"""

slides["cover"] = f"""<section id="cover" data-transition="fade" style="background:{DARK};color:{SOFT_D};{FONT};padding:128px;display:flex;flex-direction:row-reverse;align-items:center;justify-content:space-between;gap:96px">
<div style="width:1000px;display:flex;flex-direction:column;gap:32px">
<p style="font-size:28px;font-weight:600;color:{ORANGE};text-align:right">{R("פרויקט בקורס הנדסת תוכנה")}</p>
<h1 style="font-size:140px;font-weight:800;line-height:1;color:{LIGHT};text-align:right;letter-spacing:4px">BOMBERMAN</h1>
<p style="font-size:44px;line-height:1.3;color:{LIGHT};text-align:right">{R("מאפיון ועד משחק שרץ באמת")}</p>
<div style="display:flex;flex-direction:row-reverse;gap:16px">
<p style="font-size:24px;color:{LIGHT};background:{DARK2};padding:8px 20px;border-radius:999px;white-space:nowrap">{R("חמישה שלבים")}</p>
<p style="font-size:24px;color:{LIGHT};background:{DARK2};padding:8px 20px;border-radius:999px;white-space:nowrap">{R("עברית ואנגלית")}</p>
<p style="font-size:24px;color:{LIGHT};background:{DARK2};padding:8px 20px;border-radius:999px;white-space:nowrap">{R("כל 84 הבדיקות עוברות")}</p>
<p style="font-size:24px;color:{LIGHT};background:{DARK2};padding:8px 20px;border-radius:999px;white-space:nowrap">Python + Pygame</p>
</div>
<p style="font-size:24px;color:#7F89A8;text-align:right">{R("[שמות חברי הצוות] · [שם הקורס והמרצה] · [תאריך ההצגה]")}</p>
</div>
{bomb_svg}
<aside>{R("פתיחה: אנחנו נציג משחק Bomberman שבנינו מאפס, כולל מסמך אפיון, תכנון, קוד ובדיקות. בסוף נעשה הדגמה חיה.")}</aside>
</section>
"""


# 2 ── what we built ────────────────────────────────────────────────────────
def stat(num, label):
    return (
        f'<div style="flex:1;display:flex;flex-direction:column;gap:12px;background:{CARD};padding:40px;border:2px solid {LINE};border-radius:20px">\n'
        f'<p style="font-size:120px;font-weight:800;line-height:1;color:{ORANGE_TXT};text-align:right">{num}</p>\n'
        f'<p style="font-size:32px;color:{INK};text-align:right">{R(label)}</p>\n</div>'
    )


body = heading("המוצר", "משחק מבוך קלאסי, שלם ומוכן להצגה") + f"""
<div style="display:flex;flex-direction:row-reverse;gap:32px">
{stat("5", "שלבים, כל אחד קשה מהקודם")}
{stat("2", "שפות: עברית ואנגלית")}
{stat("10", "צלילים, ועוד מוזיקת רקע")}
{stat("84", "בדיקות אוטומטיות שעוברות")}
</div>
<p style="font-size:32px;line-height:1.4;color:{BODY};text-align:right">{R("הגרפיקה מצוירת בקוד והצלילים נוצרים בקוד, בלי קובצי מדיה, ולכן המשחק עצמאי לגמרי ורץ על כל מערכת הפעלה")}</p>"""
slides["product"] = light_section("product", body, 2, R("המספרים המרכזיים. להדגיש: הכול רץ, הכול נבדק, ואין תלות בקבצים חיצוניים."))


# 3 ── how to play ──────────────────────────────────────────────────────────
def rule_card(icon, title, text):
    return (
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:end;gap:20px;background:{CARD};padding:40px;border:2px solid {LINE};border-radius:20px">\n'
        f'<x-icon name="{icon}" style="color:{ORANGE_TXT};width:64px;height:64px"></x-icon>\n'
        f'<h3 style="font-size:44px;font-weight:700;color:{INK};text-align:right">{R(title)}</h3>\n'
        f'<p style="font-size:28px;line-height:1.45;color:{BODY};text-align:right">{R(text)}</p>\n</div>'
    )


body = heading("חוקי המשחק", "מפוצצים לבנים, מחסלים אויבים, מוצאים את היציאה") + f"""
<div style="display:flex;flex-direction:row-reverse;gap:32px">
{rule_card("Lightning", "פצצות", "מתפוצצות אחרי 2.5 שניות. הלהבה נעצרת בקיר והורסת רק את הלבנה הראשונה בכל כיוון")}
{rule_card("Users", "אויבים", "האויב הוורוד נודד באקראי. הסגול רודף אחרי השחקן במסלול הקצר ביותר")}
{rule_card("Star", "שיפורים", "האות B מוסיפה פצצה, F מגדילה את טווח הפיצוץ, ו-S מאיצה את השחקן")}
{rule_card("Key", "יציאה", "מוסתרת מתחת ללבנה, ונפתחת רק אחרי שכל האויבים מתו")}
</div>"""
slides["rules"] = light_section("rules", body, 3, R("שלוש חיים, 180 שניות לשלב. מוות מתחיל את השלב מחדש, אבל הניקוד והשיפורים נשמרים."))


# 3b ── what's new in 1.1
body = heading("גרסה 1.1: מה חדש", "צלילים, עברית וחמישה שלבים") + f"""
<div style="display:flex;flex-direction:row-reverse;gap:32px">
{rule_card("Play", "צלילים ומוזיקה", "אפקט קולי לכל אירוע ומוזיקת רקע. הכול נוצר בקוד, בלי קובצי שמע, ומקש M משתיק")}
{rule_card("Globe", "עברית ואנגלית", "בוחרים שפה בתפריט. העברית מוצגת מימין לשמאל, ושורת המצב מתהפכת")}
{rule_card("Star", "חמישה שלבים", "בשלבים 4 ו-5 יש יותר לבנים, ועד שבעה אויבים סגולים שרודפים אחריך")}
</div>
<p style="font-size:28px;line-height:1.4;color:{BODY};text-align:right">{R("הבחירה בשפה ובצלילים נשמרת בקובץ settings.json, ובהפעלה הבאה המשחק נפתח באותו מצב")}</p>"""
slides["features"] = light_section("features", body, 4, R("הגרסה הראשונה הייתה באנגלית, בלי צלילים ועם 3 שלבים. התוספות נכנסו כדרישות FR-16 ו-FR-17 במסמך האפיון, ויש להן 22 בדיקות חדשות."))


# 4 ── requirements ─────────────────────────────────────────────────────────
def req_card(tag, count, items, accent=False):
    bg = DARK if accent else CARD
    tc = LIGHT if accent else INK
    bc = SOFT_D if accent else BODY
    border = DARK if accent else LINE
    rows = "\n".join(
        f'<p style="font-size:28px;line-height:1.35;color:{bc};text-align:right">{R(i)}</p>' for i in items
    )
    return (
        f'<div style="flex:1;display:flex;flex-direction:column;gap:16px;background:{bg};padding:40px;border:2px solid {border};border-radius:20px">\n'
        f'<p style="font-size:28px;font-weight:600;color:{ORANGE if accent else ORANGE_TXT};text-align:right">{R(tag)}</p>\n'
        f'<h3 style="font-size:72px;font-weight:800;line-height:1;color:{tc};text-align:right">{count}</h3>\n'
        f"{rows}\n</div>"
    )


body = heading("מסמך האפיון", "יש 29 דרישות, ולכל אחת מהן יש דרך לבדוק אותה") + f"""
<div style="display:flex;flex-direction:row-reverse;gap:32px">
{req_card("דרישות חובה", "14", ["טעינת 5 שלבים ואימות", "תנועה, פצצות ופיצוצים", "אויבים ומגע", "חיים, עצירה ומעבר שלב", "שיאים, תפריט ושורת מצב", "צלילים ובחירת שפה"], accent=True)}
{req_card("דרישות רצויות", "3", ["תגובת שרשרת", "שיפורים", "שעון לכל שלב"])}
{req_card("דרישות לא-פונקציונליות", "12", ["קצב של 60 פריימים לשנייה", "כיסוי בדיקות של 90% לפחות", "שלב חדש הוא קובץ טקסט אחד", "שפה חדשה בלי שינוי לוגיקה"])}
</div>"""
slides["requirements"] = light_section("requirements", body, 5, R("17 דרישות פונקציונליות ועוד 12 לא-פונקציונליות. כל דרישה לא-פונקציונלית קיבלה קריטריון מדיד, ולכן אפשר לבדוק אותה. הפירוט המלא נמצא במסמך האפיון."))


# 5 ── architecture ─────────────────────────────────────────────────────────
def mod(name, sub, hi=False):
    bg = "#FFE7CC" if hi else CARD
    bd = ORANGE_TXT if hi else LINE
    return (
        f'<div style="flex:1;display:flex;flex-direction:column;gap:4px;background:{bg};padding:14px 16px;border:2px solid {bd};border-radius:14px">\n'
        f'<p style="{MONO};font-size:24px;font-weight:700;color:{INK};text-align:center">{name}</p>\n'
        f'<p style="font-size:24px;color:{BODY};text-align:center">{R(sub)}</p>\n</div>'
    )


def layer(title, note, inner, tint):
    return (
        f'<div style="display:flex;flex-direction:column;gap:10px;background:{tint};padding:18px 28px;border-radius:20px">\n'
        f'<div style="display:flex;flex-direction:row-reverse;gap:16px;align-items:baseline">\n'
        f'<h3 style="font-size:32px;font-weight:700;color:{INK};text-align:right">{R(title)}</h3>\n'
        f'<p style="font-size:24px;color:{BODY};text-align:right">{R(note)}</p>\n</div>\n'
        f'<div style="display:flex;flex-direction:row-reverse;gap:20px">\n{inner}\n</div>\n</div>'
    )


ui = "\n".join([mod("app.py", "לולאה, קלט ומסכים"), mod("renderer.py", "ציור המסך"), mod("sound.py", "צלילים ומוזיקה")])
logic = "\n".join([
    mod("game.py", "חוקים ומצבים", hi=True), mod("ai.py", "נדידה ומרדף"),
    mod("entities.py", "שחקן, אויב, פצצה"), mod("grid.py", "מפת המשבצות"),
    mod("level.py", "טעינת 5 שלבים"),
])
support = "\n".join([
    mod("i18n.py", "תרגומים"), mod("text.py", "עברית מימין לשמאל"),
    mod("settings.py", "שפה וצלילים"), mod("highscores.py", "טבלת שיאים"),
])
body = heading("ארכיטקטורה", "הלוגיקה נפרדת מהתצוגה ונבדקת בלי חלון") + f"""
<div style="display:flex;flex-direction:column;gap:10px">
{layer("שכבת התצוגה", "השכבה היחידה שתלויה בספריית הגרפיקה", ui, "#ECE4D3")}
<div style="display:flex;flex-direction:row;justify-content:center;gap:16px;align-items:center">
<x-shape kind="arrow-down" style="background:{ORANGE_TXT};width:32px;height:40px"></x-shape>
<p style="font-size:24px;color:{BODY}">{R("קוראת ל-update ומציירת את המצב")}</p>
</div>
{layer("שכבת הלוגיקה", "קוד נקי, בלי גרפיקה", logic, "#E6EBF2")}
{layer("שירותים משותפים", "גם הם בלי גרפיקה, ונבדקים אוטומטית", support, "#E9E4F0")}
</div>"""
slides["architecture"] = light_section("architecture", body, 6, R("דפוס דומה ל-MVC: Game הוא המודל, Renderer הוא התצוגה ו-App הוא הבקר. כל הקבועים נמצאים ב-config.py."))


# 6 ── state machine ───────────────────────────────────────────────────────
def state(name, sub, hi=False):
    bg = DARK if hi else CARD
    tc = LIGHT if hi else INK
    sc = SOFT_D if hi else BODY
    bd = DARK if hi else LINE
    return (
        f'<div style="width:300px;display:flex;flex-direction:column;gap:8px;background:{bg};padding:28px 20px;border:2px solid {bd};border-radius:18px">\n'
        f'<p style="{MONO};font-size:28px;font-weight:700;color:{tc};text-align:center">{name}</p>\n'
        f'<p style="font-size:24px;color:{sc};text-align:center">{R(sub)}</p>\n</div>'
    )


def arrow(label):
    return (
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:8px">\n'
        f'<p style="font-size:24px;color:{BODY};text-align:center">{R(label)}</p>\n'
        f'<x-shape kind="arrow-left" style="background:{ORANGE_TXT};width:80px;height:36px"></x-shape>\n</div>'
    )


def side_card(name, text):
    return (
        f'<div style="flex:1;display:flex;flex-direction:column;gap:10px;background:{CARD};padding:28px 32px;border:2px solid {LINE};border-radius:18px">\n'
        f'<p style="{MONO};font-size:28px;font-weight:700;color:{INK};text-align:right">{name}</p>\n'
        f'<p style="font-size:28px;line-height:1.4;color:{BODY};text-align:right">{R(text)}</p>\n</div>'
    )


body = heading("מכונת המצבים", "שבעה מצבים, והמשחק תמיד חוזר לתפריט") + f"""
<div style="display:flex;flex-direction:row-reverse;align-items:center;gap:8px">
{state("MENU", "תפריט ראשי")}
{arrow("התחלה")}
{state("PLAYING", "משחק פעיל", hi=True)}
{arrow("הגיע ליציאה")}
{state("LEVEL_COMPLETE", "מעבר לשלב הבא")}
{arrow("שלב אחרון")}
{state("VICTORY", "ניצחון")}
</div>
<div style="display:flex;flex-direction:row-reverse;gap:32px">
{side_card("PAUSED", "לחיצה על P או Esc עוצרת את המשחק. השעון, הפצצות והאויבים קופאים")}
{side_card("PLAYER_DIED", "אם נשארו חיים, השלב מתחיל מחדש. אחרת המשחק עובר למסך הסיום")}
{side_card("GAME_OVER", "לחיצה על Enter מובילה לטבלת השיאים, ומשם חוזרים לתפריט")}
</div>"""
slides["states"] = light_section("states", body, 7, R("כל המצב נשמר במשתנה אחד, Game.state. הפונקציה update בודקת אותו ומריצה רק את הלוגיקה של המצב הנוכחי. בעצירה היא לא עושה כלום, ולכן הכול קופא."))


# 7 ── algorithms ───────────────────────────────────────────────────────────
def code_block(lines):
    html = "<br>".join(l.replace(" ", "&#160;") for l in lines)
    return f'<p style="{MONO};font-size:24px;line-height:1.55;color:#E8EBF5;background:{DARK2};padding:28px 32px;border-radius:16px;text-align:left">{html}</p>'


def algo_card(title, text, code):
    return (
        f'<div style="flex:1;display:flex;flex-direction:column;gap:20px">\n'
        f'<h3 style="font-size:44px;font-weight:700;color:{LIGHT};text-align:right">{R(title)}</h3>\n'
        f'<p style="font-size:28px;line-height:1.45;color:{SOFT_D};text-align:right">{R(text)}</p>\n'
        f"{code_block(code)}\n</div>"
    )


bfs = [
    "queue = deque([(start, None)])",
    "while queue:",
    "    pos, first = queue.popleft()",
    "    for d in Direction:",
    "        nxt = step(pos, d)",
    "        if nxt == goal: return first or d",
    "        if walkable(nxt) and nxt not in seen:",
    "            seen.add(nxt)",
    "            queue.append((nxt, first or d))",
]
chain = [
    "queue = list(due_bombs)",
    "while queue:",
    "    bomb = queue.pop()",
    "    if bomb in done: continue",
    "    done.append(bomb)",
    "    for tile in flame_path(bomb):",
    "        other = bomb_at(tile)",
    "        if other and other not in done:",
    "            queue.append(other)",
]
body = heading("אלגוריתמים", "שני רעיונות שעושים את המשחק חכם", dark=True) + f"""
<div style="display:flex;flex-direction:row-reverse;gap:56px">
{algo_card("האויב הסגול רודף בעזרת חיפוש לרוחב", "חיפוש לרוחב (BFS) מוצא את הצעד הראשון במסלול הקצר ביותר אל השחקן, ועוקף קירות ופצצות", bfs)}
{algo_card("תגובת שרשרת עם תור", "כל פצצה שהלהבה פוגעת בה נכנסת לתור. כל פצצה מתפוצצת פעם אחת בלבד", chain)}
</div>"""
slides["algorithms"] = dark_section("algorithms", body, 8, R("BFS מבטיח מסלול קצר ביותר. על מפה של 195 משבצות הוא רץ בפחות ממילישנייה. התור בתגובת השרשרת מונע רקורסיה עמוקה ופיצוץ כפול."))


# 8 ── testing ──────────────────────────────────────────────────────────────
rows = [
    ("17", "טעינת 5 שלבים, אימות ומפה", "test_level.py"),
    ("9", "תנועה, חסימות ושיפורים", "test_player.py"),
    ("9", "פצצות, להבות ושרשרת", "test_bombs.py"),
    ("11", "נדידה, מרדף BFS, מגע ופגיעה בלהבה", "test_enemies.py"),
    ("10", "חיים, שעון, עצירה ומעבר שלב", "test_game_flow.py"),
    ("6", "מיון, שמירה וקובץ פגום", "test_highscores.py"),
    ("15", "תרגומים, עברית והגדרות", "test_localization.py"),
    ("7", "סינתוז צלילים ויצירת קובצי שמע", "test_sound.py"),
]
trs = "\n".join(
    f'<tr><td style="width:14%;text-align:left;color:{INK}">{n}</td>'
    f'<td style="width:50%;text-align:right">{R(what)}</td>'
    f'<td style="width:36%;text-align:right;color:{INK}">{f}</td></tr>'
    for n, what, f in rows
)
table = (
    f'<table style="font-size:26px;color:{BODY};{FONT}">\n'
    f'<tr><th style="width:14%;text-align:left">{R("בדיקות")}</th><th style="width:50%;text-align:right">{R("מה נבדק")}</th><th style="width:36%;text-align:right">{R("קובץ")}</th></tr>\n'
    f"{trs}\n</table>"
)
body = heading("בדיקות", "כל 84 הבדיקות עוברות בפחות משנייה") + f"""
<div style="display:flex;flex-direction:row-reverse;gap:56px;align-items:start">
<div style="flex:1">
{table}
</div>
<div style="width:500px;display:flex;flex-direction:column;gap:16px;background:{DARK};padding:40px;border-radius:20px">
<p style="font-size:120px;font-weight:800;line-height:1;color:{ORANGE};text-align:right">95%</p>
<p style="font-size:32px;color:{LIGHT};text-align:right">{R("בערך זה הכיסוי של קוד הלוגיקה")}</p>
<p style="font-size:24px;line-height:1.45;color:{SOFT_D};text-align:right">{R("כל דרישה פונקציונלית מקושרת לבדיקה במטריצת העקיבות שבמסמך האפיון")}</p>
<p style="{MONO};font-size:24px;color:{YELLOW};text-align:left">python -m pytest -v</p>
</div>
</div>"""
slides["testing"] = light_section("testing", body, 9, R("הבדיקות משתמשות ב-seed קבוע, ולכן הן יציבות. יש גם בדיקת עשן שמריצה דקה של משחק אקראי על השלבים האמיתיים. את הממשק הגרפי בודקים ידנית לפי תסריט."))


# 9 ── work plan (Gantt, RTL: week 1 on the right) ─────────────────────────
phases = [
    ("מסמך אפיון ודרישות", {1, 2}),
    ("תכנון וארכיטקטורה", {2, 3}),
    ("ליבה: מפה, תנועה ופצצות", {3, 4, 5}),
    ("אויבים, שיפורים ושלבים", {5, 6}),
    ("ממשק, תפריטים ושיאים", {6, 7}),
    ("צלילים ושפות", {6, 7}),
    ("בדיקות אוטומטיות", {3, 4, 5, 6, 7}),
    ("מבחן משתמשים ותיקונים", {7}),
    ("מצגת והגשה", {8}),
]
cells = []
# header row: weeks 8..1 then label column
for w in range(8, 0, -1):
    cells.append(f'<p style="font-size:24px;font-weight:600;color:{BODY};text-align:center">{w}</p>')
cells.append(f'<p style="font-size:24px;font-weight:600;color:{BODY};text-align:right">{R("שבוע")}</p>')
for name, weeks in phases:
    for w in range(8, 0, -1):
        if w in weeks:
            cells.append(f'<div style="height:44px;background:{ORANGE};border-radius:8px"></div>')
        else:
            cells.append(f'<div style="height:44px;background:#ECE4D3;border-radius:8px"></div>')
    cells.append(f'<p style="font-size:26px;color:{INK};text-align:right">{R(name)}</p>')
grid = (
    '<div style="display:grid;grid-template-columns:repeat(8, 1fr) 470px;gap:10px 8px;align-items:center">\n'
    + "\n".join(cells)
    + "\n</div>"
)
body = heading("תוכנית עבודה", "שמונה שבועות, ובדיקות לאורך כל הדרך") + "\n" + grid
slides["plan"] = light_section("plan", body, 10, R("ההנחה היא צוות של 4 ו-8 שבועות, ואפשר להתאים. בדיקות נכתבות במקביל למימוש ולא בסוף. שבוע 8 שמור להגשה ולהדגמה, כמרווח ביטחון."))


# 10 ── team roles ──────────────────────────────────────────────────────────
def role(title, who, duties, files):
    return (
        f'<div style="flex:1;display:flex;flex-direction:column;gap:16px;background:{CARD};padding:36px;border:2px solid {LINE};border-radius:20px">\n'
        f'<p style="font-size:24px;font-weight:600;color:{ORANGE_TXT};text-align:right">{R(who)}</p>\n'
        f'<h3 style="font-size:36px;font-weight:700;line-height:1.2;color:{INK};text-align:right">{R(title)}</h3>\n'
        f'<p style="font-size:26px;line-height:1.45;color:{BODY};text-align:right">{R(duties)}</p>\n'
        f'<p style="{MONO};font-size:24px;line-height:1.5;color:{INK};text-align:right">{files}</p>\n</div>'
    )


body = heading("חלוקת תפקידים", "כל חבר צוות אחראי על שכבה ועל הבדיקות שלה") + f"""
<div style="display:flex;flex-direction:row-reverse;gap:28px">
{role("ניהול ואפיון", "[שם]", "מסמך האפיון, לוח הזמנים, מעקב דרישות והמצגת", "README<br>config.py")}
{role("לוגיקת המשחק", "[שם]", "מודל המשחק, מכונת המצבים, פצצות והתנגשויות", "game.py<br>entities.py<br>grid.py")}
{role("אויבים ושלבים", "[שם]", "בינה מלאכותית של אויבים, פורמט שלבים ומחולל השלבים", "ai.py<br>level.py<br>levels/")}
{role("ממשק ואיכות", "[שם]", "לולאת המשחק, ציור, תפריטים, צלילים, שפות ותשתית הבדיקות", "app.py<br>renderer.py<br>sound.py<br>i18n.py<br>tests/")}
</div>"""
slides["team"] = light_section("team", body, 11, R("להחליף את [שם] בשמות האמיתיים. כל אחד כותב את הבדיקות של המודולים שלו, ובכל שינוי מריצים את כל הבדיקות."))

# 11 ── demo ────────────────────────────────────────────────────────────────
def key(k, label):
    return (
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:12px;background:{DARK2};padding:28px;border-radius:18px">\n'
        f'<p style="{MONO};font-size:36px;font-weight:700;color:{YELLOW};text-align:center">{k}</p>\n'
        f'<p style="font-size:28px;color:{LIGHT};text-align:center">{R(label)}</p>\n</div>'
    )


body = heading("הדגמה", "שלוש פקודות, ומשחקים", dark=True) + f"""
{code_block(["python -m pip install -r requirements.txt", "python main.py", "python -m pytest -v"]).replace('font-size:24px', 'font-size:36px')}
<div style="display:flex;flex-direction:row-reverse;gap:24px">
{key("← ↑ → ↓", "תנועה")}
{key("Space", "הנחת פצצה")}
{key("P / Esc", "עצירה")}
{key("M", "השתקת צלילים")}
{key("Enter", "אישור")}
</div>"""
slides["demo"] = dark_section("demo", body, 12, R("בהדגמה: להחליף לעברית בתפריט, להראות פיצוץ שרשרת, איסוף שיפור, O’Neal שרודף, חשיפת היציאה והזנת שם לטבלת השיאים. אחר כך להריץ את הבדיקות מול הקהל."))

# 12 ── closing (accent statement slide) ───────────────────────────────────
def lesson(n, text):
    return (
        f'<div style="flex:1;display:flex;flex-direction:column;gap:12px;background:#FFA64D;padding:32px;border-radius:20px">\n'
        f'<p style="font-size:44px;font-weight:800;color:{DARK};text-align:right">{n}</p>\n'
        f'<p style="font-size:30px;line-height:1.4;color:{DARK};text-align:right">{R(text)}</p>\n</div>'
    )


slides["closing"] = f"""<section id="closing" data-transition="fade" style="background:{ORANGE};color:{DARK};{FONT};padding:128px 128px 160px;display:flex;flex-direction:column;justify-content:space-between;gap:40px">
<div style="display:flex;flex-direction:column;gap:16px">
<p style="font-size:28px;font-weight:600;color:{DARK};text-align:right">{R("מה למדנו")}</p>
<h2 style="font-size:72px;font-weight:700;line-height:1.1;color:{DARK};text-align:right">{R("תכנון טוב בהתחלה חסך לנו זמן בסוף")}</h2>
</div>
<div style="display:flex;flex-direction:row-reverse;gap:32px">
{lesson("01", "הפרדה בין לוגיקה לתצוגה הפכה את הבדיקות לפשוטות ומהירות")}
{lesson("02", "דרישות עם קריטריון מדיד סגרו ויכוחים לפני שהתחלנו לכתוב קוד")}
{lesson("03", "מטריצת העקיבות הראתה מיד אילו דרישות עוד לא נבדקו")}
</div>
<h1 style="font-size:120px;font-weight:800;line-height:1;color:{DARK};text-align:right">{R("שאלות?")}</h1>
<p style="position:absolute;left:128px;bottom:64px;width:1200px;font-size:24px;color:{DARK};text-align:left">13 / {TOTAL}</p>
<aside>{R("סיכום ושאלות. כדאי להתכונן לשאלות: למה Pygame, איך בדקתם את הממשק, ומה הייתם מוסיפים בגרסה הבאה (מרובה משתתפים, סאונד, עורך שלבים).")}</aside>
</section>
"""

order = ["cover", "product", "rules", "features", "requirements", "architecture", "states",
         "algorithms", "testing", "plan", "team", "demo", "closing"]
assert set(order) == set(slides)
for sid, html in slides.items():
    (OUT / "slides" / f"{sid}.html").write_text(html, encoding="utf-8")

deck = {
    "v": 4,
    "createdOnFiles": {"v": 1, "at": "2026-11-11T18:30:00Z"},
    "lists": "css",
    "title": "Bomberman – מצגת פרויקט ותוכנית עבודה",
    "cover": "cover",
    "order": order,
    "sections": {
        "s1": {"description": "פתיחה: מה בנינו ואיך משחקים", "start": "cover"},
        "s2": {"description": "אפיון ותכנון: דרישות, ארכיטקטורה ומצבים", "start": "requirements"},
        "s3": {"description": "מימוש ובדיקות", "start": "algorithms"},
        "s4": {"description": "תוכנית עבודה, צוות, הדגמה וסיכום", "start": "plan"},
    },
    "faces": {
        "rubik": {"family": "Rubik", "href": "https://fonts.googleapis.com/css2?family=Rubik:wght@300..900&display=swap"},
        "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"},
    },
    "designSystems": [],
}
(OUT / "deck.json").write_text(json.dumps(deck, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok", len(slides))
