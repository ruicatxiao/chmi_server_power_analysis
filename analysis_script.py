#!/usr/bin/env python3
"""
UPS Power Log Analysis Script - Multi-Server Edition
Analyzes power consumption data for multiple servers with comparison
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import json
import os
import warnings
warnings.filterwarnings('ignore')

# Set style for publication-quality figures
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11

# Paths
OUTPUT_DIR = 'servers_power_analysis'
DATA_DIR = f'{OUTPUT_DIR}/data'
STATS_DIR = f'{OUTPUT_DIR}/statistics'

def load_and_clean_data(filepath):
    """Load and clean the power log data"""
    df = pd.read_csv(filepath, sep='\t')
    
    # Create datetime column
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    df = df.sort_values('datetime').reset_index(drop=True)
    
    # Extract time components
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.day_name()
    df['month'] = df['datetime'].dt.to_period('M')
    df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
    
    return df

def compute_descriptive_stats(df):
    """Compute comprehensive descriptive statistics"""
    stats = {
        'count': int(len(df)),
        'mean': float(df['load'].mean()),
        'median': float(df['load'].median()),
        'std': float(df['load'].std()),
        'min': int(df['load'].min()),
        'max': int(df['load'].max()),
        'percentiles': {
            '10th': int(np.percentile(df['load'], 10)),
            '25th': int(np.percentile(df['load'], 25)),
            '50th': int(np.percentile(df['load'], 50)),
            '75th': int(np.percentile(df['load'], 75)),
            '90th': int(np.percentile(df['load'], 90)),
            '95th': int(np.percentile(df['load'], 95)),
            '99th': int(np.percentile(df['load'], 99))
        },
        'variance': float(df['load'].var()),
        'cv': float(df['load'].std() / df['load'].mean()),
        'total_energy_kwh': float((df['load'] * 1).sum() / 1000),
        'avg_daily_kwh': float((df.groupby(df['datetime'].dt.date)['load'].sum()).mean() / 1000)
    }
    
    return stats

def identify_peak_events(df, threshold_percentile=90):
    """Identify peak load events"""
    threshold = np.percentile(df['load'], threshold_percentile)
    peaks = df[df['load'] >= threshold].copy()
    top_peaks = df.nlargest(10, 'load')[['datetime', 'load']].copy()
    
    return top_peaks, peaks, threshold

def analyze_hourly_patterns(df):
    """Analyze load patterns by hour of day"""
    hourly_stats = df.groupby('hour')['load'].agg(['mean', 'std', 'min', 'max', 'count']).reset_index()
    weekday_avg = df[~df['is_weekend']].groupby('hour')['load'].mean()
    weekend_avg = df[df['is_weekend']].groupby('hour')['load'].mean()
    
    return hourly_stats, weekday_avg, weekend_avg

def analyze_daily_patterns(df):
    """Analyze load patterns by day of week"""
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_stats = df.groupby('day_of_week')['load'].agg(['mean', 'std', 'min', 'max']).reset_index()
    daily_stats = daily_stats.set_index('day_of_week').reindex(day_order).reset_index()
    return daily_stats

def analyze_monthly_trends(df):
    """Analyze monthly trends"""
    monthly_stats = df.groupby('month')['load'].agg(['mean', 'std', 'min', 'max', 'count']).reset_index()
    monthly_stats['month_str'] = monthly_stats['month'].astype(str)
    return monthly_stats

def detect_anomalies(df, n_std=2):
    """Detect anomalous load values"""
    mean = df['load'].mean()
    std = df['load'].std()
    upper_threshold = mean + n_std * std
    lower_threshold = mean - n_std * std
    anomalies = df[(df['load'] > upper_threshold) | (df['load'] < lower_threshold)].copy()
    
    return anomalies, lower_threshold, upper_threshold

# ============== VISUALIZATION FUNCTIONS ==============

def plot_time_series(df, save_path, title_suffix=""):
    """Time series of hourly load"""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(df['datetime'], df['load'], linewidth=0.8, color='#2E86AB', alpha=0.7)
    ax.fill_between(df['datetime'], df['load'], alpha=0.3, color='#2E86AB')
    
    ax.set_xlabel('Date')
    ax.set_ylabel('Power Load (W)')
    ax.set_title(f'UPS Power Load Over Time {title_suffix}')
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def plot_hourly_boxplot(df, save_path, title_suffix=""):
    """Hourly load distribution"""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    hourly_data = [df[df['hour'] == h]['load'].values for h in range(24)]
    bp = ax.boxplot(hourly_data, whis=1.5, patch_artist=True)
    
    for patch in bp['boxes']:
        patch.set_facecolor('#A8D8EA')
        patch.set_edgecolor('#2E86AB')
    
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Power Load (W)')
    ax.set_title(f'Hourly Power Load Distribution {title_suffix}')
    ax.set_xticks(range(1, 25))
    ax.set_xticklabels(range(24))
    
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def plot_weekday_comparison(df, weekday_avg, weekend_avg, save_path, title_suffix=""):
    """Weekday vs Weekend comparison"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    hours = range(24)
    ax.plot(hours, weekday_avg.values, linewidth=2, label='Weekday', color='#2E86AB')
    ax.plot(hours, weekend_avg.values, linewidth=2, label='Weekend', color='#AA96DA')
    
    ax.fill_between(hours, weekday_avg.values, alpha=0.3, color='#2E86AB')
    ax.fill_between(hours, weekend_avg.values, alpha=0.3, color='#AA96CA')
    
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Average Power Load (W)')
    ax.set_title(f'Weekday vs Weekend Power Load Patterns {title_suffix}')
    ax.set_xticks(range(0, 24, 3))
    ax.legend()
    ax.axvline(x=9, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=17, color='gray', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def plot_monthly_trend(monthly_stats, save_path, title_suffix=""):
    """Monthly trend"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    months = range(len(monthly_stats))
    ax.errorbar(months, monthly_stats['mean'], yerr=monthly_stats['std'], 
                fmt='o-', linewidth=2, capsize=5, color='#FCBAD3', label='Mean ± Std')
    
    ax.set_xlabel('Month')
    ax.set_ylabel('Average Power Load (W)')
    ax.set_title(f'Monthly Average Power Load Trend {title_suffix}')
    ax.set_xticks(months)
    ax.set_xticklabels(monthly_stats['month_str'], rotation=45)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def plot_load_distribution(df, save_path, title_suffix=""):
    """Load distribution histogram"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    n, bins, patches = ax.hist(df['load'], bins=50, density=True, alpha=0.6, 
                               color='#FFA8A8', edgecolor='black', linewidth=0.5)
    
    from scipy.stats import gaussian_kde
    kde = gaussian_kde(df['load'])
    x_kde = np.linspace(df['load'].min(), df['load'].max(), 200)
    ax.plot(x_kde, kde(x_kde), linewidth=2, color='#2E86AB', label='KDE')
    
    mean = df['load'].mean()
    median = df['load'].median()
    ax.axvline(mean, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean:.0f} W')
    ax.axvline(median, color='green', linestyle='--', linewidth=2, label=f'Median: {median:.0f} W')
    
    ax.set_xlabel('Power Load (W)')
    ax.set_ylabel('Density')
    ax.set_title(f'Power Load Distribution {title_suffix}')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def plot_peak_events(df, top_peaks, save_path, title_suffix=""):
    """Peak events highlighted"""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(df['datetime'], df['load'], linewidth=0.5, color='lightgray', alpha=0.5)
    ax.scatter(top_peaks['datetime'], top_peaks['load'], 
               c='red', s=100, zorder=5, label='Top 10 Peaks', edgecolors='darkred')
    
    ax.set_xlabel('Date')
    ax.set_ylabel('Power Load (W)')
    ax.set_title(f'Peak Power Load Events {title_suffix}')
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def plot_cumulative_energy(df, save_path, title_suffix=""):
    """Cumulative energy consumption"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    df_sorted = df.sort_values('datetime').copy()
    df_sorted['cumulative_kwh'] = df_sorted['load'].cumsum() / 1000
    
    ax.plot(df_sorted['datetime'], df_sorted['cumulative_kwh'], linewidth=2, color='#2E86AB')
    ax.fill_between(df_sorted['datetime'], df_sorted['cumulative_kwh'], alpha=0.3, color='#2E86AB')
    
    ax.set_xlabel('Date')
    ax.set_ylabel('Cumulative Energy (kWh)')
    ax.set_title(f'Cumulative Energy Consumption {title_suffix}')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def generate_server_report(server_name, stats, top_peaks, anomalies, df, hourly_stats, daily_stats, monthly_stats, lower_thresh, upper_thresh):
    """Generate report for a single server"""
    print(f"\nGenerating report for {server_name}...")
    
    report = f"""# {server_name} Power Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Data Period:** {df['datetime'].min().strftime('%Y-%m-%d')} to {df['datetime'].max().strftime('%Y-%m-%d')}
