import os
from playwright.sync_api import sync_playwright

BASE = "file:///home/user/server_power_analysis/interactive"
OUT = "/home/user/server_power_analysis/previews"
os.makedirs(OUT, exist_ok=True)

files = {
    "00_dashboard.html": "00_dashboard",
    "01_interactive_timeseries.html": "01_interactive_timeseries",
    "02_heatmap_hour_weekday.html": "02_heatmap_hour_weekday",
    "03_hourly_box.html": "03_hourly_box",
    "04_3d_surface.html": "04_3d_surface",
    "05_distribution.html": "05_distribution",
    "06_monthly_violin.html": "06_monthly_violin",
}

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel="chromium-headless-shell",
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--disable-setuid-sandbox"],
    )
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    for fname, slug in files.items():
        url = f"{BASE}/{fname}"
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3500)  # allow Plotly to render from CDN
        page.screenshot(path=f"{OUT}/{slug}.jpg", full_page=False)
        print(f"shot: {slug}")
    browser.close()
print("DONE")
