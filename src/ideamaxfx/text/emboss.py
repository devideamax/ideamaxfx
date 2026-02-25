"""Embossed (3-D) text effect."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont


def _lighten(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    """Return *color* with each channel increased by *amount*, clamped to 255.

    Args:
        color: Base RGB colour.
        amount: Value to add to each channel.

    Returns:
        A new RGB tuple with lightened values.
    """
    return (
        min(color[0] + amount, 255),
        min(color[1] + amount, 255),
        min(color[2] + amount, 255),
    )


def _darken(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    """Return *color* with each channel decreased by *amount*, clamped to 0.

    Args:
        color: Base RGB colour.
        amount: Value to subtract from each channel.

    Returns:
        A new RGB tuple with darkened values.
    """
    return (
        max(color[0] - amount, 0),
        max(color[1] - amount, 0),
        max(color[2] - amount, 0),
    )


def emboss_text(
    img: Image.Image,
    x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    color: tuple[int, int, int] = (200, 200, 200),
    depth: int = 2,
) -> Image.Image:
    """Draw text with a 3-D embossed appearance.

    Three text layers are composited:

    1. **Highlight** — drawn at ``(x - depth, y - depth)`` in a
       lightened variant of *color*, simulating a top-left light source.
    2. **Shadow** — drawn at ``(x + depth, y + depth)`` in a darkened
       variant of *color*, simulating the bottom-right shadow.
    3. **Face** — drawn at the exact ``(x, y)`` position in *color*.

    Args:
        img: Base image to draw on.  Not modified in place.
        x: Left edge of the main text.
        y: Top edge of the main text.
        text: The string to render.
        font: PIL font used for rendering.
        color: RGB base colour of the embossed text face.
        depth: Pixel offset for highlight and shadow layers.

    Returns:
        A new ``Image.Image`` with the embossed text composited on top.
    """
    result = img.convert("RGBA")
    width, height = result.size

    highlight_color = _lighten(color, 80)
    shadow_color = _darken(color, 80)

    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # --- Highlight (top-left offset) -----------------------------------------
    draw.text(
        (x - depth, y - depth),
        text,
        fill=(*highlight_color, 255),
        font=font,
    )

    # --- Shadow (bottom-right offset) ----------------------------------------
    draw.text(
        (x + depth, y + depth),
        text,
        fill=(*shadow_color, 255),
        font=font,
    )

    # --- Main face text on top -----------------------------------------------
    draw.text((x, y), text, fill=(*color, 255), font=font)

    result = Image.alpha_composite(result, layer)
    return result