**Total Records:** {stats['count']} hourly readings

---

## Executive Summary

**Key Findings:**
- Average power load: **{stats['mean']:.1f} W**
- Peak power load: **{stats['max']} W**
- Total energy consumed: **{stats['total_energy_kwh']:,.0f} kWh**
- Average daily consumption: **{stats['avg_daily_kwh']:.1f} kWh/day**

---

## 1. Descriptive Statistics

| Metric | Value |
|--------|-------|
| Mean Load | {stats['mean']:.1f} W |
| Median Load | {stats['median']:.1f} W |
| Standard Deviation | {stats['std']:.1f} W |
| Minimum | {stats['min']} W |
| Maximum | {stats['max']} W |
| Coefficient of Variation | {stats['cv']:.3f} |

### Percentile Distribution
| Percentile | Load (W) |
|------------|----------|
| 10th | {stats['percentiles']['10th']} |
| 25th | {stats['percentiles']['25th']} |
| 50th (Median) | {stats['percentiles']['50th']} |
| 75th | {stats['percentiles']['75th']} |
| 90th | {stats['percentiles']['90th']} |
| 95th | {stats['percentiles']['95th']} |
| 99th | {stats['percentiles']['99th']} |

---

## 2. Peak Load Analysis

### Top 10 Peak Load Events
| Rank | Date/Time | Load (W) |
|------|-----------|----------|
"""
    
    for i, (_, row) in enumerate(top_peaks.iterrows(), 1):
        dt_str = row['datetime'].strftime('%Y-%m-%d %H:%M')
        report += f"| {i} | {dt_str} | {row['load']} |\n"
    
    report += f"""
