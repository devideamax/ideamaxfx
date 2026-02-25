"""ideamaxfx - Post-production effects, animated build-up, and visual toolkit.

A Python library for applying cinematic finishing effects to any PIL Image,
generating animated chart build-ups as GIF/APNG, and providing a rich set
of text effects, layout components, color utilities, and image composition tools.

Example::

    from ideamaxfx import EffectsPipeline
    from PIL import Image

    img = Image.open("chart.png")
    result = (EffectsPipeline(img)
              .grain(0.06)
              .glow(color=(0, 245, 212))
              .scanlines(spacing=4)
              .vignette(0.3)
              .export("finished.png"))
"""

from __future__ import annotations

__version__ = "0.1.1"

from ideamaxfx.effects.pipeline import EffectsPipeline

__all__ = ["EffectsPipeline", "__version__"]
