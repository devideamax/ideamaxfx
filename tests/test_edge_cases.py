"""Comprehensive enterprise-grade edge case tests for ideamaxfx.

Covers degenerate images, boundary parameters, invalid inputs,
pipeline mode flow, color edge cases, animation edge cases,
export edge cases, text edge cases, compose edge cases, and
texture edge cases.
"""

from __future__ import annotations

import pathlib

import numpy as np
import pytest
from PIL import Image, ImageFont

from ideamaxfx.effects import (
    EffectsPipeline,
    bloom,
    chromatic_aberration,
    duotone,
    grain,
    glow,
    halftone,
    scanlines,
    vignette,
)
from ideamaxfx.color import (
    contrast_ratio,
    darken,
    extract_palette,
    hex_to_rgb,
    interpolate_colors,
    lighten,
    rgb_to_hex,
    split_complementary,
    wcag_check,
)
from ideamaxfx.animate import (
    bar_grow,
    compose_animations,
    counter_roll,
    export_apng,
    export_gif,
    heatmap_reveal,
    line_draw,
    morph,
    pie_fill,
    stagger_delays,
)
from ideamaxfx.text import gradient_text, neon_text
from ideamaxfx.compose import (
    drop_shadow,
    mirror_reflection,
    pixelate,
    rounded_corners,
)
from ideamaxfx.texture import (
    dot_pattern,
    grid_pattern,
    perlin_noise,
    stripe_pattern,
)
from ideamaxfx.utils.fonts import load_font


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_rgb(w: int, h: int, color: tuple[int, int, int] = (128, 128, 128)) -> Image.Image:
    """Create a solid RGB image of the given size."""
    return Image.new("RGB", (w, h), color)


def _make_rgba(w: int, h: int, color: tuple[int, int, int, int] = (128, 128, 128, 200)) -> Image.Image:
    """Create a solid RGBA image of the given size."""
    return Image.new("RGBA", (w, h), color)


def _pixel_diff(a: Image.Image, b: Image.Image) -> float:
    """Return the average per-channel absolute difference between two same-size RGB images."""
    a_rgb = a.convert("RGB")
    b_rgb = b.convert("RGB")
    arr_a = np.array(a_rgb, dtype=np.float64)
    arr_b = np.array(b_rgb, dtype=np.float64)
    return float(np.mean(np.abs(arr_a - arr_b)))


# ===========================================================================
# 1. TestDegenerateImages
# ===========================================================================