### Peak Load Statistics
- **Peak threshold (>90th percentile):** {np.percentile(df['load'], 90):.0f} W
- **Number of peak events:** {len(df[df['load'] >= np.percentile(df['load'], 90)])}
- **Peak load range:** {top_peaks['load'].min()} W to {top_peaks['load'].max()} W

---

## 3. Hourly Patterns

- **Lowest average load:** Hour {hourly_stats.loc[hourly_stats['mean'].idxmin(), 'hour']}:00 ({hourly_stats['mean'].min():.1f} W)
- **Highest average load:** Hour {hourly_stats.loc[hourly_stats['mean'].idxmax(), 'hour']}:00 ({hourly_stats['mean'].max():.1f} W)
- **Load variation across hours:** {hourly_stats['mean'].max() - hourly_stats['mean'].min():.1f} W

---

## 4. Daily Patterns (Weekday vs Weekend)

**Observations:**
- Weekday average: {df[~df['is_weekend']]['load'].mean():.1f} W
- Weekend average: {df[df['is_weekend']]['load'].mean():.1f} W
- Weekday/Weekend difference: {df[~df['is_weekend']]['load'].mean() - df[df['is_weekend']]['load'].mean():.1f} W

---

## 5. Monthly Trends

| Month | Mean (W) | Std (W) | Min (W) | Max (W) | Records |
|-------|----------|---------|---------|---------|---------|
"""
    
    for _, row in monthly_stats.iterrows():
        report += f"| {row['month_str']} | {row['mean']:.1f} | {row['std']:.1f} | {int(row['min'])} | {int(row['max'])} | {int(row['count'])} |\n"

    report += f"""
---

## 6. Anomaly Detection

Anomalies detected using ±2 standard deviations from mean:
- **Lower threshold:** {lower_thresh:.0f} W
- **Upper threshold:** {upper_thresh:.0f} W
- **Number of anomalies:** {len(anomalies)}
- **Anomaly rate:** {100*len(anomalies)/len(df):.2f}%

---

## 7. Energy Consumption Summary

- **Total energy consumed:** {stats['total_energy_kwh']:,.0f} kWh
- **Average daily consumption:** {stats['avg_daily_kwh']:.1f} kWh/day
- **Estimated monthly consumption:** {stats['avg_daily_kwh']*30:.1f} kWh/month

---

## 8. Recommendations

1. **Peak Load Management:** Monitor high-load periods during business hours.
2. **Weekend Optimization:** Consider power-saving modes during low-usage periods.
3. **Capacity Planning:** Ensure UPS capacity provides 20-30% headroom above peak ({stats['max']} W).
4. **Anomaly Monitoring:** Investigate {len(anomalies)} anomalous readings.

