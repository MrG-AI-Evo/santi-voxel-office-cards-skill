#!/usr/bin/env python3
"""Render approved Chinese copy over separate voxel scenes as opaque PNG cards."""

from __future__ import annotations

import argparse
import json
import re
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, PngImagePlugin


WIDTH = 1080
HEIGHT = 1440
SCENE_HEIGHT = 648
LEFT = 64
RIGHT = 64
TEXT_WIDTH = WIDTH - LEFT - RIGHT
TEXT_TOP = SCENE_HEIGHT + 52
BOTTOM_MARGIN = 60
ASSET_DIR = Path(__file__).resolve().parent.parent / "assets"
REGULAR_FONT = ASSET_DIR / "NotoSansCJKsc-Regular.otf"
BOLD_FONT = ASSET_DIR / "NotoSansCJKsc-Bold.otf"
BLACK = (12, 12, 12)
RED = (213, 18, 22)
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINE_START_FORBIDDEN = set("，。、；：！？）】》’”%")
LINE_END_FORBIDDEN = set("（【《‘“")
PREFERRED_BREAK = set("，、；：。！？")


def read_spec(path: Path) -> tuple[str, list[dict[str, str]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Spec must be a JSON object")
    series = data.get("series_title")
    cards = data.get("cards")
    if not isinstance(series, str) or not series.strip():
        raise ValueError("series_title must be nonempty text")
    if not isinstance(cards, list) or not cards:
        raise ValueError("cards must be a nonempty array")
    seen: set[str] = set()
    for number, card in enumerate(cards, 1):
        if not isinstance(card, dict):
            raise ValueError(f"Card {number} must be an object")
        for field in ("id", "title", "body", "punchline", "scene_image"):
            if not isinstance(card.get(field), str) or not card[field].strip():
                raise ValueError(f"Card {number}: {field} must be nonempty text")
        if not SLUG.fullmatch(card["id"]):
            raise ValueError(f"Card {number}: id must be a lowercase ASCII slug")
        if card["id"] in seen:
            raise ValueError(f"Duplicate card id: {card['id']}")
        seen.add(card["id"])
        if not Path(card["scene_image"]).expanduser().is_file():
            raise ValueError(f"Card {number}: scene_image does not exist")
    return series, cards


def wrap_text(draw: ImageDraw.ImageDraw, value: str, font: ImageFont.FreeTypeFont) -> list[str]:
    """Balance CJK lines without losing characters or orphaning punctuation."""
    lines: list[str] = []
    for paragraph in value.split("\n"):
        if not paragraph:
            lines.append("")
            continue

        n = len(paragraph)

        @lru_cache(maxsize=None)
        def width(start: int, end: int) -> float:
            return draw.textlength(paragraph[start:end], font=font)

        def can_break(end: int) -> bool:
            if end == n:
                return True
            before, after = paragraph[end - 1], paragraph[end]
            if before in LINE_END_FORBIDDEN or after in LINE_START_FORBIDDEN:
                return False
            if before.isascii() and after.isascii() and before.isalnum() and after.isalnum():
                return False
            return True

        @lru_cache(maxsize=None)
        def min_lines(start: int) -> int:
            if start == n:
                return 0
            best = n + 1
            for end in range(start + 1, n + 1):
                if width(start, end) > TEXT_WIDTH:
                    break
                if can_break(end):
                    best = min(best, 1 + min_lines(end))
            return best

        count = min_lines(0)
        if count > n:
            raise ValueError("A word is too wide to fit in the text area")
        target = width(0, n) / count

        @lru_cache(maxsize=None)
        def best_breaks(start: int, remaining: int) -> tuple[float, tuple[int, ...]]:
            if start == n:
                return (0.0, ()) if remaining == 0 else (float("inf"), ())
            if remaining == 0:
                return float("inf"), ()
            best_score = float("inf")
            best_ends: tuple[int, ...] = ()
            for end in range(start + 1, n + 1):
                line_width = width(start, end)
                if line_width > TEXT_WIDTH:
                    break
                if not can_break(end) or min_lines(end) > remaining - 1:
                    continue
                future_score, future_ends = best_breaks(end, remaining - 1)
                bonus = 1500 if end < n and paragraph[end - 1] in PREFERRED_BREAK else 0
                score = (line_width - target) ** 2 - bonus + future_score
                if score < best_score:
                    best_score = score
                    best_ends = (end,) + future_ends
            return best_score, best_ends

        _, ends = best_breaks(0, count)
        start = 0
        for end in ends:
            lines.append(paragraph[start:end])
            start = end
    return lines


def layout_copy(draw: ImageDraw.ImageDraw, series: str, card: dict[str, str]):
    for factor in (1.0, 0.96, 0.92, 0.88, 0.84, 0.80, 0.76):
        font_sizes = {
            "series": round(35 * factor),
            "title": round(70 * factor),
            "body": round(43 * factor),
            "punchline": round(48 * factor),
        }
        fonts = {
            "series": ImageFont.truetype(str(BOLD_FONT), font_sizes["series"]),
            "title": ImageFont.truetype(str(BOLD_FONT), font_sizes["title"]),
            "body": ImageFont.truetype(str(REGULAR_FONT), font_sizes["body"]),
            "punchline": ImageFont.truetype(str(BOLD_FONT), font_sizes["punchline"]),
        }
        lines = {
            "series": wrap_text(draw, series, fonts["series"]),
            "title": wrap_text(draw, card["title"], fonts["title"]),
            "body": wrap_text(draw, card["body"], fonts["body"]),
            "punchline": wrap_text(draw, card["punchline"], fonts["punchline"]),
        }
        if any(len(lines[key]) > limit for key, limit in
               (("series", 1), ("title", 2), ("body", 4), ("punchline", 3))):
            continue
        leading = {key: round(font_sizes[key] * 1.30) for key in font_sizes}
        gap = {"series": 24, "title": 30, "body": 30, "punchline": 0}
        needed = sum(len(lines[key]) * leading[key] + gap[key]
                     for key in ("series", "title", "body", "punchline"))
        if TEXT_TOP + needed <= HEIGHT - BOTTOM_MARGIN:
            return fonts, lines, leading, gap
    raise ValueError(
        f"Text does not fit for card {card['id']}; shorten the approved copy "
        "or use a smaller number of lines"
    )


def render_scene(scene_path: Path) -> Image.Image:
    with Image.open(scene_path) as source:
        scene = ImageOps.exif_transpose(source).convert("RGBA")
    white = Image.new("RGBA", scene.size, (255, 255, 255, 255))
    white.alpha_composite(scene)
    return ImageOps.fit(
        white.convert("RGB"),
        (WIDTH, SCENE_HEIGHT),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )


def render_card(series: str, card: dict[str, str], destination: Path) -> None:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "white")
    canvas.paste(render_scene(Path(card["scene_image"]).expanduser()), (0, 0))
    draw = ImageDraw.Draw(canvas)
    fonts, lines, leading, gap = layout_copy(draw, series, card)
    y = TEXT_TOP
    for key in ("series", "title", "body", "punchline"):
        color = RED if key == "punchline" else BLACK
        for line in lines[key]:
            draw.text((LEFT, y), line, font=fonts[key], fill=color, anchor="lt")
            y += leading[key]
        y += gap[key]
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("series_title", series)
    for field in ("title", "body", "punchline"):
        metadata.add_text(field, card[field])
    canvas.save(destination, format="PNG", pnginfo=metadata, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True, help="UTF-8 JSON card spec")
    parser.add_argument("--output-dir", type=Path, required=True, help="directory for independent PNG files")
    parser.add_argument("--overwrite", action="store_true", help="replace existing card PNGs")
    args = parser.parse_args()
    for font_file in (REGULAR_FONT, BOLD_FONT):
        if not font_file.is_file():
            raise SystemExit(f"Missing bundled font: {font_file}")
    try:
        series, cards = read_spec(args.spec)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        destinations = [args.output_dir / f"{card['id']}.png" for card in cards]
        if not args.overwrite:
            existing = [str(path) for path in destinations if path.exists()]
            if existing:
                raise ValueError("Output exists; use --overwrite or another directory: " + ", ".join(existing))
        for card, destination in zip(cards, destinations):
            render_card(series, card, destination)
            print(destination)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"Render failed: {error}") from error


if __name__ == "__main__":
    main()
