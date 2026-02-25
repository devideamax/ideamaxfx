"""Stat card layout component."""

from __future__ import annotations

from PIL import Image, ImageDraw

from ideamaxfx.utils.fonts import load_font


def stat_card(
    value: str,
    label: str,
    width: int = 280,
    height: int = 120,
    bg_color: tuple[int, int, int] = (20, 24, 33),
    text_color: tuple[int, int, int] = (255, 255, 255),
    accent_color: tuple[int, int, int] = (0, 245, 212),
    accent_height: int = 4,
    font_path: str | None = None,
) -> Image.Image:
    """Create a stat card with a number, label, and accent bar.

    Args:
        value: The main number/stat to display.
        label: Descriptive label below the value.
        width: Card width in pixels.
        height: Card height in pixels.
        bg_color: Background color RGB.
        text_color: Text color RGB.
        accent_color: Accent bar color RGB.
        accent_height: Height of the accent bar at top.
        font_path: Optional path to a .ttf font file.

    Returns:
        PIL Image of the stat card.
    """
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Accent bar at top
    draw.rectangle([0, 0, width, accent_height], fill=accent_color)

    # Value text
    value_font = load_font(size=36, path=font_path)
    label_font = load_font(size=14, path=font_path)

    value_bbox = draw.textbbox((0, 0), value, font=value_font)
    value_w = value_bbox[2] - value_bbox[0]
    value_x = (width - value_w) // 2
    value_y = accent_height + 16

    draw.text((value_x, value_y), value, fill=text_color, font=value_font)

    # Label text
    label_bbox = draw.textbbox((0, 0), label, font=label_font)
    label_w = label_bbox[2] - label_bbox[0]
    label_x = (width - label_w) // 2
    label_y = value_y + (value_bbox[3] - value_bbox[1]) + 8

    muted = tuple(max(0, c - 80) for c in text_color)
    draw.text((label_x, label_y), label, fill=muted, font=label_font)

    return img
