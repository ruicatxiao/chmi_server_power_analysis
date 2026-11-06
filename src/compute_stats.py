#!/usr/bin/env python3
"""Compute headline statistics for the report and save as JSON + markdown."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

from pipeline import build_all

ROOT = Path(__file__).resolve().parent.parent
servers = build_all()
A, B = servers["A"], servers["B"]

stats_out = {}

def summarize(name, df):
    s = df["load"]
    return {
        "server": name,
        "n_hours": int(len(df)),
        "start": str(df.index.min()),
        "end": str(df.index.max()),
        "span_days": int((df.index.max() - df.index.min()).days),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "std": float(s.std()),
        "min": float(s.min()),
        "max": float(s.max()),
        "p01": float(np.percentile(s, 1)),
        "p25": float(np.percentile(s, 25)),
        "p75": float(np.percentile(s, 75)),
        "p99": float(np.percentile(s, 99)),
        "total_load": float(s.sum()),
        "peak_hour_mean": float(df.groupby("hour")["load"].mean().max()),
        "peak_hour": int(df.groupby("hour")["load"].mean().idxmax()),
        "trough_hour": int(df.groupby("hour")["load"].mean().idxmin()),
        "weekday_mean": float(df[~df["is_weekend"]]["load"].mean()),
        "weekend_mean": float(df[df["is_weekend"]]["load"].mean()),
        "monthly_means": {int(k): float(v) for k, v in df.groupby("month")["load"].mean().items()},
        "season_means": {k: float(v) for k, v in df.groupby("season")["load"].mean().items()},
    }

stats_out["A"] = summarize("A", A)
stats_out["B"] = summarize("B", B)

# Comparisons
common = A.index.intersection(B.index)
a, b = A.loc[common, "load"], B.loc[common, "load"]
diff = b - a
pearson, pval = stats.pearsonr(a, b)
spearman, _ = stats.spearmanr(a, b)
stats_out["comparison"] = {
    "n_common": int(len(common)),
    "mean_diff_B_minus_A": float(diff.mean()),
    "median_diff_B_minus_A": float(diff.median()),
    "std_diff": float(diff.std()),
    "pct_time_B_higher": float((diff > 0).mean() * 100),
    "pearson_r": float(pearson),
    "pearson_p": float(pval),
    "spearman_rho": float(spearman),
    "ratio_means_B_over_A": float(b.mean() / a.mean()),
    "ratio_total_B_over_A": float(b.sum() / a.sum()),
}

# Energy ratio
stats_out["comparison"]["relative_energy_ratio_B_over_A"] = float(b.sum() / a.sum())

with open(ROOT / "data" / "summary_stats.json", "w") as f:
    json.dump(stats_out, f, indent=2)

# Print a compact markdown block
print("## Key statistics")
print(f"- Server A: mean {stats_out['A']['mean']:.0f}, median {stats_out['A']['median']:.0f}, "
      f"range {stats_out['A']['min']:.0f}–{stats_out['A']['max']:.0f}, std {stats_out['A']['std']:.0f}")
print(f"- Server B: mean {stats_out['B']['mean']:.0f}, median {stats_out['B']['median']:.0f}, "
      f"range {stats_out['B']['min']:.0f}–{stats_out['B']['max']:.0f}, std {stats_out['B']['std']:.0f}")
print(f"- Mean B/A ratio: {stats_out['comparison']['ratio_means_B_over_A']:.2f}")
print(f"- B higher than A {stats_out['comparison']['pct_time_B_higher']:.1f}% of the time")
print(f"- Pearson r = {pearson:.3f} (p={pval:.2e}), Spearman ρ = {spearman:.3f}")
print(f"- Cumulative load ratio B/A = {stats_out['comparison']['relative_energy_ratio_B_over_A']:.2f}")
