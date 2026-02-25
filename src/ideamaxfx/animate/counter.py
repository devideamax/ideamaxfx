"""Animated number counter roll."""

from __future__ import annotations

from typing import Callable

from PIL import Image, ImageDraw

from ideamaxfx.animate.core import generate_frames
from ideamaxfx.utils.fonts import load_font


def counter_roll(
    start: float = 0,
    end: float = 100,
    prefix: str = "",
    suffix: str = "",
    decimals: int = 0,
    width: int = 400,
    height: int = 200,
    bg_color: tuple[int, int, int] = (13, 17, 23),
    text_color: tuple[int, int, int] = (255, 255, 255),
    accent_color: tuple[int, int, int] = (0, 245, 212),
    label: str = "",
    fps: int = 15,
    duration: float = 2.0,
    hold_seconds: float = 2.0,
    easing: str | Callable[[float], float] = "ease_out_expo",
    font_path: str | None = None,
) -> list[Image.Image]:
    """Generate animated number counter frames.

    Args:
        start: Starting value.
        end: Ending value.
        prefix: Text before number (e.g. "$").
        suffix: Text after number (e.g. "%").
        decimals: Decimal places.
        width: Image width.
        height: Image height.
        bg_color: Background color.
        text_color: Number text color.
        accent_color: Label text color.
        label: Description label below the number.
        fps: Frames per second.
        duration: Animation duration.
        hold_seconds: Hold final frame.
        easing: Easing function name or callable.
        font_path: Optional font path.

    Returns:
        List of PIL Image frames.
    """
    number_font = load_font(size=52, path=font_path)
    label_font = load_font(size=16, path=font_path)

    def render(progress: float) -> Image.Image:
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        current = start + (end - start) * progress
        if decimals == 0:
            num_text = f"{prefix}{int(current)}{suffix}"
        else:
            num_text = f"{prefix}{current:.{decimals}f}{suffix}"

        # Center the number
        nbbox = draw.textbbox((0, 0), num_text, font=number_font)
        nw = nbbox[2] - nbbox[0]
        nh = nbbox[3] - nbbox[1]
        ny = (height - nh) // 2 - (12 if label else 0)
        draw.text(((width - nw) // 2, ny), num_text, fill=text_color, font=number_font)

        # Label below
        if label:
            lbbox = draw.textbbox((0, 0), label, font=label_font)
            lw = lbbox[2] - lbbox[0]
            draw.text(((width - lw) // 2, ny + nh + 12), label, fill=accent_color, font=label_font)

        return img

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
