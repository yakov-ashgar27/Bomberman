"""Draw the game icon (a bomb with a lit fuse) and save it as assets/bomberman.ico.

Run: python tools/make_icon.py   (needs Pillow; the .ico is committed, so players don't need this)
"""
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "bomberman.ico"
S = 256


def draw() -> Image.Image:
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((8, 8, S - 8, S - 8), radius=48, fill=(20, 26, 46, 255))      # dark tile
    d.ellipse((44, 72, 204, 232), fill=(10, 12, 22, 255), outline=(70, 82, 120, 255), width=8)  # bomb
    d.ellipse((78, 104, 118, 144), fill=(60, 70, 104, 255))                               # shine
    d.polygon([(150, 70), (178, 52), (196, 80), (168, 98)], fill=(70, 82, 120, 255))     # cap
    d.line([(186, 64), (206, 38), (224, 34)], fill=(222, 204, 160, 255), width=10)       # fuse
    star = [(226, 8), (234, 26), (252, 24), (240, 38), (250, 54), (232, 48), (222, 64), (218, 46), (200, 42), (214, 30)]
    d.polygon(star, fill=(255, 138, 31, 255))                                             # spark
    d.ellipse((216, 26, 236, 46), fill=(255, 212, 71, 255))
    return img


if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    draw().save(OUT, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("saved", OUT)
