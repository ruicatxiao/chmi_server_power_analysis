import os
from playwright.sync_api import sync_playwright

os.makedirs("/home/user/output", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel="chromium-headless-shell",
        headless=True,
        args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--disable-setuid-sandbox"],
    )
    page = browser.new_page(viewport={"width": 1400, "height": 1600})
    page.goto("http://localhost:8123/index.html", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)
    # get page height
    height = page.evaluate("document.body.scrollHeight")
    print("page height:", height)
    # capture in viewport chunks
    chunk = 1600
    step = 1400  # slight overlap
    pos = 0
    n = 0
    while pos < height:
        page.evaluate(f"window.scrollTo(0, {pos})")
        page.wait_for_timeout(800)
        page.screenshot(path=f"/home/user/output/landing_scroll_{n:02d}.png")
        pos += step
        n += 1
        if n > 12:
            break
    print("captured", n, "chunks")
    broken = page.evaluate("() => Array.from(document.images).filter(i => !i.complete || i.naturalWidth === 0).map(i => i.getAttribute('src'))")
    print("broken images:", broken)
    browser.close()
