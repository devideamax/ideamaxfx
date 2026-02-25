"""Bloom (bright-area glow) effect."""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter


def bloom(
    img: Image.Image,
    threshold: int = 200,
    radius: int = 15,
    intensity: float = 0.4,
) -> Image.Image:
    """Add a bloom effect by blurring and screen-blending bright areas.

    Pixels with luminance above *threshold* are isolated, Gaussian-
    blurred to create a halo, and screen-blended back onto the original
    image at the given *intensity*.

    Args:
        img: Source image (any mode; converted to RGB internally).
        threshold: Luminance cutoff (0 -- 255) above which pixels
            contribute to the bloom.
        radius: Gaussian blur radius controlling the bloom spread.
        intensity: Strength of the bloom layer (0.0 = off, 1.0 = full).

    Returns:
        RGB image with bloom applied.
    """
    img = img.convert("RGB")
    arr = np.array(img, dtype=np.float64)

    # Compute per-pixel luminance.
    gray = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]

    # Mask pixels above the brightness threshold.
    mask = (gray > threshold).astype(np.float64)[:, :, np.newaxis]

    # Extract bright-only image, blur it, and scale by intensity.
    bright = (arr * mask).astype(np.uint8)
    bright_img = Image.fromarray(bright, mode="RGB")
    blurred = bright_img.filter(ImageFilter.GaussianBlur(radius=radius))

    blurred_arr = np.array(blurred, dtype=np.float64) * intensity

    # Screen blend: 1 - (1 - base) * (1 - overlay)
    base = arr / 255.0
    overlay = blurred_arr / 255.0
    blended = 1.0 - (1.0 - base) * (1.0 - overlay)

    result = np.clip(blended * 255.0, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(result, mode="RGB")
