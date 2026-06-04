from __future__ import annotations

import math
import random
import tkinter as tk
from typing import Any, Callable

from .styles import COLORS, font, ui_font


class DiceRollAnimation:
    """Canvas-based dice roll animation with a fantasy tabletop mood."""

    def __init__(self, canvas: tk.Canvas) -> None:
        self.canvas = canvas
        self._rng = random.Random()
        self._after_id: str | None = None
        self._is_rolling = False
        self._frame = 0
        self._reveal_frame = 0
        self._total_frames = 48
        self._result: dict[str, Any] | None = None
        self._on_complete: Callable[[dict[str, Any]], None] | None = None
        self._particles = self._make_particles()
        self._idle_sides = 20

    @property
    def is_rolling(self) -> bool:
        return self._is_rolling

    def cancel(self) -> None:
        if self._after_id is not None:
            self.canvas.after_cancel(self._after_id)
            self._after_id = None
        self._is_rolling = False

    def render_idle(self, sides: int | None = None) -> None:
        if self._is_rolling:
            return
        if sides is not None:
            self._idle_sides = sides
        self._draw_scene(
            number_text=f"D{self._idle_sides}",
            title="DADO ARCANO",
            subtitle="",
            progress=0.0,
            rotation=0.0,
            mood="idle",
        )

    def start_roll(
        self,
        result: dict[str, Any],
        roll_name: str,
        on_complete: Callable[[dict[str, Any]], None],
    ) -> None:
        self.cancel()
        self._is_rolling = True
        self._frame = 0
        self._reveal_frame = 0
        self._result = result
        self._on_complete = on_complete
        self._particles = self._make_particles(80)
        self._roll_name = roll_name
        self._tick_roll()

    def _tick_roll(self) -> None:
        if not self._result:
            return

        progress = min(self._frame / self._total_frames, 1.0)
        sides = int(self._result["sides"])
        if self._frame >= self._total_frames:
            number = str(self._result["natural_result"])
        else:
            number = str(self._rng.randint(1, sides))

        easing = 1 - (1 - progress) ** 3
        rotation = self._frame * 0.28 + easing * 2.2
        self._draw_scene(
            number_text=number,
            title=f"ROLANDO D{sides}",
            subtitle=self._roll_name,
            progress=progress,
            rotation=rotation,
            mood="rolling",
        )

        self._frame += 1
        if self._frame <= self._total_frames:
            delay = int(20 + 125 * (progress**2.55))
            self._after_id = self.canvas.after(delay, self._tick_roll)
        else:
            self._after_id = self.canvas.after(90, self._tick_reveal)

    def _tick_reveal(self) -> None:
        if not self._result:
            return

        reveal_total = 30
        progress = min(self._reveal_frame / reveal_total, 1.0)
        mood = "success" if self._result["is_critical_success"] else "failure" if self._result["is_critical_failure"] else "final"
        title = "RESULTADO FINAL"
        if mood == "success":
            title = "ACERTO CRITICO!"
        elif mood == "failure":
            title = "FALHA CRITICA!"

        self._draw_scene(
            number_text=str(self._result["natural_result"]),
            title=title,
            subtitle=f"Total: {self._result['final_result']}",
            progress=progress,
            rotation=2.2 + progress * 0.35,
            mood=mood,
            final=True,
        )

        self._reveal_frame += 1
        if self._reveal_frame <= reveal_total:
            self._after_id = self.canvas.after(34, self._tick_reveal)
            return

        self._is_rolling = False
        completed = self._result
        callback = self._on_complete
        self._after_id = None
        if callback:
            callback(completed)

    def _size(self) -> tuple[int, int]:
        width = max(self.canvas.winfo_width(), 620)
        height = max(self.canvas.winfo_height(), 420)
        return width, height

    def _draw_scene(
        self,
        *,
        number_text: str,
        title: str,
        subtitle: str,
        progress: float,
        rotation: float,
        mood: str,
        final: bool = False,
    ) -> None:
        width, height = self._size()
        cx = width / 2
        cy = height / 2 + 4

        shake = 0.0
        if mood == "rolling":
            shake = math.sin(self._frame * 1.85) * (1 - progress) * 8
        elif mood == "failure":
            shake = math.sin(self._reveal_frame * 2.2) * (1 - progress) * 7

        cx += shake
        cy += math.cos(rotation * 1.7) * (1 - progress) * 3

        self.canvas.delete("all")
        self._draw_background(width, height, mood)
        self._draw_particles(cx, cy, width, height, mood, rotation, progress, final)
        self._draw_magic_circle(cx, cy, mood, rotation, progress)
        self._draw_die(cx, cy, mood, rotation, progress, final)
        self._draw_number(cx, cy, number_text, mood, final)
        self._draw_titles(width, height, title, subtitle, mood, final)

    def _draw_background(self, width: int, height: int, mood: str) -> None:
        top = COLORS["bg_deep"]
        bottom = COLORS["bg_mid"]
        if mood == "success":
            bottom = "#241b0a"
        elif mood == "failure":
            bottom = "#1f090d"

        steps = max(height // 4, 1)
        for i in range(steps):
            ratio = i / steps
            color = self._mix(top, bottom, ratio)
            y0 = i * 4
            self.canvas.create_rectangle(0, y0, width, y0 + 5, fill=color, outline=color)

        self.canvas.create_rectangle(14, 14, width - 14, height - 14, outline=COLORS["border_soft"], width=2)
        self.canvas.create_rectangle(22, 22, width - 22, height - 22, outline=COLORS["border"], width=1)

        for x in range(38, width, 72):
            self.canvas.create_line(x, 24, x + 24, 24, fill=COLORS["border_soft"], width=1)
            self.canvas.create_line(x, height - 24, x + 24, height - 24, fill=COLORS["border_soft"], width=1)

    def _draw_particles(
        self,
        cx: float,
        cy: float,
        width: int,
        height: int,
        mood: str,
        rotation: float,
        progress: float,
        final: bool,
    ) -> None:
        if mood == "success":
            primary = COLORS["gold_light"]
            secondary = COLORS["gold"]
        elif mood == "failure":
            primary = COLORS["red"]
            secondary = "#7f2328"
        else:
            primary = COLORS["gold"]
            secondary = COLORS["bronze"]

        burst = 1.0 + (1 - abs(progress - 0.22)) * 0.28 if final else 1.0
        for particle in self._particles:
            angle = particle["angle"] + rotation * particle["speed"]
            radius = particle["radius"] * burst
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius * 0.64
            if 28 < x < width - 28 and 28 < y < height - 28:
                size = particle["size"] * (1.2 if final else 1.0)
                color = primary if particle["twinkle"] > math.sin(rotation + particle["phase"]) else secondary
                self.canvas.create_oval(x - size, y - size, x + size, y + size, fill=color, outline="")

    def _draw_magic_circle(self, cx: float, cy: float, mood: str, rotation: float, progress: float) -> None:
        color = COLORS["gold"]
        if mood == "failure":
            color = COLORS["red"]
        elif mood == "success":
            color = COLORS["gold_light"]

        pulse = 1 + math.sin(rotation * 2.3) * 0.025
        base = 154 * pulse
        for index, radius in enumerate((base, base * 0.78, base * 1.17)):
            start = (rotation * 35 + index * 60) % 360
            extent = 260 if index != 1 else -220
            self.canvas.create_arc(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                start=start,
                extent=extent,
                outline=color,
                width=2 if index == 0 else 1,
                style=tk.ARC,
            )

        for index in range(12):
            angle = rotation + index * math.tau / 12
            r1 = base * 0.9
            r2 = base * (1.03 + 0.08 * (index % 2))
            x1 = cx + math.cos(angle) * r1
            y1 = cy + math.sin(angle) * r1
            x2 = cx + math.cos(angle) * r2
            y2 = cy + math.sin(angle) * r2
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=1)

        if mood in {"success", "failure"}:
            glow = COLORS["gold_light"] if mood == "success" else COLORS["red"]
            spread = 184 + math.sin(progress * math.pi) * 18
            self.canvas.create_oval(cx - spread, cy - spread, cx + spread, cy + spread, outline=glow, width=3)

    def _draw_die(self, cx: float, cy: float, mood: str, rotation: float, progress: float, final: bool) -> None:
        radius = 102 + (math.sin(progress * math.pi) * 10 if final else 0)
        vertices = 8
        points = self._polygon_points(cx, cy, radius, vertices, rotation)
        shadow = [(x + 8, y + 10) for x, y in points]

        self.canvas.create_polygon(self._flatten(shadow), fill=COLORS["shadow"], outline="")
        outline = COLORS["gold_light"] if mood == "success" else COLORS["red"] if mood == "failure" else COLORS["gold"]
        fill = "#211721" if mood != "failure" else "#281116"
        self.canvas.create_polygon(self._flatten(points), fill=fill, outline=outline, width=3)

        center = (cx, cy)
        facet_colors = ["#322335", "#211722", "#3a2a2a", "#19111a"]
        if mood == "success":
            facet_colors = ["#473519", "#2d2212", "#5b421b", "#21180b"]
        elif mood == "failure":
            facet_colors = ["#37151a", "#220b10", "#531b22", "#16070b"]

        for index in range(vertices):
            p1 = points[index]
            p2 = points[(index + 1) % vertices]
            color = facet_colors[index % len(facet_colors)]
            self.canvas.create_polygon(cx, cy, p1[0], p1[1], p2[0], p2[1], fill=color, outline=COLORS["border_soft"])

        inner = self._polygon_points(cx, cy, radius * 0.55, 4, -rotation * 0.7)
        self.canvas.create_polygon(self._flatten(inner), fill="#120d13", outline=outline, width=1)
        self.canvas.create_oval(cx - 18, cy - 18, cx + 18, cy + 18, outline=COLORS["border"], width=1)

        for point in points[::2]:
            self.canvas.create_line(center[0], center[1], point[0], point[1], fill=COLORS["border"], width=1)

    def _draw_number(self, cx: float, cy: float, number_text: str, mood: str, final: bool) -> None:
        fill = COLORS["text"]
        if mood == "success":
            fill = COLORS["gold_light"]
        elif mood == "failure":
            fill = "#ffb4aa"

        if final:
            self.canvas.create_text(cx + 3, cy + 5, text=number_text, fill=COLORS["shadow"], font=font(54, "bold"))
            self.canvas.create_text(cx, cy, text=number_text, fill=fill, font=font(54, "bold"))
        else:
            self.canvas.create_text(cx + 2, cy + 4, text=number_text, fill=COLORS["shadow"], font=font(46, "bold"))
            self.canvas.create_text(cx, cy, text=number_text, fill=fill, font=font(46, "bold"))

    def _draw_titles(self, width: int, height: int, title: str, subtitle: str, mood: str, final: bool) -> None:
        color = COLORS["gold_light"] if mood == "success" else COLORS["red"] if mood == "failure" else COLORS["parchment"]
        title_size = 18 if final else 15
        self.canvas.create_text(width / 2, 54, text=title, fill=color, font=font(title_size, "bold"))
        if subtitle:
            self.canvas.create_text(width / 2, height - 52, text=subtitle, fill=COLORS["text_muted"], font=ui_font(12))

    def _make_particles(self, amount: int = 58) -> list[dict[str, float]]:
        return [
            {
                "angle": self._rng.uniform(0, math.tau),
                "radius": self._rng.uniform(80, 238),
                "speed": self._rng.uniform(-0.45, 0.55),
                "size": self._rng.uniform(1.1, 3.0),
                "phase": self._rng.uniform(0, math.tau),
                "twinkle": self._rng.uniform(-0.6, 0.6),
            }
            for _ in range(amount)
        ]

    @staticmethod
    def _polygon_points(cx: float, cy: float, radius: float, vertices: int, rotation: float) -> list[tuple[float, float]]:
        points = []
        for index in range(vertices):
            angle = rotation + index * math.tau / vertices - math.pi / 2
            wobble = 0.9 + (0.12 if index % 2 == 0 else -0.04)
            x = cx + math.cos(angle) * radius * wobble
            y = cy + math.sin(angle) * radius * wobble * 0.86
            points.append((x, y))
        return points

    @staticmethod
    def _flatten(points: list[tuple[float, float]]) -> list[float]:
        return [coordinate for point in points for coordinate in point]

    @staticmethod
    def _hex_to_rgb(color: str) -> tuple[int, int, int]:
        color = color.lstrip("#")
        return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)

    @classmethod
    def _mix(cls, a: str, b: str, ratio: float) -> str:
        ar, ag, ab = cls._hex_to_rgb(a)
        br, bg, bb = cls._hex_to_rgb(b)
        rr = int(ar + (br - ar) * ratio)
        rg = int(ag + (bg - ag) * ratio)
        rb = int(ab + (bb - ab) * ratio)
        return f"#{rr:02x}{rg:02x}{rb:02x}"
