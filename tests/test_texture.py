"""Tests for the texture module."""

from __future__ import annotations

import pytest
from PIL import Image

from ideamaxfx.texture import (
    perlin_noise,
    grid_pattern,
    stripe_pattern,
    dot_pattern,
)


class TestPerlinNoise:
    def test_creates_image(self) -> None:
        img = perlin_noise(width=64, height=64)
        assert isinstance(img, Image.Image)

    def test_correct_size(self) -> None:
        img = perlin_noise(width=100, height=80)
        assert img.size == (100, 80)

    def test_grayscale_mode(self) -> None:
        img = perlin_noise(width=64, height=64)
        assert img.mode == "L"

    def test_default_size(self) -> None:
        img = perlin_noise()
        assert img.size == (512, 512)

    def test_different_scales(self) -> None:
        small_scale = perlin_noise(width=64, height=64, scale=10.0, seed=42)
        large_scale = perlin_noise(width=64, height=64, scale=50.0, seed=42)
        # Different scales should produce different patterns
        assert list(small_scale.getdata()) != list(large_scale.getdata())

    def test_different_octaves(self) -> None:
        one_oct = perlin_noise(width=64, height=64, octaves=1, seed=42)
        four_oct = perlin_noise(width=64, height=64, octaves=4, seed=42)
        assert list(one_oct.getdata()) != list(four_oct.getdata())

    def test_seeded_reproducibility(self) -> None:
        img1 = perlin_noise(width=64, height=64, seed=123)
        img2 = perlin_noise(width=64, height=64, seed=123)
        assert list(img1.getdata()) == list(img2.getdata())

    def test_different_seeds_differ(self) -> None:
        img1 = perlin_noise(width=64, height=64, seed=1)
        img2 = perlin_noise(width=64, height=64, seed=2)
        assert list(img1.getdata()) != list(img2.getdata())

    def test_pixel_range(self) -> None:
        img = perlin_noise(width=64, height=64, seed=0)
        lo, hi = img.getextrema()
        assert lo >= 0
        assert hi <= 255

    def test_not_flat(self) -> None:
        img = perlin_noise(width=64, height=64, seed=7)
        lo, hi = img.getextrema()
        # Noise should have some variation
        assert hi - lo > 10


class TestGridPattern:
    def test_lines_style(self) -> None:
        img = grid_pattern(width=100, height=100, style="lines")
        assert isinstance(img, Image.Image)
        assert img.mode == "RGB"
        assert img.size == (100, 100)

    def test_dots_style(self) -> None:
        img = grid_pattern(width=100, height=100, style="dots")
        assert img.size == (100, 100)
        assert img.mode == "RGB"

    def test_crosses_style(self) -> None:
        img = grid_pattern(width=100, height=100, style="crosses")
        assert img.size == (100, 100)
        assert img.mode == "RGB"

    def test_invalid_style_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown style"):
            grid_pattern(style="zigzag")

    def test_custom_colors(self) -> None:
        img = grid_pattern(
            width=100, height=100,
            color=(255, 0, 0), bg_color=(0, 0, 255),
            style="lines", spacing=20,
        )
        # Background pixel far from grid lines should be blue
        # spacing=20, so pixel (10, 10) is between grid lines
        px = img.getpixel((10, 10))
        assert px == (0, 0, 255)

    def test_default_size(self) -> None:
        img = grid_pattern()
        assert img.size == (512, 512)

    def test_custom_spacing(self) -> None:
        img = grid_pattern(width=100, height=100, spacing=50, style="lines")
        assert img.size == (100, 100)

    def test_lines_draws_on_grid(self) -> None:
        img = grid_pattern(
            width=100, height=100,
            spacing=20, line_width=1,
            color=(255, 0, 0), bg_color=(0, 0, 0),
            style="lines",
        )
        # Pixel at grid intersection (0, 0) should be colored
        px = img.getpixel((0, 0))
        assert px == (255, 0, 0)


class TestStripePattern:
    def test_horizontal(self) -> None:
        img = stripe_pattern(width=100, height=100, direction="horizontal")
        assert isinstance(img, Image.Image)
        assert img.mode == "RGB"
        assert img.size == (100, 100)

    def test_vertical(self) -> None:
        img = stripe_pattern(width=100, height=100, direction="vertical")
        assert img.size == (100, 100)
        assert img.mode == "RGB"

    def test_diagonal(self) -> None:
        img = stripe_pattern(width=100, height=100, direction="diagonal")
        assert img.size == (100, 100)
        assert img.mode == "RGB"

    def test_invalid_direction_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown direction"):
            stripe_pattern(direction="curved")

    def test_default_size(self) -> None:
        img = stripe_pattern()
        assert img.size == (512, 512)

    def test_custom_colors(self) -> None:
        img = stripe_pattern(
            width=100, height=100,
            color=(255, 255, 0), bg_color=(0, 0, 0),
            direction="horizontal", spacing=20, thickness=2,
        )
        # A stripe-free zone between stripes should be bg_color
        # First stripe is at y=0, next at y=20; y=10 should be background
        px = img.getpixel((50, 10))
        assert px == (0, 0, 0)

    def test_horizontal_stripe_present(self) -> None:
        img = stripe_pattern(
            width=100, height=100,
            color=(255, 0, 0), bg_color=(0, 0, 0),
            direction="horizontal", spacing=20, thickness=4,
        )
        # At y=0 the stripe should be drawn
        px = img.getpixel((50, 0))
        assert px == (255, 0, 0)

    def test_diagonal_has_both_colors(self) -> None:
        img = stripe_pattern(
            width=100, height=100,
            color=(255, 255, 255), bg_color=(0, 0, 0),
            direction="diagonal", spacing=20, thickness=5,
        )
        data = list(img.getdata())
        has_white = any(px == (255, 255, 255) for px in data)
        has_black = any(px == (0, 0, 0) for px in data)
        assert has_white and has_black


class TestDotPattern:
    def test_creates_image(self) -> None:
        img = dot_pattern(width=100, height=100)
        assert isinstance(img, Image.Image)
        assert img.mode == "RGB"

    def test_correct_size(self) -> None:
        img = dot_pattern(width=120, height=80)
        assert img.size == (120, 80)

    def test_default_size(self) -> None:
        img = dot_pattern()
        assert img.size == (512, 512)

    def test_custom_spacing(self) -> None:
        tight = dot_pattern(width=100, height=100, spacing=10, radius=2,
                            color=(255, 0, 0), bg_color=(0, 0, 0))
        wide = dot_pattern(width=100, height=100, spacing=40, radius=2,
                           color=(255, 0, 0), bg_color=(0, 0, 0))
        # Tighter spacing means more colored pixels
        tight_reds = sum(1 for px in tight.getdata() if px[0] > 200)
        wide_reds = sum(1 for px in wide.getdata() if px[0] > 200)
        assert tight_reds > wide_reds

    def test_custom_colors(self) -> None:
        img = dot_pattern(
            width=100, height=100,
            color=(0, 255, 0), bg_color=(128, 128, 128),
            spacing=20, radius=3,
        )
        # Background far from dots should be gray
        # Dot at (0,0), next at (20,20); pixel (10, 10) should be bg
        px = img.getpixel((10, 10))
        assert px == (128, 128, 128)

    def test_dots_visible(self) -> None:
        img = dot_pattern(
            width=100, height=100,
            color=(255, 0, 0), bg_color=(0, 0, 0),
            spacing=20, radius=5,
        )
        # Center of first dot at origin - pixel (0,0) should be red
        px = img.getpixel((0, 0))
        assert px == (255, 0, 0)
