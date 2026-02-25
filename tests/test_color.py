"""Tests for the color module."""

from __future__ import annotations

import pytest
from PIL import Image

from ideamaxfx.color import (
    hex_to_rgb,
    rgb_to_hex,
    rgb_to_hsl,
    hsl_to_rgb,
    darken,
    lighten,
    saturate,
    desaturate,
    interpolate_colors,
    complementary,
    triadic,
    analogous,
    contrast_ratio,
    wcag_check,
    suggest_readable,
    extract_palette,
)


class TestConvert:
    def test_hex_to_rgb(self) -> None:
        assert hex_to_rgb("#ff0000") == (255, 0, 0)
        assert hex_to_rgb("00ff00") == (0, 255, 0)
        assert hex_to_rgb("#0000FF") == (0, 0, 255)

    def test_rgb_to_hex(self) -> None:
        assert rgb_to_hex(255, 0, 0) == "#ff0000"
        assert rgb_to_hex(0, 255, 0) == "#00ff00"

    def test_roundtrip_hsl(self) -> None:
        for color in [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]:
            h, s, l = rgb_to_hsl(*color)
            back = hsl_to_rgb(h, s, l)
            for a, b in zip(color, back):
                assert abs(a - b) <= 1, f"HSL roundtrip failed for {color}"


class TestAdjust:
    def test_darken(self) -> None:
        result = darken((200, 200, 200), 0.2)
        assert all(0 <= c <= 255 for c in result)
        # Should be darker
        assert sum(result) < sum((200, 200, 200))

    def test_lighten(self) -> None:
        result = lighten((100, 100, 100), 0.2)
        assert all(0 <= c <= 255 for c in result)
        assert sum(result) > sum((100, 100, 100))

    def test_saturate_desaturate(self) -> None:
        original = (180, 50, 50)
        sat = saturate(original, 0.3)
        desat = desaturate(original, 0.3)
        # Saturated should be more vivid, desaturated less
        assert sat != desat


class TestInterpolate:
    def test_basic(self) -> None:
        colors = interpolate_colors("#000000", "#ffffff", steps=3)
        assert len(colors) == 3
        assert colors[0] == (0, 0, 0)
        assert colors[-1] == (255, 255, 255)
        # Middle should be grayish
        assert 100 < colors[1][0] < 160

    def test_tuple_input(self) -> None:
        colors = interpolate_colors((255, 0, 0), (0, 0, 255), steps=5)
        assert len(colors) == 5


class TestHarmonies:
    def test_complementary(self) -> None:
        result = complementary((255, 0, 0))
        assert len(result) == 1
        # Red's complement should be cyan-ish
        assert result[0][1] > 200  # Green channel high
        assert result[0][2] > 200  # Blue channel high

    def test_triadic(self) -> None:
        result = triadic((255, 0, 0))
        assert len(result) == 2

    def test_analogous(self) -> None:
        result = analogous("#ff0000")
        assert len(result) == 2


class TestAccessibility:
    def test_contrast_ratio_black_white(self) -> None:
        ratio = contrast_ratio((0, 0, 0), (255, 255, 255))
        assert 20 < ratio < 22  # Should be ~21:1

    def test_wcag_check(self) -> None:
        assert wcag_check((0, 0, 0), (255, 255, 255), level="AAA")
        assert not wcag_check((200, 200, 200), (220, 220, 220), level="AA")

    def test_suggest_readable(self) -> None:
        # On white background, suggest black
        assert suggest_readable((255, 255, 255)) == (0, 0, 0)
        # On black background, suggest white
        assert suggest_readable((0, 0, 0)) == (255, 255, 255)


class TestPalette:
    def test_extract(self, sample_image: Image.Image) -> None:
        palette = extract_palette(sample_image, n_colors=3)
        assert len(palette) == 3
        for color in palette:
            assert len(color) == 3
            assert all(0 <= c <= 255 for c in color)
