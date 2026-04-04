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


class TesseractOCRExtractor:
    """Real OCR extractor using Tesseract with Swedish + English language support."""

    name = "tesseract"

    def extract_text(self, raw: bytes, *, file_name: str | None = None, mime_type: str | None = None) -> ExtractedText:
        try:
            from PIL import Image, ImageOps
            import pytesseract
        except ImportError:
            return ExtractedText(
                text=None,
                extraction_mode="ocr_missing_dependency",
                notes=["OCR kräver pytesseract och Pillow. Installera med: pip install pytesseract Pillow"],
            )

        try:
            image = Image.open(io.BytesIO(raw))
        except Exception as exc:
            return ExtractedText(
                text=None,
                extraction_mode="ocr_image_unreadable",
                notes=[f"Bilden kunde inte öppnas: {exc}"],
            )

        try:
            prepared = ImageOps.grayscale(image)
            if prepared.width < 2200:
                scale = max(2, int(round(2200 / max(prepared.width, 1))))
                prepared = prepared.resize((prepared.width * scale, prepared.height * scale))
            ocr_text = pytesseract.image_to_string(prepared, lang="swe+eng", config="--psm 6")
        except pytesseract.TesseractNotFoundError:
            return ExtractedText(
                text=None,
                extraction_mode="ocr_tesseract_missing",
                notes=["Tesseract är inte installerat på servern. Installera med: apt install tesseract-ocr tesseract-ocr-swe"],
            )
        except Exception as exc:
            return ExtractedText(
                text=None,
                extraction_mode="ocr_failed",
                notes=[f"OCR misslyckades: {exc}"],
            )

        normalized = normalize_ingest_text(ocr_text) if ocr_text else None
        if not normalized:
            return ExtractedText(
                text=None,
                extraction_mode="ocr_no_text",
                notes=["OCR hittade ingen läsbar text i bilden."],
            )

        confidence_note = "Text extraherades via Tesseract OCR (swe+eng). OCR-text kan innehålla felläsningar."
        return ExtractedText(
            text=normalized,
            extraction_mode="ocr_tesseract",
            notes=[confidence_note],
        )


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


_default_ocr_extractor = TesseractOCRExtractor()


def normalize_ingest_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "")
    text = re.sub(r"\f", "\n", text)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    collapsed = "\n".join(lines)
    collapsed = re.sub(r"\n{3,}", "\n\n", collapsed)
    return collapsed.strip()


def detect_input_hints(text: str) -> list[str]:
    """Return lightweight structural hints about the input text for the AI prompt."""
    hints: list[str] = []
    lower = text.lower()
    if any(kw in lower for kw in ["faktura", "invoice", "förfallodatum", "betalningsvillkor", "ocr-nummer", "bankgiro"]):
        hints.append("invoice_keywords")
    if any(kw in lower for kw in ["abonnemang", "avtal", "bindningstid", "uppsägningstid", "avtalsperiod", "prenumeration"]):
        hints.append("subscription_keywords")
    if any(kw in lower for kw in ["bokföringsdatum", "transaktionsdatum", "saldo", "kontonummer", "transaktionstext"]):
        hints.append("bank_statement_keywords")
    if re.search(r"\d{1,3}[\s\u00a0]?\d{3}[,\.]\d{2}", text):
        hints.append("swedish_amounts")
    if re.search(r"\d{4}-\d{2}-\d{2}", text):
        hints.append("iso_dates")
    if re.search(r"(?:moms|vat|mva)\s", lower):
        hints.append("vat_present")
    if any(kw in lower for kw in ["kr/mån", "kr/månad", "sek/mån", "per månad", "/mån"]):
        hints.append("monthly_cost_pattern")
    return hints


def _looks_textual(raw: bytes) -> bool:
    if not raw:
        return False
    if b"\x00" in raw:
        return False
    sample = raw[:4096]
    printable = sum(1 for byte in sample if 9 <= byte <= 13 or 32 <= byte <= 126)
    return printable / max(len(sample), 1) >= 0.85


def _extract_pdf_text(raw: bytes, *, ocr_extractor: OCRExtractor | None = None) -> ExtractedText:
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

    if extracted_pages:
        normalized = normalize_ingest_text("\n\n".join(extracted_pages))
        if normalized:
            return ExtractedText(
                text=normalized,
                extraction_mode="pdf_text",
                notes=["Text extraherades från PDF utan OCR."],
            )

    extractor = ocr_extractor or _default_ocr_extractor
    return _extract_pdf_ocr(raw, reader, extractor)


def _extract_pdf_ocr(raw: bytes, reader: PdfReader, extractor: OCRExtractor) -> ExtractedText:
    """Try OCR on a scanned PDF by rendering pages to images."""
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        return ExtractedText(
            text=None,
            extraction_mode="pdf_ocr_missing_dependency",
            notes=["PDF:en verkar vara skannad men OCR-beroenden saknas (pytesseract, Pillow)."],
        )

    ocr_pages: list[str] = []
    notes: list[str] = []

    for page_idx, page in enumerate(reader.pages[:10]):
        images_on_page = []
        try:
            if hasattr(page, "images") and page.images:
                for img in page.images:
                    try:
                        image = Image.open(io.BytesIO(img.data))
                        images_on_page.append(image)
                    except Exception:
                        continue
        except Exception:
            pass

        for image in images_on_page:
            try:
                page_text = pytesseract.image_to_string(image, lang="swe+eng", config="--psm 6")
                normalized = normalize_ingest_text(page_text) if page_text else ""
                if normalized:
                    ocr_pages.append(normalized)
            except Exception as exc:
                notes.append(f"OCR misslyckades för bild på sida {page_idx + 1}: {exc}")

    if not ocr_pages:
        return ExtractedText(
            text=None,
            extraction_mode="pdf_no_text",
            notes=["PDF:en innehöll ingen extraherbar text, varken via textlager eller OCR."] + notes,
        )

    combined = normalize_ingest_text("\n\n".join(ocr_pages))
    return ExtractedText(
        text=combined or None,
        extraction_mode="pdf_ocr",
        notes=["Text extraherades från skannad PDF via OCR (Tesseract swe+eng). Resultat kan innehålla felläsningar."] + notes,
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
        extractor = ocr_extractor or _default_ocr_extractor
        return extractor.extract_text(raw, file_name=file_name, mime_type=mime_type)

    if suffix in PDF_EXTENSIONS or mime == "application/pdf":
        return _extract_pdf_text(raw, ocr_extractor=ocr_extractor)

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
