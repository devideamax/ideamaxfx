"""Tests for the utils module."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image, ImageFont

from ideamaxfx.utils import (
    pil_to_numpy,
    numpy_to_pil,
    load_font,
)


class TestPilToNumpy:
    def test_rgb_shape(self, sample_image: Image.Image) -> None:
        arr = pil_to_numpy(sample_image)
        assert arr.shape == (200, 200, 3)

    def test_dtype_uint8(self, sample_image: Image.Image) -> None:
        arr = pil_to_numpy(sample_image)
        assert arr.dtype == np.uint8

    def test_grayscale_shape(self) -> None:
        gray = Image.new("L", (50, 50), 128)
        arr = pil_to_numpy(gray)
        assert arr.shape == (50, 50)
        assert arr.dtype == np.uint8

    def test_rgba_shape(self) -> None:
        rgba = Image.new("RGBA", (30, 40), (100, 150, 200, 255))
        arr = pil_to_numpy(rgba)
        assert arr.shape == (40, 30, 4)
        assert arr.dtype == np.uint8

    def test_pixel_values_preserved(self) -> None:
        img = Image.new("RGB", (2, 2), (10, 20, 30))
        arr = pil_to_numpy(img)
        assert arr[0, 0, 0] == 10
        assert arr[0, 0, 1] == 20
        assert arr[0, 0, 2] == 30

    def test_small_image(self, small_image: Image.Image) -> None:
        arr = pil_to_numpy(small_image)
        assert arr.shape == (50, 50, 3)
        # small_image is white
        assert np.all(arr == 255)


class TestNumpyToPil:
    def test_rgb(self) -> None:
        arr = np.zeros((60, 80, 3), dtype=np.uint8)
        arr[:, :, 0] = 100
        img = numpy_to_pil(arr)
        assert isinstance(img, Image.Image)
        assert img.mode == "RGB"
        assert img.size == (80, 60)

    def test_grayscale(self) -> None:
        arr = np.full((40, 50), 200, dtype=np.uint8)
        img = numpy_to_pil(arr)
        assert img.mode == "L"
        assert img.size == (50, 40)

    def test_rgba(self) -> None:
        arr = np.zeros((30, 40, 4), dtype=np.uint8)
        arr[:, :, 3] = 255
        img = numpy_to_pil(arr)
        assert img.mode == "RGBA"
        assert img.size == (40, 30)

    def test_pixel_values_preserved(self) -> None:
        arr = np.array([[[10, 20, 30], [40, 50, 60]]], dtype=np.uint8)
        img = numpy_to_pil(arr)
        assert img.getpixel((0, 0)) == (10, 20, 30)
        assert img.getpixel((1, 0)) == (40, 50, 60)

    def test_roundtrip_rgb(self, sample_image: Image.Image) -> None:
        arr = pil_to_numpy(sample_image)
        img_back = numpy_to_pil(arr)
        assert img_back.size == sample_image.size
        assert img_back.mode == sample_image.mode
        assert list(img_back.getdata()) == list(sample_image.getdata())

    def test_roundtrip_grayscale(self) -> None:
        original = Image.new("L", (20, 20), 128)
        arr = pil_to_numpy(original)
        restored = numpy_to_pil(arr)
        assert restored.mode == "L"
        assert list(restored.getdata()) == list(original.getdata())


class TestLoadFont:
    def test_returns_font_object(self) -> None:
        font = load_font(size=20)
        # Should be either a FreeTypeFont or ImageFont
        assert isinstance(font, (ImageFont.FreeTypeFont, ImageFont.ImageFont))

    def test_custom_size(self) -> None:
        font = load_font(size=40)
        assert isinstance(font, (ImageFont.FreeTypeFont, ImageFont.ImageFont))

    def test_small_size(self) -> None:
        font = load_font(size=8)
        assert isinstance(font, (ImageFont.FreeTypeFont, ImageFont.ImageFont))

    def test_nonexistent_path_falls_back(self) -> None:
        # A non-existent path should fall back to system font or default
        font = load_font(size=20, path="/nonexistent/fake_font.ttf")
        assert isinstance(font, (ImageFont.FreeTypeFont, ImageFont.ImageFont))

    def test_none_path(self) -> None:
        font = load_font(size=16, path=None)
        assert isinstance(font, (ImageFont.FreeTypeFont, ImageFont.ImageFont))

    def test_font_can_render(self) -> None:
        font = load_font(size=20)
        # Verify the font can actually be used for rendering
        img = Image.new("RGB", (100, 30), (0, 0, 0))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        # Should not raise
        draw.text((5, 5), "Hello", fill=(255, 255, 255), font=font)
        # The image should have some non-black pixels now
        data = list(img.getdata())
        has_white = any(px != (0, 0, 0) for px in data)
        assert has_white

    def test_different_sizes_produce_different_metrics(self) -> None:
        small = load_font(size=10)
        large = load_font(size=40)
        # Measure the same text with both fonts
        img = Image.new("RGB", (1, 1))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        bbox_small = draw.textbbox((0, 0), "Test", font=small)
        bbox_large = draw.textbbox((0, 0), "Test", font=large)
        small_w = bbox_small[2] - bbox_small[0]
        large_w = bbox_large[2] - bbox_large[0]
        assert large_w > small_w
