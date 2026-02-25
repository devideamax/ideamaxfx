"""Colour-overlay composition effect."""

from __future__ import annotations

import numpy as np
from PIL import Image


def color_overlay(
    img: Image.Image,
    color: tuple[int, int, int] = (0, 0, 0),
    opacity: float = 0.3,
    mode: str = "normal",
) -> Image.Image:
    """Apply a colour overlay to an image.

    Supports three blend modes:

    * **normal** -- simple alpha blend between the image and a solid
      colour layer.
    * **multiply** -- ``result = image * overlay / 255``.
    * **screen** -- ``result = 255 - (255 - image) * (255 - overlay) / 255``.

    Args:
        img: Source image (any mode).
        color: RGB colour for the overlay.
        opacity: Blend strength (0.0 = no effect, 1.0 = full overlay).
        mode: Blend mode -- one of ``"normal"``, ``"multiply"``, or
            ``"screen"``.

    Returns:
        RGBA image with the overlay applied.

    Raises:
        ValueError: If *mode* is not one of the supported values.
    """
    supported_modes = ("normal", "multiply", "screen")
    if mode not in supported_modes:
        raise ValueError(f"Unsupported blend mode {mode!r}. Choose from {supported_modes!r}.")

    img = img.convert("RGBA")
    opacity = max(0.0, min(1.0, opacity))

    # Separate alpha so we can preserve it unchanged.
    arr = np.array(img, dtype=np.float64)
    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3]

    overlay = np.full_like(rgb, color, dtype=np.float64)

    if mode == "normal":
        blended = rgb * (1.0 - opacity) + overlay * opacity

    elif mode == "multiply":
        multiplied = rgb * overlay / 255.0
        blended = rgb * (1.0 - opacity) + multiplied * opacity

    elif mode == "screen":
        screened = 255.0 - (255.0 - rgb) * (255.0 - overlay) / 255.0
        blended = rgb * (1.0 - opacity) + screened * opacity

    # Reassemble with original alpha.
    result = np.dstack([blended, alpha])
    result = np.clip(result, 0, 255).astype(np.uint8)
    return Image.fromarray(result, mode="RGBA")
