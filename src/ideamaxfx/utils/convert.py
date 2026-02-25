"""Conversion utilities between matplotlib, numpy, and PIL."""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

if TYPE_CHECKING:
    from numpy.typing import NDArray


def mpl_to_pil(fig: object, dpi: int = 150) -> Image.Image:
    """Convert a matplotlib Figure to a PIL Image.

    Args:
        fig: A matplotlib Figure object.
        dpi: Resolution in dots per inch.

    Returns:
        RGB PIL Image.
    """
    buf = io.BytesIO()
    fig.savefig(  # type: ignore[union-attr]
        buf,
        format="png",
        dpi=dpi,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),  # type: ignore[union-attr]
        edgecolor="none",
        pad_inches=0.3,
    )
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def numpy_to_pil(arr: NDArray[np.uint8]) -> Image.Image:
    """Convert a numpy uint8 array (H, W, 3) or (H, W) to PIL Image.

    Args:
        arr: Numpy array with dtype uint8.

    Returns:
        PIL Image in RGB or L mode.
    """
    if arr.ndim == 2:
        return Image.fromarray(arr, mode="L")
    if arr.ndim == 3 and arr.shape[2] == 4:
        return Image.fromarray(arr, mode="RGBA")
    return Image.fromarray(arr, mode="RGB")


def pil_to_numpy(img: Image.Image) -> NDArray[np.uint8]:
    """Convert a PIL Image to a numpy uint8 array.

    Args:
        img: PIL Image.

    Returns:
        Numpy array with dtype uint8.
    """
    return np.array(img, dtype=np.uint8)
