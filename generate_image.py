#!/usr/bin/env python3
"""Generate entry.png for the make.fun bounty
"the-picture-that-tastes-of-one-20261122-2047".

Concept: "SATU SARANG MADU" - one golden honeycomb chunk, macro
close-up on a near-black slate background, dramatic top light, thick
honey dripping. Pure stdlib (zlib + struct + math). Fully
deterministic: same input -> byte-identical output.
"""
import math
import os
import struct
import sys
import zlib

W = H = 1024

# ---------------------------------------------------------------- palette
BG_TOP = (24, 22, 28)
BG_BOT = (8, 8, 11)
WAX = (110, 66, 8)          # dark honeycomb wax rim
WAX_DARK = (74, 44, 6)
HONEY = (232, 160, 32)      # base honey amber
HONEY_LIGHT = (255, 201, 60)
HONEY_DEEP = (185, 106, 0)
OPEN_CELL = (122, 74, 8)    # empty cell interior
OPEN_DEEP = (82, 48, 4)
DRIP = (240, 168, 24)
DRIP_LIGHT = (255, 211, 77)
PUDDLE = (226, 150, 20)
PUDDLE_LIGHT = (245, 180, 40)
RIM = (255, 205, 80)
SPEC = (255, 240, 200)      # specular glint
TEXT_GOLD = (255, 217, 122)
TEXT_SHADOW = (122, 74, 0)
SPARKLE = (255, 230, 160)


def clamp(v):
    return 0 if v < 0 else 255 if v > 255 else int(v)


def shade(color, factor):
    return (clamp(color[0] * factor), clamp(color[1] * factor),
            clamp(color[2] * factor))


# ---------------------------------------------------------------- canvas
pixels = [bytearray(W * 3) for _ in range(H)]


def fill_rect(x0, y0, x1, y1, color):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W - 1, x1)
    y1 = min(H - 1, y1)
    r, g, b = color
    for y in range(y0, y1 + 1):
        row = pixels[y]
        for x in range(x0, x1 + 1):
            i = x * 3
            row[i] = r
            row[i + 1] = g
            row[i + 2] = b


def fill_poly(pts, color):
    """Scanline fill of a simple polygon (list of (x, y) ints)."""
    ys = [p[1] for p in pts]
    y0 = max(0, min(ys))
    y1 = min(H - 1, max(ys))
    n = len(pts)
    r, g, b = color
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x1, y1p = pts[i]
            x2, y2p = pts[(i + 1) % n]
            if (y1p <= y < y2p) or (y2p <= y < y1p):
                xs.append(x1 + (y - y1p) * (x2 - x1) / (y2p - y1p))
        if len(xs) < 2:
            continue
        xs.sort()
        row = pixels[y]
        for k in range(0, len(xs) - 1, 2):
            xa = max(0, int(xs[k] + 0.5))
            xb = min(W - 1, int(xs[k + 1] + 0.5))
            for x in range(xa, xb + 1):
                i = x * 3
                row[i] = r
                row[i + 1] = g
                row[i + 2] = b


def fill_ellipse(cx, cy, rx, ry, color):
    r, g, b = color
    y0 = max(0, int(cy - ry))
    y1 = min(H - 1, int(cy + ry))
    for y in range(y0, y1 + 1):
        dy = (y - cy) / ry
        rem = 1.0 - dy * dy
        if rem < 0:
            continue
        dx = rx * math.sqrt(rem)
        xa = max(0, int(cx - dx + 0.5))
        xb = min(W - 1, int(cx + dx + 0.5))
        row = pixels[y]
        for x in range(xa, xb + 1):
            i = x * 3
            row[i] = r
            row[i + 1] = g
            row[i + 2] = b


def hex_points(cx, cy, r):
    return [(int(cx + r * math.cos(math.radians(60 * k))),
             int(cy + r * math.sin(math.radians(60 * k))))
            for k in range(6)]


