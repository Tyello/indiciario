"""Smoke test manual de PDFs via Playwright/Chromium.

Uso:
    python -m scripts.smoke_playwright_pdf
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from generator.renderer import _html_para_pdf


async def main() -> None:
    output_dir = Path("output/smoke")
    output_dir.mkdir(parents=True, exist_ok=True)
    portrait = output_dir / "smoke_portrait.pdf"
    landscape = output_dir / "smoke_landscape.pdf"
    html = """
    <html><body style='font-family: sans-serif'>
      <h1>Smoke Playwright</h1>
      <p>Renderização técnica do Indiciário via Chromium.</p>
    </body></html>
    """
    try:
        await _html_para_pdf(html, portrait, landscape=False)
        await _html_para_pdf(html, landscape, landscape=True)
    except ModuleNotFoundError as exc:
        if exc.name == "playwright":
            raise SystemExit(
                "Playwright não está instalado. Rode: pip install -r requirements.txt "
                "&& python -m playwright install chromium"
            ) from exc
        raise
    print(f"PDF portrait: {portrait}")
    print(f"PDF landscape: {landscape}")


if __name__ == "__main__":
    asyncio.run(main())
