"""Tests for the compose module."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from ideamaxfx.compose import (
    rounded_corners,
    drop_shadow,
    mirror_reflection,
    tilt_shift,
    pixelate,
    color_overlay,
)


class TestRoundedCorners:
    def test_returns_rgba(self, sample_image: Image.Image) -> None:
        result = rounded_corners(sample_image)
        assert result.mode == "RGBA"

    def test_correct_size(self, sample_image: Image.Image) -> None:
        result = rounded_corners(sample_image)
        assert result.size == sample_image.size

    def test_corners_transparent(self, sample_image: Image.Image) -> None:
        result = rounded_corners(sample_image, radius=20)
        # Top-left corner pixel should be transparent
        px = result.getpixel((0, 0))
        assert px[3] == 0

    def test_center_opaque(self, sample_image: Image.Image) -> None:
        result = rounded_corners(sample_image, radius=20)
        cx, cy = sample_image.size[0] // 2, sample_image.size[1] // 2
        px = result.getpixel((cx, cy))
        assert px[3] == 255

    def test_zero_radius(self, sample_image: Image.Image) -> None:
        result = rounded_corners(sample_image, radius=0)
        assert result.size == sample_image.size

    def test_large_radius_clamped(self, small_image: Image.Image) -> None:
        # Radius larger than half the shortest side should be clamped
        result = rounded_corners(small_image, radius=100)
        assert result.size == small_image.size

    def test_custom_bg_color(self, sample_image: Image.Image) -> None:
        result = rounded_corners(sample_image, radius=20,
                                 bg_color=(255, 0, 0, 255))
        # Corner should be the background color
        px = result.getpixel((0, 0))
        assert px == (255, 0, 0, 255)

    def test_from_rgb_input(self) -> None:
        img = Image.new("RGB", (50, 50), (128, 128, 128))
        result = rounded_corners(img, radius=10)
        assert result.mode == "RGBA"
        assert result.size == (50, 50)


class TestDropShadow:
    def test_output_larger_than_input(self, sample_image: Image.Image) -> None:
        result = drop_shadow(sample_image)
        assert result.size[0] > sample_image.size[0]
        assert result.size[1] > sample_image.size[1]

    def test_returns_rgba(self, sample_image: Image.Image) -> None:
        result = drop_shadow(sample_image)
        assert result.mode == "RGBA"

    def test_custom_offset(self, small_image: Image.Image) -> None:
        result = drop_shadow(small_image, offset=(5, 5))
        assert result.size[0] > small_image.size[0]

    def test_zero_offset(self, small_image: Image.Image) -> None:
        result = drop_shadow(small_image, offset=(0, 0))
        # Should still be larger due to blur margin
        assert result.size[0] > small_image.size[0]

    def test_custom_blur_radius(self, small_image: Image.Image) -> None:
        small_blur = drop_shadow(small_image, blur_radius=5)
        large_blur = drop_shadow(small_image, blur_radius=25)
        # Larger blur means larger canvas
        assert large_blur.size[0] > small_blur.size[0]

    def test_custom_shadow_color(self, small_image: Image.Image) -> None:
        result = drop_shadow(small_image, shadow_color=(255, 0, 0))
        assert result.mode == "RGBA"

    def test_custom_opacity(self, small_image: Image.Image) -> None:
        result = drop_shadow(small_image, opacity=200)
        assert result.size[0] > small_image.size[0]

    def test_negative_offset(self, small_image: Image.Image) -> None:
        result = drop_shadow(small_image, offset=(-10, -10))
        assert result.size[0] > small_image.size[0]


class TestMirrorReflection:
    def test_output_taller_than_input(self, sample_image: Image.Image) -> None:
        result = mirror_reflection(sample_image)
        assert result.size[1] > sample_image.size[1]

    def test_same_width(self, sample_image: Image.Image) -> None:
        result = mirror_reflection(sample_image)
        assert result.size[0] == sample_image.size[0]

    def test_returns_rgba(self, sample_image: Image.Image) -> None:
        result = mirror_reflection(sample_image)
        assert result.mode == "RGBA"

    def test_height_ratio(self, sample_image: Image.Image) -> None:
        result = mirror_reflection(sample_image, height_ratio=0.5, gap=0)
        expected_h = sample_image.size[1] + int(sample_image.size[1] * 0.5)
        assert result.size[1] == expected_h

    def test_gap(self, sample_image: Image.Image) -> None:
        no_gap = mirror_reflection(sample_image, gap=0)
        with_gap = mirror_reflection(sample_image, gap=10)
        assert with_gap.size[1] == no_gap.size[1] + 10

    def test_zero_height_ratio(self, sample_image: Image.Image) -> None:
        # Clamped to at least 1 pixel reflection
        result = mirror_reflection(sample_image, height_ratio=0.0)
        assert result.size[1] >= sample_image.size[1]

    def test_full_height_ratio(self, sample_image: Image.Image) -> None:
        result = mirror_reflection(sample_image, height_ratio=1.0, gap=0)
        assert result.size[1] == sample_image.size[1] * 2

    def test_opacity_gradient(self, sample_image: Image.Image) -> None:
        result = mirror_reflection(sample_image, height_ratio=0.4,
                                   opacity_start=200, opacity_end=0, gap=2)
        # Reflection area: the alpha at top of reflection should be higher
        # than at the bottom of reflection
        ref_top_y = sample_image.size[1] + 2  # just below gap
        ref_bot_y = result.size[1] - 1
        top_alpha = result.getpixel((result.size[0] // 2, ref_top_y))[3]
        bot_alpha = result.getpixel((result.size[0] // 2, ref_bot_y))[3]
        assert top_alpha >= bot_alpha


class TestTiltShift:
    def test_correct_size(self, sample_image: Image.Image) -> None:
        result = tilt_shift(sample_image)
        assert result.size == sample_image.size

    def test_returns_rgba(self, sample_image: Image.Image) -> None:
        result = tilt_shift(sample_image)
        assert result.mode == "RGBA"

    def test_does_not_crash_defaults(self, sample_image: Image.Image) -> None:
        result = tilt_shift(sample_image)
        assert isinstance(result, Image.Image)

    def test_custom_focus_y(self, sample_image: Image.Image) -> None:
        result = tilt_shift(sample_image, focus_y=0.3)
        assert result.size == sample_image.size

    def test_custom_focus_height(self, sample_image: Image.Image) -> None:
        result = tilt_shift(sample_image, focus_height=0.5)
        assert result.size == sample_image.size

    def test_custom_blur_amount(self, sample_image: Image.Image) -> None:
        result = tilt_shift(sample_image, blur_amount=15)
        assert result.size == sample_image.size

    def test_focus_at_top(self, sample_image: Image.Image) -> None:
        result = tilt_shift(sample_image, focus_y=0.0)
        assert result.size == sample_image.size

    def test_focus_at_bottom(self, sample_image: Image.Image) -> None:
        result = tilt_shift(sample_image, focus_y=1.0)
        assert result.size == sample_image.size

    def test_small_image(self, small_image: Image.Image) -> None:
        result = tilt_shift(small_image)
        assert result.size == small_image.size


class TestPixelate:
    def test_full_image(self, sample_image: Image.Image) -> None:
        result = pixelate(sample_image, block_size=10)
        assert isinstance(result, Image.Image)

    def test_returns_rgba(self, sample_image: Image.Image) -> None:
        result = pixelate(sample_image, block_size=10)
        assert result.mode == "RGBA"

    def test_correct_size(self, sample_image: Image.Image) -> None:
        result = pixelate(sample_image, block_size=10)
        assert result.size == sample_image.size

    def test_region_mode(self, sample_image: Image.Image) -> None:
        result = pixelate(sample_image, block_size=10,
                          region=(20, 20, 100, 100))
        assert result.size == sample_image.size

    def test_region_preserves_outside(self, sample_image: Image.Image) -> None:
        result = pixelate(sample_image, block_size=10,
                          region=(50, 50, 150, 150))
        # Pixel outside the region at (0,0) should be unchanged
        original_rgba = sample_image.convert("RGBA")
        assert result.getpixel((0, 0)) == original_rgba.getpixel((0, 0))

    def test_block_size_one(self, sample_image: Image.Image) -> None:
        # block_size=1 means no visible pixelation
        result = pixelate(sample_image, block_size=1)
        assert result.size == sample_image.size

    def test_large_block_size(self, small_image: Image.Image) -> None:
        result = pixelate(small_image, block_size=50)
        assert result.size == small_image.size

    def test_invalid_region_returns_copy(self, sample_image: Image.Image) -> None:
        # Region where x2 <= x1 should return a copy
        result = pixelate(sample_image, block_size=10, region=(100, 100, 50, 50))
        assert result.size == sample_image.size

    def test_region_clamped_to_bounds(self, small_image: Image.Image) -> None:
        result = pixelate(small_image, block_size=5,
                          region=(-10, -10, 200, 200))
        assert result.size == small_image.size


class TestColorOverlay:
    def test_normal_mode(self, sample_image: Image.Image) -> None:
        result = color_overlay(sample_image, color=(255, 0, 0), mode="normal")
        assert isinstance(result, Image.Image)
        assert result.mode == "RGBA"

    def test_multiply_mode(self, sample_image: Image.Image) -> None:
        result = color_overlay(sample_image, color=(255, 0, 0), mode="multiply")
        assert result.mode == "RGBA"
        assert result.size == sample_image.size

    def test_screen_mode(self, sample_image: Image.Image) -> None:
        result = color_overlay(sample_image, color=(100, 100, 100), mode="screen")
        assert result.mode == "RGBA"
        assert result.size == sample_image.size

    def test_invalid_mode_raises(self, sample_image: Image.Image) -> None:
        with pytest.raises(ValueError, match="Unsupported blend mode"):
            color_overlay(sample_image, mode="dodge")

    def test_correct_size(self, sample_image: Image.Image) -> None:
        result = color_overlay(sample_image, color=(0, 0, 0))
        assert result.size == sample_image.size

    def test_zero_opacity(self, sample_image: Image.Image) -> None:
        result = color_overlay(sample_image, color=(255, 0, 0), opacity=0.0)
        # With zero opacity, image should be essentially unchanged
        orig_arr = np.array(sample_image.convert("RGBA"), dtype=np.uint8)
        res_arr = np.array(result, dtype=np.uint8)
        assert np.allclose(orig_arr[:, :, :3], res_arr[:, :, :3], atol=1)

    def test_full_opacity_normal(self, sample_image: Image.Image) -> None:
        result = color_overlay(sample_image, color=(128, 128, 128),
                               opacity=1.0, mode="normal")
        # All RGB pixels should be close to the overlay color
        arr = np.array(result, dtype=np.uint8)
        assert np.allclose(arr[:, :, :3], 128, atol=1)

    def test_multiply_darkens(self, sample_image: Image.Image) -> None:
        result = color_overlay(sample_image, color=(128, 128, 128),
                               opacity=1.0, mode="multiply")
        orig_mean = np.array(sample_image).mean()
        result_mean = np.array(result)[:, :, :3].mean()
        assert result_mean <= orig_mean

    def test_screen_lightens(self, dark_image: Image.Image) -> None:
        result = color_overlay(dark_image, color=(128, 128, 128),
                               opacity=1.0, mode="screen")
        orig_mean = np.array(dark_image).mean()
        result_mean = np.array(result)[:, :, :3].mean()
        assert result_mean >= orig_mean

    def test_opacity_clamped(self, sample_image: Image.Image) -> None:
        # Opacity > 1.0 should be clamped
        result = color_overlay(sample_image, color=(255, 0, 0), opacity=5.0)
        assert result.size == sample_image.size
