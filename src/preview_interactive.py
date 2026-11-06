import os
from playwright.sync_api import sync_playwright

os.makedirs("/home/user/output", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel="chromium-headless-shell",
        headless=True,
        args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--disable-setuid-sandbox"],
    )
    page = browser.new_page(viewport={"width": 1400, "height": 1000})
    page.goto("http://localhost:8123/interactive/01_interactive_timeseries.html", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    page.screenshot(path="/home/user/output/interactive_ts.png")
    print("title:", page.title())
    # count plotly traces
    n = page.evaluate("() => (window.PLOTLY !== undefined) ? document.querySelectorAll('.plotly-graph-div').length : 0")
    print("plotly graphs on page:", n)
    browser.close()
