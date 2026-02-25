"""Tests for chart_utils shared infrastructure."""

from __future__ import annotations

import pytest
from PIL import Image, ImageDraw

from ideamaxfx.animate.chart_utils import (
    _SS,
    D3_CATEGORY10,
    compute_nice_ticks,
    finalize_frame,
    format_number,
    format_number_commas,
    parse_colors,
)


class TestFormatNumber:
    def test_millions(self) -> None:
        assert format_number(1_500_000) == "1.5M"

    def test_millions_even(self) -> None:
        assert format_number(2_000_000) == "2M"

    def test_thousands(self) -> None:
        assert format_number(45_000) == "45K"

    def test_small(self) -> None:
        assert format_number(999) == "999"

    def test_zero(self) -> None:
        assert format_number(0) == "0"

    def test_negative(self) -> None:
        assert format_number(-50_000) == "-50K"

    def test_with_decimals(self) -> None:
        assert format_number(3.14, decimals=2) == "3.14"


class TestFormatNumberCommas:
    def test_basic(self) -> None:
        assert format_number_commas(1_000_000) == "1,000,000"

    def test_small(self) -> None:
        assert format_number_commas(999) == "999"

    def test_with_decimals(self) -> None:
        assert format_number_commas(1234.56, decimals=2) == "1,234.56"

    def test_custom_separator(self) -> None:
        assert format_number_commas(1000, sep=".") == "1.000"

    def test_negative(self) -> None:
        assert format_number_commas(-500_000) == "-500,000"


class TestComputeNiceTicks:
    def test_basic_range(self) -> None:
        ticks = compute_nice_ticks(0, 100)
        assert len(ticks) >= 2
        assert ticks[0] <= 0
        assert ticks[-1] >= 100

    def test_small_range(self) -> None:
        ticks = compute_nice_ticks(0, 5)
        assert len(ticks) >= 2
        assert all(isinstance(t, (int, float)) for t in ticks)

    def test_equal_values(self) -> None:
        ticks = compute_nice_ticks(50, 50)
        assert len(ticks) >= 1
        assert 50 in ticks or any(abs(t - 50) < 10 for t in ticks)

    def test_negative_range(self) -> None:
        ticks = compute_nice_ticks(-100, 100)
        assert ticks[0] <= -100
        assert ticks[-1] >= 100

    def test_large_range(self) -> None:
        ticks = compute_nice_ticks(0, 1_000_000)
        assert len(ticks) >= 2


class TestParseColors:
    def test_hex_colors(self) -> None:
        result = parse_colors(["#ff0000", "#00ff00"], 2)
        assert result == [(255, 0, 0), (0, 255, 0)]

    def test_rgb_colors(self) -> None:
        result = parse_colors([(255, 0, 0)], 1)
        assert result == [(255, 0, 0)]

    def test_none_uses_default(self) -> None:
        result = parse_colors(None, 3)
        assert len(result) == 3
        assert result[0] == D3_CATEGORY10[0]

    def test_cycling(self) -> None:
        result = parse_colors(["#ff0000"], 3)
        assert len(result) == 3
        assert result[0] == result[1] == result[2] == (255, 0, 0)


class TestFinalizeFrame:
    def test_downscale_dimensions(self) -> None:
        img = Image.new("RGB", (800, 500), (100, 100, 100))
        result = finalize_frame(img, 400, 250)
        assert result.size == (400, 250)

    def test_sharpen_on(self) -> None:
        img = Image.new("RGB", (200, 200), (50, 50, 50))
        result = finalize_frame(img, 100, 100, sharpen=True)
        assert result.size == (100, 100)

    def test_sharpen_off(self) -> None:
        img = Image.new("RGB", (200, 200), (50, 50, 50))
        result = finalize_frame(img, 100, 100, sharpen=False)
        assert result.size == (100, 100)

    def test_rgba_input(self) -> None:
        img = Image.new("RGBA", (200, 200), (50, 50, 50, 255))
        result = finalize_frame(img, 100, 100)
        assert result.mode == "RGB"
