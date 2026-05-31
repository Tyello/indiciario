"""Backend de PDF: usa pypdf quando disponível e fallback mínimo para testes offline."""

from __future__ import annotations

import re
from pathlib import Path
from typing import BinaryIO

try:  # pragma: no cover - caminho principal quando dependência está instalada.
    from pypdf import PdfReader, PdfWriter
except ImportError:  # pragma: no cover - exercitado apenas em ambientes sem rede/dependência.

    class _MediaBox:
        def __init__(self, width: float, height: float) -> None:
            self.width = width
            self.height = height

    class _Page:
        def __init__(self, width: float = 595, height: float = 842) -> None:
            self.mediabox = _MediaBox(width, height)

    class PdfReader:  # type: ignore[no-redef]
        def __init__(self, stream: str | Path | BinaryIO) -> None:
            if hasattr(stream, "read"):
                raw = stream.read()
            else:
                raw = Path(stream).read_bytes()
            if isinstance(raw, str):
                raw_bytes = raw.encode("latin-1")
            else:
                raw_bytes = raw
            text = raw_bytes.decode("latin-1", errors="ignore")
            if "%PDF" not in text or "%%EOF" not in text:
                raise ValueError("Arquivo não parece ser um PDF válido")
            page_matches = [m for m in re.finditer(r"/Type\s*/Page\b", text)]
            boxes = re.findall(r"/MediaBox\s*\[\s*0\s+0\s+([0-9.]+)\s+([0-9.]+)\s*\]", text)
            self.pages = []
            for index, _match in enumerate(page_matches):
                if index < len(boxes):
                    width, height = boxes[index]
                    self.pages.append(_Page(float(width), float(height)))
                else:
                    self.pages.append(_Page())

    class PdfWriter:  # type: ignore[no-redef]
        def __init__(self) -> None:
            self._pages: list[_Page] = []

        def add_blank_page(self, width: float = 595, height: float = 842) -> _Page:
            page = _Page(width, height)
            self._pages.append(page)
            return page

        def add_page(self, page: _Page) -> None:
            self._pages.append(_Page(float(page.mediabox.width), float(page.mediabox.height)))

        def write(self, stream: BinaryIO) -> None:
            objects: list[str] = ["<< /Type /Catalog /Pages 2 0 R >>"]
            kids = " ".join(f"{3 + i} 0 R" for i in range(len(self._pages)))
            objects.append(f"<< /Type /Pages /Count {len(self._pages)} /Kids [{kids}] >>")
            for page in self._pages:
                objects.append(
                    "<< /Type /Page /Parent 2 0 R "
                    f"/MediaBox [0 0 {page.mediabox.width:g} {page.mediabox.height:g}] "
                    "/Resources << >> >>"
                )
            pdf = "%PDF-1.4\n"
            offsets = [0]
            for number, obj in enumerate(objects, start=1):
                offsets.append(len(pdf.encode("latin-1")))
                pdf += f"{number} 0 obj\n{obj}\nendobj\n"
            xref_offset = len(pdf.encode("latin-1"))
            pdf += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
            for offset in offsets[1:]:
                pdf += f"{offset:010d} 00000 n \n"
            pdf += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
            stream.write(pdf.encode("latin-1"))
