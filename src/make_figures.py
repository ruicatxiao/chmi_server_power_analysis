"""
CHMI Server Power Analysis — static figures
===========================================
Generates the full suite of publication-quality static figures into figures/.
Run from the repo root:  python src/make_figures.py
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize, TwoSlopeNorm
from scipy import stats

from pipeline import build_all, SERVER_COLOR, SERVER_LABEL
from style import (
    apply_theme,
    add_branding,
    style_axes,
    save,
    SERIES_COLORS,
    CMAP_A,
    CMAP_B,
    CMAP_DIFF,
    BG,
    PANEL,
    FG,
    MUTED,
    GRID,
)

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"

servers = build_all()
A, B = servers["A"], servers["B"]

# Combined long frame for anything that needs both
comb = pd.concat(servers.values())


def _figsize(w=12, h=6):
    return (w, h)


# ---------------------------------------------------------------------------
# 1. Full time series
# ---------------------------------------------------------------------------
def fig_timeseries():
    apply_theme("dark")
    fig, axes = plt.subplots(
        3, 1, figsize=_figsize(15, 9), sharex=True,
        gridspec_kw={"height_ratios": [2.4, 1.4, 1.4]},
    )
    ax = axes[0]
    for name, df in servers.items():
        ax.plot(df.index, df["load"], lw=0.9, alpha=0.55, color=SERIES_COLORS[name],
                label=SERVER_LABEL[name])
        ax.plot(df.index, df["load"].rolling(24 * 7, center=True).mean(),
                lw=2.4, color=SERIES_COLORS[name], alpha=1.0,
                label=f"{SERVER_LABEL[name]} (7-day mean)")
    ax.set_ylabel("Load index")
    add_branding(ax, "CHMI Server Power Load — full record",
                 "Oct 2025 → Nov 2026 · hourly readings · 7-day rolling mean overlaid")
    ax.legend(loc="upper right", ncol=2, frameon=True, fontsize=8.5)
    style_axes(ax)

    # Residuals around weekly mean
    for i, (name, df) in enumerate(servers.items(), start=1):
        ax = axes[i]
        wmean = df["load"].rolling(24 * 7, center=True).mean()
        resid = df["load"] - wmean
        ax.plot(df.index, resid, lw=0.7, color=SERIES_COLORS[name], alpha=0.6)
        ax.axhline(0, color=GRID, lw=1.0)
        ax.set_ylabel("Δ from 7-day mean")
        add_branding(ax, f"{SERVER_LABEL[name]} — deviation", "")
        style_axes(ax)

    axes[-1].xaxis.set_major_locator(mdates.MonthLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    axes[-1].xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=0))
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()
    save(fig, FIG / "01_full_timeseries.png")


# ---------------------------------------------------------------------------
# 2. Overlay time series (zoomed start)
# ---------------------------------------------------------------------------
def fig_overlay():
    apply_theme("dark")
    fig, ax = plt.subplots(figsize=_figsize(14, 5))
    for name, df in servers.items():
        ax.plot(df.index, df["load"], lw=0.8, alpha=0.5, color=SERIES_COLORS[name])
        ax.plot(df.index, df["load"].rolling(24 * 7, center=True).mean(),
                lw=2.4, color=SERIES_COLORS[name])
    ax.set_ylabel("Load index")
    add_branding(ax, "Both servers, overlaid",
                 "Server B (red) runs a systematically higher baseline than Server A (blue)")
    ax.legend([SERVER_LABEL[k] for k in ["A", "B"]], loc="upper right", fontsize=8.5)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate(rotation=30)
    style_axes(ax)
    fig.tight_layout()
    save(fig, FIG / "02_overlay_timeseries.png")


# ---------------------------------------------------------------------------
# 3. Distribution (histogram + KDE)
# ---------------------------------------------------------------------------
def fig_distribution():
    apply_theme("dark")
    fig, axes = plt.subplots(1, 2, figsize=_figsize(13, 5))
    ax = axes[0]
    for name, df in servers.items():
        ax.hist(df["load"], bins=70, density=True, alpha=0.5,
                color=SERIES_COLORS[name], label=SERVER_LABEL[name])
        kde_x = np.linspace(df["load"].min(), df["load"].max(), 300)
        kde = stats.gaussian_kde(df["load"])(kde_x)
        ax.plot(kde_x, kde, lw=2.4, color=SERIES_COLORS[name])
    add_branding(ax, "Load distribution", "KDE overlaid · Server B is broader and shifted right")
    ax.set_xlabel("Load index")
    ax.set_ylabel("Density")
    ax.legend()
    style_axes(ax)

    ax = axes[1]
    data = [df["load"] for df in servers.values()]
    bp = ax.boxplot(data, patch_artist=True, tick_labels=["Server A", "Server B"],
                    widths=0.5)
    for patch, color in zip(bp["boxes"], [SERIES_COLORS["A"], SERIES_COLORS["B"]]):
        patch.set_facecolor(color)
        patch.set_alpha(0.5)
    for med in bp["medians"]:
        med.set_color(FG)
        med.set_linewidth(2)
    for whisk in bp["whiskers"] + bp["caps"] + bp["fliers"]:
        whisk.set_color(MUTED)
    add_branding(ax, "Box plot comparison", "")
    ax.set_ylabel("Load index")
    style_axes(ax)
    fig.tight_layout()
    save(fig, FIG / "03_distribution.png")


# ---------------------------------------------------------------------------
# 4. Hour-of-day profile (weekday vs weekend)
# ---------------------------------------------------------------------------
def fig_daily_profile():
    apply_theme("dark")
    fig, axes = plt.subplots(1, 2, figsize=_figsize(13, 5))
    for ax, (name, df) in zip(axes, servers.items()):
        prof = df.groupby(["hour", "weekend_label"])["load"].mean().unstack()
        for col, ls in [("Weekday", "-"), ("Weekend", "--")]:
            if col in prof:
                ax.plot(prof.index, prof[col], ls=ls, lw=2.2,
                        color=SERIES_COLORS[name], alpha=0.85,
                        label=f"{col}")
        ax.set_xlabel("Hour of day")
        ax.set_ylabel("Mean load")
        ax.set_xticks(range(0, 24, 3))
        add_branding(ax, SERVER_LABEL[name], "Average load by hour · weekday vs weekend")
        ax.legend()
        style_axes(ax)
    fig.tight_layout()
    save(fig, FIG / "04_daily_profile.png")


# ---------------------------------------------------------------------------
# 5. Heatmap: hour-of-day x day-of-week average load
# ---------------------------------------------------------------------------
def fig_heatmap_hour_weekday():
    apply_theme("dark")
    fig, axes = plt.subplots(1, 2, figsize=_figsize(15, 5))
    for ax, (name, df), cmap in zip(axes, servers.items(), [CMAP_A, CMAP_B]):
        piv = df.pivot_table(index="weekday", columns="hour", values="load",
                             aggfunc="mean").reindex(range(7))
        im = ax.imshow(piv, aspect="auto", cmap=cmap)
        ax.set_yticks(range(7))
        ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        ax.set_xticks(range(0, 24, 2))
        ax.set_xticklabels(range(0, 24, 2))
        ax.set_xlabel("Hour of day")
        ax.set_title(SERVER_LABEL[name], color=FG, fontweight="bold")
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        cbar.ax.tick_params(colors=MUTED)
        cbar.set_label("Mean load", color=MUTED)
        style_axes(ax)
    fig.suptitle("Load by hour-of-day × weekday", color=FG, fontweight="bold", y=1.02)
    fig.tight_layout()
    save(fig, FIG / "05_heatmap_hour_weekday.png")


# ---------------------------------------------------------------------------
# 6. Monthly / seasonal profile
# ---------------------------------------------------------------------------
def fig_monthly():
    apply_theme("dark")
    fig, axes = plt.subplots(1, 2, figsize=_figsize(13, 5))
    ax = axes[0]
    for name, df in servers.items():
        m = df.groupby("month")["load"].mean()
        ax.plot(m.index, m.values, "-o", lw=2.2, color=SERIES_COLORS[name],
                label=SERVER_LABEL[name])
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    add_branding(ax, "Monthly mean load", "Seasonal pattern across the year")
    ax.set_ylabel("Mean load")
    ax.legend()
    style_axes(ax)

    ax = axes[1]
    for name, df in servers.items():
        s = df.groupby("season")["load"].agg(["mean", "std"]).reindex(
            ["Winter", "Spring", "Summer", "Fall"])
        ax.errorbar(s.index, s["mean"], yerr=s["std"], fmt="-o", lw=2.2,
                    color=SERIES_COLORS[name], capsize=4, label=SERVER_LABEL[name])
    add_branding(ax, "Seasonal mean ± std", "")
    ax.set_ylabel("Mean load")
    ax.legend()
    style_axes(ax)
    fig.tight_layout()
    save(fig, FIG / "06_monthly_seasonal.png")


# ---------------------------------------------------------------------------
# 7. Calendar-style monthly heatmaps (heatmap grid of all months)
# ---------------------------------------------------------------------------
def fig_calendar_heatmap():
    apply_theme("dark")
    for name, df, cmap in [("A", A, CMAP_A), ("B", B, CMAP_B)]:
        monthly = df.groupby("month")["load"].mean()
        daily = df.groupby(["month", "day"])["load"].mean()
        fig, ax = plt.subplots(figsize=_figsize(15, 6))
        # Build a matrix of month x day (1..31)
        mat = np.full((12, 31), np.nan)
        for (mo, day), v in daily.items():
            mat[mo - 1, day - 1] = v
        im = ax.imshow(mat, aspect="auto", cmap=cmap)
        ax.set_yticks(range(12))
        ax.set_yticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        ax.set_xlabel("Day of month")
        add_branding(ax, f"{SERVER_LABEL[name]} — month × day heatmap",
                     "Average load by calendar day (NaN = no reading)")
        cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
        cbar.set_label("Mean load", color=MUTED)
        cbar.ax.tick_params(colors=MUTED)
        style_axes(ax)
        # Reserve headroom so the two-line title does not overlap the top row
        fig.subplots_adjust(top=0.86)
        fig.tight_layout(rect=(0, 0, 1, 0.92))
        save(fig, FIG / f"07_calendar_heatmap_{name}.png")


# ---------------------------------------------------------------------------
# 8. Load distribution by month (violin)
# ---------------------------------------------------------------------------
def fig_violin_month():
    apply_theme("dark")
    fig, axes = plt.subplots(1, 2, figsize=_figsize(15, 6))
    for ax, (name, df), color in zip(axes, servers.items(), [SERIES_COLORS["A"], SERIES_COLORS["B"]]):
        parts = ax.violinplot(
            [df[df["month"] == m]["load"].values for m in range(1, 13)],
            positions=range(1, 13), showmedians=True, widths=0.8,
        )
        for pc in parts["bodies"]:
            pc.set_facecolor(color)
            pc.set_alpha(0.5)
        for key in ["cmedians", "cbars", "cmins", "cmaxes"]:
            parts[key].set_color(FG)
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
        add_branding(ax, SERVER_LABEL[name], "Monthly load distribution")
        ax.set_ylabel("Load index")
        style_axes(ax)
    fig.tight_layout()
    save(fig, FIG / "08_violin_month.png")


# ---------------------------------------------------------------------------
# 9. A vs B scatter / correlation
# ---------------------------------------------------------------------------
def fig_ab_scatter():
    apply_theme("dark")
    # Align on common timestamps
    common = A.index.intersection(B.index)
    a, b = A.loc[common, "load"], B.loc[common, "load"]
    fig, ax = plt.subplots(figsize=_figsize(8, 8))
    ax.scatter(a, b, s=4, alpha=0.25, color="#4fa3e3", edgecolors="none")
    lims = [min(a.min(), b.min()) - 50, max(a.max(), b.max()) + 50]
    ax.plot(lims, lims, "--", color=MUTED, lw=1.4, label="y = x")
    r, p = stats.pearsonr(a, b)
    rho, _ = stats.spearmanr(a, b)
    ax.text(0.06, 0.10, f"Pearson r = {r:.3f}\nSpearman ρ = {rho:.3f}\nn = {len(a):,}",
            transform=ax.transAxes, va="bottom", color=FG,
            bbox=dict(boxstyle="round", facecolor=PANEL, edgecolor=GRID))
    ax.set_xlabel("Server A load")
    ax.set_ylabel("Server B load")
    add_branding(ax, "Server A vs Server B — simultaneous load",
                 "Weak association · the servers do not track each other tightly")
    ax.legend(loc="lower right", fontsize=8.5)
    style_axes(ax)
    fig.tight_layout()
    save(fig, FIG / "09_ab_scatter.png")


# ---------------------------------------------------------------------------
# 10. Difference (B - A) over time
# ---------------------------------------------------------------------------
def fig_difference():
    apply_theme("dark")
    common = A.index.intersection(B.index)
    diff = B.loc[common, "load"] - A.loc[common, "load"]
    fig, ax = plt.subplots(figsize=_figsize(15, 5))
    ax.plot(diff.index, diff, lw=0.8, alpha=0.5, color=SERIES_COLORS["B"])
    ax.plot(diff.index, diff.rolling(24 * 7, center=True).mean(), lw=2.2,
            color="#ffd166", label="7-day mean difference")
    ax.axhline(0, color=GRID, lw=1.2)
    ax.set_ylabel("Server B − Server A (load)")
    add_branding(ax, "Difference (B − A) over time",
                 f"Mean gap = {diff.mean():.0f} load units · B is almost always higher")
    ax.legend()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate(rotation=30)
    style_axes(ax)
    fig.tight_layout()
    save(fig, FIG / "10_difference_over_time.png")


# ---------------------------------------------------------------------------
# 11. Energy / cumulative area chart
# ---------------------------------------------------------------------------
def fig_energy():
    apply_theme("dark")
    fig, ax = plt.subplots(figsize=_figsize(15, 6))
    for name, df, color in [("A", A, SERIES_COLORS["A"]), ("B", B, SERIES_COLORS["B"])]:
        cum = df["load"].cumsum() / 1000.0  # thousands of load·hours
        ax.plot(df.index, cum, lw=2.0, color=color, label=SERVER_LABEL[name])
        ax.fill_between(df.index, cum, color=color, alpha=0.15)
    ax.set_ylabel("Cumulative load·hours (thousands)")
    add_branding(ax, "Cumulative energy footprint",
                 "Relative energy index = sum(load) per hour · Server B consumes ~55% more over the record")
    ax.legend(loc="upper left", fontsize=8.5)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate(rotation=30)
    style_axes(ax)
    fig.tight_layout()
    save(fig, FIG / "11_cumulative_energy.png")


# ---------------------------------------------------------------------------
# 12. Hourly load — boxplot by hour (full record)
# ---------------------------------------------------------------------------
def fig_hour_box():
    apply_theme("dark")
    fig, axes = plt.subplots(1, 2, figsize=_figsize(15, 6))
    for ax, (name, df), color in zip(axes, servers.items(), [SERIES_COLORS["A"], SERIES_COLORS["B"]]):
        data = [df[df["hour"] == h]["load"].values for h in range(24)]
        bp = ax.boxplot(data, showfliers=False, patch_artist=True)
        for patch in bp["boxes"]:
            patch.set_facecolor(color)
            patch.set_alpha(0.4)
        for key in ["medians", "whiskers", "caps"]:
            for el in bp[key]:
                el.set_color(MUTED)
        for med in bp["medians"]:
            med.set_color(FG)
            med.set_linewidth(2)
        ax.set_xticks(range(1, 25, 2))
        ax.set_xticklabels(range(0, 24, 2))
        add_branding(ax, SERVER_LABEL[name], "Load distribution by hour of day (all days)")
        ax.set_xlabel("Hour of day")
        ax.set_ylabel("Load index")
        style_axes(ax)
    fig.tight_layout()
    save(fig, FIG / "12_hourly_box.png")


if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    fig_timeseries()
    fig_overlay()
    fig_distribution()
    fig_daily_profile()
    fig_heatmap_hour_weekday()
    fig_monthly()
    fig_calendar_heatmap()
    fig_violin_month()
    fig_ab_scatter()
    fig_difference()
    fig_energy()
    fig_hour_box()
    print("ALL STATIC FIGURES DONE")