# ---------------------------------------------------------------- background
# Vertical gradient + warm amber glow from above + darkened edges.
for y in range(H):
    t = y / (H - 1)
    br = BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t
    bg = BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t
    bb = BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t
    row = pixels[y]
    dy = y - 380
    for x in range(W):
        dx = x - 512
        d = math.sqrt(dx * dx + dy * dy)
        g = max(0.0, 1.0 - d / 650.0)
        g = g * g
        dc = math.sqrt(dx * dx + (y - 512) * (y - 512)) / 724.0
        edge = 1.0
        if dc > 0.55:
            edge = 1.0 - 0.30 * (dc - 0.55) / 0.45
        i = x * 3
        row[i] = clamp((br + 72 * g) * edge)
        row[i + 1] = clamp((bg + 40 * g) * edge)
        row[i + 2] = clamp((bb + 7 * g) * edge)


# ---------------------------------------------------------------- honeycomb
# One big chunk: flat-top hex cells inside an ellipse, light from top.
COMB_CX, COMB_CY = 512, 540
COMB_RX, COMB_RY = 305, 225
HEX_R = 58
SQ3 = math.sqrt(3.0)


def cell_hash(col, row):
    return ((col * 73856093) ^ (row * 19349663)) & 0xFFFF


for col in range(-4, 5):
    for row in range(-3, 4):
        cx = COMB_CX + 1.5 * HEX_R * col
        cy = COMB_CY + SQ3 * HEX_R * (row + 0.5 * (col & 1))
        nx = (cx - COMB_CX) / COMB_RX
        ny = (cy - COMB_CY) / COMB_RY
        if nx * nx + ny * ny > 0.98:
            continue
        # light falls from the top-left: brighter up high, dimmer low/out
        light = 1.15 - 0.50 * ((cy - 315) / 450.0) - 0.18 * abs(cx - 512) / 310.0
        light = max(0.50, min(1.15, light))
        h = cell_hash(col, row)
        is_open = h % 4 == 0  # ~25% of cells are empty (dark, deep)
        # wax rim: outer hex dark, inner hex honey
        fill_poly(hex_points(cx, cy, HEX_R), WAX_DARK)
        fill_poly(hex_points(cx, cy, HEX_R * 0.93), shade(WAX, light))
        if is_open:
            fill_poly(hex_points(cx, cy, HEX_R * 0.80), shade(OPEN_CELL, light))
            fill_poly(hex_points(cx, cy, HEX_R * 0.55),
                      shade(OPEN_DEEP, light))
            # thin bright rim on the top edge of the empty cell
            fill_poly(hex_points(cx - 4, cy - 8, HEX_R * 0.80),
                      shade((150, 95, 14), light))
            fill_poly(hex_points(cx - 4, cy - 8, HEX_R * 0.72),
                      shade(OPEN_CELL, light))
        else:
            fill_poly(hex_points(cx, cy, HEX_R * 0.80),
                      shade(HONEY, light))
            fill_poly(hex_points(cx, cy, HEX_R * 0.62),
                      shade(HONEY_LIGHT, light * 0.98))
            # specular glint, top-left of the cell
            fill_ellipse(int(cx - 14), int(cy - 16), 9, 6,
                         shade(SPEC, min(1.0, light + 0.1)))


