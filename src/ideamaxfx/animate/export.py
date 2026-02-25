"""GIF/APNG/WebP/MP4 export with optimization."""

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
    max_colors: int = 256,
    max_kb: int = 2000,
    lossy: int = 0,
    optimize: bool = True,
) -> str:
    """Export frames as optimized GIF.

    Uses gifsicle for optimization if available, otherwise falls back
    to imageio-based GIF export with optional Pillow re-quantization.

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
                ["gifsicle", "-O3", "--lossy=40", "--colors=128", "-o", output_path, raw_path],
                check=True,
                capture_output=True,
            )

        if os.path.exists(raw_path):
            os.remove(raw_path)
    else:
        # Fallback: imageio writes clean GIFs with consistent palette
        iio.imwrite(output_path, np_frames, fps=fps, loop=0)

        # If oversized, re-export with reduced colors via Pillow global palette
        size_kb = os.path.getsize(output_path) / 1024
        if size_kb > max_kb:
            colors = min(max_colors, 128)
            duration_ms = int(1000 / fps)
            # Build a global palette from the first frame
            palette_img = frames[0].convert("RGB").quantize(colors=colors)
            pil_frames = []
            for f in frames:
                q = f.convert("RGB").quantize(colors=colors, palette=palette_img)
                pil_frames.append(q)
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


def export_webp(
    frames: list[Image.Image],
    output_path: str,
    fps: int = 15,
    quality: int = 80,
    lossless: bool = False,
) -> str:
    """Export frames as animated WebP (24-bit color, no 256-color limit).

    Uses Pillow's native WebP support — zero additional dependencies.

    Args:
        frames: List of PIL Image frames.
        output_path: Output file path.
        fps: Frames per second.
        quality: WebP quality (1-100). Higher = better quality, larger file.
        lossless: If True, use lossless compression.

    Returns:
        Path to the saved WebP.
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
        quality=quality,
        lossless=lossless,
    )
    return output_path


def export_mp4(
    frames: list[Image.Image],
    output_path: str,
    fps: int = 15,
    codec: str = "libx264",
    quality: int = 23,
) -> str:
    """Export frames as MP4 video.

    Requires the ``imageio-ffmpeg`` package (install via
    ``pip install ideamaxfx[video]``).

    Args:
        frames: List of PIL Image frames.
        output_path: Output file path.
        fps: Frames per second.
        codec: Video codec (default libx264).
        quality: CRF quality value (lower = better, 0-51). Default 23.

    Returns:
        Path to the saved MP4.

    Raises:
        ImportError: If imageio-ffmpeg is not installed.
    """
    if not frames:
        raise ValueError("No frames to export")
    if fps <= 0:
        raise ValueError(f"fps must be positive, got {fps}")

    try:
        import imageio_ffmpeg  # noqa: F401
    except ImportError:
        raise ImportError(
            "MP4 export requires imageio-ffmpeg. "
            "Install it with: pip install ideamaxfx[video]"
        ) from None

    np_frames = [np.array(f.convert("RGB"), dtype=np.uint8) for f in frames]
    iio.imwrite(
        output_path,
        np_frames,
        fps=fps,
        codec=codec,
        quality=quality,
    )
    return output_path
