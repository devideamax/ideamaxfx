"""Shared test fixtures for ideamaxfx."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def sample_image() -> Image.Image:
    """Create a 200x200 test image with color gradient."""
    arr = np.zeros((200, 200, 3), dtype=np.uint8)
    for y in range(200):
        for x in range(200):
            arr[y, x] = [x % 256, y % 256, (x + y) % 256]
    return Image.fromarray(arr, mode="RGB")


@pytest.fixture
def small_image() -> Image.Image:
    """Create a 50x50 white test image."""
    return Image.new("RGB", (50, 50), (255, 255, 255))


@pytest.fixture
def dark_image() -> Image.Image:
    """Create a 200x200 dark test image with some bright spots."""
    arr = np.full((200, 200, 3), 20, dtype=np.uint8)
    # Add bright spots
    arr[50:60, 50:60] = 240
    arr[100:110, 150:160] = 230
    return Image.fromarray(arr, mode="RGB")
