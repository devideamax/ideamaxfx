"""Outlined text effect — stroke around text glyphs."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont


def outline_text(
    img: Image.Image,
    x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill_color: tuple[int, int, int] = (255, 255, 255),
    outline_color: tuple[int, int, int] = (0, 0, 0),
    outline_width: int = 2,
) -> Image.Image:
    """Draw text with a uniform outline (stroke).

    The outline is created by drawing the text multiple times, offset in
    all 8 cardinal and diagonal directions at *outline_width* distance,
    using *outline_color*.  A single draw at the exact position with
    *fill_color* is placed on top so the interior is clean.

    Args:
        img: Base image to draw on.  Not modified in place.
        x: Left edge of the text.
        y: Top edge of the text.
        text: The string to render.
        font: PIL font used for rendering.
        fill_color: RGB colour of the main text face.
        outline_color: RGB colour of the outline stroke.
        outline_width: Pixel distance for each outline offset.

    Returns:
        A new ``Image.Image`` with the outlined text composited on top.
    """
    result = img.convert("RGBA")
    layer = Image.new("RGBA", result.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # --- 8 cardinal + diagonal offsets at outline_width distance -------------
    offsets: list[tuple[int, int]] = []
    for dx in (-outline_width, 0, outline_width):
        for dy in (-outline_width, 0, outline_width):
            if dx == 0 and dy == 0:
                continue
            offsets.append((dx, dy))

    # Draw outline copies
    for dx, dy in offsets:
        draw.text((x + dx, y + dy), text, fill=(*outline_color, 255), font=font)

    # Draw main text on top
    draw.text((x, y), text, fill=(*fill_color, 255), font=font)

    result = Image.alpha_composite(result, layer)
    return result
