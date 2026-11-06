#!/usr/bin/env python3
"""Quick profiling of CHMI server power logs (early exploration script).

Run from the repo root:  python src/explore.py
"""
import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "raw_data"

def load(name):
    df = pd.read_csv(RAW / name, sep="\t", dtype={"date": str, "time": str, "load": int})
    df["dt"] = pd.to_datetime(df["date"] + " " + df["time"], format="%Y-%m-%d %H:%M")
    df = df.drop_duplicates(subset="dt", keep="first").set_index("dt").sort_index()
    return df

a = load("chmi_server_a_power_log.txt")
b = load("chmi_server_b_power_log.txt")

for label, df in [("Server A", a), ("Server B", b)]:
    print(f"===== {label} =====")
    print("rows:", len(df))
    print("range:", df.index.min(), "->", df.index.max())
    print("span days:", (df.index.max()-df.index.min()).days)
    print("load: min=%d max=%d mean=%.1f median=%.1f std=%.1f" % (
        df.load.min(), df.load.max(), df.load.mean(), df.load.median(), df.load.std()))
    print("pctiles:", np.percentile(df.load, [1,5,25,50,75,95,99]).round(1))
    # missing hours
    full = pd.date_range(df.index.min(), df.index.max(), freq="h")
    missing = full.difference(df.index)
    print("missing hours:", len(missing))
    if len(missing):
        # group consecutive
        idx = missing.to_series()
        print("  first few:", list(missing[:5]))
        print("  last few:", list(missing[-5:]))
    # dupes
    print("dupes (all):", df.index.duplicated().sum())
    print()