---

*Report generated automatically by UPS Power Analysis Script*
"""
    
    return report

def generate_comparison_report(server_a_data, server_b_data):
    """Generate comparison report between two servers"""
    print("\nGenerating comparison report...")
    
    s1_name, s1_stats, s1_df = server_a_data
    s2_name, s2_stats, s2_df = server_b_data
    
    report = f"""# Server Power Comparison Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

This report compares power consumption patterns between **{s1_name}** and **{s2_name}**.

### Key Comparison Metrics

| Metric | {s1_name} | {s2_name} | Difference |
|--------|-----------|-----------|------------|
| Average Load | {s1_stats['mean']:.1f} W | {s2_stats['mean']:.1f} W | {s1_stats['mean'] - s2_stats['mean']:.1f} W |
| Peak Load | {s1_stats['max']} W | {s2_stats['max']} W | {s1_stats['max'] - s2_stats['max']} W |
| Total Energy (kWh) | {s1_stats['total_energy_kwh']:,.0f} | {s2_stats['total_energy_kwh']:,.0f} | {s1_stats['total_energy_kwh'] - s2_stats['total_energy_kwh']:,.0f} |
| Avg Daily (kWh) | {s1_stats['avg_daily_kwh']:.1f} | {s2_stats['avg_daily_kwh']:.1f} | {s1_stats['avg_daily_kwh'] - s2_stats['avg_daily_kwh']:.1f} |
| Std Dev | {s1_stats['std']:.1f} W | {s2_stats['std']:.1f} W | {s1_stats['std'] - s2_stats['std']:.1f} W |
| Coefficient of Variation | {s1_stats['cv']:.3f} | {s2_stats['cv']:.3f} | {s1_stats['cv'] - s2_stats['cv']:.3f} |

---

## 1. Load Distribution Comparison

### Percentile Comparison
| Percentile | {s1_name} (W) | {s2_name} (W) | Difference (W) |
|------------|---------------|---------------|----------------|
"""
    
    for p in ['10th', '25th', '50th', '75th', '90th', '95th', '99th']:
        diff = s1_stats['percentiles'][p] - s2_stats['percentiles'][p]
        report += f"| {p} | {s1_stats['percentiles'][p]} | {s2_stats['percentiles'][p]} | {diff:+.0f} |\n"
    
    report += f"""
---

## 2. Daily Pattern Comparison

### Weekday vs Weekend Analysis

| Server | Weekday Avg (W) | Weekend Avg (W) | Difference (W) |
|--------|-----------------|-----------------|----------------|
| {s1_name} | {s1_df[~s1_df['is_weekend']]['load'].mean():.1f} | {s1_df[s1_df['is_weekend']]['load'].mean():.1f} | {s1_df[~s1_df['is_weekend']]['load'].mean() - s1_df[s1_df['is_weekend']]['load'].mean():.1f} |
| {s2_name} | {s2_df[~s2_df['is_weekend']]['load'].mean():.1f} | {s2_df[s2_df['is_weekend']]['load'].mean():.1f} | {s2_df[~s2_df['is_weekend']]['load'].mean() - s2_df[s2_df['is_weekend']]['load'].mean():.1f} |

---

## 3. Hourly Pattern Comparison

### Peak Hours Analysis

| Server | Lowest Hour | Lowest Avg (W) | Highest Hour | Highest Avg (W) |
|--------|-------------|----------------|--------------|-----------------|
| {s1_name} | {s1_df.groupby('hour')['load'].mean().idxmin()}:00 | {s1_df.groupby('hour')['load'].mean().min():.1f} | {s1_df.groupby('hour')['load'].mean().idxmax()}:00 | {s1_df.groupby('hour')['load'].mean().max():.1f} |
| {s2_name} | {s2_df.groupby('hour')['load'].mean().idxmin()}:00 | {s2_df.groupby('hour')['load'].mean().min():.1f} | {s2_df.groupby('hour')['load'].mean().idxmax()}:00 | {s2_df.groupby('hour')['load'].mean().max():.1f} |

---

## 4. Monthly Trend Comparison

