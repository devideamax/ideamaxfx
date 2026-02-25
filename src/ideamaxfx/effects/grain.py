"""Film grain noise effect."""

from __future__ import annotations

import numpy as np
from PIL import Image


def grain(
    img: Image.Image,
    intensity: float = 0.06,
    monochrome: bool = True,
) -> Image.Image:
    """Add film grain noise to an image.

    Generates random noise scaled by *intensity* and blends it additively
    onto the source image.  When *monochrome* is ``True`` the same noise
    value is applied to every colour channel, producing neutral grain
    similar to analogue film.

    Args:
        img: Source image (any mode; will be converted to RGB).
        intensity: Noise strength as a fraction of the full dynamic range
            (0.0 = no grain, 1.0 = maximum noise).  Defaults to 0.06.
        monochrome: If ``True`` each pixel receives the same noise on all
            channels.  If ``False`` each channel gets independent noise.

    Returns:
        RGB image with film grain applied.
    """
    img = img.convert("RGB")
    arr = np.array(img, dtype=np.float64)
    h, w, c = arr.shape

    rng = np.random.default_rng()
    scale = intensity * 255.0

    if monochrome:
        noise = rng.standard_normal((h, w, 1)) * scale
        noise = np.repeat(noise, c, axis=2)
    else:
        noise = rng.standard_normal((h, w, c)) * scale

    result = np.clip(arr + noise, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(result, mode="RGB")