# ---------------------------------------------------------------- drips
def drip(x, y_top, y_end, width):
    """A thick honey drip hanging from the comb: tapered strand + bulb."""
    top_half = width // 2
    bot_half = max(10, width // 2 - 8)
    fill_poly([(x - top_half, int(y_top)), (x + top_half, int(y_top)),
               (x + bot_half, int(y_end)), (x - bot_half, int(y_end))],
              DRIP)
    fill_poly([(x - top_half + 5, int(y_top) + 6),
               (x - top_half + 12, int(y_top) + 6),
               (x - bot_half + 7, int(y_end) - 8),
               (x - bot_half + 2, int(y_end) - 8)], DRIP_LIGHT)
    fill_ellipse(x, int(y_end), bot_half + 10, bot_half + 12, DRIP)
    fill_ellipse(x - 8, int(y_end) - 4, 7, 10, DRIP_LIGHT)
    fill_ellipse(x - 8, int(y_end) - 4, 3, 5, SPEC)


drip(400, 736, 872, 34)
drip(512, 752, 884, 40)
drip(624, 736, 868, 32)

# falling droplet on a thin strand, right side
fill_rect(708, 700, 716, 852, DRIP)
fill_ellipse(712, 872, 19, 22, DRIP)
fill_ellipse(706, 866, 6, 9, DRIP_LIGHT)
fill_ellipse(706, 866, 2, 4, SPEC)

# ---------------------------------------------------------------- puddle
fill_ellipse(512, 930, 275, 36, PUDDLE)
fill_ellipse(512, 924, 250, 28, PUDDLE_LIGHT)
fill_ellipse(512, 914, 230, 13, RIM)
fill_ellipse(430, 918, 52, 7, SPEC)
fill_ellipse(610, 926, 34, 5, SPEC)

# ---------------------------------------------------------------- sparkles
def sparkle(cx, cy, s):
    fill_rect(cx - 1, cy - s, cx + 1, cy + s, SPARKLE)
    fill_rect(cx - s, cy - 1, cx + s, cy + 1, SPARKLE)


sparkle(300, 300, 9)
sparkle(742, 330, 7)
sparkle(832, 620, 8)
sparkle(208, 642, 6)
sparkle(688, 262, 5)

# ---------------------------------------------------------------- text
# 5x7 bitmap font, drawn by hand (only the glyphs we need).
FONT = {
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "s": ["00000", "00000", "01111", "10000", "01110", "00001", "11110"],
    "a": ["00000", "00000", "01110", "00001", "01111", "10001", "01111"],
    "t": ["00100", "00100", "01110", "00100", "00100", "00100", "00010"],
    "u": ["00000", "00000", "10001", "10001", "10001", "10011", "01101"],
    "e": ["00000", "00000", "01110", "10001", "11111", "10000", "01110"],
    "r": ["00000", "00000", "10110", "11001", "10000", "10000", "10000"],
    "i": ["00100", "00000", "01100", "00100", "00100", "00100", "01110"],
    "b": ["10000", "10000", "11110", "10001", "10001", "10001", "11110"],
    ",": ["00000", "00000", "00000", "00000", "00000", "00100", "01000"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
}


def draw_text(text, x0, y0, scale, color, shadow=None):
    if shadow is not None:
        draw_text(text, x0 + 3, y0 + 4, scale, shadow)
    x = x0
    for ch in text:
        glyph = FONT[ch]
        for gy, rowbits in enumerate(glyph):
            for gx, bit in enumerate(rowbits):
                if bit == "1":
                    fill_rect(x + gx * scale, y0 + gy * scale,
                              x + gx * scale + scale - 1,
                              y0 + gy * scale + scale - 1, color)
        x += 5 * scale + scale  # glyph width + one cell spacing


def text_width(text, scale):
    return len(text) * 5 * scale + (len(text) - 1) * scale


TITLE = "MADU"
SUB = "satu tetes, seribu rasa"
tw = text_width(TITLE, 13)
draw_text(TITLE, (W - tw) // 2, 58, 13, TEXT_GOLD, shadow=TEXT_SHADOW)
sw = text_width(SUB, 4)
draw_text(SUB, (W - sw) // 2, 170, 4, (232, 182, 74), shadow=(90, 55, 0))
# thin gold rule under the subtitle
fill_rect((W - 200) // 2, 212, (W + 200) // 2, 214, HONEY)

# ---------------------------------------------------------------- PNG encode
def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += pixels[y]
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", compressed) + chunk(b"IEND", b""))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    data = png_bytes()
    with open(out, "wb") as f:
        f.write(data)
    print(f"wrote {out}: {len(data)} bytes")


if __name__ == "__main__":
    main()
