#!/usr/bin/env python3
"""Entry point for the make.fun bounty
"the-picture-that-tastes-of-one-20261122-2047".

Copies the pre-rendered entry.png into /output/entry.png and validates
it first (PNG magic bytes, dimensions 1024x1024, size under 1 MiB).
Pure stdlib - no Pillow, no external dependencies.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST = "/output/entry.png"
MAX_BYTES = 1048576

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    with open(SRC, "rb") as f:
        data = f.read()
    if data[:8] != PNG_MAGIC:
        raise SystemExit("entry.png: bad PNG magic bytes")
    if len(data) > MAX_BYTES:
        raise SystemExit(
            f"entry.png: {len(data)} bytes exceeds 1 MiB limit")
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != (1024, 1024):
        raise SystemExit(
            f"entry.png: expected 1024x1024, got {width}x{height}")
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    with open(DST, "wb") as f:
        f.write(data)
    print(f"wrote {DST} ({len(data)} bytes, {width}x{height})")


if __name__ == "__main__":
    main()
