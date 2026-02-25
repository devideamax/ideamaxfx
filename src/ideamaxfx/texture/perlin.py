"""Pure numpy 2D Perlin noise generator."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from PIL import Image


def _fade(t: NDArray[np.floating]) -> NDArray[np.floating]:
    """Compute the fade (smootherstep) curve 6t^5 - 15t^4 + 10t^3.

    Args:
        t: Array of values in [0, 1].

    Returns:
        Smoothly interpolated values.
    """
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def _lerp(
    a: NDArray[np.floating],
    b: NDArray[np.floating],
    t: NDArray[np.floating],
) -> NDArray[np.floating]:
    """Linear interpolation between *a* and *b* by factor *t*.

    Args:
        a: Start values.
        b: End values.
        t: Interpolation factor in [0, 1].

    Returns:
        Interpolated values.
    """
    return a + t * (b - a)


def _generate_gradients(
    grid_w: int,
    grid_h: int,
    rng: np.random.Generator,
) -> NDArray[np.floating]:
    """Generate unit gradient vectors at each grid point.

    Args:
        grid_w: Number of grid columns (+ 1 for wrapping).
        grid_h: Number of grid rows (+ 1 for wrapping).
        rng: Numpy random generator instance.

    Returns:
        Array of shape (grid_h, grid_w, 2) with unit gradient vectors.
    """
    angles = rng.uniform(0.0, 2.0 * np.pi, (grid_h, grid_w))
    gradients = np.stack([np.cos(angles), np.sin(angles)], axis=-1)
    return gradients


def _perlin_single_octave(
    width: int,
    height: int,
    scale: float,
    rng: np.random.Generator,
) -> NDArray[np.floating]:
    """Compute a single octave of 2D Perlin noise.

    Args:
        width: Image width in pixels.
        height: Image height in pixels.
        scale: Spatial scale of noise features.
        rng: Numpy random generator instance.

    Returns:
        2D array of noise values roughly in [-1, 1].
    """
    # Number of grid cells along each axis
    grid_w = int(np.ceil(width / scale)) + 2
    grid_h = int(np.ceil(height / scale)) + 2

    gradients = _generate_gradients(grid_w, grid_h, rng)

    # Pixel coordinates mapped to grid space
    x_coords = np.arange(width, dtype=np.float64) / scale
    y_coords = np.arange(height, dtype=np.float64) / scale

    # Grid cell indices for every pixel
    x0 = np.floor(x_coords).astype(int)
    y0 = np.floor(y_coords).astype(int)

    # Fractional position inside each cell
    xf = x_coords - x0.astype(np.float64)
    yf = y_coords - y0.astype(np.float64)

    # Meshgrid versions for broadcasting: shape (height, width)
    x0_grid, y0_grid = np.meshgrid(x0, y0)
    xf_grid, yf_grid = np.meshgrid(xf, yf)

    # Fade curves
    u = _fade(xf_grid)
    v = _fade(yf_grid)

    # Gradient vectors at 4 corners for every pixel
    g00 = gradients[y0_grid, x0_grid]  # (H, W, 2)
    g10 = gradients[y0_grid, x0_grid + 1]
    g01 = gradients[y0_grid + 1, x0_grid]
    g11 = gradients[y0_grid + 1, x0_grid + 1]

    # Distance vectors from each corner to the sample point
    d00 = np.stack([xf_grid, yf_grid], axis=-1)
    d10 = np.stack([xf_grid - 1.0, yf_grid], axis=-1)
    d01 = np.stack([xf_grid, yf_grid - 1.0], axis=-1)
    d11 = np.stack([xf_grid - 1.0, yf_grid - 1.0], axis=-1)

    # Dot products: gradient . distance
    dot00 = np.sum(g00 * d00, axis=-1)
    dot10 = np.sum(g10 * d10, axis=-1)
    dot01 = np.sum(g01 * d01, axis=-1)
    dot11 = np.sum(g11 * d11, axis=-1)

    # Bilinear interpolation with fade curves
    top = _lerp(dot00, dot10, u)
    bottom = _lerp(dot01, dot11, u)
    noise = _lerp(top, bottom, v)

    return noise


def perlin_noise(
    width: int = 512,
    height: int = 512,
    scale: float = 50.0,
    octaves: int = 4,
    seed: int | None = None,
) -> Image.Image:
    """Generate a 2D Perlin noise image using pure numpy.

    Multi-octave support combines layers with halving amplitude and
    doubling frequency to produce fractal-like detail.

    Args:
        width: Output image width in pixels.
        height: Output image height in pixels.
        scale: Base spatial scale (larger = smoother features).
        octaves: Number of noise layers to combine.
        seed: Optional RNG seed for reproducibility.

    Returns:
        Grayscale PIL Image of size (width, height).
    """
    rng = np.random.default_rng(seed)

    noise = np.zeros((height, width), dtype=np.float64)
    amplitude = 1.0
    frequency = 1.0
    max_amplitude = 0.0

    for _ in range(octaves):
        octave_scale = scale / frequency
        # Ensure scale doesn't go below 1 pixel
        if octave_scale < 1.0:
            octave_scale = 1.0
        layer = _perlin_single_octave(width, height, octave_scale, rng)
        noise += amplitude * layer
        max_amplitude += amplitude
        amplitude *= 0.5
        frequency *= 2.0

    # Normalize to [0, 255]
    if max_amplitude > 0.0:
        noise /= max_amplitude

    # Map from roughly [-1, 1] to [0, 255]
    noise_min = noise.min()
    noise_max = noise.max()
    if noise_max - noise_min > 0:
        noise = (noise - noise_min) / (noise_max - noise_min)
    else:
        noise = np.full_like(noise, 0.5)

    pixel_data = (noise * 255.0).clip(0, 255).astype(np.uint8)
    return Image.fromarray(pixel_data, mode="L")
