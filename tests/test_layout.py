"""Tests for the layout module."""

from __future__ import annotations

import pytest
from PIL import Image

from ideamaxfx.layout import (
    stat_card,
    progress_bar,
    badge,
    legend_block,
    divider,
    callout,
)


class TestStatCard:
    def test_creates_image(self) -> None:
        img = stat_card("42", "Total Items")
        assert isinstance(img, Image.Image)

    def test_default_size(self) -> None:
        img = stat_card("100", "Score")
        assert img.size == (280, 120)

    def test_custom_size(self) -> None:
        img = stat_card("7", "Days", width=400, height=200)
        assert img.size == (400, 200)

    def test_rgb_mode(self) -> None:
        img = stat_card("0", "Errors")
        assert img.mode == "RGB"

    def test_custom_bg_color(self) -> None:
        img = stat_card("5", "Items", bg_color=(255, 0, 0))
        # Top-left corner below accent bar should be red
        px = img.getpixel((0, 10))
        assert px[0] == 255

    def test_custom_accent_color(self) -> None:
        img = stat_card("9", "Wins", accent_color=(0, 0, 255), accent_height=6)
        # Pixel inside the accent bar at top should be blue
        px = img.getpixel((img.width // 2, 2))
        assert px == (0, 0, 255)

    def test_different_values(self) -> None:
        # Ensure no crash with various text inputs
        for val in ["0", "999999", "$1.5M", ""]:
            img = stat_card(val, "label")
            assert img.size[0] > 0


class TestProgressBar:
    def test_creates_image(self) -> None:
        img = progress_bar(0.5)
        assert isinstance(img, Image.Image)

    def test_rgba_mode(self) -> None:
        img = progress_bar(0.5)
        assert img.mode == "RGBA"

    def test_value_zero(self) -> None:
        img = progress_bar(0.0)
        assert img.size[0] > 0

    def test_value_half(self) -> None:
        img = progress_bar(0.5)
        assert img.size[0] > 0

    def test_value_full(self) -> None:
        img = progress_bar(1.0)
        assert img.size[0] > 0

    def test_value_clamped_above(self) -> None:
        # Value > 1.0 should be clamped, not crash
        img = progress_bar(1.5)
        assert img.size[0] > 0

    def test_value_clamped_below(self) -> None:
        # Negative value should be clamped to 0
        img = progress_bar(-0.3)
        assert img.size[0] > 0

    def test_default_size_no_glow(self) -> None:
        img = progress_bar(0.5, glow=False)
        assert img.size == (300, 30)

    def test_glow_adds_padding(self) -> None:
        no_glow = progress_bar(0.5, glow=False)
        with_glow = progress_bar(0.5, glow=True)
        assert with_glow.size[0] > no_glow.size[0]
        assert with_glow.size[1] > no_glow.size[1]

    def test_show_percent_true(self) -> None:
        # Should not crash; text is rendered
        img = progress_bar(0.75, show_percent=True)
        assert img.size[0] > 0

    def test_show_percent_false(self) -> None:
        img = progress_bar(0.75, show_percent=False)
        assert img.size[0] > 0

    def test_custom_dimensions(self) -> None:
        img = progress_bar(0.3, width=500, height=50, glow=False)
        assert img.size == (500, 50)


class TestBadge:
    def test_creates_rgba_image(self) -> None:
        img = badge("NEW")
        assert isinstance(img, Image.Image)
        assert img.mode == "RGBA"

    def test_text_renders(self) -> None:
        img = badge("BETA")
        # Image should have some non-transparent pixels
        alpha = img.split()[3]
        assert alpha.getextrema()[1] > 0

    def test_custom_colors(self) -> None:
        img = badge("OK", bg_color=(255, 0, 0), text_color=(255, 255, 255))
        assert img.size[0] > 0
        assert img.size[1] > 0

    def test_size_scales_with_text(self) -> None:
        short = badge("A")
        long = badge("A VERY LONG LABEL")
        assert long.size[0] > short.size[0]

    def test_custom_padding(self) -> None:
        normal = badge("X", padding_x=16, padding_y=6)
        padded = badge("X", padding_x=40, padding_y=20)
        assert padded.size[0] > normal.size[0]
        assert padded.size[1] > normal.size[1]

    def test_custom_font_size(self) -> None:
        small = badge("Test", font_size=10)
        large = badge("Test", font_size=30)
        # Larger font should produce a larger badge
        assert large.size[0] >= small.size[0]
        assert large.size[1] >= small.size[1]


class TestLegendBlock:
    @pytest.fixture
    def items(self) -> list[tuple[str, tuple[int, int, int]]]:
        return [
            ("Revenue", (0, 245, 212)),
            ("Expenses", (255, 99, 71)),
            ("Profit", (100, 149, 237)),
        ]

    def test_vertical_creates_image(self, items: list) -> None:
        img = legend_block(items, orientation="vertical")
        assert isinstance(img, Image.Image)
        assert img.mode == "RGBA"

    def test_horizontal_creates_image(self, items: list) -> None:
        img = legend_block(items, orientation="horizontal")
        assert isinstance(img, Image.Image)
        assert img.mode == "RGBA"

    def test_vertical_taller_than_horizontal(self, items: list) -> None:
        vert = legend_block(items, orientation="vertical")
        horiz = legend_block(items, orientation="horizontal")
        # Vertical layout should be taller
        assert vert.size[1] > horiz.size[1]

    def test_horizontal_wider_than_vertical(self, items: list) -> None:
        vert = legend_block(items, orientation="vertical")
        horiz = legend_block(items, orientation="horizontal")
        # Horizontal layout should be wider
        assert horiz.size[0] > vert.size[0]

    def test_single_item(self) -> None:
        img = legend_block([("Only", (128, 128, 128))])
        assert img.size[0] > 0
        assert img.size[1] > 0

    def test_custom_dot_size(self, items: list) -> None:
        img = legend_block(items, dot_size=20)
        assert img.size[0] > 0


class TestDivider:
    def test_fade_style(self) -> None:
        img = divider(style="fade")
        assert isinstance(img, Image.Image)
        assert img.mode == "RGBA"
        assert img.size == (600, 3)

    def test_solid_style(self) -> None:
        img = divider(style="solid")
        assert img.mode == "RGBA"
        assert img.size == (600, 3)

    def test_dashed_style(self) -> None:
        img = divider(style="dashed")
        assert img.mode == "RGBA"
        assert img.size == (600, 3)

    def test_custom_size(self) -> None:
        img = divider(width=800, height=5)
        assert img.size == (800, 5)

    def test_solid_fills_completely(self) -> None:
        img = divider(width=100, height=2, color=(255, 0, 0), style="solid")
        px = img.getpixel((50, 0))
        assert px == (255, 0, 0, 255)

    def test_dashed_has_gaps(self) -> None:
        img = divider(width=200, height=2, color=(255, 0, 0), style="dashed")
        # Check that some pixels are transparent (gap region)
        # Gap starts at position 12 in each 18-pixel cycle
        px_gap = img.getpixel((15, 0))
        assert px_gap[3] == 0  # transparent in gap

    def test_fade_center_brighter_than_edge(self) -> None:
        img = divider(width=200, height=2, style="fade")
        center_alpha = img.getpixel((100, 0))[3]
        edge_alpha = img.getpixel((0, 0))[3]
        assert center_alpha > edge_alpha

    def test_custom_color(self) -> None:
        img = divider(width=100, height=2, color=(0, 128, 255), style="solid")
        px = img.getpixel((10, 0))
        assert px[:3] == (0, 128, 255)


class TestCallout:
    def test_right_direction(self) -> None:
        img = callout("Note", anchor=(50, 50), direction="right")
        assert isinstance(img, Image.Image)
        assert img.mode == "RGBA"

    def test_left_direction(self) -> None:
        img = callout("Note", anchor=(200, 50), direction="left")
        assert img.size == (400, 100)

    def test_up_direction(self) -> None:
        img = callout("Note", anchor=(50, 80), direction="up")
        assert img.size == (400, 100)

    def test_down_direction(self) -> None:
        img = callout("Note", anchor=(50, 20), direction="down")
        assert img.size == (400, 100)

    def test_default_canvas_size(self) -> None:
        img = callout("Test")
        assert img.size == (400, 100)

    def test_custom_canvas_size(self) -> None:
        img = callout("Test", canvas_size=(800, 200))
        assert img.size == (800, 200)

    def test_has_content(self) -> None:
        img = callout("Label", anchor=(50, 50), direction="right",
                       line_color=(255, 0, 0))
        # The image should not be fully transparent
        alpha = img.split()[3]
        assert alpha.getextrema()[1] > 0
