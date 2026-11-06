"""
CHMI Server Power Analysis — interactive Plotly figures
=======================================================
Writes standalone HTML files into interactive/ so they can be opened
directly in a browser (or served from GitHub Pages). No server needed.
Run:  python src/make_interactive.py
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from pipeline import build_all, SERVER_LABEL
from style import SERIES_COLORS, BG, PANEL, FG, MUTED, GRID

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "interactive"

servers = build_all()
A, B = servers["A"], servers["B"]

# Common plotly layout template (dark, professional)
def base_layout(title, height=600, **kw):
    layout = dict(
        title=dict(text=title, x=0.02, font=dict(size=18, color=FG)),
        paper_bgcolor=BG,
        plot_bgcolor=PANEL,
        font=dict(color=FG),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID),
        margin=dict(l=60, r=30, t=70, b=50),
        hovermode="x unified",
        height=height,
    )
    layout.update(kw)
    return layout


def write(fig, name):
    path = OUT / name
    fig.write_html(path, include_plotlyjs="cdn", full_html=True,
                   config={"displaylogo": False})
    print(f"[interactive] {path}")


# ---------------------------------------------------------------------------
# 1. Main interactive time series with range slider + rolling mean toggle
# ---------------------------------------------------------------------------
def interactive_timeseries():
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        row_heights=[0.62, 0.38],
                        subplot_titles=("Hourly load & 7-day mean", "Difference (B − A)"))
    for name, df in [("A", A), ("B", B)]:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["load"], mode="lines", name=f"{SERVER_LABEL[name]} (hourly)",
            line=dict(width=0.7, color=SERIES_COLORS[name]), opacity=0.45,
            hovertemplate="%{x|%b %d %Y %H:%M}<br>load=%{y}<extra></extra>",
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["load"].rolling(24 * 7, center=True).mean(),
            mode="lines", name=f"{SERVER_LABEL[name]} (7-day mean)",
            line=dict(width=2.6, color=SERIES_COLORS[name]),
            hovertemplate="%{x|%b %d %Y %H:%M}<br>7d mean=%{y}<extra></extra>",
        ), row=1, col=1)

    common = A.index.intersection(B.index)
    diff = B.loc[common, "load"] - A.loc[common, "load"]
    fig.add_trace(go.Scatter(
        x=diff.index, y=diff, mode="lines", name="B − A (hourly)",
        line=dict(width=0.7, color="#ffd166"), opacity=0.5,
        hovertemplate="%{x|%b %d %Y %H:%M}<br>Δ=%{y}<extra></extra>",
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=diff.index, y=diff.rolling(24 * 7, center=True).mean(), mode="lines",
        name="B − A (7-day mean)", line=dict(width=2.6, color="#ffffff"),
        hovertemplate="%{x|%b %d %Y %H:%M}<br>Δ(7d)=%{y}<extra></extra>",
    ), row=2, col=1)

    fig.update_layout(**base_layout("CHMI Server Power — interactive time series", height=750))
    fig.update_xaxes(rangeslider_visible=False, rangeselector=dict(
        buttons=[dict(count=7, label="1w", step="day", stepmode="backward"),
                 dict(count=30, label="1m", step="day", stepmode="backward"),
                 dict(count=90, label="3m", step="day", stepmode="backward"),
                 dict(count=365, label="1y", step="day", stepmode="backward"),
                 dict(step="all", label="All")]))
    fig.update_yaxes(title_text="Load index", row=1, col=1)
    fig.update_yaxes(title_text="Δ (B − A)", row=2, col=1)
    write(fig, "01_interactive_timeseries.html")


# ---------------------------------------------------------------------------
# 2. Hour-of-day × weekday heatmap (interactive)
# ---------------------------------------------------------------------------
def interactive_heatmap():
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Server A", "Server B"))
    for i, (name, df) in enumerate([("A", A), ("B", B)], start=1):
        piv = df.pivot_table(index="weekday", columns="hour", values="load",
                             aggfunc="mean").reindex(range(7))
        piv = piv.iloc[::-1]
        fig.add_trace(go.Heatmap(
            z=piv.values, x=list(range(24)), y=["Sun", "Sat", "Fri", "Thu", "Wed", "Tue", "Mon"],
            colorscale=[[0, "#0f1420"], [0.5, SERIES_COLORS[name]], [1, "#ffffff"]],
            colorbar=dict(tickfont=dict(color=MUTED), title=dict(text="Mean load", font=dict(color=MUTED))),
            hovertemplate="%{y} %{x}:00<br>mean load=%{z}<extra></extra>",
        ), row=1, col=i)
    fig.update_layout(**base_layout("Load by hour-of-day × weekday", height=500))
    fig.update_xaxes(title_text="Hour of day")
    write(fig, "02_heatmap_hour_weekday.html")


# ---------------------------------------------------------------------------
# 3. Hourly load — box plot per hour with hover stats (interactive)
# ---------------------------------------------------------------------------
def interactive_hourly_box():
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Server A", "Server B"))
    for i, (name, df) in enumerate([("A", A), ("B", B)], start=1):
        fig.add_trace(go.Box(
            y=df["load"], x=df["hour"], name=SERVER_LABEL[name],
            boxpoints="outliers", marker=dict(color=SERIES_COLORS[name], size=2),
            line=dict(color=SERIES_COLORS[name]),
            fillcolor="rgba(0,0,0,0)", hovertemplate="hour %{x}<br>load %{y}<extra></extra>",
        ), row=1, col=i)
    fig.update_layout(**base_layout("Load distribution by hour of day", height=520))
    fig.update_xaxes(title_text="Hour of day")
    fig.update_yaxes(title_text="Load index")
    write(fig, "03_hourly_box.html")


# ---------------------------------------------------------------------------
# 4. 3D surface of hour × month average load (interactive)
# ---------------------------------------------------------------------------
def interactive_3d():
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Server A", "Server B"),
                        specs=[[{"type": "surface"}, {"type": "surface"}]])
    for i, (name, df) in enumerate([("A", A), ("B", B)], start=1):
        piv = df.pivot_table(index="month", columns="hour", values="load",
                             aggfunc="mean").reindex(range(1, 13))
        fig.add_trace(go.Surface(
            z=piv.values, x=list(range(24)), y=piv.index,
            colorscale=[[0, "#0f1420"], [0.5, SERIES_COLORS[name]], [1, "#ffffff"]],
            colorbar=dict(tickfont=dict(color=MUTED), title=dict(text="Mean load", font=dict(color=MUTED))),
            hovertemplate="month %{y}, hour %{x}:00<br>mean=%{z}<extra></extra>",
        ), row=1, col=i)
    fig.update_layout(**base_layout("Hour × month average load surface", height=650))
    fig.update_xaxes(title_text="Hour of day")
    fig.update_yaxes(title_text="Month")
    write(fig, "04_3d_surface.html")


# ---------------------------------------------------------------------------
# 5. Distribution overlay (interactive KDE)
# ---------------------------------------------------------------------------
def interactive_distribution():
    from scipy import stats
    fig = go.Figure()
    for name, df in [("A", A), ("B", B)]:
        fig.add_trace(go.Histogram(
            x=df["load"], name=f"{SERVER_LABEL[name]}", histnorm="probability density",
            marker=dict(color=SERIES_COLORS[name], line=dict(width=0)), opacity=0.4,
            nbinsx=70, hovertemplate="load %{x}<br>density %{y}<extra></extra>",
        ))
        kde_x = np.linspace(df["load"].min(), df["load"].max(), 300)
        kde = stats.gaussian_kde(df["load"])(kde_x)
        fig.add_trace(go.Scatter(
            x=kde_x, y=kde, mode="lines", name=f"{SERVER_LABEL[name]} KDE",
            line=dict(width=3, color=SERIES_COLORS[name]),
            hovertemplate="load %{x}<br>density %{y}<extra></extra>",
        ))
    fig.update_layout(**base_layout("Load distribution (interactive)", height=520),
                      barmode="overlay")
    fig.update_xaxes(title_text="Load index")
    fig.update_yaxes(title_text="Density")
    write(fig, "05_distribution.html")


# ---------------------------------------------------------------------------
# 6. Month-by-month violin (interactive)
# ---------------------------------------------------------------------------
def interactive_violin():
    fig = go.Figure()
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for name, df in [("A", A), ("B", B)]:
        fig.add_trace(go.Violin(
            x=df["month"].astype(str) + "-" + name, y=df["load"], name=SERVER_LABEL[name],
            box_visible=True, meanline_visible=True, points=False,
            line=dict(color=SERIES_COLORS[name]), fillcolor="rgba(0,0,0,0)",
            hovertemplate="month %{x}<br>load %{y}<extra></extra>",
        ))
    fig.update_layout(**base_layout("Monthly load distribution (interactive)", height=560),
                      violinmode="group")
    write(fig, "06_monthly_violin.html")


# ---------------------------------------------------------------------------
# 7. Combined overview dashboard
# ---------------------------------------------------------------------------
def interactive_dashboard():
    fig = make_subplots(
        rows=3, cols=2, subplot_titles=(
            "Hourly load & 7-day mean", "Load distribution",
            "Hour × weekday heatmap (A)", "Hour × weekday heatmap (B)",
            "Monthly mean", "Cumulative energy"),
        specs=[[{}, {}], [{}, {}], [{}, {}]],
        vertical_spacing=0.09, horizontal_spacing=0.09,
    )
    # (0,0) timeseries
    for name, df in [("A", A), ("B", B)]:
        fig.add_trace(go.Scatter(x=df.index, y=df["load"], name=f"{SERVER_LABEL[name]} hourly",
                                 line=dict(width=0.6, color=SERIES_COLORS[name]), opacity=0.4,
                                 showlegend=True), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["load"].rolling(24 * 7, center=True).mean(),
                                 name=f"{SERVER_LABEL[name]} 7d", line=dict(width=2.2, color=SERIES_COLORS[name]),
                                 showlegend=False), row=1, col=1)
    # (0,1) distribution
    for name, df in [("A", A), ("B", B)]:
        fig.add_trace(go.Histogram(x=df["load"], name=f"{SERVER_LABEL[name]}",
                                   histnorm="probability density", opacity=0.5,
                                   marker=dict(color=SERIES_COLORS[name], line=dict(width=0)),
                                   nbinsx=60, showlegend=False), row=1, col=2)
    # (1,0) and (1,1) heatmaps
    for i, (name, df) in enumerate([("A", A), ("B", B)], start=1):
        piv = df.pivot_table(index="weekday", columns="hour", values="load",
                             aggfunc="mean").reindex(range(7))
        piv = piv.iloc[::-1]
        fig.add_trace(go.Heatmap(
            z=piv.values, x=list(range(24)), y=["Sun", "Sat", "Fri", "Thu", "Wed", "Tue", "Mon"],
            colorscale=[[0, "#0f1420"], [0.5, SERIES_COLORS[name]], [1, "#ffffff"]],
            showscale=False, hovertemplate="%{y} %{x}:00 %{z}<extra></extra>",
        ), row=2, col=i)
    # (2,0) monthly mean
    for name, df in [("A", A), ("B", B)]:
        m = df.groupby("month")["load"].mean()
        fig.add_trace(go.Scatter(x=m.index, y=m.values, mode="lines+markers", name=f"{SERVER_LABEL[name]}",
                                 line=dict(width=2.4, color=SERIES_COLORS[name]), showlegend=False), row=3, col=1)
    # (2,1) cumulative energy
    for name, df in [("A", A), ("B", B)]:
        cum = df["load"].cumsum() / 1000.0
        fig.add_trace(go.Scatter(x=df.index, y=cum, mode="lines", name=f"{SERVER_LABEL[name]}",
                                 fill="tozeroy", line=dict(width=2, color=SERIES_COLORS[name]),
                                 showlegend=False), row=3, col=2)

    fig.update_layout(**base_layout("CHMI Server Power — interactive dashboard", height=1100))
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_xaxes(title_text="Load", row=1, col=2)
    fig.update_yaxes(title_text="Load index", row=1, col=1)
    fig.update_yaxes(title_text="Density", row=1, col=2)
    fig.update_yaxes(title_text="Mean load", row=3, col=1)
    fig.update_yaxes(title_text="Cum. load·hrs", row=3, col=2)
    write(fig, "00_dashboard.html")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    interactive_dashboard()
    interactive_timeseries()
    interactive_heatmap()
    interactive_hourly_box()
    interactive_3d()
    interactive_distribution()
    interactive_violin()
    print("ALL INTERACTIVE FIGURES DONE")
