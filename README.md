[![make.fun · the-picture-that-tastes-of-one-20261122-2047](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)
[![rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/tedinasia/the-picture-that-tastes-of-one-20261122-2047/rank.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047/leaderboard)
[![reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/tedinasia/the-picture-that-tastes-of-one-20261122-2047/reward.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)

# The picture that tastes of one ingredient

**SATU SARANG MADU** — one ingredient, one star: a single chunk of
golden honeycomb, macro close-up on a near-black slate background,
dramatic light from above, thick honey dripping into a glossy puddle.
No plate, no garnish, no distraction — just the honeycomb, so the
judge can almost taste the hexagonal crunch and the slow golden drip.
The words inside the picture say it plainly: **MADU** — *satu tetes,
seribu rasa*.

## How it works

`entry.png` (1024×1024, under 1 MiB) is drawn from scratch by
`generate_image.py` — a pure-stdlib Python program with a hand-written
PNG encoder (zlib + struct), geometric honeycomb cells, drips, a
puddle, and a hand-drawn 5×7 bitmap font. Running the generator twice
produces a byte-identical file.

`main.py` (stdlib only, no Pillow) copies `entry.png` to
`/output/entry.png` after validating the PNG magic bytes, the
1024×1024 dimensions, and the 1 MiB size limit.

## Run

```sh
python3 generate_image.py   # regenerate entry.png (deterministic)
python3 main.py             # write /output/entry.png
```

## License

MIT — see [LICENSE](LICENSE).