| Month | {s1_name} Mean (W) | {s2_name} Mean (W) | Difference (W) |
|-------|-------------------|-------------------|----------------|
"""
    
    s1_monthly = s1_df.groupby('month')['load'].mean()
    s2_monthly = s2_df.groupby('month')['load'].mean()
    all_months = sorted(set(s1_monthly.index) | set(s2_monthly.index))
    
    for month in all_months:
        s1_val = s1_monthly.get(month, np.nan)
        s2_val = s2_monthly.get(month, np.nan)
        diff = s1_val - s2_val if not np.isnan(s1_val) and not np.isnan(s2_val) else np.nan
        s1_str = f"{s1_val:.1f}" if not np.isnan(s1_val) else "N/A"
        s2_str = f"{s2_val:.1f}" if not np.isnan(s2_val) else "N/A"
        diff_str = f"{diff:.1f}" if not np.isnan(diff) else "N/A"
        report += f"| {month} | {s1_str} | {s2_str} | {diff_str} |\n"
    
    report += f"""
---

## 5. Energy Efficiency Analysis

### Energy Consumption Comparison

| Metric | {s1_name} | {s2_name} | Analysis |
|--------|-----------|-----------|----------|
| Total Energy | {s1_stats['total_energy_kwh']:,.0f} kWh | {s2_stats['total_energy_kwh']:,.0f} kWh | {s1_name if s1_stats['total_energy_kwh'] < s2_stats['total_energy_kwh'] else s2_name} uses less total energy |
| Avg Hourly Load | {s1_stats['mean']:.1f} W | {s2_stats['mean']:.1f} W | {s1_name if s1_stats['mean'] < s2_stats['mean'] else s2_name} has lower average load |
| Load Stability (CV) | {s1_stats['cv']:.3f} | {s2_stats['cv']:.3f} | {s1_name if s1_stats['cv'] < s2_stats['cv'] else s2_name} has more stable load |

---

## 6. Key Findings & Recommendations

### Comparative Insights

1. **Average Load Difference:** {s1_name} averages **{abs(s1_stats['mean'] - s2_stats['mean']):.1f} W** {'higher' if s1_stats['mean'] > s2_stats['mean'] else 'lower'} than {s2_name}

2. **Peak Load Analysis:** 
   - {s1_name} peak: {s1_stats['max']} W
   - {s2_name} peak: {s2_stats['max']} W
   - {'{s1_name} has the higher peak load' if s1_stats['max'] > s2_stats['max'] else '{s2_name} has the higher peak load'}

3. **Load Variability:** 
   - {s1_name} CV: {s1_stats['cv']:.3f}
   - {s2_name} CV: {s2_stats['cv']:.3f}
   - {'{s1_name} has more variable load' if s1_stats['cv'] > s2_stats['cv'] else '{s2_name} has more variable load'}

4. **Energy Efficiency:** 
   - {'{s1_name} is more energy efficient' if s1_stats['avg_daily_kwh'] < s2_stats['avg_daily_kwh'] else '{s2_name} is more energy efficient'} with {'{s1_stats["avg_daily_kwh"]:.1f}' if s1_stats['avg_daily_kwh'] < s2_stats['avg_daily_kwh'] else '{s2_stats["avg_daily_kwh"]:.1f}'} kWh/day average

### Recommendations

1. **Load Balancing:** Consider redistributing workloads to balance power consumption between servers.

2. **Peak Management:** {'{s1_name}' if s1_stats['max'] > s2_stats['max'] else '{s2_name}'} has higher peaks - investigate causes and consider load shedding strategies.

3. **Capacity Planning:** Size UPS systems based on the higher peak load ({max(s1_stats['max'], s2_stats['max'])} W) with 20-30% headroom.

4. **Monitoring:** Implement continuous monitoring to track power efficiency improvements over time.

---

