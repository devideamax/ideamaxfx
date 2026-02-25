"""Tests for the watermark module."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from ideamaxfx.watermark import (
    text_watermark,
    image_watermark,
    footer_bar,
)


@pytest.fixture
def logo_image() -> Image.Image:
    """Create a small 30x30 RGBA logo for testing."""
    img = Image.new("RGBA", (30, 30), (255, 0, 0, 200))
    return img


class TestTextWatermark:
    def test_returns_image(self, sample_image: Image.Image) -> None:
        result = text_watermark(sample_image, text="DRAFT")
        assert isinstance(result, Image.Image)

    def test_correct_size(self, sample_image: Image.Image) -> None:
        result = text_watermark(sample_image, text="DRAFT")
        assert result.size == sample_image.size

    def test_rgb_output(self, sample_image: Image.Image) -> None:
        result = text_watermark(sample_image, text="TEST")
        assert result.mode == "RGB"

    def test_changes_image(self, sample_image: Image.Image) -> None:
        result = text_watermark(sample_image, text="WATERMARK", opacity=120)
        original_data = list(sample_image.getdata())
        result_data = list(result.getdata())
        # At least some pixels should differ
        diff_count = sum(1 for a, b in zip(original_data, result_data) if a != b)
        assert diff_count > 0

    def test_custom_opacity(self, small_image: Image.Image) -> None:
        # Low opacity should still produce a valid image
        result = text_watermark(small_image, text="HI", opacity=10)
        assert result.size == small_image.size

    def test_custom_font_size(self, sample_image: Image.Image) -> None:
        result = text_watermark(sample_image, text="BIG", font_size=100)
        assert result.size == sample_image.size

    def test_custom_angle(self, sample_image: Image.Image) -> None:
        result = text_watermark(sample_image, text="TILT", angle=-45.0)
        assert result.size == sample_image.size

    def test_custom_color(self, sample_image: Image.Image) -> None:
        result = text_watermark(sample_image, text="RED", color=(255, 0, 0))
        assert result.size == sample_image.size


class TestImageWatermark:
    def test_returns_image(self, sample_image: Image.Image,
                           logo_image: Image.Image) -> None:
        result = image_watermark(sample_image, logo_image)
        assert isinstance(result, Image.Image)

    def test_correct_size(self, sample_image: Image.Image,
                          logo_image: Image.Image) -> None:
        result = image_watermark(sample_image, logo_image)
        assert result.size == sample_image.size

    def test_rgb_output(self, sample_image: Image.Image,
                        logo_image: Image.Image) -> None:
        result = image_watermark(sample_image, logo_image)
        assert result.mode == "RGB"

    def test_bottom_right(self, sample_image: Image.Image,
                          logo_image: Image.Image) -> None:
        result = image_watermark(sample_image, logo_image, position="bottom-right")
        assert result.size == sample_image.size

    def test_top_left(self, sample_image: Image.Image,
                      logo_image: Image.Image) -> None:
        result = image_watermark(sample_image, logo_image, position="top-left")
        assert result.size == sample_image.size

    def test_center(self, sample_image: Image.Image,
                    logo_image: Image.Image) -> None:
        result = image_watermark(sample_image, logo_image, position="center")
        assert result.size == sample_image.size

    def test_top_right(self, sample_image: Image.Image,
                       logo_image: Image.Image) -> None:
        result = image_watermark(sample_image, logo_image, position="top-right")
        assert result.size == sample_image.size

    def test_bottom_left(self, sample_image: Image.Image,
                         logo_image: Image.Image) -> None:
        result = image_watermark(sample_image, logo_image, position="bottom-left")
        assert result.size == sample_image.size

    def test_custom_scale(self, sample_image: Image.Image,
                          logo_image: Image.Image) -> None:
        result = image_watermark(sample_image, logo_image, scale=0.5)
        assert result.size == sample_image.size

    def test_custom_opacity(self, sample_image: Image.Image,
                            logo_image: Image.Image) -> None:
        result = image_watermark(sample_image, logo_image, opacity=0.3)
        assert result.size == sample_image.size

    def test_full_opacity(self, sample_image: Image.Image,
                          logo_image: Image.Image) -> None:
        result = image_watermark(sample_image, logo_image, opacity=1.0)
        assert result.size == sample_image.size

    def test_changes_image(self, sample_image: Image.Image,
                           logo_image: Image.Image) -> None:
        result = image_watermark(sample_image, logo_image,
                                 position="center", opacity=1.0)
        original_data = list(sample_image.getdata())
        result_data = list(result.getdata())
        diff_count = sum(1 for a, b in zip(original_data, result_data) if a != b)
        assert diff_count > 0


class TestFooterBar:
    def test_adds_height(self, sample_image: Image.Image) -> None:
        result = footer_bar(sample_image, height=40)
        assert result.size[0] == sample_image.size[0]
        assert result.size[1] == sample_image.size[1] + 40

    def test_rgb_output(self, sample_image: Image.Image) -> None:
        result = footer_bar(sample_image)
        assert result.mode == "RGB"

    def test_default_height(self, sample_image: Image.Image) -> None:
        result = footer_bar(sample_image)
        assert result.size[1] == sample_image.size[1] + 40

    def test_custom_height(self, sample_image: Image.Image) -> None:
        result = footer_bar(sample_image, height=80)
        assert result.size[1] == sample_image.size[1] + 80

    def test_with_text(self, sample_image: Image.Image) -> None:
        result = footer_bar(sample_image, text="Source: example.com")
        assert result.size[1] > sample_image.size[1]

    def test_without_text(self, sample_image: Image.Image) -> None:
        result = footer_bar(sample_image, text="")
        assert result.size[1] > sample_image.size[1]

    def test_with_logo(self, sample_image: Image.Image,
                       logo_image: Image.Image) -> None:
        result = footer_bar(sample_image, logo=logo_image)
        assert result.size[1] > sample_image.size[1]

    def test_without_logo(self, sample_image: Image.Image) -> None:
        result = footer_bar(sample_image, logo=None)
        assert result.size[1] > sample_image.size[1]

    def test_with_logo_and_text(self, sample_image: Image.Image,
                                logo_image: Image.Image) -> None:
        result = footer_bar(sample_image, text="Credits", logo=logo_image)
        assert result.size[1] == sample_image.size[1] + 40

    def test_footer_bg_color(self, sample_image: Image.Image) -> None:
        result = footer_bar(sample_image, bg_color=(255, 0, 0), height=40)
        # A pixel in the footer area (below original image, below accent line)
        # should be the bg_color
        footer_y = sample_image.size[1] + 10
        px = result.getpixel((result.width // 2, footer_y))
        assert px == (255, 0, 0)

    def test_preserves_original_area(self, sample_image: Image.Image) -> None:
        result = footer_bar(sample_image)
        # Top-left pixel of original image should be preserved
        original_px = sample_image.getpixel((0, 0))
        result_px = result.getpixel((0, 0))
        assert original_px == result_px

    def test_width_unchanged(self, small_image: Image.Image) -> None:
        result = footer_bar(small_image)
        assert result.size[0] == small_image.size[0]
