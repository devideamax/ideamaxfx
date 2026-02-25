"""Mirror-reflection composition effect."""

from __future__ import annotations

import numpy as np
from PIL import Image


def mirror_reflection(
    img: Image.Image,
    height_ratio: float = 0.4,
    opacity_start: int = 100,
    opacity_end: int = 0,
    gap: int = 2,
) -> Image.Image:
    """Create a mirror reflection below an image.

    Flips the image vertically, crops it to *height_ratio* of the
    original height, applies a linear gradient alpha (fading from
    *opacity_start* at the top to *opacity_end* at the bottom), and
    pastes the reflection below the original with a small *gap*.

    Args:
        img: Source image (any mode).
        height_ratio: Fraction of the original height used for the
            reflection (0.0-1.0).
        opacity_start: Alpha at the top of the reflection (0-255).
        opacity_end: Alpha at the bottom of the reflection (0-255).
        gap: Pixel gap between the original image and its reflection.

    Returns:
        RGBA image containing the original and its reflection.
    """
    img = img.convert("RGBA")
    w, h = img.size

    # Clamp height_ratio to valid range.
    height_ratio = max(0.0, min(1.0, height_ratio))
    ref_h = max(1, int(h * height_ratio))

    # Flip and crop to the desired reflection height (bottom part of
    # the original becomes the top of the reflection).
    flipped = img.transpose(Image.FLIP_TOP_BOTTOM)
    reflection = flipped.crop((0, 0, w, ref_h))

    # Build a gradient column vector and broadcast across the width.
    gradient_col = np.linspace(opacity_start, opacity_end, ref_h, dtype=np.float64)
    gradient_arr = np.tile(gradient_col[:, np.newaxis], (1, w))

    # Multiply the reflection's existing alpha by the gradient so that
    # already-transparent areas stay transparent.
    ref_arr = np.array(reflection, dtype=np.float64)
    ref_arr[:, :, 3] = ref_arr[:, :, 3] * gradient_arr / 255.0
    ref_arr = np.clip(ref_arr, 0, 255).astype(np.uint8)
    reflection = Image.fromarray(ref_arr, mode="RGBA")

    # Assemble final canvas.
    canvas_h = h + gap + ref_h
    canvas = Image.new("RGBA", (w, canvas_h), (0, 0, 0, 0))
    canvas.paste(img, (0, 0), img)
    canvas.paste(reflection, (0, h + gap), reflection)
    return canvas
