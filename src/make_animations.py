"""
CHMI Server Power Analysis — animations
=======================================
Creates MP4 (and GIF) animations into animations/ using matplotlib + ffmpeg.

Animations:
  1. power_sweep        — rolling window over the full record, both servers
  2. hour_clock         — average load as a "day clock" spinning through hours
  3. heatmap_evolve     — hour×weekday heatmap that builds up month by month
  4. calendar_year      — monthly calendar heatmap that fills in day by day
  5. distribution_evolve— KDE distribution that grows as more data arrives

Run:  python src/make_animations.py
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib as mpl
import matplotlib.animation as animation
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize

from pipeline import build_all, SERVER_LABEL
from style import apply_theme, add_branding, style_axes, save, SERIES_COLORS, BG, PANEL, FG, MUTED, GRID

ROOT = Path(__file__).resolve().parent.parent
ANIM = ROOT / "animations"

servers = build_all()
A, B = servers["A"], servers["B"]

# Downsample for animation performance (sample every N hours for sweep)
sweep_sample = 4


def _writer(fps=30):
    return animation.FFMpegWriter(fps=fps, bitrate=2400)


# ---------------------------------------------------------------------------
# 1. Power sweep — sliding window over full record
# ---------------------------------------------------------------------------
def anim_power_sweep():
    """Reveal-history: the record grows left→right as the date advances."""
    apply_theme("dark")
    common = A.index.intersection(B.index)
    idx = common[::sweep_sample]
    x = idx
    fig, ax = plt.subplots(figsize=(14, 6))
    lines = {}
    fill = {}
    # Seed each fill with one real point so it is registered in the axes,
    # then update its vertices in-place each frame (avoids remove() bookkeeping).
    x0 = mdates.date2num(idx[0])
    for name in servers:
        (ln,) = ax.plot([], [], lw=1.6, color=SERIES_COLORS[name], label=SERVER_LABEL[name])
        (rm,) = ax.plot([], [], lw=2.8, color=SERIES_COLORS[name], alpha=0.95)
        fl = ax.fill_between([x0, x0], [0, 0], color=SERIES_COLORS[name], alpha=0.10, lw=0)
        lines[name] = (ln, rm)
        fill[name] = fl

    ax.set_xlim(common.min(), common.max())
    ax.set_ylim(min(A["load"].min(), B["load"].min()) - 60,
                max(A["load"].max(), B["load"].max()) + 60)
    ax.set_ylabel("Load index")
    add_branding(ax, "CHMI Server Power — data accumulation",
                 "Hourly load with 7-day rolling mean · the record reveals itself over time")
    ax.legend(loc="upper right", fontsize=8.5)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    style_axes(ax)

    date_text = ax.text(0.99, 0.04, "", transform=ax.transAxes, ha="right",
                        color=FG, fontsize=12, fontweight="bold")
    n = len(x)

    def init():
        for name in lines:
            lines[name][0].set_data([], [])
            lines[name][1].set_data([], [])
        return []

    def update(i):
        sl = idx[:i + 1]
        for name, df in servers.items():
            sub = df.loc[sl]
            lines[name][0].set_data(sub.index, sub["load"])
            rm = sub["load"].rolling(24 * 7, min_periods=1, center=True).mean()
            lines[name][1].set_data(sub.index, rm)
            # Update the fill polygon in place (x must be numeric for set_verts)
            xs = mdates.date2num(sub.index)
            ys = sub["load"].values
            verts = [list(zip(xs, ys)) + list(zip(xs[::-1], np.zeros_like(ys)))]
            fill[name].set_verts(verts)
        date_text.set_text(x[i].strftime("%b %d, %Y"))
        return [ln for pair in lines.values() for ln in pair] + [date_text]

    ani = animation.FuncAnimation(fig, update, frames=n, init_func=init,
                                  blit=False, interval=25)
    path = ANIM / "01_power_sweep.mp4"
    ani.save(path, writer=_writer(fps=15))
    plt.close(fig)
    print(f"[animation] {path}")


# ---------------------------------------------------------------------------
# 2. Hour clock — average load as a spinning dial
# ---------------------------------------------------------------------------
def anim_hour_clock():
    apply_theme("dark")
    # Average load by hour-of-day (full record), separately weekend/weekday
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), subplot_kw={"projection": "polar"})
    angles = np.linspace(0, 2 * np.pi, 24, endpoint=False)

    for ax, (name, df) in zip(axes, servers.items()):
        prof = df.groupby(["hour", "weekend_label"])["load"].mean().unstack()
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_xticks(angles)
        ax.set_xticklabels([f"{h}:00" for h in range(24)], color=MUTED, fontsize=7)
        ax.set_facecolor(PANEL)
        ax.grid(color=GRID, alpha=0.6)
        ax.set_title(SERVER_LABEL[name], color=FG, fontweight="bold")

    ax_text = axes[0].text(0, 0, "", ha="center", va="center", color=FG, fontsize=12)

    weekday = {"A": None, "B": None}
    weekend = {"A": None, "B": None}
    for name, df in servers.items():
        prof = df.groupby(["hour", "weekend_label"])["load"].mean().unstack()
        weekday[name] = prof["Weekday"].values
        weekend[name] = prof["Weekend"].values

    rmax = max(max(weekday["A"]), max(weekday["B"]), max(weekend["A"]), max(weekend["B"])) * 1.15

    def init():
        return []

    def update(i):
        # i in 0..47: first 24 = weekday ring, next 24 = weekend ring
        mode = "Weekday" if i < 24 else "Weekend"
        h = i % 24
        for ax, name in zip(axes, ["A", "B"]):
            vals = weekday[name] if mode == "Weekday" else weekend[name]
            ax.clear()
            ax.set_theta_zero_location("N")
            ax.set_theta_direction(-1)
            ax.set_xticks(angles)
            ax.set_xticklabels([f"{h2}:00" for h2 in range(24)], color=MUTED, fontsize=7)
            ax.set_facecolor(PANEL)
            ax.grid(color=GRID, alpha=0.6)
            ax.set_ylim(0, rmax)
            ax.set_title(f"{SERVER_LABEL[name]} · {mode}", color=FG, fontweight="bold")
            # draw ring up to hour h
            up_to = h + 1
            ax.plot(angles[:up_to], vals[:up_to], color=SERIES_COLORS[name], lw=2.4)
            ax.fill(angles[:up_to], vals[:up_to], color=SERIES_COLORS[name], alpha=0.2)
            # current point
            ax.scatter([angles[h]], [vals[h]], color="#ffffff", s=50, zorder=5)
        ax_text.set_text(f"{mode} · {h:02d}:00")
        ax_text.set_position((0, 0))
        return [ax_text]

    ani = animation.FuncAnimation(fig, update, frames=48, init_func=init,
                                  blit=False, interval=300)
    path = ANIM / "02_hour_clock.mp4"
    ani.save(path, writer=_writer(fps=10))
    plt.close(fig)
    print(f"[animation] {path}")


# ---------------------------------------------------------------------------
# 3. Heatmap evolution — hour×weekday heatmap built up over months
# ---------------------------------------------------------------------------
def anim_heatmap_evolve():
    apply_theme("dark")
    months = list(range(1, 13))
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    ims = {}
    for ax, name in zip(axes, ["A", "B"]):
        ax.set_yticks(range(7))
        ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        ax.set_xticks(range(0, 24, 2))
        ax.set_xlabel("Hour of day")
        ax.set_title(SERVER_LABEL[name], color=FG, fontweight="bold")
        style_axes(ax)
        cmap = "Blues" if name == "A" else "Reds"
        ims[name] = ax.imshow(np.zeros((7, 24)), aspect="auto", cmap=cmap)

    fig.colorbar(ims["A"], ax=axes[0], fraction=0.046, pad=0.03)
    fig.colorbar(ims["B"], ax=axes[1], fraction=0.046, pad=0.03)
    title = fig.suptitle("", color=FG, fontweight="bold")
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",
                   "Aug", "Sep", "Oct", "Nov", "Dec"]

    cum = {}
    for name, df in servers.items():
        cum[name] = []
        for m in months:
            sub = df[df["month"] <= m]
            p = sub.pivot_table(index="weekday", columns="hour", values="load",
                                aggfunc="mean").reindex(range(7))
            cum[name].append(p.iloc[::-1])

    def update(i):
        m = months[i]
        for name in ["A", "B"]:
            p = cum[name][i]
            vmin = p.min().min()
            vmax = p.max().max()
            ims[name].set_data(p.values)
            ims[name].set_clim(vmin, vmax)
        title.set_text(f"Cumulative mean load up to {month_names[m-1]}")
        return [ims["A"], ims["B"], title]

    ani = animation.FuncAnimation(fig, update, frames=12, interval=600, blit=False)
    path = ANIM / "03_heatmap_evolve.mp4"
    ani.save(path, writer=_writer(fps=4))
    plt.close(fig)
    print(f"[animation] {path}")


# ---------------------------------------------------------------------------
# 4. Calendar fill — day-by-day calendar heatmap
# ---------------------------------------------------------------------------
def anim_calendar_fill():
    apply_theme("dark")
    # Take a single representative month (e.g., Jan 2026) and animate filling days
    month = 1
    year = 2026
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    ims = {}
    for ax, name in zip(axes, ["A", "B"]):
        ax.set_xlabel("Day of month")
        ax.set_title(SERVER_LABEL[name], color=FG, fontweight="bold")
        style_axes(ax)
        ims[name] = ax.imshow(np.full((1, 31), np.nan), aspect="auto",
                              cmap="viridis", vmin=0, vmax=600)
    title = fig.suptitle("", color=FG, fontweight="bold")

    # For each server, the daily mean load for January
    daily = {}
    for name, df in servers.items():
        sub = df[(df["month"] == month) & (df.index.year == year)]
        d = sub.groupby("day")["load"].mean().reindex(range(1, 32))
        daily[name] = d.values

    def update(i):
        # i = number of days revealed (1..31)
        for name in ["A", "B"]:
            vals = daily[name].copy()
            revealed = np.full(31, np.nan)
            revealed[:i] = vals[:i]
            ims[name].set_data(revealed.reshape(1, -1))
            finite = vals[:i][~np.isnan(vals[:i])]
            if len(finite):
                ims[name].set_clim(finite.min(), finite.max())
        title.set_text(f"January {year} — day {i} revealed")
        return [ims["A"], ims["B"], title]

    ani = animation.FuncAnimation(fig, update, frames=32, interval=300, blit=False)
    path = ANIM / "04_calendar_fill.mp4"
    ani.save(path, writer=_writer(fps=6))
    plt.close(fig)
    print(f"[animation] {path}")


# ---------------------------------------------------------------------------
# 5. Distribution evolution — KDE grows over time
# ---------------------------------------------------------------------------
def anim_distribution_evolve():
    from scipy import stats
    apply_theme("dark")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlabel("Load index")
    ax.set_ylabel("Density")
    add_branding(ax, "Load distribution — growing with data",
                 "KDE as the observation window expands")
    style_axes(ax)
    lines = {}
    for name in ["A", "B"]:
        (ln,) = ax.plot([], [], lw=2.6, color=SERIES_COLORS[name], label=SERVER_LABEL[name])
        lines[name] = ln
    ax.legend(loc="upper right", fontsize=8.5)
    date_text = ax.text(0.99, 0.04, "", transform=ax.transAxes, ha="right",
                        color=FG, fontsize=11)

    # monthly expansion points
    month_starts = pd.date_range(A.index.min(), A.index.max(), freq="MS")
    n = len(month_starts)

    def init():
        return []

    def update(i):
        cutoff = month_starts[i]
        for name, df in servers.items():
            sub = df[df.index <= cutoff]["load"]
            if len(sub) > 10:
                kde_x = np.linspace(sub.min(), sub.max(), 200)
                kde = stats.gaussian_kde(sub)(kde_x)
                lines[name].set_data(kde_x, kde)
            else:
                lines[name].set_data([], [])
        date_text.set_text(f"Through {cutoff.strftime('%b %Y')}")
        return list(lines.values()) + [date_text]

    ani = animation.FuncAnimation(fig, update, frames=n, init_func=init,
                                  blit=False, interval=150)
    path = ANIM / "05_distribution_evolve.mp4"
    ani.save(path, writer=_writer(fps=8))
    plt.close(fig)
    print(f"[animation] {path}")


if __name__ == "__main__":
    mpl.use("Agg")
    os.makedirs(ANIM, exist_ok=True)
    anim_power_sweep()
    anim_hour_clock()
    anim_heatmap_evolve()
    anim_calendar_fill()
    anim_distribution_evolve()
    print("ALL ANIMATIONS DONE")
