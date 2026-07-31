import asyncio
import html
from pathlib import Path

from playwright.async_api import async_playwright


FONT_PATH = Path(
    r"C:\Users\ammar\OneDrive\Desktop\largelisaanmodel"
    r"\Kanz-al-Marjaan\build\Kanz-al-Marjaan-Regular.ttf"
).resolve()

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "synthetic_dataset" / "images"
LABEL_PATH = BASE_DIR / "synthetic_dataset" / "train.txt"

sentences = [
    "الله تعالى ني نعمت",
    "اپنے مولا ني ذكر",
    "پہلے مؤمنين نے عرض كيدو",
    "لئے مؤمنين ني جماعت",
    "بسم الله الرحمن الرحيم",
]


async def generate_images() -> None:
    if not FONT_PATH.is_file():
        raise FileNotFoundError(f"Font not found: {FONT_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    labels: list[str] = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page(
            viewport={"width": 1600, "height": 220},
            device_scale_factor=1,
        )

        for index, text in enumerate(sentences, start=1):
            safe_text = html.escape(text)

            document = f"""
            <!DOCTYPE html>
            <html lang="ur" dir="rtl">
            <head>
                <meta charset="UTF-8">

                <style>
                    @font-face {{
                        font-family: "Kanz";
                        src: url("{FONT_PATH.as_uri()}") format("truetype");
                        font-weight: normal;
                        font-style: normal;
                    }}

                    html, body {{
                        margin: 0;
                        padding: 0;
                        width: 1600px;
                        height: 220px;
                        background: white;
                        overflow: hidden;
                    }}

                    #text-line {{
                        box-sizing: border-box;
                        width: 100%;
                        height: 100%;
                        padding: 35px 50px;

                        direction: rtl;
                        text-align: right;
                        white-space: nowrap;

                        font-family: "Kanz", serif;
                        font-size: 72px;
                        line-height: 1.6;
                        color: black;
                    }}
                </style>
            </head>

            <body>
                <div id="text-line">{safe_text}</div>
            </body>
            </html>
            """

            await page.set_content(document)

            # Wait for the custom font to finish loading.
            await page.evaluate("document.fonts.ready")

            font_loaded = await page.evaluate(
                "document.fonts.check('72px Kanz')"
            )

            if not font_loaded:
                raise RuntimeError(
                    f"The Kanz font was not loaded for line {index}."
                )

            image_path = OUTPUT_DIR / f"line_{index:05d}.png"

            # Screenshot only the text element rather than the whole page.
            await page.locator("#text-line").screenshot(
                path=str(image_path)
            )

            relative_path = image_path.relative_to(BASE_DIR).as_posix()
            labels.append(f"{relative_path}\t{text}")

            print(f"Created: {image_path.name}")

        await browser.close()

    LABEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    LABEL_PATH.write_text("\n".join(labels), encoding="utf-8")

    print(f"\nGenerated {len(labels)} images")
    print(f"Images: {OUTPUT_DIR}")
    print(f"Labels: {LABEL_PATH}")


if __name__ == "__main__":
    if hasattr(asyncio, "WindowsProactorEventLoopPolicy"):
        asyncio.set_event_loop_policy(
            asyncio.WindowsProactorEventLoopPolicy()
        )

    asyncio.run(generate_images())