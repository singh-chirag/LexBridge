#!/usr/bin/env python3
"""
PDF + OCR text extraction utilities for LexBridge.

Supports:
- Text-based PDFs (PyMuPDF)
- Scanned/image PDFs (Tesseract OCR)
- Smart fallback extraction
"""

import os
from typing import List

import fitz
import pytesseract
from PIL import Image


# ============================================================================
# ⚙️ OPTIONAL TESSERACT PATH (Windows)
# ============================================================================

# Uncomment and adjust if Tesseract is not detected automatically.

# pytesseract.pytesseract.tesseract_cmd = (
#     r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# )


# ============================================================================
# 📄 STANDARD PDF TEXT EXTRACTION
# ============================================================================

def extract_pdf_text(
    file_path: str
) -> str:
    """
    Extract text directly from PDF using PyMuPDF.

    Best for:
    - digitally generated PDFs
    - selectable text PDFs

    Args:
        file_path: path to PDF

    Returns:
        extracted text
    """

    try:

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        document = fitz.open(file_path)

        text_parts: List[str] = []

        for page in document:

            page_text = page.get_text()

            if page_text.strip():

                text_parts.append(
                    page_text.strip()
                )

        document.close()

        return "\n\n".join(text_parts)

    except Exception as e:

        print(f"⚠️ PDF extraction failed: {e}")

        return ""


# ============================================================================
# 🖼️ OCR EXTRACTION FOR SCANNED PDFs
# ============================================================================

def ocr_pdf(
    file_path: str,
    dpi: int = 200
) -> str:
    """
    Extract text using OCR.

    Converts PDF pages into images
    then runs Tesseract OCR.

    Best for:
    - scanned PDFs
    - photographed documents
    - image-only PDFs

    Args:
        file_path: path to PDF
        dpi: render quality

    Returns:
        OCR extracted text
    """

    try:

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        document = fitz.open(file_path)

        text_parts: List[str] = []

        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)

        for page_number in range(len(document)):

            page = document[page_number]

            pixmap = page.get_pixmap(
                matrix=matrix
            )

            image = Image.frombytes(
                "RGB",
                [pixmap.width, pixmap.height],
                pixmap.samples
            )

            page_text = pytesseract.image_to_string(
                image,
                lang="eng+spa+fra"
            )

            if page_text.strip():

                text_parts.append(
                    f"[Page {page_number + 1} - OCR]\n"
                    f"{page_text.strip()}"
                )

        document.close()

        return "\n\n".join(text_parts)

    except Exception as e:

        print(f"⚠️ OCR extraction failed: {e}")

        return ""


# ============================================================================
# 🧠 SMART EXTRACTION
# ============================================================================

def smart_extract(
    file_path: str,
    min_words: int = 50
) -> str:
    """
    Smart extraction pipeline.

    Workflow:
    1. Try direct PDF extraction
    2. If text too short → OCR fallback

    Args:
        file_path: path to PDF
        min_words: threshold for OCR fallback

    Returns:
        extracted text
    """

    # =========================================================================
    # STEP 1 — DIRECT EXTRACTION
    # =========================================================================

    text = extract_pdf_text(file_path)

    word_count = len(text.split())

    # =========================================================================
    # STEP 2 — OCR FALLBACK
    # =========================================================================

    if word_count < min_words:

        print(
            f"ℹ️ Low text yield ({word_count} words). "
            "Using OCR fallback..."
        )

        text = ocr_pdf(file_path)

    return text.strip()


# ============================================================================
# 🧪 LOCAL TESTING
# ============================================================================

if __name__ == "__main__":

    sample_file = "sample.pdf"

    print("🔍 Testing PDF extraction...")

    if not os.path.exists(sample_file):

        print("❌ sample.pdf not found")

    else:

        extracted = smart_extract(sample_file)

        print("\n✅ Extraction complete")
        print(f"📄 Characters extracted: {len(extracted)}")

        preview = extracted[:1000]

        print("\n📌 Preview:\n")
        print(preview)