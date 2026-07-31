from __future__ import annotations

import asyncio
import base64
import html
import sys
from pathlib import Path

from playwright.async_api import async_playwright


async def render_text(
    font_path: Path,
    output_path: Path,
    text: str,
    font_size: int = 70,
    canvas_width: int = 1800,
    canvas_height: int = 230,
) -> None:
    if not font_path.is_file():
        raise FileNotFoundError(f"Font not found: {font_path}")

    encoded_font = base64.b64encode(
        font_path.read_bytes()
    ).decode("ascii")

    font_data_url = f"data:font/ttf;base64,{encoded_font}"
    safe_text = html.escape(text)

    document = f"""
    <!DOCTYPE html>
    <html lang="ur" dir="rtl">
    <head>
        <meta charset="UTF-8">

        <style>
            @font-face {{
                font-family: "Kanz";
                src: url("{font_data_url}") format("truetype");
                font-weight: normal;
                font-style: normal;
                font-display: block;
            }}

            html, body {{
                margin: 0;
                padding: 0;
                width: {canvas_width}px;
                height: {canvas_height}px;
                background: white;
                overflow: hidden;
            }}

            #text-line {{
                box-sizing: border-box;
                width: 100%;
                height: 100%;
                padding: 30px 50px;

                direction: rtl;
                text-align: right;
                white-space: nowrap;

                font-family: "Kanz";
                font-size: {font_size}px;
                line-height: 1.6;

                color: black;
                background: white;
            }}
        </style>
    </head>

    <body>
        <div id="text-line">{safe_text}</div>
    </body>
    </html>
    """

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True
        )

        page = await browser.new_page(
            viewport={
                "width": canvas_width,
                "height": canvas_height,
            }
        )

        await page.set_content(
            document,
            wait_until="load",
        )

        await page.evaluate(
            f"""
            async () => {{
                await document.fonts.load(
                    '{font_size}px "Kanz"'
                );
                await document.fonts.ready;
            }}
            """
        )

        font_loaded = await page.evaluate(
            f'document.fonts.check(\'{font_size}px "Kanz"\')'
        )

        if not font_loaded:
            raise RuntimeError(
                "Chromium could not load the Kanz font."
            )

        await page.locator("#text-line").screenshot(
            path=str(output_path)
        )

        await browser.close()


def main() -> None:
    if len(sys.argv) < 4:
        raise SystemExit(
            "Usage: python render_worker.py "
            "<font_path> <output_path> <text> [font_size]"
        )

    font_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    text = sys.argv[3]

    font_size = (
        int(sys.argv[4])
        if len(sys.argv) > 4
        else 70
    )

    asyncio.run(
        render_text(
            font_path=font_path,
            output_path=output_path,
            text=text,
            font_size=font_size,
        )
    )


if __name__ == "__main__":
    main()