"""Blue noise dither pattern generator."""

from __future__ import annotations

import numpy as np
from PIL import Image


def blue_noise(
    width: int = 512,
    height: int = 512,
    density: float = 0.1,
) -> Image.Image:
    """Generate a blue noise dither pattern.

    Uses a simplified void-and-cluster approach: random candidate points
    are placed and accepted only when they maintain a minimum distance
    from all existing points.  The resulting distribution has fewer
    low-frequency clumps than white noise, making it ideal for dithering.

    Args:
        width: Output image width in pixels.
        height: Output image height in pixels.
        density: Fraction of pixels that should be set (0.0 -- 1.0).
            Higher values produce a denser pattern.

    Returns:
        Grayscale (mode ``L``) PIL image where set pixels are white
        (255) and the background is black (0).
    """
    rng = np.random.default_rng()
    target_count = int(width * height * density)

    # Minimum distance between points (derived from density).
    # For a uniform hex-grid the ideal spacing is sqrt(2 / (density * sqrt(3)))
    # but we use a simpler heuristic for the void-and-cluster approach.
    min_dist = max(1.0, 1.0 / (density**0.5) * 0.7)

    points: list[tuple[float, float]] = []
    coords = np.empty((0, 2), dtype=np.float64)

    max_attempts = target_count * 30  # Safety cap to avoid infinite loops.
    attempts = 0

    while len(points) < target_count and attempts < max_attempts:
        cx = rng.uniform(0, width)
        cy = rng.uniform(0, height)
        attempts += 1

        if coords.shape[0] == 0:
            points.append((cx, cy))
            coords = np.array([[cx, cy]], dtype=np.float64)
            continue

        # Vectorised distance check against all existing points.
        diffs = coords - np.array([cx, cy])
        dists = np.sqrt(np.sum(diffs**2, axis=1))

        if np.all(dists >= min_dist):
            points.append((cx, cy))
            coords = np.vstack([coords, [cx, cy]])

    # Render to a grayscale image.
    canvas = np.zeros((height, width), dtype=np.uint8)
    for px, py in points:
        ix = int(px) % width
        iy = int(py) % height
        canvas[iy, ix] = 255

    return Image.fromarray(canvas, mode="L")
