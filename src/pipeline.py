"""
CHMI Server Power Analysis — data pipeline
==========================================
Loads the raw hourly power logs for CHMI Server A and Server B,
cleans them, fills gaps, and engineers time-based features.

Input (raw_data/):  tab-separated files with columns date, time, load
Output (data/):     tidy CSV per server + a combined CSV + derived features
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw_data"
DATA = ROOT / "data"

SERVERS = {
    "A": RAW / "chmi_server_a_power_log.txt",
    "B": RAW / "chmi_server_b_power_log.txt",
}

SERVER_COLOR = {"A": "#1f77b4", "B": "#d62728"}
SERVER_LABEL = {"A": "CHMI Server A", "B": "CHMI Server B"}


# ---------------------------------------------------------------------------
# Loading / cleaning
# ---------------------------------------------------------------------------
def load_raw(name: str) -> pd.DataFrame:
    """Read one raw power log into a cleaned hourly-indexed DataFrame.

    Duplicate timestamps (DST fall-back hour appears twice) are resolved by
    averaging the two readings, which is the physically sensible thing to do
    for a single wall-clock hour.
    """
    path = SERVERS[name]
    df = pd.read_csv(
        path,
        sep="\t",
        dtype={"date": str, "time": str, "load": float},
    )
    df["timestamp"] = pd.to_datetime(
        df["date"] + " " + df["time"], format="%Y-%m-%d %H:%M"
    )
    # Average duplicated wall-clock timestamps (DST fall-back)
    df = (
        df.groupby("timestamp", as_index=True)["load"]
        .mean()
        .sort_index()
        .rename("load")
        .to_frame()
    )
    df.index.name = "timestamp"
    return df


def resample_hourly(df: pd.DataFrame) -> pd.DataFrame:
    """Resample to a complete hourly grid, linearly interpolating small gaps.

    Gaps (mostly a few hours, some multi-day windows) are forward-filled first
    to avoid extrapolating, then linearly interpolated. This keeps the series
    continuous for time-series analysis and animation.
    """
    full = pd.date_range(df.index.min(), df.index.max(), freq="h", name="timestamp")
    out = df.reindex(full)
    out["load"] = out["load"].interpolate(method="time", limit_direction="both")
    return out


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add calendar / time-of-day / seasonal features used across the repo."""
    out = df.copy()
    ts = out.index
    out["hour"] = ts.hour
    out["day"] = ts.day
    out["month"] = ts.month
    out["weekday"] = ts.dayofweek  # 0 = Monday
    out["weekday_name"] = ts.day_name()
    out["is_weekend"] = ts.dayofweek >= 5
    out["day_of_year"] = ts.dayofyear
    out["week_of_year"] = ts.isocalendar().week.astype(int)
    out["quarter"] = ts.quarter
    out["season"] = pd.cut(
        ts.month,
        bins=[0, 3, 6, 9, 12],
        labels=["Winter", "Spring", "Summer", "Fall"],
    ).astype(str)
    out["weekend_label"] = np.where(out["is_weekend"], "Weekend", "Weekday")
    out["date"] = ts.date
    return out


def build_server(name: str) -> pd.DataFrame:
    """Full pipeline for a single server."""
    df = load_raw(name)
    df = resample_hourly(df)
    df = engineer_features(df)
    df["server"] = name
    return df


def build_all() -> dict[str, pd.DataFrame]:
    return {name: build_server(name) for name in SERVERS}


def save_all(servers: dict[str, pd.DataFrame]) -> None:
    DATA.mkdir(exist_ok=True)
    combined = pd.concat(servers.values())
    for name, df in servers.items():
        df.to_csv(DATA / f"server_{name.lower()}_clean.csv")
    combined.to_csv(DATA / "combined_clean.csv")
    # long-form summary for plotting
    summary = combined.reset_index()
    summary.to_csv(DATA / "combined_long.csv", index=False)
    print(f"[pipeline] wrote clean data to {DATA}")


if __name__ == "__main__":
    servers = build_all()
    save_all(servers)
    for name, df in servers.items():
        print(
            f"Server {name}: {len(df)} hours, "
            f"{df.index.min()} -> {df.index.max()}, "
            f"mean={df.load.mean():.1f}, min={df.load.min():.0f}, max={df.load.max():.0f}"
        )
