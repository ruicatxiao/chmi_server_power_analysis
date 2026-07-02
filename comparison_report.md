# Server Power Comparison Report

**Generated:** 2026-07-02 12:20:27

---

## Executive Summary

This report compares power consumption patterns between **Server A** and **Server B**.

### Key Comparison Metrics

| Metric | Server A | Server B | Difference |
|--------|-----------|-----------|------------|
| Average Load | 307.3 W | 451.8 W | -144.5 W |
| Peak Load | 621 W | 1035 W | -414 W |
| Total Energy (kWh) | 1,965 | 2,843 | -878 |
| Avg Daily (kWh) | 7.3 | 10.7 | -3.4 |
| Std Dev | 108.2 W | 78.2 W | 30.1 W |
| Coefficient of Variation | 0.352 | 0.173 | 0.179 |

---

## 1. Load Distribution Comparison

### Percentile Comparison
| Percentile | Server A (W) | Server B (W) | Difference (W) |
|------------|---------------|---------------|----------------|
| 10th | 180 | 369 | -189 |
| 25th | 198 | 396 | -198 |
| 50th | 288 | 450 | -162 |
| 75th | 387 | 468 | -81 |
| 90th | 459 | 558 | -99 |
| 95th | 504 | 630 | -126 |
| 99th | 567 | 711 | -144 |

---

## 2. Daily Pattern Comparison

### Weekday vs Weekend Analysis

| Server | Weekday Avg (W) | Weekend Avg (W) | Difference (W) |
|--------|-----------------|-----------------|----------------|
| Server A | 309.6 | 301.5 | 8.1 |
| Server B | 456.2 | 441.2 | 15.0 |

---

## 3. Hourly Pattern Comparison

### Peak Hours Analysis

| Server | Lowest Hour | Lowest Avg (W) | Highest Hour | Highest Avg (W) |
|--------|-------------|----------------|--------------|-----------------|
| Server A | 10:00 | 296.0 | 16:00 | 316.8 |
| Server B | 5:00 | 437.5 | 12:00 | 465.9 |

---

## 4. Monthly Trend Comparison

| Month | Server A Mean (W) | Server B Mean (W) | Difference (W) |
|-------|-------------------|-------------------|----------------|
| 2025-10 | 370.0 | 409.0 | -38.9 |
| 2025-11 | 288.8 | 472.0 | -183.2 |
| 2025-12 | 329.6 | 416.1 | -86.5 |
| 2026-01 | 315.9 | 438.6 | -122.7 |
| 2026-02 | 228.9 | 405.0 | -176.2 |
| 2026-03 | 239.5 | 454.5 | -215.1 |
| 2026-04 | 385.5 | 500.7 | -115.1 |
| 2026-05 | 379.8 | 486.3 | -106.5 |
| 2026-06 | 240.2 | 475.1 | -234.9 |
| 2026-07 | 206.5 | 484.9 | -278.4 |

---

## 5. Energy Efficiency Analysis

### Energy Consumption Comparison

| Metric | Server A | Server B | Analysis |
|--------|-----------|-----------|----------|
| Total Energy | 1,965 kWh | 2,843 kWh | Server A uses less total energy |
| Avg Hourly Load | 307.3 W | 451.8 W | Server A has lower average load |
| Load Stability (CV) | 0.352 | 0.173 | Server B has more stable load |

---

## 6. Key Findings & Recommendations

### Comparative Insights

1. **Average Load Difference:** Server A averages **144.5 W** lower than Server B

2. **Peak Load Analysis:** 
   - Server A peak: 621 W
   - Server B peak: 1035 W
   - {s2_name} has the higher peak load

3. **Load Variability:** 
   - Server A CV: 0.352
   - Server B CV: 0.173
   - {s1_name} has more variable load

4. **Energy Efficiency:** 
   - {s1_name} is more energy efficient with {s1_stats["avg_daily_kwh"]:.1f} kWh/day average

### Recommendations

1. **Load Balancing:** Consider redistributing workloads to balance power consumption between servers.

2. **Peak Management:** {s2_name} has higher peaks - investigate causes and consider load shedding strategies.

3. **Capacity Planning:** Size UPS systems based on the higher peak load (1035 W) with 20-30% headroom.

4. **Monitoring:** Implement continuous monitoring to track power efficiency improvements over time.

---

*Comparison report generated automatically by UPS Power Analysis Script*
