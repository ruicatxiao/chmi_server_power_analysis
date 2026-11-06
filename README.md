# CHMI Server Power Analysis

> A complete, reproducible analysis of hourly power/load logs for **CHMI Server A** and **CHMI Server B**, covering **2025-10-07 → 2026-11-05** (≈13 months, hourly resolution).

**▶ Live showcase:** [https://ruicatxiao.github.io/chmi_server_power_analysis/](https://ruicatxiao.github.io/chmi_server_power_analysis/) — the full landing page with every figure, animation, and interactive dashboard.

This repository is a **ready-to-deploy showcase**. It contains the raw data, a clean and reproducible data pipeline, a full suite of publication-quality **static figures**, **interactive Plotly dashboards** (openable directly in a browser, no server required), **MP4 animations**, and a written analysis report. Everything is wired up so you can host it on **GitHub Pages** or any static host with one command.

---

## 📜 Prior analysis (archived)

This `main` branch contains the **new full showcase** (Oct 2025 → Nov 2026). The **earlier analysis** (Oct 2025 → Jul 2026) that previously lived on `main` has been archived so nothing is lost:

- **Release:** [Prior analysis — Oct 2025 → Jul 2026](https://github.com/ruicatxiao/chmi_server_power_analysis/releases/tag/prior-analysis-2026-07)
- **Tag:** `prior-analysis-2026-07`
- **Branch:** [`prior-analysis`](https://github.com/ruicatxiao/chmi_server_power_analysis/tree/prior-analysis)

That archived snapshot retains the original `README.md`, `analysis_script.py`, `server_a_report.md`, `server_b_report.md`, `comparison_report.md`, the per-server figures (`figures_server_a/`, `figures_server_b/`), `data/`, and `statistics/`.

---

## 🚀 Quick start (deploy)

```bash
# Clone / copy the repo, then just serve it:
cd server_power_analysis
python3 -m http.server 8000
# open http://localhost:8000/ in your browser
```

Or deploy to **GitHub Pages**:

```bash
git init
git add .
git commit -m "CHMI server power analysis"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
# Then enable GitHub Pages for the repo root
```

The `index.html` landing page links to every figure, dashboard, and animation. Each item is displayed **one per row** with a live preview, and the written report is rendered as a styled HTML page at `report/index.html`.

---

## 📁 Repository layout

```
server_power_analysis/
├── index.html                 # Landing page / showcase hub
├── README.md                  # This file
├── raw_data/                  # Original power logs (A & B)
├── data/                      # Cleaned CSVs + summary_stats.json
├── src/                       # Reproducible analysis code
│   ├── pipeline.py            # Load, clean, feature-engineer
│   ├── style.py               # Shared matplotlib theme
│   ├── make_figures.py        # Static figures  → figures/
│   ├── make_interactive.py    # Plotly HTML      → interactive/
│   ├── make_animations.py     # MP4 animations   → animations/
│   ├── compute_stats.py       # Headline stats   → data/summary_stats.json
│   ├── explore.py             # Early EDA / profiling script
│   ├── build_report.py        # Render report/analysis_report.md → report/index.html
│   ├── shot_dashboards.py     # Capture live previews of each dashboard
│   └── test_site.py           # Playwright QA (broken-image / poster checks)
├── figures/                   # PNG static figures (01–12)
├── interactive/               # Standalone HTML dashboards
├── animations/                # MP4 animations
├── previews/                  # Live previews (dashboard screenshots + video posters)
└── report/                    # Written analysis report
    ├── analysis_report.md     #   Markdown source
    └── index.html             #   Rendered HTML page (on the showcase)
```

---

## 🎯 What the data shows

| Metric | Server A | Server B |
|---|---|---|
| Hours recorded | 9,458 | 9,457 |
| Mean load | **295** | **462** |
| Median load | 279 | 459 |
| Min – Max | 135 – 621 | 315 – 1035 |
| Std dev | 103 | 76 |
| Peak hour (mean) | midday | midday |

**Headline findings:**
- **Server B runs ~57% higher** on average than Server A (mean ratio **1.57×**), and is the higher of the two **~90% of the time**.
- Both servers show a **clear diurnal pattern** — peak load around midday, trough overnight.
- **Weekday load > weekend load** for both, with a distinct weekday/weekend gap.
- Server A's distribution is **bimodal** (a low "idle" mode and a high "active" mode), while Server B is more concentrated around a single higher baseline.
- The two servers are **essentially uncorrelated** (Pearson r ≈ 0.05) — they do **not** track each other's load, implying independent workloads.
- Server B's **cumulative energy footprint is ~57% larger** than Server A's over the record.

> ⚠️ **Note on units:** The `load` column is an arbitrary **load index** (not a calibrated wattage). We report relative comparisons and a relative energy index (`Σ load × 1h`), not absolute kWh.

---

## 📊 Static figures (`figures/`)

| File | Description |
|---|---|
| `01_full_timeseries.png` | Full hourly series + 7-day mean + deviations |
| `02_overlay_timeseries.png` | Both servers overlaid |
| `03_distribution.png` | Histogram + KDE + boxplot comparison |
| `04_daily_profile.png` | Hour-of-day profile, weekday vs weekend |
| `05_heatmap_hour_weekday.png` | Hour × weekday heatmaps |
| `06_monthly_seasonal.png` | Monthly + seasonal means |
| `07_calendar_heatmap_{A,B}.png` | Month × day calendar heatmaps |
| `08_violin_month.png` | Monthly load distributions (violin) |
| `09_ab_scatter.png` | Server A vs B scatter + correlation |
| `10_difference_over_time.png` | B − A difference over time |
| `11_cumulative_energy.png` | Cumulative energy footprint |
| `12_hourly_box.png` | Load distribution by hour (box) |

---

## 🖱️ Interactive dashboards (`interactive/`)

Each file is a **self-contained HTML** (loads Plotly.js from CDN) — open it directly in any browser. They support zoom, pan, hover, and range selection.

- `00_dashboard.html` — combined multi-panel overview
- `01_interactive_timeseries.html` — time series with 1w/1m/3m/1y/All range buttons + B−A panel
- `02_heatmap_hour_weekday.html` — interactive hour×weekday heatmaps
- `03_hourly_box.html` — interactive per-hour box plots
- `04_3d_surface.html` — 3D hour×month surface
- `05_distribution.html` — interactive histogram + KDE
- `06_monthly_violin.html` — interactive monthly violins

---

## 🎬 Animations (`animations/`)

MP4 files, playable in any browser / media player:

- `01_power_sweep.mp4` — sliding window sweep through the full record
- `02_hour_clock.mp4` — spinning "day clock" of average load
- `03_heatmap_evolve.mp4` — hour×weekday heatmap building up month-by-month
- `04_calendar_fill.mp4` — calendar heatmap filling day-by-day (Jan 2026)
- `05_distribution_evolve.mp4` — load distribution KDE growing as data accumulates

---

## 🔁 Reproducibility

You can regenerate everything with the provided `Makefile`:

```bash
make data       # clean + feature-engineer
make figures    # static PNGs
make interactive# Plotly HTML
make animations # MP4 clips
make stats      # headline stats
make serve      # serve locally on :8000
```

Or run each script individually:

```bash
# 1. Clean data
python3 src/pipeline.py

# 2. Static figures
python3 src/make_figures.py

# 3. Interactive dashboards
python3 src/make_interactive.py

# 4. Animations
python3 src/make_animations.py

# 5. Headline statistics
python3 src/compute_stats.py
```

### Dependencies

- Python 3.10+
- `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `statsmodels`, `plotly`
- `ffmpeg` (for MP4 animation encoding)

```bash
pip install pandas numpy matplotlib seaborn scipy statsmodels plotly
# ffmpeg is required for animation encoding; install via your system package manager
```

---

## ⚙️ Data handling notes

- Raw files are tab-separated with columns `date`, `time`, `load` (hourly).
- **DST duplicates:** on the fall-back hour (e.g. `2025-11-02 01:00`) two rows exist for the same wall-clock time. These are **averaged** (physically sensible for a single hour).
- **Gaps:** missing hours (a few isolated + some multi-day windows) are **linearly interpolated** to produce a continuous series for time-series analysis and animation. See `pipeline.py` for details.

---

## 📝 Report

The full written analysis is rendered as a styled page on the showcase: **[`report/index.html`](report/index.html)**.

The Markdown source is at [`report/analysis_report.md`](report/analysis_report.md). To regenerate the HTML page:

```bash
python3 src/build_report.py
```

### Live previews (`previews/`)

The landing page shows a live preview for **every** item:

- **Interactive dashboards** — real Plotly screenshots (`previews/00_dashboard.jpg`, etc.), captured with Playwright via `src/shot_dashboards.py`.
- **Animations** — a poster frame from each MP4 (`previews/01_power_sweep.jpg`, etc.), extracted with `ffmpeg`.

These give a visual at-a-glance before you click through.

---

*Generated by the CHMI-LLM research assistant · University of Pennsylvania · 2026-11-05*