class TestDegenerateImages:
    """Effects applied to degenerate (1x1, 2x2, non-square, RGBA, L, P) inputs."""

    # --- 1x1 pixel image through each effect --------------------------------

    def test_grain_1x1(self) -> None:
        img = _make_rgb(1, 1)
        result = grain(img, intensity=0.05)
        assert result.size == (1, 1)
        assert result.mode == "RGB"

    def test_vignette_1x1(self) -> None:
        img = _make_rgb(1, 1)
        result = vignette(img, strength=0.3)
        assert result.size == (1, 1)
        assert result.mode == "RGB"

    def test_scanlines_1x1(self) -> None:
        img = _make_rgb(1, 1)
        result = scanlines(img, spacing=4)
        assert result.size == (1, 1)
        assert result.mode == "RGB"

    def test_chromatic_aberration_1x1(self) -> None:
        img = _make_rgb(1, 1)
        result = chromatic_aberration(img, offset=5)
        assert result.size == (1, 1)
        assert result.mode == "RGB"

    def test_bloom_1x1(self) -> None:
        img = _make_rgb(1, 1)
        result = bloom(img, threshold=200)
        assert result.size == (1, 1)
        assert result.mode == "RGB"

    def test_duotone_1x1(self) -> None:
        img = _make_rgb(1, 1)
        result = duotone(img)
        assert result.size == (1, 1)
        assert result.mode == "RGB"

    def test_halftone_1x1(self) -> None:
        img = _make_rgb(1, 1)
        result = halftone(img)
        assert result.size == (1, 1)
        assert result.mode == "L"

    # --- 2x2 pixel image through each effect --------------------------------

    def test_grain_2x2(self) -> None:
        img = _make_rgb(2, 2)
        result = grain(img, intensity=0.05)
        assert result.size == (2, 2)

    def test_vignette_2x2(self) -> None:
        img = _make_rgb(2, 2)
        result = vignette(img, strength=0.3)
        assert result.size == (2, 2)

    def test_scanlines_2x2(self) -> None:
        img = _make_rgb(2, 2)
        result = scanlines(img, spacing=4)
        assert result.size == (2, 2)

    def test_chromatic_aberration_2x2(self) -> None:
        img = _make_rgb(2, 2)
        result = chromatic_aberration(img, offset=5)
        assert result.size == (2, 2)

    def test_bloom_2x2(self) -> None:
        img = _make_rgb(2, 2)
        result = bloom(img, threshold=200)
        assert result.size == (2, 2)

    def test_duotone_2x2(self) -> None:
        img = _make_rgb(2, 2)
        result = duotone(img)
        assert result.size == (2, 2)

    def test_halftone_2x2(self) -> None:
        img = _make_rgb(2, 2)
        result = halftone(img)
        assert result.size == (2, 2)

    # --- Non-square images ---------------------------------------------------

    def test_grain_1x200(self) -> None:
        img = _make_rgb(1, 200)
        result = grain(img, intensity=0.05)
        assert result.size == (1, 200)

    def test_grain_200x1(self) -> None:
        img = _make_rgb(200, 1)
        result = grain(img, intensity=0.05)
        assert result.size == (200, 1)

    def test_vignette_1x200(self) -> None:
        img = _make_rgb(1, 200)
        result = vignette(img, strength=0.3)
        assert result.size == (1, 200)

    def test_vignette_200x1(self) -> None:
        img = _make_rgb(200, 1)
        result = vignette(img, strength=0.3)
        assert result.size == (200, 1)

    # --- RGBA input (alpha may be stripped by convert to RGB) ----------------

    def test_grain_rgba(self) -> None:
        img = _make_rgba(30, 30)
        result = grain(img, intensity=0.05)
        assert result.size == (30, 30)
        assert result.mode == "RGB"

    def test_scanlines_rgba(self) -> None:
        img = _make_rgba(30, 30)
        result = scanlines(img, spacing=4)
        assert result.size == (30, 30)
        assert result.mode == "RGB"

    def test_vignette_rgba(self) -> None:
        img = _make_rgba(30, 30)
        result = vignette(img, strength=0.3)
        assert result.size == (30, 30)
        assert result.mode == "RGB"

    # --- Grayscale "L" mode input -------------------------------------------

    def test_grain_grayscale(self) -> None:
        img = Image.new("L", (30, 30), 128)
        result = grain(img, intensity=0.05)
        assert result.size == (30, 30)
        assert result.mode == "RGB"

    def test_vignette_grayscale(self) -> None:
        img = Image.new("L", (30, 30), 128)
        result = vignette(img, strength=0.3)
        assert result.size == (30, 30)
        assert result.mode == "RGB"

    # --- Palette "P" mode input ---------------------------------------------

    def test_grain_palette(self) -> None:
        img = Image.new("P", (30, 30))
        result = grain(img, intensity=0.05)
        assert result.size == (30, 30)
        assert result.mode == "RGB"


# ===========================================================================
# 2. TestBoundaryParameters
# ===========================================================================


