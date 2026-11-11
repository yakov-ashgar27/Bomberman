"""Right-to-left text support.

pygame draws text strictly left to right, so Hebrew would come out backwards.
to_visual() reorders a logical string (the order it is typed/stored in) into
the visual order pygame must draw, following the core of the Unicode bidi
algorithm for a right-to-left paragraph:

* Hebrew letters form right-to-left runs (characters reversed).
* Latin letters and digits form left-to-right runs (kept as they are), so
  "Python 3.13" or "1/5" stay readable inside a Hebrew sentence.
* Spaces and punctuation between two left-to-right runs join them; elsewhere
  they follow the paragraph direction (right to left).
* The runs are then laid out from right to left, and brackets are mirrored.
"""
from __future__ import annotations

MIRROR = {"(": ")", ")": "(", "[": "]", "]": "[", "{": "}", "}": "{", "<": ">", ">": "<"}


def is_rtl(ch: str) -> bool:
    code = ord(ch)
    return 0x0590 <= code <= 0x05FF or 0xFB1D <= code <= 0xFB4F


def is_ltr(ch: str) -> bool:
    return ch.isalnum() and not is_rtl(ch)


def has_rtl(text: str) -> bool:
    return any(is_rtl(ch) for ch in text)


def to_visual(text: str) -> str:
    if not has_rtl(text):
        return text

    kinds = ["R" if is_rtl(c) else "L" if is_ltr(c) else "N" for c in text]

    # Resolve neutrals: between two L's they become L, otherwise R.
    resolved = kinds[:]
    i = 0
    while i < len(kinds):
        if kinds[i] != "N":
            i += 1
            continue
        j = i
        while j < len(kinds) and kinds[j] == "N":
            j += 1
        before = kinds[i - 1] if i > 0 else "R"
        after = kinds[j] if j < len(kinds) else "R"
        fill = "L" if before == after == "L" else "R"
        for k in range(i, j):
            resolved[k] = fill
        i = j

    # Group into runs of one direction.
    runs: list[tuple[str, str]] = []
    for ch, kind in zip(text, resolved):
        if runs and runs[-1][0] == kind:
            runs[-1] = (kind, runs[-1][1] + ch)
        else:
            runs.append((kind, ch))

    out = []
    for kind, chunk in reversed(runs):
        if kind == "R":
            out.append("".join(MIRROR.get(c, c) for c in reversed(chunk)))
        else:
            out.append(chunk)
    return "".join(out)
