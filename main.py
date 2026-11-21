#!/usr/bin/env python3
"""
SOLMARA - Isle of the Twin Suns
Travel poster for a place that does not exist.

Entry for make.fun: "The Poster for a Place That Isn't There".
Writes /output/entry.png (PNG, 1024x1024, < 1 MiB).

The poster is drawn entirely in code (Pillow only, no network, no
external assets) in a vintage travel-poster style:
  - a dusk sky that never fully darkens, lit by TWO suns;
  - a faceted crystal spire on a small island - the landmark of Solmara;
  - a calm turquoise lagoon with the suns' light path on the water;
  - the invented place name SOLMARA set large and legible at the top,
    with one short descriptor line beneath it. No quotes, no star
    ratings, no other copy.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = "/output/entry.png"

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, box, top, bottom):
    """Vertical gradient fill of box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    span = max(1, y1 - y0)
    for y in range(y0, y1):
        draw.line([(x0, y), (x1, y)], fill=lerp(top, bottom, (y - y0) / span))


def tracked_text(draw, cx, y, text, font, fill, tracking=0, shadow=None):
    """Draw centred text with letter tracking; returns text height."""
    widths = []
    total = 0
    for ch in text:
        w = draw.textlength(ch, font=font)
        widths.append(w)
        total += w
    total += tracking * (len(text) - 1)
    x = cx - total / 2
    ascent, descent = font.getmetrics()
    if shadow is not None:
        sx = x
        for ch, w in zip(text, widths):
            draw.text((sx + shadow[0], y + shadow[1]), ch, font=font, fill=shadow[2])
            sx += w + tracking
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking
    return ascent + descent


