"""Neon glow text effect — multi-pass gaussian blur."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def neon_text(
    img: Image.Image,
    x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    color: tuple[int, int, int],
    passes: int = 5,
    spread: float = 2.0,
) -> Image.Image:
    """Draw text with a multi-pass neon glow.

    Each pass (from outermost to innermost) renders the text on an RGBA
    layer with low alpha, applies a gaussian blur with a decreasing
    radius, and composites it onto the result.  A final sharp text layer
    at full alpha is drawn on top so the core remains crisp.

    Args:
        img: Base image to draw on.  Not modified in place.
        x: Left edge of the text.
        y: Top edge of the text.
        text: The string to render.
        font: PIL font used for rendering.
        color: RGB colour of the neon glow and core text.
        passes: Number of blur passes (more = softer, wider glow).
        spread: Base blur radius multiplier.  The outermost pass uses
            ``spread * passes`` as its gaussian radius.

    Returns:
        A new ``Image.Image`` with the neon text composited on top.
    """
    result = img.convert("RGBA")
    width, height = result.size

    # --- Glow passes (outermost → innermost) ---------------------------------
    for i in range(passes, 0, -1):
        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        # Alpha decreases for outer passes, increases for inner passes
        alpha = int(255 * (1.0 - (i - 1) / passes) * 0.6)
        alpha = max(alpha, 30)
        draw.text((x, y), text, fill=(*color, alpha), font=font)

        radius = spread * i
        layer = layer.filter(ImageFilter.GaussianBlur(radius=radius))
        result = Image.alpha_composite(result, layer)

    # --- Sharp core text on top ----------------------------------------------
    sharp_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sharp_draw = ImageDraw.Draw(sharp_layer)
    sharp_draw.text((x, y), text, fill=(*color, 255), font=font)
    result = Image.alpha_composite(result, sharp_layer)

    return result
