# CHMI Server Power — Analysis Report

**Prepared:** 2026-11-05 · **Data window:** 2025-10-07 14:00 → 2026-11-05 15:00 (≈13 months, hourly)

---

## 1. Overview

Two hourly power/load logs were provided — one for **CHMI Server A** and one for **CHMI Server B**. Each record contains a `load` index sampled once per hour. This report summarizes a comprehensive exploratory analysis of the pair, including time-series structure, distributions, diurnal and seasonal patterns, cross-server relationships, and a relative energy comparison.

> **Units.** The `load` column is an arbitrary *load index*, not a calibrated wattage. All figures compare the two servers on a relative basis; "energy" below is a *relative energy index* = Σ(load × 1 h), not absolute kWh.

---

## 2. Data quality & preprocessing

| Item | Server A | Server B |
|---|---|---|
| Raw rows | 9,421 | 9,340 |
| Clean hourly records | 9,458 | 9,457 |
| Start | 2025-10-07 14:00 | 2025-10-07 15:00 |
| End | 2026-11-05 15:00 | 2026-11-05 15:00 |

- **DST duplicates.** On the fall-back days (`2025-11-02` and `2026-11-01`), the 01:00 wall-clock hour appears twice. These were **averaged** — the physically sensible resolution for a single hour.
- **Gaps.** A small number of hours are missing (39 for A, 119 for B), including a few multi-day windows (e.g. mid-May 2026). These were **linearly interpolated** to produce a continuous, animation-friendly series.
- After cleaning, the series are continuous at hourly resolution.

---

## 3. Headline statistics

| Metric | Server A | Server B |
|---|---|---|
| Mean load | **295** | **462** |
| Median load | 279 | 459 |
| Std dev | 103 | 76 |
| Minimum | 135 | 315 |
| Maximum | 621 | 1035 |
| 1st percentile | 162 | 342 |
| 99th percentile | 558 | 711 |
| Peak hour (mean) | midday | midday |

**Cross-server comparison (on 9,457 aligned hours):**

| Metric | Value |
|---|---|
| Mean difference (B − A) | **+167** |
| Median difference (B − A) | +176 |
| % of hours B > A | **90.1%** |
| Mean ratio (B / A) | **1.57×** |
| Cumulative energy ratio (B / A) | **1.57×** |
| Pearson r | 0.048 |
| Spearman ρ | −0.008 |

**Interpretation.** Server B runs a systematically **~57% higher** baseline load than Server A and is the higher of the two about **90% of the time**. Yet the two servers are **essentially uncorrelated** (r ≈ 0.05). This tells us their workloads are **independent** — they do not rise and fall together.

---

## 4. Time-series structure

- Both servers show a **sustained, slowly-varying baseline** with substantial **hour-to-hour volatility** superimposed.
- The 7-day rolling mean reveals **slow multi-week oscillations** (likely weekly/fortnightly workload cycles) rather than a monotonic trend.
- Server B's rolling mean is consistently above Server A's throughout the record; the gap narrows slightly around mid-2026 but remains positive.

---

## 5. Distribution

- **Server A is clearly bimodal.** There is a low "idle" mode around 170–190 and a higher "active" mode around 280–300. This suggests the server alternates between two distinct operating states.
- **Server B is unimodal** and tightly concentrated around ~450–470, with a long right tail (outliers up to ~1035, e.g. heavy burst loads).
- Server A's wider spread (std 103 vs 76) reflects its bimodality; Server B's tighter core reflects a more stable but higher baseline.

---

## 6. Diurnal (time-of-day) pattern

- Both servers peak **around midday (10:00–15:00)** and trough overnight.
- **Weekday load > weekend load** for both. The weekday/weekend gap is most visible for Server A.
- The **hour-of-day × weekday heatmap** shows the classic "workweek" pattern: bright (high load) on weekdays mid-day, darker on weekends and overnight.

---

## 7. Seasonal pattern

- Monthly mean loads show a **weak seasonal signature**; there is no dramatic winter/summer swing, but there are month-to-month variations.
- The **calendar heatmap** (month × day) reveals **short, high-load episodes** (bright horizontal bands) that are more pronounced for Server B — likely specific multi-day bursts of heavy computation.

---

## 8. Cross-server relationship

- A scatter of Server A vs Server B (aligned timestamps) shows a **diffuse cloud** with **no strong linear or monotonic relationship** (r ≈ 0.05, ρ ≈ 0).
- The **difference series (B − A)** is mostly positive and stable, reinforcing that the gap between the servers is structural rather than a shared, synchronous workload.
- **Practical implication:** total system power draw does **not** simply double with a second server of similar type; the two servers are driven by independent workloads.

---

## 9. Energy footprint

- The **cumulative load·hours** (relative energy index) shows Server B accumulating energy at a **~57% higher rate** than Server A.
- Because the two servers are uncorrelated, combining them produces a **more stable aggregate** load profile than either server alone (diversification), which is useful for capacity planning.

---

## 10. Conclusions & recommendations

1. **Server B is the higher-consumption unit** (~1.57× Server A). If consolidation or load-balancing is a goal, B is the first candidate to examine.
2. **Independent workloads.** The near-zero correlation means neither server's load can be used to predict the other's. Any predictive model should treat them separately.
3. **Diurnal optimization.** Both servers idle overnight and peak mid-day. If power is a constraint, consider **scheduling heavy jobs to off-peak hours** or **right-sizing** the machines to the observed baseline.
4. **Server A's bimodality** suggests an opportunity to **consolidate** its low-load idle periods — it may be running two distinct workload classes.
5. **Data caveat.** Since `load` is an uncalibrated index, absolute power (W or kWh) cannot be derived. Pairing these logs with a known PSU/PDU wattage would enable true energy and cost estimates.

---

*Generated by CHMI-LLM · University of Pennsylvania · 2026-11-05*
