from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from .animation import DiceRollAnimation
from .dice_engine import build_history_line, format_modifier, roll_dice
from .styles import COLORS, DICE_PRESETS, ROLL_PRESETS, configure_ttk, configure_window, font, style_button, style_entry, ui_font
from .validators import ValidationError, validate_roll_inputs


class DiceRollerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        configure_window(root)
        configure_ttk(root)

        self.history: list[tuple[str, dict[str, Any]]] = []
        self.sides_var = tk.StringVar(value="20")
        self.modifier_var = tk.StringVar(value="+0")
        self.roll_name_var = tk.StringVar(value="Ataque")
        self.status_var = tk.StringVar(value="")
        self.natural_var = tk.StringVar(value="-")
        self.modifier_result_var = tk.StringVar(value="+0")
        self.final_var = tk.StringVar(value="-")

        self._build_layout()
        self.animation = DiceRollAnimation(self.canvas)
        self.root.after(80, lambda: self.animation.render_idle(20))
        self.root.bind("<Return>", self._on_enter)

    def _build_layout(self) -> None:
        shell = tk.Frame(self.root, bg=COLORS["bg_deep"])
        shell.pack(fill="both", expand=True, padx=20, pady=20)
        shell.grid_columnconfigure(0, weight=0, minsize=310)
        shell.grid_columnconfigure(1, weight=1)
        shell.grid_rowconfigure(1, weight=1)

        header = tk.Frame(shell, bg=COLORS["bg_deep"])
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        tk.Label(
            header,
            text="Dice Roller Arcano",
            bg=COLORS["bg_deep"],
            fg=COLORS["gold_light"],
            font=font(24, "bold"),
        ).pack(side="left")
        tk.Label(
            header,
            text="Mesa digital de fantasia",
            bg=COLORS["bg_deep"],
            fg=COLORS["text_muted"],
            font=ui_font(11),
        ).pack(side="left", padx=(18, 0), pady=(7, 0))

        controls = self._panel(shell)
        controls.grid(row=1, column=0, sticky="nsew", padx=(0, 16))
        controls.grid_columnconfigure(0, weight=1)

        self._build_controls(controls)

        stage = tk.Frame(shell, bg=COLORS["bg_deep"])
        stage.grid(row=1, column=1, sticky="nsew")
        stage.grid_rowconfigure(0, weight=1)
        stage.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            stage,
            bg=COLORS["bg_deep"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border_soft"],
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        bottom = tk.Frame(stage, bg=COLORS["bg_deep"])
        bottom.grid(row=1, column=0, sticky="ew", pady=(14, 0))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)
        self._build_result_panel(bottom)
        self._build_history_panel(bottom)

    def _build_controls(self, parent: tk.Frame) -> None:
        self._section_label(parent, "Rolagem").grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))

        form = tk.Frame(parent, bg=COLORS["panel"])
        form.grid(row=1, column=0, sticky="ew", padx=18)
        form.grid_columnconfigure(0, weight=1)

        self._field_label(form, "Lados do dado").grid(row=0, column=0, sticky="w", pady=(0, 6))
        sides_entry = tk.Entry(form, textvariable=self.sides_var)
        style_entry(sides_entry)
        sides_entry.grid(row=1, column=0, sticky="ew", ipady=9)

        dice_grid = tk.Frame(form, bg=COLORS["panel"])
        dice_grid.grid(row=2, column=0, sticky="ew", pady=(10, 16))
        for index, sides in enumerate(DICE_PRESETS):
            button = tk.Button(dice_grid, text=f"D{sides}", command=lambda value=sides: self._choose_sides(value))
            style_button(button, "secondary")
            button.grid(row=index // 3, column=index % 3, sticky="ew", padx=3, pady=3)
            dice_grid.grid_columnconfigure(index % 3, weight=1)

        self._field_label(form, "Modificador").grid(row=3, column=0, sticky="w", pady=(0, 6))
        modifier_entry = tk.Entry(form, textvariable=self.modifier_var)
        style_entry(modifier_entry)
        modifier_entry.grid(row=4, column=0, sticky="ew", ipady=9)

        modifier_steps = tk.Frame(form, bg=COLORS["panel"])
        modifier_steps.grid(row=5, column=0, sticky="ew", pady=(10, 16))
        for column, (label, amount) in enumerate((("-5", -5), ("-1", -1), ("0", 0), ("+1", 1), ("+5", 5))):
            button = tk.Button(modifier_steps, text=label, command=lambda value=amount: self._adjust_modifier(value))
            style_button(button, "secondary")
            button.grid(row=0, column=column, sticky="ew", padx=3)
            modifier_steps.grid_columnconfigure(column, weight=1)

        self._field_label(form, "Teste").grid(row=6, column=0, sticky="w", pady=(0, 6))
        roll_name = ttk.Combobox(
            form,
            textvariable=self.roll_name_var,
            values=ROLL_PRESETS,
            style="Fantasy.TCombobox",
            font=ui_font(11),
        )
        roll_name.grid(row=7, column=0, sticky="ew", ipady=5)

        self.roll_button = tk.Button(parent, text="Rolar Dado", command=self.roll)
        style_button(self.roll_button, "primary")
        self.roll_button.grid(row=2, column=0, sticky="ew", padx=18, pady=(18, 10), ipady=4)

        status = tk.Label(
            parent,
            textvariable=self.status_var,
            bg=COLORS["panel"],
            fg=COLORS["red"],
            font=ui_font(10, "bold"),
            wraplength=250,
            justify="left",
        )
        status.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 18))

        flourish = tk.Canvas(parent, height=90, bg=COLORS["panel"], bd=0, highlightthickness=0)
        flourish.grid(row=4, column=0, sticky="ew", padx=18, pady=(6, 18))
        flourish.bind("<Configure>", self._draw_control_flourish)

    def _build_result_panel(self, parent: tk.Frame) -> None:
        result_panel = self._panel(parent)
        result_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        result_panel.grid_columnconfigure((0, 1, 2), weight=1)

        self._section_label(result_panel, "Resultado").grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(14, 10))
        self._metric(result_panel, "Natural", self.natural_var).grid(row=1, column=0, sticky="nsew", padx=(16, 6), pady=(0, 16))
        self._metric(result_panel, "Mod", self.modifier_result_var).grid(row=1, column=1, sticky="nsew", padx=6, pady=(0, 16))
        self._metric(result_panel, "Final", self.final_var, large=True).grid(row=1, column=2, sticky="nsew", padx=(6, 16), pady=(0, 16))

    def _build_history_panel(self, parent: tk.Frame) -> None:
        history_panel = self._panel(parent)
        history_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        history_panel.grid_rowconfigure(1, weight=1)
        history_panel.grid_columnconfigure(0, weight=1)

        self._section_label(history_panel, "Historico").grid(row=0, column=0, sticky="w", padx=16, pady=(14, 10))
        self.history_text = tk.Text(
            history_panel,
            height=7,
            bg=COLORS["entry"],
            fg=COLORS["parchment"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border_soft"],
            padx=10,
            pady=8,
            font=ui_font(10),
            wrap="word",
            state="disabled",
        )
        self.history_text.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.history_text.tag_configure("success", foreground=COLORS["gold_light"])
        self.history_text.tag_configure("failure", foreground="#ff9b91")
        self.history_text.tag_configure("normal", foreground=COLORS["parchment"])

    def roll(self) -> None:
        if self.animation.is_rolling:
            return

        try:
            values = validate_roll_inputs(self.sides_var.get(), self.modifier_var.get(), self.roll_name_var.get())
        except ValidationError as exc:
            self.status_var.set(str(exc))
            return

        self.status_var.set("")
        sides = int(values["sides"])
        modifier = int(values["modifier"])
        roll_name = str(values["name"])
        result = roll_dice(sides, modifier)

        self.roll_button.configure(state="disabled")
        self.natural_var.set("...")
        self.modifier_result_var.set(format_modifier(modifier))
        self.final_var.set("...")
        self.animation.start_roll(result, roll_name, self._complete_roll)

    def _complete_roll(self, result: dict[str, Any]) -> None:
        self.roll_button.configure(state="normal")
        self.natural_var.set(str(result["natural_result"]))
        self.modifier_result_var.set(format_modifier(result["modifier"]))
        self.final_var.set(str(result["final_result"]))
        roll_name = self.roll_name_var.get().strip() or "Rolagem"
        self.history.insert(0, (roll_name, result))
        self.history = self.history[:12]
        self._render_history()

    def _render_history(self) -> None:
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", tk.END)
        if not self.history:
            self.history_text.insert(tk.END, "Nenhuma rolagem ainda.", "normal")
        for name, result in self.history:
            tag = "success" if result["is_critical_success"] else "failure" if result["is_critical_failure"] else "normal"
            self.history_text.insert(tk.END, build_history_line(name, result) + "\n", tag)
        self.history_text.configure(state="disabled")

    def _choose_sides(self, sides: int) -> None:
        self.sides_var.set(str(sides))
        self.animation.render_idle(sides)

    def _adjust_modifier(self, amount: int) -> None:
        if amount == 0:
            self.modifier_var.set("+0")
            return
        try:
            current = int(self.modifier_var.get().strip().replace(" ", "") or "0")
        except ValueError:
            current = 0
        self.modifier_var.set(format_modifier(current + amount))

    def _on_enter(self, _event: tk.Event) -> None:
        self.roll()

    def _on_canvas_resize(self, _event: tk.Event) -> None:
        try:
            sides = int(self.sides_var.get().strip().lstrip("Dd") or "20")
        except ValueError:
            sides = 20
        self.animation.render_idle(sides)

    def _panel(self, parent: tk.Misc) -> tk.Frame:
        panel = tk.Frame(
            parent,
            bg=COLORS["panel"],
            highlightthickness=1,
            highlightbackground=COLORS["border_soft"],
            highlightcolor=COLORS["border"],
        )
        return panel

    def _section_label(self, parent: tk.Misc, text: str) -> tk.Label:
        return tk.Label(parent, text=text.upper(), bg=COLORS["panel"], fg=COLORS["gold_light"], font=ui_font(10, "bold"))

    def _field_label(self, parent: tk.Misc, text: str) -> tk.Label:
        return tk.Label(parent, text=text, bg=COLORS["panel"], fg=COLORS["text_muted"], font=ui_font(10, "bold"))

    def _metric(self, parent: tk.Misc, label: str, variable: tk.StringVar, large: bool = False) -> tk.Frame:
        frame = tk.Frame(parent, bg=COLORS["panel_soft"], highlightthickness=1, highlightbackground=COLORS["border_soft"])
        tk.Label(frame, text=label.upper(), bg=COLORS["panel_soft"], fg=COLORS["text_muted"], font=ui_font(8, "bold")).pack(pady=(9, 0))
        tk.Label(
            frame,
            textvariable=variable,
            bg=COLORS["panel_soft"],
            fg=COLORS["gold_light"] if large else COLORS["text"],
            font=font(24 if large else 20, "bold"),
        ).pack(pady=(0, 10))
        return frame

    def _draw_control_flourish(self, event: tk.Event) -> None:
        canvas = event.widget
        canvas.delete("all")
        width = event.width
        height = event.height
        mid_y = height / 2
        canvas.create_line(8, mid_y, width - 8, mid_y, fill=COLORS["border_soft"], width=1)
        for index, radius in enumerate((32, 22, 12)):
            color = COLORS["gold"] if index == 0 else COLORS["border"]
            canvas.create_oval(width / 2 - radius, mid_y - radius, width / 2 + radius, mid_y + radius, outline=color, width=1)
        for side in (-1, 1):
            x = width / 2 + side * 64
            canvas.create_polygon(x, mid_y - 8, x + side * 16, mid_y, x, mid_y + 8, fill=COLORS["border"], outline="")


def main() -> None:
    root = tk.Tk()
    app = DiceRollerApp(root)
    app._render_history()
    root.mainloop()
