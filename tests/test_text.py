"""Tests for the text module."""

from __future__ import annotations

import pytest
from PIL import Image

from ideamaxfx.text import gradient_text, neon_text, outline_text, shadow_text, emboss_text
from ideamaxfx.utils.fonts import load_font


@pytest.fixture
def canvas() -> Image.Image:
    """200x100 dark canvas."""
    return Image.new("RGB", (200, 100), (13, 17, 23))


@pytest.fixture
def font():  # type: ignore[no-untyped-def]
    """Default font."""
    return load_font(size=20)


class TestGradientText:
    def test_output_size(self, canvas: Image.Image, font: object) -> None:
        result = gradient_text(
            canvas, 10, 10, "Hello",
            font=font,  # type: ignore[arg-type]
            color_start=(255, 0, 0),
            color_end=(0, 0, 255),
        )
        assert result.size == canvas.size

    def test_vertical(self, canvas: Image.Image, font: object) -> None:
        result = gradient_text(
            canvas, 10, 10, "Test",
            font=font,  # type: ignore[arg-type]
            color_start=(0, 255, 0),
            color_end=(255, 0, 255),
            direction="vertical",
        )
        assert result.size == canvas.size


class TestNeonText:
    def test_output_size(self, canvas: Image.Image, font: object) -> None:
        result = neon_text(
            canvas, 10, 10, "Neon",
            font=font,  # type: ignore[arg-type]
            color=(0, 245, 212),
        )
        assert result.size == canvas.size

    def test_changes_image(self, canvas: Image.Image, font: object) -> None:
        result = neon_text(
            canvas, 10, 10, "Glow",
            font=font,  # type: ignore[arg-type]
            color=(255, 0, 100),
        )
        assert list(result.getdata()) != list(canvas.getdata())


class TestOutlineText:
    def test_output_size(self, canvas: Image.Image, font: object) -> None:
        result = outline_text(
            canvas, 10, 10, "Outline",
            font=font,  # type: ignore[arg-type]
        )
        assert result.size == canvas.size


class TestShadowText:
    def test_output_size(self, canvas: Image.Image, font: object) -> None:
        result = shadow_text(
            canvas, 10, 10, "Shadow",
            font=font,  # type: ignore[arg-type]
        )
        assert result.size == canvas.size


class TestEmbossText:
    def test_output_size(self, canvas: Image.Image, font: object) -> None:
        result = emboss_text(
            canvas, 10, 10, "Emboss",
            font=font,  # type: ignore[arg-type]
        )
        assert result.size == canvas.size