class TestBoundaryParameters:
    """Effects at extreme / boundary parameter values."""

    def test_grain_zero_intensity_is_near_identity(self) -> None:
        img = _make_rgb(50, 50, (100, 150, 200))
        result = grain(img, intensity=0.0)
        diff = _pixel_diff(img, result)
        assert diff < 1.0, f"Expected near-identity, got mean diff {diff}"

    def test_grain_max_intensity_is_noisy(self) -> None:
        img = _make_rgb(50, 50, (100, 150, 200))
        result = grain(img, intensity=1.0)
        diff = _pixel_diff(img, result)
        assert diff > 10.0, f"Expected heavy noise, got mean diff {diff}"

    def test_scanlines_spacing_1_affects_every_row(self) -> None:
        img = _make_rgb(20, 20, (200, 200, 200))
        result = scanlines(img, spacing=1, opacity=0.5)
        # With spacing=1, every row gets the scanline blended.
        arr = np.array(result)
        # All rows should be darker than the original (200) due to black scanline blend
        assert arr.mean() < 200

    def test_vignette_zero_strength_is_identity(self) -> None:
        img = _make_rgb(50, 50, (100, 150, 200))
        result = vignette(img, strength=0.0)
        diff = _pixel_diff(img, result)
        assert diff < 1.0, f"Expected identity, got mean diff {diff}"

    def test_vignette_max_strength_strong_darkening(self) -> None:
        img = _make_rgb(50, 50, (200, 200, 200))
        result = vignette(img, strength=1.0)
        corner = result.getpixel((0, 0))
        assert sum(corner) < sum((200, 200, 200)), "Corner should be darker than original"

    def test_chromatic_offset_zero_is_identity(self) -> None:
        img = _make_rgb(50, 50, (100, 150, 200))
        result = chromatic_aberration(img, offset=0)
        # offset=0 returns the original image object
        assert list(result.getdata()) == list(img.convert("RGB").getdata())

    def test_chromatic_negative_offset_reverses_direction(self) -> None:
        img = _make_rgb(50, 50, (100, 150, 200))
        pos = chromatic_aberration(img, offset=5)
        neg = chromatic_aberration(img, offset=-5)
        # Negative offset should produce a different result from positive
        assert pos.size == neg.size == (50, 50)
        # The channels should be swapped compared to positive offset
        pos_arr = np.array(pos)
        neg_arr = np.array(neg)
        # Red channel of positive should equal blue channel of negative (swapped)
        np.testing.assert_array_equal(pos_arr[:, :, 0], neg_arr[:, :, 2])

    def test_bloom_threshold_zero_everything_bright(self) -> None:
        img = _make_rgb(30, 30, (50, 50, 50))
        result = bloom(img, threshold=0, intensity=0.5)
        assert result.size == (30, 30)
        # With threshold=0, everything contributes to bloom
        result_arr = np.array(result, dtype=np.float64)
        img_arr = np.array(img.convert("RGB"), dtype=np.float64)
        # Screen blend makes it brighter or equal
        assert result_arr.mean() >= img_arr.mean() - 1.0

    def test_bloom_threshold_255_nothing_bright(self) -> None:
        img = _make_rgb(30, 30, (50, 50, 50))
        result = bloom(img, threshold=255, intensity=0.5)
        # Nothing above 255 luminance, so bloom is essentially zero
        diff = _pixel_diff(img, result)
        assert diff < 2.0, f"Expected near-identity, got mean diff {diff}"

    def test_glow_radius_zero_no_spread(self) -> None:
        img = _make_rgb(30, 30, (50, 50, 50))
        result = glow(img, radius=0, intensity=0.5)
        assert result.size == (30, 30)
        assert result.mode == "RGB"


# ===========================================================================
# 3. TestInvalidInputs
# ===========================================================================


