"""Local render of the slide files with Playwright (an approximation of the real viewer): one PNG per slide + a PDF.

Run: pip install playwright && playwright install chromium && python render_pdf.py
"""
import json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

DECK = Path(__file__).resolve().parent
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent / "build")); OUT.mkdir(parents=True, exist_ok=True)
order = json.loads((DECK / "deck.json").read_text(encoding="utf-8"))["order"]

ARROWS = {"arrow-left": "M100 20 L40 20 L40 0 L0 50 L40 100 L40 80 L100 80 Z",
          "arrow-down": "M20 0 L80 0 L80 60 L100 60 L50 100 L0 60 L20 60 Z",
          "arrow-right": "M0 20 L60 20 L60 0 L100 50 L60 100 L60 80 L0 80 Z"}
def shapes(html):
    def shape(m):
        kind, style = m.group(1), m.group(2)
        color = re.search(r"background:([^;]+)", style).group(1)
        w = re.search(r"width:(\d+)px", style).group(1); h = re.search(r"height:(\d+)px", style).group(1)
        return (f'<svg width="{w}" height="{h}" viewBox="0 0 100 100" preserveAspectRatio="none">'
                f'<path d="{ARROWS.get(kind, "")}" fill="{color}"/></svg>')
    html = re.sub(r'<x-shape kind="([^"]+)" style="([^"]+)"></x-shape>', shape, html)
    def icon(m):
        style = m.group(2); color = re.search(r"color:([^;]+)", style).group(1)
        return f'<div style="width:64px;height:64px;border-radius:50%;border:6px solid {color};box-sizing:border-box"></div>'
    return re.sub(r'<x-icon name="([^"]+)" style="([^"]+)"></x-icon>', icon, html)

page_css = ("*{margin:0;padding:0;box-sizing:border-box} body{width:1920px} "
            "section{width:1920px;height:1080px;position:relative;overflow:hidden;page-break-after:always} "
            "aside{display:none} table{border-collapse:collapse;width:100%} td,th{border-bottom:1px solid #d9d0bd;padding:.35em .6em}")
sections = [shapes((DECK / "slides" / f"{sid}.html").read_text(encoding="utf-8")) for sid in order]
html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{page_css}</style></head><body>{''.join(sections)}</body></html>"
(OUT / "deck.html").write_text(html, encoding="utf-8")
with sync_playwright() as pw:
    b = pw.chromium.launch()
    p = b.new_page(viewport={"width": 1920, "height": 1080})
    p.goto((OUT / "deck.html").as_uri())
    for i, sid in enumerate(order, 1):
        p.locator("section").nth(i - 1).screenshot(path=str(OUT / f"{i:02d}-{sid}.png"))
    p.pdf(path=str(OUT / "presentation.pdf"), width="1920px", height="1080px", print_background=True)
    b.close()
print("rendered", len(order))