*Comparison report generated automatically by UPS Power Analysis Script*
"""
    
    return report

def main():
    """Main analysis pipeline for multiple servers"""
    print("=" * 60)
    print("Multi-Server UPS Power Log Analysis")
    print("=" * 60)
    
    # Define servers to analyze
    servers = [
        ('Server A', 'ups_power_log_server_a.txt', 'figures_server_a'),
        ('Server B', 'ups_power_log_server_b.txt', 'figures_server_b')
    ]
    
    server_data = {}
    
    for server_name, filepath, fig_dir in servers:
        print(f"\n{'='*60}")
        print(f"Analyzing {server_name}")
        print('='*60)
        
        # Load data
        df = load_and_clean_data(filepath)
        print(f"  Loaded {len(df)} hourly readings")
        print(f"  Date range: {df['datetime'].min()} to {df['datetime'].max()}")
        
        # Compute statistics
        stats = compute_descriptive_stats(df)
        print(f"  Mean load: {stats['mean']:.1f} W")
        print(f"  Peak load: {stats['max']} W")
        print(f"  Total energy: {stats['total_energy_kwh']:.0f} kWh")
        
        # Identify peaks
        top_peaks, peaks, threshold = identify_peak_events(df)
        print(f"  Peak threshold: {threshold:.0f} W")
        print(f"  Number of peak events: {len(peaks)}")
        
        # Detect anomalies
        anomalies, lower_thresh, upper_thresh = detect_anomalies(df)
        print(f"  Anomalies detected: {len(anomalies)}")
        
        # Analyze patterns
        hourly_stats, weekday_avg, weekend_avg = analyze_hourly_patterns(df)
        daily_stats = analyze_daily_patterns(df)
        monthly_stats = analyze_monthly_trends(df)
        
        # Save data
        df_out = df.copy()
        df_out['datetime'] = df_out['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df_out.to_csv(f'{DATA_DIR}/{server_name.lower().replace(" ", "_")}_cleaned_data.csv', index=False)
        
        top_peaks_out = top_peaks.copy()
        top_peaks_out['datetime'] = top_peaks_out['datetime'].dt.strftime('%Y-%m-%d %H:%M')
        top_peaks_out.to_csv(f'{DATA_DIR}/{server_name.lower().replace(" ", "_")}_top_peaks.csv', index=False)
        
        if len(anomalies) > 0:
            anomalies_out = anomalies.copy()
            anomalies_out['datetime'] = anomalies_out['datetime'].dt.strftime('%Y-%m-%d %H:%M')
            anomalies_out.to_csv(f'{DATA_DIR}/{server_name.lower().replace(" ", "_")}_anomalies.csv', index=False)
        
        # Save statistics
        stats['file'] = filepath
        with open(f'{STATS_DIR}/{server_name.lower().replace(" ", "_")}_stats.json', 'w') as f:
            json.dump(stats, f, indent=2)
        
        # Generate visualizations
        print(f"\n  Generating visualizations in {fig_dir}/...")
        plot_time_series(df, f'{OUTPUT_DIR}/{fig_dir}/fig1_time_series.png', f"({server_name})")
        plot_hourly_boxplot(df, f'{OUTPUT_DIR}/{fig_dir}/fig2_hourly_boxplot.png', f"({server_name})")
        plot_weekday_comparison(df, weekday_avg, weekend_avg, f'{OUTPUT_DIR}/{fig_dir}/fig3_weekday_comparison.png', f"({server_name})")
        plot_monthly_trend(monthly_stats, f'{OUTPUT_DIR}/{fig_dir}/fig4_monthly_trend.png', f"({server_name})")
        plot_load_distribution(df, f'{OUTPUT_DIR}/{fig_dir}/fig5_load_distribution.png', f"({server_name})")
        plot_peak_events(df, top_peaks, f'{OUTPUT_DIR}/{fig_dir}/fig6_peak_events.png', f"({server_name})")
        plot_cumulative_energy(df, f'{OUTPUT_DIR}/{fig_dir}/fig7_cumulative_energy.png', f"({server_name})")
        
        # Generate individual report
        report = generate_server_report(
            server_name, stats, top_peaks, anomalies, df, 
            hourly_stats, daily_stats, monthly_stats, lower_thresh, upper_thresh
        )
        with open(f'{OUTPUT_DIR}/{server_name.lower().replace(" ", "_")}_report.md', 'w') as f:
            f.write(report)
        
        # Store for comparison
        server_data[server_name] = (server_name, stats, df)
        print(f"  Saved {server_name} report and figures")
    
    # Generate comparison report
    print("\n" + "=" * 60)
    print("Generating Comparison Report")
    print("=" * 60)
    
    comparison_report = generate_comparison_report(
        server_data['Server A'],
        server_data['Server B']
    )
    
    with open(f'{OUTPUT_DIR}/comparison_report.md', 'w') as f:
        f.write(comparison_report)
    
    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)
    print(f"\nOutput directory: {OUTPUT_DIR}/")
    print("  - Server A report: server_a_report.md")
    print("  - Server B report: server_b_report.md")
    print("  - Comparison report: comparison_report.md")
    print("  - Figures Server A: figures_server_a/ (7 PNG)")
    print("  - Figures Server B: figures_server_b/ (7 PNG)")
    print("  - Data: data/ (cleaned data, summaries)")
    print("  - Statistics: statistics/ (JSON)")

if __name__ == '__main__':
    main()
