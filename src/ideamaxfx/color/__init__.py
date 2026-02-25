"""Color utilities for ideamaxfx."""

from __future__ import annotations

from ideamaxfx.color.convert import hex_to_rgb, rgb_to_hex, rgb_to_hsl, hsl_to_rgb
from ideamaxfx.color.adjust import darken, lighten, saturate, desaturate
from ideamaxfx.color.interpolate import interpolate_colors
from ideamaxfx.color.harmonies import complementary, triadic, analogous, split_complementary
from ideamaxfx.color.palette import extract_palette
from ideamaxfx.color.accessibility import contrast_ratio, wcag_check, suggest_readable

__all__ = [
    "hex_to_rgb",
    "rgb_to_hex",
    "rgb_to_hsl",
    "hsl_to_rgb",
    "darken",
    "lighten",
    "saturate",
    "desaturate",
    "interpolate_colors",
    "complementary",
    "triadic",
    "analogous",
    "split_complementary",
    "extract_palette",
    "contrast_ratio",
    "wcag_check",
    "suggest_readable",
]
