import os
from playwright.sync_api import sync_playwright

os.makedirs("/home/user/output", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel="chromium-headless-shell",
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-setuid-sandbox",
        ],
    )
    page = browser.new_page(viewport={"width": 1400, "height": 1200})
    page.goto("file:///home/user/server_power_analysis/interactive/00_dashboard.html", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    page.screenshot(path="/home/user/output/dash_preview.png", full_page=True)
    print("saved dashboard preview")
    browser.close()
