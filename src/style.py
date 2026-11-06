"""
Shared plotting style for CHMI Server Power Analysis.
Centralizes colors, matplotlib rcParams, and helper functions so every
figure in the repo looks like it belongs to the same family.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch

from pipeline import SERVER_COLOR, SERVER_LABEL

# ---------------------------------------------------------------------------
# Palette — a calm, professional "server room" theme
# ---------------------------------------------------------------------------
BG = "#0f1420"          # deep navy background
PANEL = "#171e2e"       # panel
FG = "#e6ebf5"          # near-white text
MUTED = "#8a97b0"       # muted text
GRID = "#2a3450"        # grid lines
ACCENT = "#4dd0e1"      # cyan accent

SERIES_COLORS = {
    "A": "#4fa3e3",     # Server A — blue
    "B": "#ff6b6b",     # Server B — red
}

# Custom sequential colormaps (background-aware)
CMAP_A = LinearSegmentedColormap.from_list(
    "chmi_a", ["#0f1420", "#123a63", "#1f6fb2", "#4fa3e3", "#a9d6f5"]
)
CMAP_B = LinearSegmentedColormap.from_list(
    "chmi_b", ["#0f1420", "#5c1a1a", "#a33030", "#e05555", "#ffb3b3"]
)
CMAP_DIFF = LinearSegmentedColormap.from_list(
    "chmi_diff", ["#1f6fb2", "#0f1420", "#e05555"]
)


def apply_theme(style: str = "dark") -> None:
    """Apply a global matplotlib theme."""
    if style == "dark":
        mpl.rcParams.update(
            {
                "figure.facecolor": BG,
                "axes.facecolor": PANEL,
                "savefig.facecolor": BG,
                "text.color": FG,
                "axes.labelcolor": FG,
                "axes.edgecolor": GRID,
                "xtick.color": MUTED,
                "ytick.color": MUTED,
                "axes.titlecolor": FG,
                "axes.titleweight": "bold",
                "axes.titlesize": 13,
                "axes.titlepad": 10,
                "axes.labelsize": 11,
                "axes.grid": True,
                "grid.color": GRID,
                "grid.linewidth": 0.7,
                "grid.alpha": 0.6,
                "legend.facecolor": PANEL,
                "legend.edgecolor": GRID,
                "legend.framealpha": 0.9,
                "font.size": 10,
                "font.family": "DejaVu Sans",
                "xtick.labelsize": 9,
                "ytick.labelsize": 9,
                "lines.linewidth": 1.6,
                "axes.prop_cycle": mpl.cycler(color=[SERIES_COLORS["A"], SERIES_COLORS["B"]]),
            }
        )
    else:
        mpl.rcParams.update(
            {
                "figure.facecolor": "white",
                "axes.facecolor": "white",
                "text.color": "#222",
                "axes.labelcolor": "#333",
                "axes.edgecolor": "#ccc",
                "xtick.color": "#666",
                "ytick.color": "#666",
                "axes.titlecolor": "#111",
                "axes.grid": True,
                "grid.color": "#e0e0e0",
                "grid.linewidth": 0.7,
                "legend.facecolor": "white",
                "font.size": 10,
                "font.family": "DejaVu Sans",
            }
        )


def add_branding(ax, title: str, subtitle: str | None = None, title_fs: float = 13):
    """Standard title + subtitle block on a dark theme."""
    if subtitle:
        ax.set_title(f"{title}\n{subtitle}", fontsize=title_fs, color=FG, loc="left",
                     pad=10)
    else:
        ax.set_title(title, fontsize=title_fs, color=FG, loc="left", pad=10)


def style_axes(ax, remove_top_right: bool = True) -> None:
    """Consistent axis styling."""
    if remove_top_right:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    for sp in ax.spines.values():
        sp.set_color(GRID)


def save(fig, path, dpi=150):
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[figure] {path}")


# ---------------------------------------------------------------------------
# Helpers used by many figures
# ---------------------------------------------------------------------------
def rolling(df: pd.DataFrame, window: int = 24 * 7, min_periods: int = 1) -> pd.Series:
    """Weekly rolling mean of the load series."""
    return df["load"].rolling(window, min_periods=min_periods, center=True).mean()


def to_energy(df: pd.DataFrame, watts_per_unit: float = 1.0) -> float:
    """Integrate hourly power readings to energy (kWh-equivalent) over the span.

    The raw 'load' column is an arbitrary load indicator (not a calibrated
    wattage). We still compute a relative energy index = sum(load) * 1h.
    """
    return float(df["load"].sum())


def daily_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Average load by hour-of-day, split weekday/weekend."""
    return (
        df.groupby(["hour", "weekend_label"])["load"]
        .mean()
        .unstack()
        .reindex(columns=["Weekday", "Weekend"])
    )
