"""Duotone colour-mapping effect."""

from __future__ import annotations

import numpy as np
from PIL import Image


def duotone(
    img: Image.Image,
    dark_color: tuple[int, int, int] = (10, 10, 40),
    light_color: tuple[int, int, int] = (255, 200, 50),
) -> Image.Image:
    """Map an image to a two-colour duotone palette.

    The image is first converted to grayscale.  Each pixel's luminance
    is then used to linearly interpolate between *dark_color* (for black)
    and *light_color* (for white).

    Args:
        img: Source image (any mode; converted to grayscale internally).
        dark_color: RGB colour that replaces the darkest tones.
        light_color: RGB colour that replaces the brightest tones.

    Returns:
        RGB image mapped to the duotone palette.
    """
    gray = img.convert("L")
    arr = np.array(gray, dtype=np.float64) / 255.0  # 0..1

    dark = np.array(dark_color, dtype=np.float64)
    light = np.array(light_color, dtype=np.float64)

    # Linear interpolation: dark * (1 - t) + light * t  for each pixel.
    h, w = arr.shape
    t = arr.reshape(h, w, 1)
    result = dark * (1.0 - t) + light * t

    result = np.clip(result, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(result, mode="RGB")