class TestInvalidInputs:
    """Graceful handling of edge-case / boundary inputs that might crash."""

    def test_bar_grow_all_zero_values(self) -> None:
        """bar_grow with values=[0,0,0] should not crash (max_val guard)."""
        frames = bar_grow(
            labels=["A", "B", "C"],
            values=[0, 0, 0],
            width=200,
            height=150,
            fps=5,
            duration=0.5,
            hold_seconds=0.2,
        )
        assert len(frames) > 0
        assert all(isinstance(f, Image.Image) for f in frames)

    def test_bar_grow_mismatched_labels_empty_values(self) -> None:
        """bar_grow with labels but empty values should raise ValueError."""
        with pytest.raises(ValueError, match="labels.*values.*same length"):
            bar_grow(
                labels=["A"],
                values=[],
                width=200,
                height=150,
                fps=5,
                duration=0.5,
                hold_seconds=0.2,
            )

    def test_stagger_delays_count_zero(self) -> None:
        result = stagger_delays(count=0)
        assert result == []

    def test_stagger_delays_count_one(self) -> None:
        result = stagger_delays(count=1)
        assert result == [0.0]

    def test_stagger_delays_full_overlap(self) -> None:
        result = stagger_delays(count=5, overlap=1.0)
        assert len(result) == 5
        # With overlap=1.0, step = total * 0.0 / (n-1) = 0, so all delays are 0
        assert all(d == pytest.approx(0.0) for d in result)

    def test_interpolate_colors_boundary_two_steps(self) -> None:
        colors = interpolate_colors("#ff0000", "#0000ff", steps=2)
        assert len(colors) == 2
        assert colors[0] == (255, 0, 0)
        assert colors[1] == (0, 0, 255)

    def test_interpolate_colors_same_color(self) -> None:
        colors = interpolate_colors("#ff0000", "#ff0000", steps=5)
        assert len(colors) == 5
        for c in colors:
            assert c == (255, 0, 0)

    def test_export_gif_very_low_fps(self, tmp_path: pathlib.Path) -> None:
        frame = _make_rgb(20, 20)
        frames = [frame, frame.copy()]
        out = str(tmp_path / "low_fps.gif")
        result = export_gif(frames, out, fps=1, optimize=False)
        assert pathlib.Path(result).exists()

    def test_export_apng_single_frame(self, tmp_path: pathlib.Path) -> None:
        frame = _make_rgb(20, 20)
        out = str(tmp_path / "single.apng")
        result = export_apng([frame], out, fps=10)
        assert pathlib.Path(result).exists()

    def test_extract_palette_uniform_image(self) -> None:
        """extract_palette on a uniform-color image should return 1 color."""
        img = _make_rgb(50, 50, (42, 42, 42))
        colors = extract_palette(img, n_colors=5)
        # Only 1 unique color exists, so n_colors is clamped down
        assert len(colors) >= 1
        assert all(isinstance(c, tuple) and len(c) == 3 for c in colors)
        # All returned colors should be near the input
        for c in colors:
            assert abs(c[0] - 42) < 5
            assert abs(c[1] - 42) < 5
            assert abs(c[2] - 42) < 5


# ===========================================================================
# 4. TestPipelineModeFlow
# ===========================================================================


class TestPipelineModeFlow:
    """EffectsPipeline chainable API edge cases."""

    def test_noop_returns_copy(self) -> None:
        img = _make_rgb(50, 50, (100, 150, 200))
        result = EffectsPipeline(img).image
        # Should be a copy, not the same object
        assert result is not img
        assert result.size == img.size
        assert list(result.getdata()) == list(img.getdata())

    def test_full_chain(self) -> None:
        img = _make_rgb(50, 50, (100, 150, 200))
        result = (
            EffectsPipeline(img)
            .grain(0.05)
            .vignette(0.3)
            .scanlines(4)
            .image
        )
        assert result.size == (50, 50)
        assert result.mode == "RGB"

    def test_rgba_input_through_pipeline(self) -> None:
        img = _make_rgba(50, 50)
        result = EffectsPipeline(img).grain(0.05).image
        assert result.size == (50, 50)

    def test_pipeline_export_to_temp(self, tmp_path: pathlib.Path) -> None:
        img = _make_rgb(50, 50)
        out = tmp_path / "pipeline_out.png"
        result = EffectsPipeline(img).grain(0.03).export(str(out))
        assert out.exists()
        assert isinstance(result, Image.Image)

    def test_pipeline_chain_every_method(self) -> None:
        img = _make_rgb(50, 50, (100, 150, 200))
        result = (
            EffectsPipeline(img)
            .grain(0.02)
            .glow(color=(255, 100, 50), radius=5, intensity=0.3)
            .halftone(dot_size=3, spacing=5)
            .scanlines(spacing=3, opacity=0.2)
            .glass(x=5, y=5, w=20, h=20, blur=5)
            .duotone(dark=(10, 10, 40), light=(255, 200, 50))
            .vignette(strength=0.2)
            .chromatic(offset=2)
            .bloom(threshold=150, radius=5, intensity=0.3)
            .image
        )
        assert result.size == (50, 50)


# ===========================================================================
# 5. TestColorEdgeCases
# ===========================================================================


