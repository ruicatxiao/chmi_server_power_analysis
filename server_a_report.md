# Server A Power Analysis Report

**Generated:** 2026-07-02 12:20:23
**Data Period:** 2025-10-07 to 2026-07-02
**Total Records:** 6393 hourly readings

---

## Executive Summary

**Key Findings:**
- Average power load: **307.3 W**
- Peak power load: **621 W**
- Total energy consumed: **1,965 kWh**
- Average daily consumption: **7.3 kWh/day**

---

## 1. Descriptive Statistics

| Metric | Value |
|--------|-------|
| Mean Load | 307.3 W |
| Median Load | 288.0 W |
| Standard Deviation | 108.2 W |
| Minimum | 135 W |
| Maximum | 621 W |
| Coefficient of Variation | 0.352 |

### Percentile Distribution
| Percentile | Load (W) |
|------------|----------|
| 10th | 180 |
| 25th | 198 |
| 50th (Median) | 288 |
| 75th | 387 |
| 90th | 459 |
| 95th | 504 |
| 99th | 567 |

---

## 2. Peak Load Analysis

### Top 10 Peak Load Events
| Rank | Date/Time | Load (W) |
|------|-----------|----------|
| 1 | 2026-04-24 00:00 | 621 |
| 2 | 2026-04-24 02:00 | 621 |
| 3 | 2026-04-24 04:00 | 612 |
| 4 | 2026-04-24 09:00 | 612 |
| 5 | 2026-04-27 22:00 | 612 |
| 6 | 2026-04-23 21:00 | 603 |
| 7 | 2026-04-23 23:00 | 603 |
| 8 | 2026-04-24 03:00 | 603 |
| 9 | 2026-04-24 08:00 | 603 |
| 10 | 2026-04-28 00:00 | 603 |

### Peak Load Statistics
- **Peak threshold (>90th percentile):** 459 W
- **Number of peak events:** 662
- **Peak load range:** 603 W to 621 W

---

## 3. Hourly Patterns

- **Lowest average load:** Hour 10:00 (296.0 W)
- **Highest average load:** Hour 16:00 (316.8 W)
- **Load variation across hours:** 20.7 W

---

## 4. Daily Patterns (Weekday vs Weekend)

**Observations:**
- Weekday average: 309.6 W
- Weekend average: 301.5 W
- Weekday/Weekend difference: 8.1 W

---

## 5. Monthly Trends

| Month | Mean (W) | Std (W) | Min (W) | Max (W) | Records |
|-------|----------|---------|---------|---------|---------|
| 2025-10 | 370.0 | 81.6 | 135 | 549 | 586 |
| 2025-11 | 288.8 | 111.0 | 171 | 585 | 720 |
| 2025-12 | 329.6 | 95.1 | 171 | 558 | 726 |
| 2026-01 | 315.9 | 55.0 | 180 | 495 | 740 |
| 2026-02 | 228.9 | 59.1 | 162 | 549 | 672 |
| 2026-03 | 239.5 | 68.5 | 162 | 486 | 743 |
| 2026-04 | 385.5 | 130.3 | 162 | 621 | 720 |
| 2026-05 | 379.8 | 113.3 | 162 | 603 | 729 |
| 2026-06 | 240.2 | 69.9 | 162 | 513 | 720 |
| 2026-07 | 206.5 | 47.0 | 162 | 306 | 37 |

---

## 6. Anomaly Detection

Anomalies detected using ±2 standard deviations from mean:
- **Lower threshold:** 91 W
- **Upper threshold:** 524 W
- **Number of anomalies:** 212
- **Anomaly rate:** 3.32%

---

## 7. Energy Consumption Summary

- **Total energy consumed:** 1,965 kWh
- **Average daily consumption:** 7.3 kWh/day
- **Estimated monthly consumption:** 219.1 kWh/month

---

## 8. Recommendations

1. **Peak Load Management:** Monitor high-load periods during business hours.
2. **Weekend Optimization:** Consider power-saving modes during low-usage periods.
3. **Capacity Planning:** Ensure UPS capacity provides 20-30% headroom above peak (621 W).
4. **Anomaly Monitoring:** Investigate 212 anomalous readings.

---

*Report generated automatically by UPS Power Analysis Script*
