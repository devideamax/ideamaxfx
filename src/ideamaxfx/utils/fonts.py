"""Font loading with system fallbacks."""

from __future__ import annotations

import os
import sys

from PIL import ImageFont

_FALLBACK_NAMES = [
    "DejaVuSans.ttf",
    "Arial.ttf",
    "arial.ttf",
    "Helvetica.ttf",
    "LiberationSans-Regular.ttf",
    "FreeSans.ttf",
]

_FONT_DIRS: list[str] = []
if sys.platform == "win32":
    _FONT_DIRS.append(os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"))
elif sys.platform == "darwin":
    _FONT_DIRS.extend(["/Library/Fonts", os.path.expanduser("~/Library/Fonts")])
else:
    _FONT_DIRS.extend(
        [
            "/usr/share/fonts/truetype",
            "/usr/share/fonts/truetype/dejavu",
            "/usr/share/fonts",
            os.path.expanduser("~/.local/share/fonts"),
        ]
    )


def _find_system_font() -> str | None:
    """Search system font directories for a usable font."""
    for font_dir in _FONT_DIRS:
        if not os.path.isdir(font_dir):
            continue
        for root, _dirs, files in os.walk(font_dir):
            for name in _FALLBACK_NAMES:
                if name in files:
                    return os.path.join(root, name)
    return None


def load_font(
    size: int = 20, path: str | None = None
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a TrueType font with fallback to system fonts.

    Args:
        size: Font size in pixels.
        path: Optional explicit path to a .ttf file.

    Returns:
        A PIL font object.
    """
    if path and os.path.isfile(path):
        return ImageFont.truetype(path, size)

    system_font = _find_system_font()
    if system_font:
        return ImageFont.truetype(system_font, size)

    return ImageFont.load_default()