class TestColorEdgeCases:
    """Color conversion, adjustment, harmony, and accessibility edge cases."""

    def test_hex_to_rgb_short_form_raises(self) -> None:
        with pytest.raises(ValueError, match="Expected 6 hex digits"):
            hex_to_rgb("#FFF")

    def test_hex_to_rgb_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="Expected 6 hex digits"):
            hex_to_rgb("")

    def test_rgb_to_hex_overflow_raises(self) -> None:
        with pytest.raises(ValueError, match="r must be 0-255"):
            rgb_to_hex(256, 0, 0)

    def test_rgb_to_hex_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="r must be 0-255"):
            rgb_to_hex(-1, 0, 0)

    def test_darken_zero_amount_identity(self) -> None:
        color = (200, 200, 200)
        result = darken(color, amount=0.0)
        assert result == color

    def test_darken_full_amount_near_black(self) -> None:
        result = darken((200, 200, 200), amount=1.0)
        # Lightness reduced by 1.0 should bring it near or at black
        assert all(c <= 10 for c in result)

    def test_lighten_full_amount_near_white(self) -> None:
        result = lighten((50, 50, 50), amount=1.0)
        # Lightness increased by 1.0 should bring it near or at white
        assert all(c >= 245 for c in result)

    def test_contrast_ratio_same_color(self) -> None:
        ratio = contrast_ratio((128, 128, 128), (128, 128, 128))
        assert ratio == pytest.approx(1.0, abs=0.01)

    def test_split_complementary_red(self) -> None:
        result = split_complementary((255, 0, 0))
        assert isinstance(result, list)
        assert len(result) == 2
        for c in result:
            assert isinstance(c, tuple)
            assert len(c) == 3
            assert all(0 <= v <= 255 for v in c)

    def test_wcag_check_aaa_black_on_white(self) -> None:
        result = wcag_check((0, 0, 0), (255, 255, 255), level="AAA")
        assert result is True

    def test_wcag_check_aaa_same_color_fails(self) -> None:
        result = wcag_check((128, 128, 128), (128, 128, 128), level="AAA")
        assert result is False


# ===========================================================================
# 6. TestAnimationEdgeCases
# ===========================================================================


class TestAnimationEdgeCases:
    """Animation generators at edge-case parameter values."""

    def test_bar_grow_single_bar(self) -> None:
        frames = bar_grow(
            labels=["A"],
            values=[50],
            width=200,
            height=150,
            fps=5,
            duration=0.5,
            hold_seconds=0.2,
        )
        assert len(frames) > 0
        assert all(isinstance(f, Image.Image) for f in frames)

    def test_line_draw_two_points(self) -> None:
        frames = line_draw(
            x_values=[0.0, 1.0],
            y_values=[0.0, 1.0],
            width=200,
            height=150,
            fps=5,
            duration=0.5,
            hold_seconds=0.2,
        )
        assert len(frames) > 0
        assert all(isinstance(f, Image.Image) for f in frames)

    def test_pie_fill_single_sector(self) -> None:
        frames = pie_fill(
            labels=["Only"],
            values=[100.0],
            width=200,
            height=200,
            fps=5,
            duration=0.5,
            hold_seconds=0.2,
        )
        assert len(frames) > 0

    def test_heatmap_reveal_1x1_data(self) -> None:
        frames = heatmap_reveal(
            data=[[42.0]],
            width=200,
            height=200,
            fps=5,
            duration=0.5,
            hold_seconds=0.2,
        )
        assert len(frames) > 0

    def test_counter_roll_start_equals_end(self) -> None:
        frames = counter_roll(
            start=50,
            end=50,
            width=200,
            height=100,
            fps=5,
            duration=0.5,
            hold_seconds=0.2,
        )
        assert len(frames) > 0
        # Every frame should show the same number (50)

    def test_morph_different_sized_images(self) -> None:
        img_a = _make_rgb(30, 20, (255, 0, 0))
        img_b = _make_rgb(50, 40, (0, 0, 255))
        frames = morph(img_a, img_b, fps=5, duration=0.5, hold_seconds=0.2)
        assert len(frames) > 0
        # Output should be resized to max of both dimensions
        assert frames[0].size == (50, 40)

    def test_frame_count_exact(self) -> None:
        """fps=10, duration=1.0, hold=0.5 should produce 10 + 5 = 15 frames."""
        frames = bar_grow(
            labels=["A", "B"],
            values=[10, 20],
            width=200,
            height=150,
            fps=10,
            duration=1.0,
            hold_seconds=0.5,
        )
        # generate_frames: n_anim = max(1, int(10*1.0)) = 10
        #                  n_hold = max(1, int(10*0.5)) = 5
        assert len(frames) == 15

    def test_compose_animations_empty_input(self) -> None:
        result = compose_animations([], layout="sequence")
        assert result == []

    def test_compose_animations_single_animation_side_by_side(self) -> None:
        frame = _make_rgb(20, 20)
        result = compose_animations([[frame]], layout="side_by_side")
        assert len(result) == 1
        assert isinstance(result[0], Image.Image)


