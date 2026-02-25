"""Layer blending modes."""

from __future__ import annotations

import numpy as np
from PIL import Image


def blend(
    base: Image.Image,
    overlay: Image.Image,
    mode: str = "screen",
    opacity: float = 1.0,
) -> Image.Image:
    """Blend two images using a Photoshop-style blending mode.

    Both images are resized to the dimensions of *base* before blending.
    Supported modes:

    * ``"screen"``  -- lightens (``1 - (1-a)(1-b)``).
    * ``"multiply"`` -- darkens (``a * b``).
    * ``"overlay"`` -- contrast-enhancing combination of screen and multiply.
    * ``"soft_light"`` -- softer version of overlay.
    * ``"add"`` -- simple additive blend, clipped to 255.

    Args:
        base: Bottom layer image (any mode; converted to RGB).
        overlay: Top layer image (any mode; converted to RGB and resized
            to match *base*).
        mode: Blending mode name (see list above).
        opacity: Opacity of the overlay layer before blending
            (0.0 = invisible, 1.0 = fully opaque).

    Returns:
        RGB image with the blend applied.

    Raises:
        ValueError: If *mode* is not one of the supported names.
    """
    base = base.convert("RGB")
    overlay = overlay.convert("RGB").resize(base.size, Image.LANCZOS)

    a = np.array(base, dtype=np.float64) / 255.0
    b = np.array(overlay, dtype=np.float64) / 255.0

    # Pre-multiply overlay opacity.
    b = b * opacity

    if mode == "screen":
        result = 1.0 - (1.0 - a) * (1.0 - b)
    elif mode == "multiply":
        result = a * b
    elif mode == "overlay":
        # overlay = 2ab  when a < 0.5 else 1 - 2(1-a)(1-b)
        low = 2.0 * a * b
        high = 1.0 - 2.0 * (1.0 - a) * (1.0 - b)
        result = np.where(a < 0.5, low, high)
    elif mode == "soft_light":
        # Pegtop formula: (1-2b)*a^2 + 2b*a
        result = (1.0 - 2.0 * b) * (a**2) + 2.0 * b * a
    elif mode == "add":
        result = a + b
    else:
        raise ValueError(
            f"Unknown blend mode {mode!r}. "
            f"Choose from 'screen', 'multiply', 'overlay', 'soft_light', 'add'."
        )

    result = np.clip(result * 255.0, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(result, mode="RGB")
