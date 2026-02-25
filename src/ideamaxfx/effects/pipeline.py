"""Chainable effects pipeline."""

from __future__ import annotations

from PIL import Image

from ideamaxfx.effects.grain import grain as _grain
from ideamaxfx.effects.glow import glow as _glow
from ideamaxfx.effects.halftone import halftone as _halftone
from ideamaxfx.effects.scanlines import scanlines as _scanlines
from ideamaxfx.effects.glass import glass_card as _glass_card
from ideamaxfx.effects.duotone import duotone as _duotone
from ideamaxfx.effects.vignette import vignette as _vignette
from ideamaxfx.effects.chromatic import chromatic_aberration as _chromatic_aberration
from ideamaxfx.effects.bloom import bloom as _bloom


class EffectsPipeline:
    """Chainable effects pipeline.

    Wraps a PIL image and exposes effect methods that each return
    ``self``, allowing a fluent call chain::

        result = (
            EffectsPipeline(img)
            .grain(0.04)
            .vignette(0.3)
            .scanlines(spacing=3)
            .export("output.png")
        )

    Args:
        img: The starting image for the pipeline.
    """

    def __init__(self, img: Image.Image) -> None:
        self._img: Image.Image = img.copy()

    # ------------------------------------------------------------------
    # Effect methods
    # ------------------------------------------------------------------

    def grain(
        self,
        intensity: float = 0.06,
        monochrome: bool = True,
    ) -> EffectsPipeline:
        """Apply film grain.

        Args:
            intensity: Noise strength (0.0 -- 1.0).
            monochrome: Use the same noise value on all channels.

        Returns:
            Self for chaining.
        """
        self._img = _grain(self._img, intensity=intensity, monochrome=monochrome)
        return self

    def glow(
        self,
        color: tuple[int, int, int] = (0, 245, 212),
        radius: int = 20,
        intensity: float = 0.5,
    ) -> EffectsPipeline:
        """Apply bright-area glow.

        Args:
            color: RGB tint for the glow.
            radius: Gaussian blur radius.
            intensity: Blend strength.

        Returns:
            Self for chaining.
        """
        self._img = _glow(self._img, color=color, radius=radius, intensity=intensity)
        return self

    def halftone(
        self,
        dot_size: int = 6,
        spacing: int = 8,
        angle: float = 45.0,
    ) -> EffectsPipeline:
        """Convert to halftone dot pattern.

        Args:
            dot_size: Maximum dot radius in pixels.
            spacing: Grid spacing in pixels.
            angle: Grid rotation in degrees.

        Returns:
            Self for chaining.
        """
        self._img = _halftone(self._img, dot_size=dot_size, spacing=spacing, angle=angle)
        return self

    def scanlines(
        self,
        spacing: int = 4,
        opacity: float = 0.3,
        color: tuple[int, int, int] = (0, 0, 0),
    ) -> EffectsPipeline:
        """Overlay CRT scanlines.

        Args:
            spacing: Pixels between scanlines.
            opacity: Scanline opacity.
            color: Scanline colour.

        Returns:
            Self for chaining.
        """
        self._img = _scanlines(self._img, spacing=spacing, opacity=opacity, color=color)
        return self

    def glass(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        blur: int = 15,
        tint: tuple[int, int, int, int] = (20, 25, 40, 160),
        radius: int = 12,
    ) -> EffectsPipeline:
        """Apply a glassmorphism card.

        Args:
            x: Left edge of card.
            y: Top edge of card.
            w: Card width.
            h: Card height.
            blur: Blur radius.
            tint: RGBA tint colour.
            radius: Corner radius.

        Returns:
            Self for chaining.
        """
        self._img = _glass_card(
            self._img,
            x=x,
            y=y,
            w=w,
            h=h,
            blur=blur,
            tint=tint,
            radius=radius,
        )
        return self

    def duotone(
        self,
        dark: tuple[int, int, int] = (10, 10, 40),
        light: tuple[int, int, int] = (255, 200, 50),
    ) -> EffectsPipeline:
        """Map to a duotone palette.

        Args:
            dark: RGB colour for dark tones.
            light: RGB colour for light tones.

        Returns:
            Self for chaining.
        """
        self._img = _duotone(self._img, dark_color=dark, light_color=light)
        return self

    def vignette(
        self,
        strength: float = 0.3,
        radius: float = 1.0,
    ) -> EffectsPipeline:
        """Darken the image edges.

        Args:
            strength: Maximum darkening at corners.
            radius: Normalised radius of bright centre.

        Returns:
            Self for chaining.
        """
        self._img = _vignette(self._img, strength=strength, radius=radius)
        return self

    def chromatic(
        self,
        offset: int = 5,
        direction: str = "horizontal",
    ) -> EffectsPipeline:
        """Apply chromatic aberration.

        Args:
            offset: Channel shift in pixels.
            direction: ``"horizontal"`` or ``"vertical"``.

        Returns:
            Self for chaining.
        """
        self._img = _chromatic_aberration(
            self._img,
            offset=offset,
            direction=direction,
        )
        return self

    def bloom(
        self,
        threshold: int = 200,
        radius: int = 15,
        intensity: float = 0.4,
    ) -> EffectsPipeline:
        """Add a bloom glow on bright areas.

        Args:
            threshold: Luminance cutoff.
            radius: Blur radius.
            intensity: Bloom strength.

        Returns:
            Self for chaining.
        """
        self._img = _bloom(self._img, threshold=threshold, radius=radius, intensity=intensity)
        return self

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------

    def export(self, path: str, quality: int = 95) -> Image.Image:
        """Save the current image to disk and return it.

        Args:
            path: Output file path (format inferred from extension).
            quality: JPEG/WebP quality setting (1 -- 100).

        Returns:
            The final PIL image.
        """
        self._img.save(path, quality=quality)
        return self._img

    @property
    def image(self) -> Image.Image:
        """Access the current pipeline image without saving.

        Returns:
            A copy of the internal image.
        """
        return self._img.copy()
