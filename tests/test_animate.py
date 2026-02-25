"""Tests for the animate module."""

from __future__ import annotations

import os
import tempfile

import pytest
from PIL import Image

from ideamaxfx.animate import (
    linear,
    ease_out_cubic,
    ease_out_elastic,
    ease_out_bounce,
    get_easing,
    bar_grow,
    line_draw,
    radar_sweep,
    scatter_fade,
    counter_roll,
    pie_fill,
    heatmap_reveal,
    network_build,
    morph,
    stagger_delays,
    compose_animations,
    export_gif,
    export_apng,
)


class TestEasing:
    def test_linear(self) -> None:
        assert linear(0.0) == 0.0
        assert linear(0.5) == 0.5
        assert linear(1.0) == 1.0

    def test_ease_out_cubic_bounds(self) -> None:
        assert ease_out_cubic(0.0) == pytest.approx(0.0, abs=0.01)
        assert ease_out_cubic(1.0) == pytest.approx(1.0, abs=0.01)

    def test_ease_out_elastic(self) -> None:
        assert ease_out_elastic(0.0) == 0.0
        assert ease_out_elastic(1.0) == 1.0

    def test_ease_out_bounce(self) -> None:
        assert ease_out_bounce(0.0) == pytest.approx(0.0, abs=0.01)
        assert ease_out_bounce(1.0) == pytest.approx(1.0, abs=0.01)

    def test_get_easing_valid(self) -> None:
        fn = get_easing("linear")
        assert fn(0.5) == 0.5

    def test_get_easing_invalid(self) -> None:
        with pytest.raises(ValueError):
            get_easing("nonexistent")


class TestBarGrow:
    def test_generates_frames(self) -> None:
        frames = bar_grow(
            labels=["A", "B", "C"],
            values=[10, 20, 30],
            fps=10,
            duration=0.5,
            hold_seconds=0.2,
        )
        assert len(frames) > 0
        assert all(isinstance(f, Image.Image) for f in frames)

    def test_frame_dimensions(self) -> None:
        frames = bar_grow(
            labels=["X"], values=[50],
            width=400, height=300,
            fps=5, duration=0.3, hold_seconds=0.1,
        )
        assert frames[0].size == (400, 300)

    def test_custom_easing(self) -> None:
        frames = bar_grow(
            labels=["A", "B"],
            values=[68, 72],
            colors=["#d4213d", "#006633"],
            fps=10, duration=0.3, hold_seconds=0.1,
            easing="ease_out_elastic",
        )
        assert len(frames) > 0


class TestLineDraw:
    def test_single_series(self) -> None:
        frames = line_draw(
            x_values=[1, 2, 3, 4],
            y_values=[10, 20, 15, 25],
            fps=5, duration=0.3, hold_seconds=0.1,
        )
        assert len(frames) > 0

    def test_multi_series(self) -> None:
        frames = line_draw(
            x_values=[1, 2, 3],
            y_values=[[10, 20, 30], [5, 15, 25]],
            fps=5, duration=0.3, hold_seconds=0.1,
        )
        assert len(frames) > 0


class TestRadarSweep:
    def test_generates_frames(self) -> None:
        frames = radar_sweep(
            categories=["A", "B", "C", "D"],
            values=[80, 60, 90, 70],
            fps=5, duration=0.3, hold_seconds=0.1,
        )
        assert len(frames) > 0


class TestScatterFade:
    def test_generates_frames(self) -> None:
        frames = scatter_fade(
            x_values=[1, 2, 3, 4, 5],
            y_values=[5, 3, 8, 2, 7],
            fps=5, duration=0.3, hold_seconds=0.1,
        )
        assert len(frames) > 0


class TestCounterRoll:
    def test_generates_frames(self) -> None:
        frames = counter_roll(
            start=0, end=100,
            fps=5, duration=0.3, hold_seconds=0.1,
        )
        assert len(frames) > 0

    def test_with_prefix_suffix(self) -> None:
        frames = counter_roll(
            start=0, end=99.9, prefix="$", suffix="%", decimals=1,
            fps=5, duration=0.3, hold_seconds=0.1,
        )
        assert len(frames) > 0


class TestPieFill:
    def test_generates_frames(self) -> None:
        frames = pie_fill(
            labels=["A", "B", "C"],
            values=[30, 50, 20],
            fps=5, duration=0.3, hold_seconds=0.1,
        )
        assert len(frames) > 0

    def test_donut(self) -> None:
        frames = pie_fill(
            labels=["X", "Y"],
            values=[60, 40],
            donut=True,
            fps=5, duration=0.3, hold_seconds=0.1,
        )
        assert len(frames) > 0


class TestHeatmapReveal:
    def test_generates_frames(self) -> None:
        data = [[10, 20, 30], [40, 50, 60]]
        frames = heatmap_reveal(
            data=data,
            fps=5, duration=0.3, hold_seconds=0.1,
        )
        assert len(frames) > 0


class TestNetworkBuild:
    def test_generates_frames(self) -> None:
        nodes = [("A", 0.2, 0.3), ("B", 0.8, 0.3), ("C", 0.5, 0.8)]
        edges = [(0, 1, 1.0), (1, 2, 0.5), (0, 2, 0.8)]
        frames = network_build(
            nodes=nodes, edges=edges,
            fps=5, duration=0.5, hold_seconds=0.1,
        )
        assert len(frames) > 0


class TestMorph:
    def test_crossfade(self) -> None:
        img1 = Image.new("RGB", (100, 100), (255, 0, 0))
        img2 = Image.new("RGB", (100, 100), (0, 0, 255))
        frames = morph(img1, img2, fps=5, duration=0.3, hold_seconds=0.1)
        assert len(frames) > 0


class TestStagger:
    def test_sequential(self) -> None:
        delays = stagger_delays(5, total_duration=1.0, overlap=0.0)
        assert len(delays) == 5
        assert delays[0] == 0.0
        assert delays[-1] == pytest.approx(1.0, abs=0.01)

    def test_reverse(self) -> None:
        delays = stagger_delays(3, total_duration=1.0, overlap=0.0, order="reverse")
        assert delays[0] > delays[-1]


class TestComposer:
    def test_sequence(self) -> None:
        frames1 = [Image.new("RGB", (50, 50), (255, 0, 0))] * 3
        frames2 = [Image.new("RGB", (50, 50), (0, 0, 255))] * 2
        result = compose_animations([frames1, frames2], layout="sequence")
        assert len(result) == 5

    def test_side_by_side(self) -> None:
        frames1 = [Image.new("RGB", (50, 50), (255, 0, 0))] * 3
        frames2 = [Image.new("RGB", (50, 50), (0, 0, 255))] * 3
        result = compose_animations([frames1, frames2], layout="side_by_side")
        assert len(result) == 3
        assert result[0].width == 100


class TestExport:
    def test_export_gif(self) -> None:
        frames = [Image.new("RGB", (50, 50), (i * 25, 0, 0)) for i in range(5)]
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as f:
            path = f.name
        try:
            result = export_gif(frames, path, fps=5)
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_export_apng(self) -> None:
        frames = [Image.new("RGB", (50, 50), (0, i * 25, 0)) for i in range(5)]
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            result = export_apng(frames, path, fps=5)
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_export_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            export_gif([], "dummy.gif")
