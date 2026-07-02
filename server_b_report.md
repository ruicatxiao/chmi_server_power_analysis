# Server B Power Analysis Report

**Generated:** 2026-07-02 12:20:27
**Data Period:** 2025-10-07 to 2026-07-01
**Total Records:** 6292 hourly readings

---

## Executive Summary

**Key Findings:**
- Average power load: **451.8 W**
- Peak power load: **1035 W**
- Total energy consumed: **2,843 kWh**
- Average daily consumption: **10.7 kWh/day**

---

## 1. Descriptive Statistics

| Metric | Value |
|--------|-------|
| Mean Load | 451.8 W |
| Median Load | 450.0 W |
| Standard Deviation | 78.2 W |
| Minimum | 315 W |
| Maximum | 1035 W |
| Coefficient of Variation | 0.173 |

### Percentile Distribution
| Percentile | Load (W) |
|------------|----------|
| 10th | 369 |
| 25th | 396 |
| 50th (Median) | 450 |
| 75th | 468 |
| 90th | 558 |
| 95th | 630 |
| 99th | 711 |

---

## 2. Peak Load Analysis

### Top 10 Peak Load Events
| Rank | Date/Time | Load (W) |
|------|-----------|----------|
| 1 | 2025-11-10 12:00 | 1035 |
| 2 | 2025-11-18 15:00 | 918 |
| 3 | 2025-11-19 12:00 | 882 |
| 4 | 2026-04-28 07:00 | 864 |
| 5 | 2026-04-27 17:00 | 855 |
| 6 | 2026-04-27 19:00 | 855 |
| 7 | 2026-04-27 21:00 | 855 |
| 8 | 2026-04-28 11:00 | 855 |
| 9 | 2026-04-27 22:00 | 846 |
| 10 | 2026-04-28 06:00 | 837 |

### Peak Load Statistics
- **Peak threshold (>90th percentile):** 558 W
- **Number of peak events:** 636
- **Peak load range:** 837 W to 1035 W

---

## 3. Hourly Patterns

- **Lowest average load:** Hour 5:00 (437.5 W)
- **Highest average load:** Hour 12:00 (465.9 W)
- **Load variation across hours:** 28.4 W

---

## 4. Daily Patterns (Weekday vs Weekend)

**Observations:**
- Weekday average: 456.2 W
- Weekend average: 441.2 W
- Weekday/Weekend difference: 15.0 W

---

## 5. Monthly Trends

| Month | Mean (W) | Std (W) | Min (W) | Max (W) | Records |
|-------|----------|---------|---------|---------|---------|
| 2025-10 | 409.0 | 47.7 | 360 | 639 | 585 |
| 2025-11 | 472.0 | 79.0 | 369 | 1035 | 649 |
| 2025-12 | 416.1 | 55.6 | 360 | 711 | 726 |
| 2026-01 | 438.6 | 96.9 | 360 | 801 | 740 |
| 2026-02 | 405.0 | 34.0 | 360 | 612 | 672 |
| 2026-03 | 454.5 | 90.9 | 315 | 729 | 741 |
| 2026-04 | 500.7 | 96.4 | 315 | 864 | 717 |
| 2026-05 | 486.3 | 52.6 | 414 | 738 | 726 |
| 2026-06 | 475.1 | 45.3 | 441 | 747 | 720 |
| 2026-07 | 484.9 | 16.7 | 468 | 540 | 16 |

---

## 6. Anomaly Detection

Anomalies detected using ±2 standard deviations from mean:
- **Lower threshold:** 296 W
- **Upper threshold:** 608 W
- **Number of anomalies:** 364
- **Anomaly rate:** 5.79%

---

## 7. Energy Consumption Summary

- **Total energy consumed:** 2,843 kWh
- **Average daily consumption:** 10.7 kWh/day
- **Estimated monthly consumption:** 320.6 kWh/month

---

## 8. Recommendations

1. **Peak Load Management:** Monitor high-load periods during business hours.
2. **Weekend Optimization:** Consider power-saving modes during low-usage periods.
3. **Capacity Planning:** Ensure UPS capacity provides 20-30% headroom above peak (1035 W).
4. **Anomaly Monitoring:** Investigate 364 anomalous readings.

---

*Report generated automatically by UPS Power Analysis Script*