# ===========================================================================
# 7. TestExportEdgeCases
# ===========================================================================


class TestExportEdgeCases:
    """GIF/APNG export at edge conditions."""

    def test_export_gif_single_frame(self, tmp_path: pathlib.Path) -> None:
        frame = _make_rgb(20, 20, (100, 200, 50))
        out = str(tmp_path / "single_frame.gif")
        result = export_gif([frame], out, fps=10, optimize=False)
        assert pathlib.Path(result).exists()
        assert pathlib.Path(result).stat().st_size > 0

    def test_export_apng_single_frame_exists(self, tmp_path: pathlib.Path) -> None:
        frame = _make_rgb(20, 20, (100, 200, 50))
        out = str(tmp_path / "single_frame.apng")
        result = export_apng([frame], out, fps=10)
        assert pathlib.Path(result).exists()
        assert pathlib.Path(result).stat().st_size > 0

    def test_export_gif_empty_frames_raises(self, tmp_path: pathlib.Path) -> None:
        out = str(tmp_path / "empty.gif")
        with pytest.raises(ValueError, match="No frames"):
            export_gif([], out, fps=10)

    def test_export_apng_empty_frames_raises(self, tmp_path: pathlib.Path) -> None:
        out = str(tmp_path / "empty.apng")
        with pytest.raises(ValueError, match="No frames"):
            export_apng([], out, fps=10)

    def test_export_gif_to_temp_directory_cleanup(self, tmp_path: pathlib.Path) -> None:
        frame = _make_rgb(20, 20)
        out = str(tmp_path / "test_cleanup.gif")
        result_path = export_gif([frame, frame.copy()], out, fps=10, optimize=False)
        assert pathlib.Path(result_path).exists()
        # Verify the file is valid by reading it back
        loaded = Image.open(result_path)
        assert loaded.size == (20, 20)


# ===========================================================================
# 8. TestTextEdgeCases
# ===========================================================================


class TestTextEdgeCases:
    """Text effects at edge conditions (empty string, overflow, negative coords)."""

    @pytest.fixture()
    def font(self) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        return load_font(size=14)

    def test_gradient_text_empty_string(self, font: ImageFont.ImageFont) -> None:
        img = _make_rgb(50, 50)
        result = gradient_text(
            img, x=10, y=10, text="", font=font,
            color_start=(255, 0, 0), color_end=(0, 0, 255),
        )
        assert result.size == (50, 50)

    def test_neon_text_empty_string(self, font: ImageFont.ImageFont) -> None:
        img = _make_rgb(50, 50)
        result = neon_text(
            img, x=10, y=10, text="", font=font,
            color=(0, 255, 128),
        )
        assert result.size == (50, 50)

    def test_gradient_text_very_long_overflows(self, font: ImageFont.ImageFont) -> None:
        img = _make_rgb(50, 50)
        long_text = "A" * 500
        result = gradient_text(
            img, x=0, y=0, text=long_text, font=font,
            color_start=(255, 0, 0), color_end=(0, 0, 255),
        )
        # Should not crash even though text exceeds canvas
        assert result.size == (50, 50)

    def test_neon_text_very_long_overflows(self, font: ImageFont.ImageFont) -> None:
        img = _make_rgb(50, 50)
        long_text = "B" * 500
        result = neon_text(
            img, x=0, y=0, text=long_text, font=font,
            color=(0, 255, 128),
        )
        assert result.size == (50, 50)

    def test_gradient_text_negative_coords(self, font: ImageFont.ImageFont) -> None:
        img = _make_rgb(50, 50)
        result = gradient_text(
            img, x=-20, y=-20, text="Hello", font=font,
            color_start=(255, 0, 0), color_end=(0, 0, 255),
        )
        assert result.size == (50, 50)

    def test_neon_text_negative_coords(self, font: ImageFont.ImageFont) -> None:
        img = _make_rgb(50, 50)
        result = neon_text(
            img, x=-20, y=-20, text="Hello", font=font,
            color=(0, 255, 128),
        )
        assert result.size == (50, 50)

    def test_gradient_text_beyond_bounds(self, font: ImageFont.ImageFont) -> None:
        img = _make_rgb(50, 50)
        result = gradient_text(
            img, x=1000, y=1000, text="Hello", font=font,
            color_start=(255, 0, 0), color_end=(0, 0, 255),
        )
        assert result.size == (50, 50)

    def test_neon_text_beyond_bounds(self, font: ImageFont.ImageFont) -> None:
        img = _make_rgb(50, 50)
        result = neon_text(
            img, x=1000, y=1000, text="Hello", font=font,
            color=(0, 255, 128),
        )
        assert result.size == (50, 50)


