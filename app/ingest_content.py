from __future__ import annotations

import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pypdf import PdfReader


TEXT_EXTENSIONS = {
    ".csv",
    ".htm",
    ".html",
    ".ini",
    ".json",
    ".log",
    ".md",
    ".markdown",
    ".msg",
    ".text",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

PDF_EXTENSIONS = {".pdf"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff"}
TEXT_MIME_PREFIXES = ("text/",)
IMAGE_MIME_PREFIXES = ("image/",)
TEXT_MIME_TYPES = {
    "application/json",
    "application/pdf",  # handled separately below
    "application/xml",
    "application/xhtml+xml",
    "application/x-yaml",
    "application/yaml",
}


@dataclass(frozen=True)
class ExtractedText:
    text: str | None
    extraction_mode: str
    notes: list[str]


class OCRExtractor(Protocol):
    name: str

    def extract_text(self, raw: bytes, *, file_name: str | None = None, mime_type: str | None = None) -> ExtractedText:
        ...


class NotImplementedOCRExtractor:
    name = "ocr_not_implemented"

    def extract_text(self, raw: bytes, *, file_name: str | None = None, mime_type: str | None = None) -> ExtractedText:
        return ExtractedText(
            text=None,
            extraction_mode="ocr_not_implemented",
            notes=[
                "Bild- och screenshot-OCR är bara förberedd som ett separat extractor-kontrakt. Den är inte implementerad ännu.",
            ],
        )


def normalize_ingest_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    collapsed = "\n".join(lines)
    collapsed = re.sub(r"\n{3,}", "\n\n", collapsed)
    return collapsed.strip()


def _looks_textual(raw: bytes) -> bool:
    if not raw:
        return False
    if b"\x00" in raw:
        return False
    sample = raw[:4096]
    printable = sum(1 for byte in sample if 9 <= byte <= 13 or 32 <= byte <= 126)
    return printable / max(len(sample), 1) >= 0.85


def _extract_pdf_text(raw: bytes) -> ExtractedText:
    try:
        reader = PdfReader(io.BytesIO(raw))
    except Exception as exc:  # pragma: no cover - exercised by runtime integration
        return ExtractedText(
            text=None,
            extraction_mode="pdf_unreadable",
            notes=[f"PDF kunde inte läsas: {exc}"],
        )

    extracted_pages: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            extracted_pages.append(page_text)

    if not extracted_pages:
        return ExtractedText(
            text=None,
            extraction_mode="pdf_no_text",
            notes=["PDF:en innehöll ingen extraherbar text."],
        )

    normalized = normalize_ingest_text("\n\n".join(extracted_pages))
    return ExtractedText(
        text=normalized or None,
        extraction_mode="pdf_text",
        notes=["Text extraherades från PDF utan OCR."],
    )


def extract_text_from_upload(
    raw: bytes,
    *,
    file_name: str | None = None,
    mime_type: str | None = None,
    ocr_extractor: OCRExtractor | None = None,
) -> ExtractedText:
    suffix = Path(file_name or "").suffix.lower()
    mime = (mime_type or "").lower()

    if suffix in IMAGE_EXTENSIONS or mime.startswith(IMAGE_MIME_PREFIXES):
        extractor = ocr_extractor or NotImplementedOCRExtractor()
        return extractor.extract_text(raw, file_name=file_name, mime_type=mime_type)

    if suffix in PDF_EXTENSIONS or mime == "application/pdf":
        return _extract_pdf_text(raw)

    if suffix in TEXT_EXTENSIONS or mime.startswith(TEXT_MIME_PREFIXES) or mime in TEXT_MIME_TYPES:
        text = raw.decode("utf-8", errors="replace")
        normalized = normalize_ingest_text(text)
        return ExtractedText(
            text=normalized or None,
            extraction_mode="text_file",
            notes=["Text lästes direkt ur uppladdad fil."],
        )

    if _looks_textual(raw):
        text = raw.decode("utf-8", errors="replace")
        normalized = normalize_ingest_text(text)
        return ExtractedText(
            text=normalized or None,
            extraction_mode="text_sniffed",
            notes=["Filinnehållet såg textbaserat ut och lästes som text."],
        )

    return ExtractedText(
        text=None,
        extraction_mode="unsupported_binary",
        notes=["Ingen text kunde extraheras från filtypen."],
    )
