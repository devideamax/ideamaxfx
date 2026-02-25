"""Drop-shadow text effect."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def shadow_text(
    img: Image.Image,
    x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    text_color: tuple[int, int, int] = (255, 255, 255),
    shadow_color: tuple[int, int, int] = (0, 0, 0),
    offset: tuple[int, int] = (3, 3),
    blur_radius: int = 5,
) -> Image.Image:
    """Draw text with a soft drop shadow.

    The shadow is rendered on a separate RGBA layer at the given
    *offset*, blurred with a gaussian filter, and composited beneath
    the crisp main text.

    Args:
        img: Base image to draw on.  Not modified in place.
        x: Left edge of the main text.
        y: Top edge of the main text.
        text: The string to render.
        font: PIL font used for rendering.
        text_color: RGB colour of the main text.
        shadow_color: RGB colour of the shadow.
        offset: ``(dx, dy)`` pixel offset of the shadow relative to
            the main text position.
        blur_radius: Gaussian blur radius applied to the shadow layer.

    Returns:
        A new ``Image.Image`` with the shadowed text composited on top.
    """
    result = img.convert("RGBA")
    width, height = result.size

    # --- Shadow layer --------------------------------------------------------
    shadow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_draw.text(
        (x + offset[0], y + offset[1]),
        text,
        fill=(*shadow_color, 255),
        font=font,
    )

    if blur_radius > 0:
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    result = Image.alpha_composite(result, shadow_layer)

    # --- Main text layer -----------------------------------------------------
    text_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)
    text_draw.text((x, y), text, fill=(*text_color, 255), font=font)
    result = Image.alpha_composite(result, text_layer)

    return result
