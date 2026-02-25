"""Tests for the effects module."""

from __future__ import annotations

import pytest
from PIL import Image

from ideamaxfx.effects import (
    grain,
    glow,
    glow_border,
    halftone,
    scanlines,
    glass_card,
    duotone,
    vignette,
    chromatic_aberration,
    bloom,
    blue_noise,
    pattern_overlay,
    blend,
    EffectsPipeline,
)


class TestGrain:
    def test_output_size(self, sample_image: Image.Image) -> None:
        result = grain(sample_image, intensity=0.1)
        assert result.size == sample_image.size

    def test_output_mode(self, sample_image: Image.Image) -> None:
        result = grain(sample_image, intensity=0.1)
        assert result.mode == "RGB"

    def test_changes_image(self, sample_image: Image.Image) -> None:
        result = grain(sample_image, intensity=0.1)
        assert list(result.getdata()) != list(sample_image.getdata())


class TestGlow:
    def test_output_size(self, dark_image: Image.Image) -> None:
        result = glow(dark_image, color=(0, 245, 212))
        assert result.size == dark_image.size

    def test_glow_border_output(self, sample_image: Image.Image) -> None:
        points = [(10, 10), (100, 10), (100, 100), (10, 100)]
        result = glow_border(sample_image, points)
        assert result.size == sample_image.size


class TestHalftone:
    def test_output_size(self, sample_image: Image.Image) -> None:
        result = halftone(sample_image)
        assert result.size == sample_image.size


class TestScanlines:
    def test_output_size(self, sample_image: Image.Image) -> None:
        result = scanlines(sample_image, spacing=4)
        assert result.size == sample_image.size


class TestGlass:
    def test_glass_card(self, sample_image: Image.Image) -> None:
        result = glass_card(sample_image, x=20, y=20, w=100, h=80)
        assert result.size == sample_image.size


class TestDuotone:
    def test_output_size(self, sample_image: Image.Image) -> None:
        result = duotone(sample_image)
        assert result.size == sample_image.size


class TestVignette:
    def test_output_size(self, sample_image: Image.Image) -> None:
        result = vignette(sample_image, strength=0.3)
        assert result.size == sample_image.size

    def test_darkens_corners(self, small_image: Image.Image) -> None:
        result = vignette(small_image, strength=0.5)
        corner = result.getpixel((0, 0))
        center = result.getpixel((25, 25))
        assert sum(corner) < sum(center)


class TestChromatic:
    def test_output_size(self, sample_image: Image.Image) -> None:
        result = chromatic_aberration(sample_image, offset=5)
        assert result.size == sample_image.size


class TestBloom:
    def test_output_size(self, dark_image: Image.Image) -> None:
        result = bloom(dark_image, threshold=200)
        assert result.size == dark_image.size


class TestBlueNoise:
    def test_output(self) -> None:
        result = blue_noise(128, 128)
        assert result.size == (128, 128)
        assert result.mode == "L"


class TestPatternOverlay:
    def test_grid(self, sample_image: Image.Image) -> None:
        result = pattern_overlay(sample_image, pattern="grid")
        assert result.size == sample_image.size

    def test_dots(self, sample_image: Image.Image) -> None:
        result = pattern_overlay(sample_image, pattern="dots")
        assert result.size == sample_image.size


class TestBlend:
    def test_screen(self, sample_image: Image.Image) -> None:
        overlay = Image.new("RGB", sample_image.size, (50, 50, 50))
        result = blend(sample_image, overlay, mode="screen")
        assert result.size == sample_image.size

    def test_multiply(self, sample_image: Image.Image) -> None:
        overlay = Image.new("RGB", sample_image.size, (200, 200, 200))
        result = blend(sample_image, overlay, mode="multiply")
        assert result.size == sample_image.size


class TestPipeline:
    def test_chainable(self, sample_image: Image.Image) -> None:
        pipeline = EffectsPipeline(sample_image)
        result = (pipeline
                  .grain(0.05)
                  .scanlines(spacing=4)
                  .vignette(0.3))
        assert result.image.size == sample_image.size

    def test_export(self, sample_image: Image.Image, tmp_path: object) -> None:
        import pathlib
        out = pathlib.Path(str(tmp_path)) / "test_output.png"
        result = (EffectsPipeline(sample_image)
                  .grain(0.05)
                  .vignette(0.3)
                  .export(str(out)))
        assert out.exists()
        assert result.size == sample_image.size
