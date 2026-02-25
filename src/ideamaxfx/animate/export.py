"""GIF/APNG export with optimization."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import imageio.v3 as iio
import numpy as np
from PIL import Image


def export_gif(
    frames: list[Image.Image],
    output_path: str,
    fps: int = 15,
    max_colors: int = 128,
    max_kb: int = 500,
    lossy: int = 40,
    optimize: bool = True,
) -> str:
    """Export frames as optimized GIF.

    Uses gifsicle for optimization if available, otherwise falls back
    to Pillow-based GIF export.

    Args:
        frames: List of PIL Image frames.
        output_path: Output file path.
        fps: Frames per second.
        max_colors: Maximum number of colors in palette.
        max_kb: Target maximum file size in KB.
        lossy: Lossy compression level for gifsicle (0-200).
        optimize: Whether to attempt gifsicle optimization.

    Returns:
        Path to the saved GIF.
    """
    if not frames:
        raise ValueError("No frames to export")
    if fps <= 0:
        raise ValueError(f"fps must be positive, got {fps}")

    # Convert frames to numpy arrays
    np_frames = [np.array(f.convert("RGB"), dtype=np.uint8) for f in frames]

    has_gifsicle = optimize and shutil.which("gifsicle") is not None

    if has_gifsicle:
        raw_path = str(Path(output_path).with_name(Path(output_path).stem + "_raw.gif"))
        iio.imwrite(raw_path, np_frames, fps=fps, loop=0)

        subprocess.run(
            [
                "gifsicle",
                "-O3",
                f"--lossy={lossy}",
                f"--colors={max_colors}",
                "-o",
                output_path,
                raw_path,
            ],
            check=True,
            capture_output=True,
        )

        # Check size and re-optimize if needed
        size_kb = os.path.getsize(output_path) / 1024
        if size_kb > max_kb:
            subprocess.run(
                ["gifsicle", "-O3", "--lossy=80", "--colors=64", "-o", output_path, raw_path],
                check=True,
                capture_output=True,
            )

        if os.path.exists(raw_path):
            os.remove(raw_path)
    else:
        # Fallback: Pillow GIF export
        duration_ms = int(1000 / fps)
        pil_frames = [f.convert("P", palette=Image.ADAPTIVE, colors=max_colors) for f in frames]
        pil_frames[0].save(
            output_path,
            save_all=True,
            append_images=pil_frames[1:],
            duration=duration_ms,
            loop=0,
            optimize=True,
        )

    return output_path


def export_apng(
    frames: list[Image.Image],
    output_path: str,
    fps: int = 15,
) -> str:
    """Export frames as APNG (animated PNG).

    Args:
        frames: List of PIL Image frames.
        output_path: Output file path.
        fps: Frames per second.

    Returns:
        Path to the saved APNG.
    """
    if not frames:
        raise ValueError("No frames to export")
    if fps <= 0:
        raise ValueError(f"fps must be positive, got {fps}")

    duration_ms = int(1000 / fps)
    rgb_frames = [f.convert("RGBA") for f in frames]
    rgb_frames[0].save(
        output_path,
        save_all=True,
        append_images=rgb_frames[1:],
        duration=duration_ms,
        loop=0,
    )

    return output_path
