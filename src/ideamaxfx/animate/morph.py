"""Morph between two chart states (crossfade)."""

from __future__ import annotations

from typing import Callable

from PIL import Image

from ideamaxfx.animate.core import generate_frames


def morph(
    img_start: Image.Image,
    img_end: Image.Image,
    fps: int = 15,
    duration: float = 1.5,
    hold_seconds: float = 1.0,
    easing: str | Callable[[float], float] = "ease_in_out_cubic",
) -> list[Image.Image]:
    """Generate frames morphing between two images via crossfade.

    Args:
        img_start: Starting image.
        img_end: Ending image.
        fps: Frames per second.
        duration: Morph duration in seconds.
        hold_seconds: Hold final frame.
        easing: Easing function name or callable.

    Returns:
        List of PIL Image frames.
    """
    # Ensure same size
    w = max(img_start.width, img_end.width)
    h = max(img_start.height, img_end.height)
    start = img_start.resize((w, h), Image.LANCZOS).convert("RGB")
    end = img_end.resize((w, h), Image.LANCZOS).convert("RGB")

    def render(progress: float) -> Image.Image:
        return Image.blend(start, end, progress)

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
