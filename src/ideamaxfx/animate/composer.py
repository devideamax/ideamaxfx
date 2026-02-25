"""Combine multiple animations into a single sequence."""

from __future__ import annotations

from PIL import Image


def compose_animations(
    animations: list[list[Image.Image]],
    layout: str = "sequence",
    gap: int = 0,
) -> list[Image.Image]:
    """Combine multiple animation frame lists.

    Args:
        animations: List of frame lists from different animations.
        layout: "sequence" (one after another), "side_by_side" (horizontal),
            "grid_2x2" (2x2 grid).
        gap: Pixel gap between images in spatial layouts.

    Returns:
        Combined list of PIL Image frames.
    """
    if not animations:
        return []

    if layout == "sequence":
        result: list[Image.Image] = []
        for anim in animations:
            result.extend(anim)
        return result

    if layout == "side_by_side":
        # Pad all to same length
        max_len = max(len(a) for a in animations)
        padded = []
        for anim in animations:
            if not anim:
                continue
            extended = anim + [anim[-1]] * (max_len - len(anim))
            padded.append(extended)

        if not padded:
            return []

        frames: list[Image.Image] = []
        for fi in range(max_len):
            imgs = [p[fi] for p in padded]
            total_w = sum(im.width for im in imgs) + gap * (len(imgs) - 1)
            max_h = max(im.height for im in imgs)
            canvas = Image.new("RGB", (total_w, max_h), (0, 0, 0))
            x = 0
            for im in imgs:
                canvas.paste(im, (x, 0))
                x += im.width + gap
            frames.append(canvas)
        return frames

    if layout == "grid_2x2":
        # Exactly 4 animations expected; pad to same length
        while len(animations) < 4:
            animations.append(animations[-1] if animations else [])
        max_len = max(len(a) for a in animations[:4])
        padded4 = []
        for anim in animations[:4]:
            if not anim:
                padded4.append([Image.new("RGB", (100, 100), (0, 0, 0))] * max_len)
            else:
                padded4.append(anim + [anim[-1]] * (max_len - len(anim)))

        frames = []
        for fi in range(max_len):
            tl, tr, bl, br = [p[fi] for p in padded4]
            cell_w = max(tl.width, bl.width, tr.width, br.width)
            cell_h = max(tl.height, tr.height, bl.height, br.height)
            canvas = Image.new("RGB", (cell_w * 2 + gap, cell_h * 2 + gap), (0, 0, 0))
            canvas.paste(tl, (0, 0))
            canvas.paste(tr, (cell_w + gap, 0))
            canvas.paste(bl, (0, cell_h + gap))
            canvas.paste(br, (cell_w + gap, cell_h + gap))
            frames.append(canvas)
        return frames

    # Default fallback: sequence
    return compose_animations(animations, layout="sequence")
