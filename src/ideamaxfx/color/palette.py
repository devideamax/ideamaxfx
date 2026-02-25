"""Dominant-colour palette extraction from images using k-means clustering."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from PIL import Image


def _downsample(image: Image.Image, max_width: int = 200) -> Image.Image:
    """Resize *image* so its width is at most *max_width* (keeping aspect ratio).

    Args:
        image: A PIL ``Image`` instance.
        max_width: Maximum allowed width in pixels.

    Returns:
        The (possibly resized) image.
    """
    if image.width <= max_width:
        return image
    ratio = max_width / image.width
    new_height = max(1, round(image.height * ratio))
    return image.resize((max_width, new_height))


def _kmeans(
    pixels: np.ndarray,
    k: int,
    max_iterations: int = 20,
    seed: int = 42,
) -> np.ndarray:
    """Run simple k-means on an (N, 3) array of pixel values.

    Args:
        pixels: An ``(N, 3)`` float array of RGB values.
        k: Number of clusters.
        max_iterations: Maximum optimisation iterations.
        seed: Random seed for reproducible centroid initialisation.

    Returns:
        A ``(k, 3)`` float array of cluster centroids.
    """
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(pixels), size=k, replace=False)
    centroids = pixels[indices].astype(np.float64)

    for _ in range(max_iterations):
        # Assign each pixel to the nearest centroid.
        diffs = pixels[:, np.newaxis, :] - centroids[np.newaxis, :, :]
        distances = np.sum(diffs**2, axis=2)
        labels = np.argmin(distances, axis=1)

        # Recompute centroids.
        new_centroids = np.empty_like(centroids)
        for j in range(k):
            members = pixels[labels == j]
            if len(members) == 0:
                new_centroids[j] = centroids[j]
            else:
                new_centroids[j] = members.mean(axis=0)

        if np.allclose(centroids, new_centroids, atol=0.5):
            break
        centroids = new_centroids

    return centroids


def extract_palette(
    image: Image.Image,
    n_colors: int = 5,
) -> list[tuple[int, int, int]]:
    """Extract the *n_colors* most dominant colours from an image.

    The image is first downsampled to a maximum width of 200 px for speed,
    then a lightweight numpy-based k-means is run on the pixel data.

    Args:
        image: A PIL ``Image`` instance (any mode; converted to RGB
            internally).
        n_colors: Number of dominant colours to extract.  Defaults to 5.

    Returns:
        A list of ``(r, g, b)`` tuples sorted by cluster size
        (most dominant first).
    """
    if n_colors < 1:
        raise ValueError(f"n_colors must be >= 1, got {n_colors}")

    img = _downsample(image.convert("RGB"))
    pixels = np.asarray(img).reshape(-1, 3).astype(np.float64)

    if len(pixels) < n_colors:
        n_colors = len(pixels)

    unique_count = len(np.unique(pixels, axis=0))
    n_colors = min(n_colors, unique_count)
    if n_colors == 0:
        return []

    centroids = _kmeans(pixels, k=n_colors)

    # Sort by cluster size (most dominant first).
    diffs = pixels[:, np.newaxis, :] - centroids[np.newaxis, :, :]
    distances = np.sum(diffs**2, axis=2)
    labels = np.argmin(distances, axis=1)
    counts = np.bincount(labels, minlength=n_colors)
    order = np.argsort(-counts)

    return [
        (
            int(round(centroids[idx][0])),
            int(round(centroids[idx][1])),
            int(round(centroids[idx][2])),
        )
        for idx in order
    ]