# ===========================================================================
# 9. TestComposeEdgeCases
# ===========================================================================


class TestComposeEdgeCases:
    """Compose module functions at boundary parameters."""

    def test_rounded_corners_radius_zero(self) -> None:
        img = _make_rgb(50, 50, (200, 100, 50))
        result = rounded_corners(img, radius=0)
        assert result.size == (50, 50)
        assert result.mode == "RGBA"
        # With radius=0, no rounding occurs; content should be preserved
        result_rgb = result.convert("RGB")
        diff = _pixel_diff(img, result_rgb)
        assert diff < 2.0

    def test_pixelate_block_size_one_identity(self) -> None:
        img = _make_rgb(50, 50, (200, 100, 50))
        result = pixelate(img, block_size=1)
        assert result.size == (50, 50)
        result_rgb = result.convert("RGB")
        diff = _pixel_diff(img, result_rgb)
        assert diff < 2.0, f"Expected near-identity, got mean diff {diff}"

    def test_drop_shadow_zero_offset(self) -> None:
        img = _make_rgb(30, 30, (200, 100, 50))
        result = drop_shadow(img, offset=(0, 0), blur_radius=5)
        assert isinstance(result, Image.Image)
        assert result.mode == "RGBA"
        # Canvas should still be larger due to blur margin
        assert result.width >= 30
        assert result.height >= 30

    def test_mirror_reflection_zero_height(self) -> None:
        img = _make_rgb(30, 30, (200, 100, 50))
        result = mirror_reflection(img, height_ratio=0.0)
        assert isinstance(result, Image.Image)
        assert result.mode == "RGBA"
        # height_ratio=0.0 means ref_h = max(1, int(0)) = 1 pixel reflection
        # The result height = original_h + gap + ref_h >= 30
        assert result.height >= 30

    def test_mirror_reflection_full_height(self) -> None:
        img = _make_rgb(30, 30, (200, 100, 50))
        result = mirror_reflection(img, height_ratio=1.0, gap=2)
        assert isinstance(result, Image.Image)
        assert result.mode == "RGBA"
        # Full reflection: height = 30 + 2 + 30 = 62
        assert result.height == 62


# ===========================================================================
# 10. TestTextureEdgeCases
# ===========================================================================


class TestTextureEdgeCases:
    """Texture generators at boundary dimensions and parameters."""

    def test_perlin_noise_1x1(self) -> None:
        result = perlin_noise(width=1, height=1, seed=42)
        assert result.size == (1, 1)
        assert result.mode == "L"

    def test_grid_pattern_spacing_one(self) -> None:
        result = grid_pattern(width=20, height=20, spacing=1)
        assert result.size == (20, 20)
        assert result.mode == "RGB"

    def test_stripe_pattern_thickness_greater_than_spacing(self) -> None:
        result = stripe_pattern(width=30, height=30, spacing=5, thickness=10)
        assert result.size == (30, 30)
        assert result.mode == "RGB"

    def test_dot_pattern_radius_greater_than_spacing(self) -> None:
        result = dot_pattern(width=30, height=30, spacing=5, radius=10)
        assert result.size == (30, 30)
        assert result.mode == "RGB"
