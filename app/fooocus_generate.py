from playwright.sync_api import sync_playwright
import time
from pathlib import Path

FOOOCUS_URL = "http://127.0.0.1:7865"
OUTPUT_DIR = Path(r"D:\Fooocus\Fooocus_win64_2-5-0\Fooocus\outputs")

PROMPT = """
AI cinematic still, ultra realistic photograph,East Asian woman, emotional expression,cinematic lighting, shallow depth of field,35mm film still, professional photography,influencer aesthetic, soft skin, detailed eyes
"""

NEGATIVE = """
unrealistic, saturated, high contrast, big nose, painting, drawing, sketch, cartoon, anime, manga, render, CG, 3d, watermark, signature, label,blurry, low quality, distorted face, bad anatomy,
extra fingers, text
"""

def latest_image(before: set):
    images = set(OUTPUT_DIR.glob("*.png"))
    new = images - before
    return max(new, key=lambda p: p.stat().st_mtime) if new else None


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(FOOOCUS_URL, timeout=60_000)

    # Počkať na UI
    page.wait_for_selector("textarea", timeout=60_000)
    time.sleep(2)

    before = set(OUTPUT_DIR.glob("*.png"))

    # =========================
    # PROMPT
    # =========================
    page.locator("textarea").first.fill(PROMPT)

    # =========================
    # ADVANCED CHECKBOX
    # =========================
    advanced_checkbox = page.locator(
        "label:has-text('Advanced') input[type='checkbox']"
    ).first

    if not advanced_checkbox.is_checked():
        advanced_checkbox.click()
        print("Advanced enabled")
    time.sleep(2)
    
    # Počkať na Negative Prompt textarea
    negative_box = page.locator('#negative_prompt textarea')
    negative_box.wait_for(state='visible')
    time.sleep(2)
    # =========================
    # NEGATIVE PROMPT
    # =========================
    negative_box.fill(NEGATIVE)

    # =========================
    # QUALITY MODE (nie Speed)
    # =========================
    quality_radio = page.locator(
        "label[data-testid='Quality-radio-label'] input[type='radio']"
    )

    if not quality_radio.is_checked():
        quality_radio.click()
        print("Quality mode selected")

    time.sleep(1)

    # =========================
    # GENERATE
    # =========================
    page.locator("#generate_button").click()
    print("Generating image...")

    # =========================
    # WAIT FOR OUTPUT
    # =========================
    for _ in range(180):  # Quality = dlhšie
        img = latest_image(before)
        if img:
            print("Image created:", img)
            break
        time.sleep(2)

    
