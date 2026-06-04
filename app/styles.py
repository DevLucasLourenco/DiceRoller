from __future__ import annotations

import tkinter as tk
from tkinter import ttk


COLORS = {
    "bg_deep": "#08070b",
    "bg_mid": "#151019",
    "panel": "#1d1720",
    "panel_raised": "#2a2028",
    "panel_soft": "#221b20",
    "border": "#8a6431",
    "border_soft": "#4a3822",
    "gold": "#d9a441",
    "gold_light": "#f7d88a",
    "bronze": "#a8662a",
    "parchment": "#ead9b0",
    "text": "#f6efe1",
    "text_muted": "#b7a88d",
    "red": "#c94f46",
    "red_dark": "#4f1518",
    "green": "#72a667",
    "shadow": "#050307",
    "entry": "#100d12",
}

DICE_PRESETS = (4, 5, 6, 8, 10, 12, 20, 50, 100)

ROLL_PRESETS = (
    "Ataque",
    "Teste de Forca",
    "Teste de Destreza",
    "Teste de Carisma",
    "Percepcao",
    "Iniciativa",
    "Dano",
    "Teste personalizado",
)

FONT_FAMILY = "Georgia"
FONT_FALLBACK = "Segoe UI"


def configure_window(root: tk.Tk) -> None:
    root.title("Dice Roller Arcano")
    root.geometry("1080x740")
    root.minsize(920, 640)
    root.configure(bg=COLORS["bg_deep"])


def configure_ttk(root: tk.Tk) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "Fantasy.TCombobox",
        fieldbackground=COLORS["entry"],
        background=COLORS["panel_raised"],
        foreground=COLORS["text"],
        arrowcolor=COLORS["gold"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["shadow"],
        padding=7,
    )
    style.map(
        "Fantasy.TCombobox",
        fieldbackground=[("readonly", COLORS["entry"])],
        foreground=[("readonly", COLORS["text"])],
    )


def font(size: int, weight: str = "normal", family: str = FONT_FAMILY) -> tuple[str, int, str]:
    return (family, size, weight)


def ui_font(size: int, weight: str = "normal") -> tuple[str, int, str]:
    return (FONT_FALLBACK, size, weight)


def style_button(button: tk.Button, variant: str = "primary") -> None:
    if variant == "primary":
        bg = COLORS["gold"]
        fg = "#171008"
        active = COLORS["gold_light"]
        border = COLORS["gold_light"]
    elif variant == "danger":
        bg = COLORS["red_dark"]
        fg = COLORS["text"]
        active = COLORS["red"]
        border = COLORS["red"]
    else:
        bg = COLORS["panel_raised"]
        fg = COLORS["parchment"]
        active = COLORS["border_soft"]
        border = COLORS["border"]

    button.configure(
        bg=bg,
        fg=fg,
        activebackground=active,
        activeforeground=fg,
        relief="flat",
        bd=0,
        cursor="hand2",
        highlightthickness=1,
        highlightbackground=border,
        highlightcolor=border,
        font=ui_font(10, "bold"),
        padx=12,
        pady=8,
    )


def style_entry(entry: tk.Entry) -> None:
    entry.configure(
        bg=COLORS["entry"],
        fg=COLORS["text"],
        insertbackground=COLORS["gold_light"],
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=COLORS["border_soft"],
        highlightcolor=COLORS["gold"],
        font=ui_font(12),
    )