def glow(draw, cx, cy, r, colour, steps=24, alpha_max=90):
    """Soft radial glow: concentric translucent circles on an overlay."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(steps, 0, -1):
        rr = r * i / steps
        a = int(alpha_max * (1 - i / steps) ** 2)
        od.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                   fill=colour + (a,))
    return overlay


def main():
    img = Image.new("RGB", (W, H), (16, 34, 64))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- sky: deep indigo dusk -> warm gold horizon -------------------
    vgrad(d, (0, 0, W, 640), (18, 38, 78), (232, 158, 92))
    # warm band hugging the horizon
    vgrad(d, (0, 520, W, 640), (232, 158, 92), (246, 196, 120))

    # ---- twin suns + glow ---------------------------------------------
    for cx, cy, r, col in ((690, 375, 88, (255, 214, 130)),
                           (835, 415, 55, (255, 178, 102))):
        img.paste(glow(d, cx, cy, r * 3.2, (255, 190, 110)), (0, 0),
                  glow(d, cx, cy, r * 3.2, (255, 190, 110)))
    d = ImageDraw.Draw(img, "RGBA")
    for cx, cy, r, col in ((690, 375, 88, (255, 222, 150)),
                           (835, 415, 55, (255, 190, 110))):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        d.ellipse([cx - r * 0.72, cy - r * 0.72, cx + r * 0.72, cy + r * 0.72],
                  fill=(255, 240, 200))

    # ---- birds ---------------------------------------------------------
    for bx, by, s in ((150, 330, 14), (230, 300, 11), (880, 300, 12),
                      (950, 345, 10)):
        d.arc([bx - s, by - s // 2, bx, by + s // 2], 200, 340,
              fill=(30, 40, 70), width=3)
        d.arc([bx, by - s // 2, bx + s, by + s // 2], 200, 340,
              fill=(30, 40, 70), width=3)

    # ---- far mountains (violet ridge) ----------------------------------
    d.polygon([(0, 640), (120, 520), (260, 600), (420, 500), (560, 590),
               (700, 520), (860, 600), (1024, 540), (1024, 640)],
              fill=(88, 74, 130))
    # snow caps on the two tallest far peaks
    d.polygon([(120, 520), (170, 566), (70, 566)], fill=(250, 235, 220))
    d.polygon([(420, 500), (472, 548), (368, 548)], fill=(250, 235, 220))

    # ---- near ridge (deep teal) ----------------------------------------
    d.polygon([(0, 640), (180, 580), (360, 630), (540, 575), (760, 630),
               (900, 585), (1024, 625), (1024, 640)],
              fill=(28, 74, 88))

    # ---- sea: turquoise -> deep teal -----------------------------------
    vgrad(d, (0, 640, W, 1024), (64, 164, 158), (10, 48, 70))
    # light path of the twin suns on the water
    for i, (y, half, a) in enumerate(
            [(660, 150, 70), (690, 190, 60), (725, 230, 50),
             (765, 270, 42), (810, 300, 34), (860, 330, 26)]):
        d.rectangle([512 - half, y, 512 + half, y + 7],
                    fill=(255, 205, 130, a))
    # gentle wave strokes
    for y in (680, 730, 790, 850, 920, 980):
        for k in range(6):
            x = 60 + k * 165 + (y % 3) * 20
            d.arc([x, y, x + 70, y + 14], 200, 340,
                  fill=(180, 225, 215, 70), width=3)

    # ---- the crystal spire island (the landmark) -----------------------
    ix, iy = 512, 700  # island waterline centre
    # island
    d.ellipse([ix - 190, iy - 26, ix + 190, iy + 26], fill=(16, 52, 58))
    d.ellipse([ix - 190, iy - 26, ix + 190, iy + 6], fill=(24, 78, 72))
    # spire: solid faceted crystal tower (three vertical facets)
    top = (ix, 380)
    base_l, base_r = (ix - 74, 690), (ix + 74, 690)
    foot = (ix, 690)
    d.polygon([top, foot, base_l], fill=(44, 110, 128))     # shaded face
    d.polygon([top, base_r, foot], fill=(150, 220, 225))    # sunlit face
    d.polygon([top, (ix - 20, 690), (ix + 20, 690)],
              fill=(205, 240, 240))                         # bright ridge
    d.polygon([(ix - 42, 690), (ix + 42, 690), (ix + 30, 648),
               (ix - 30, 648)], fill=(120, 190, 200))       # plinth
    # glowing tip
    d.ellipse([ix - 14, 366, ix + 14, 394], fill=(255, 246, 210))
    img.paste(glow(d, ix, 380, 90, (255, 230, 150), alpha_max=70), (0, 0),
              glow(d, ix, 380, 90, (255, 230, 150), alpha_max=70))
    d = ImageDraw.Draw(img, "RGBA")
    # reflection of the spire in the water
    d.polygon([(ix - 46, 712), (ix + 46, 712), (ix + 26, 830),
               (ix - 26, 830)], fill=(150, 210, 210, 60))
    d.polygon([(ix - 20, 712), (ix + 20, 712), (ix + 12, 800),
               (ix - 12, 800)], fill=(220, 245, 240, 70))

    # ---- sailboats ------------------------------------------------------
    for bx, by, s in ((215, 800, 1.0), (820, 845, 0.8)):
        d.polygon([(bx, by - 52 * s), (bx, by - 6 * s),
                   (bx + 34 * s, by - 6 * s)], fill=(250, 240, 220))
        d.polygon([(bx - 4 * s, by - 40 * s), (bx - 4 * s, by - 6 * s),
                   (bx - 26 * s, by - 6 * s)], fill=(230, 200, 170))
        d.line([(bx, by - 54 * s), (bx, by - 4 * s)], fill=(40, 40, 40),
               width=3)
        d.polygon([(bx - 34 * s, by), (bx + 34 * s, by),
                   (bx + 22 * s, by + 12 * s), (bx - 22 * s, by + 12 * s)],
                  fill=(52, 32, 28))

    # ---- foreground headland, bottom-left ------------------------------
    d.polygon([(0, 1024), (0, 880), (150, 830), (330, 880), (430, 950),
               (380, 1024)], fill=(10, 34, 40))
    # stylised cypress trees on the headland
    for tx, ty, s in ((90, 850, 1.0), (150, 838, 1.25), (215, 856, 0.9),
                      (275, 872, 0.75)):
        d.polygon([(tx, ty - 78 * s), (tx - 16 * s, ty),
                   (tx + 16 * s, ty)], fill=(8, 44, 38))
        d.rectangle([tx - 3 * s, ty, tx + 3 * s, ty + 14 * s],
                    fill=(30, 22, 18))
    # tiny lantern glow on the headland
    d.ellipse([296, 892, 308, 904], fill=(255, 220, 140))

    # ---- typography -----------------------------------------------------
    cream = (250, 238, 214)
    name_font = ImageFont.truetype(SERIF_BOLD, 118)
    sub_font = ImageFont.truetype(SANS_BOLD, 30)
    tracked_text(d, W // 2, 78, "SOLMARA", name_font, cream, tracking=26,
                 shadow=(0, 5, (12, 20, 40, 200)))
    # flanking rules
    d.line([(150, 232), (330, 232)], fill=cream, width=3)
    d.line([(694, 232), (874, 232)], fill=cream, width=3)
    d.ellipse([505, 225, 519, 239], fill=cream)
    tracked_text(d, W // 2, 252, "ISLE OF THE TWIN SUNS", sub_font, cream,
                 tracking=10, shadow=(0, 3, (12, 20, 40, 180)))

    # ---- inner frame ----------------------------------------------------
    d.rectangle([26, 26, W - 26, H - 26], outline=(250, 238, 214), width=4)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    main()
