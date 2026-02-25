"""Gradient text effect — CSS background-clip equivalent."""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def gradient_text(
    img: Image.Image,
    x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    color_start: tuple[int, int, int],
    color_end: tuple[int, int, int],
    direction: str = "horizontal",
) -> Image.Image:
    """Draw text filled with a linear gradient.

    Works like CSS ``background-clip: text``.  A white-on-black mask is
    rendered from the text, a gradient image is built by lerping between
    *color_start* and *color_end*, and ``Image.composite`` reveals the
    gradient only where the mask is white.

    Args:
        img: Base image to draw on.  Not modified in place.
        x: Left edge of the text.
        y: Top edge of the text.
        text: The string to render.
        font: PIL font used for rendering.
        color_start: RGB colour at the start of the gradient.
        color_end: RGB colour at the end of the gradient.
        direction: ``"horizontal"`` (left-to-right) or ``"vertical"``
            (top-to-bottom).

    Returns:
        A new ``Image.Image`` with the gradient text composited on top.

    Raises:
        ValueError: If *direction* is not ``"horizontal"`` or
            ``"vertical"``.
    """
    if direction not in ("horizontal", "vertical"):
        raise ValueError(f"direction must be 'horizontal' or 'vertical', got {direction!r}")

    result = img.convert("RGBA")
    width, height = result.size

    # --- 1. Draw text as white on black mask ---------------------------------
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((x, y), text, fill=255, font=font)

    # --- 2. Build gradient image (lerp between colors) -----------------------
    grad_arr = np.zeros((height, width, 4), dtype=np.uint8)
    if direction == "horizontal":
        for ch in range(3):
            grad_arr[:, :, ch] = np.linspace(
                color_start[ch], color_end[ch], width
            ).astype(np.uint8)[np.newaxis, :]
    else:
        for ch in range(3):
            col = np.linspace(color_start[ch], color_end[ch], height).astype(np.uint8)
            grad_arr[:, :, ch] = col[:, np.newaxis]
    grad_arr[:, :, 3] = 255
    gradient = Image.fromarray(grad_arr, "RGBA")

    # --- 3. Composite: gradient visible only where mask is white -------------
    transparent = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    text_layer = Image.composite(gradient, transparent, mask)
    result = Image.alpha_composite(result, text_layer)

    return result
