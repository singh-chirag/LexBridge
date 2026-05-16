#!/usr/bin/env python3
"""
PyMuPDF extraction utilities for LexBridge.

Supports:
- PDF text extraction
- page-aware formatting
- metadata extraction
"""

from typing import Dict, List

import fitz


# ============================================================================
# 📄 PDF TEXT EXTRACTION
# ============================================================================

def extract_pdf_text(
    file_path: str
) -> str:
    """
    Extract text from PDF using PyMuPDF.

    Features:
    - page-aware formatting
    - clean concatenation
    - safe fallback handling

    Args:
        file_path: path to PDF file

    Returns:
        extracted text
    """

    try:

        document = fitz.open(file_path)

        text_parts: List[str] = []

        for page_number in range(len(document)):

            page = document[page_number]

            page_text = page.get_text("text")

            if page_text.strip():

                formatted_text = (
                    f"[Page {page_number + 1}]\n"
                    f"{page_text.strip()}"
                )

                text_parts.append(formatted_text)

        document.close()

        return "\n\n".join(text_parts).strip()

    except Exception as e:

        print(f"⚠️ PyMuPDF extraction failed: {e}")

        return ""


# ============================================================================
# 📑 PDF METADATA EXTRACTION
# ============================================================================

def extract_pdf_metadata(
    file_path: str
) -> Dict:
    """
    Extract PDF metadata.

    Returns:
    - page count
    - author
    - title
    - creation date
    """

    try:

        document = fitz.open(file_path)

        metadata = {

            "page_count": len(document),

            "author": document.metadata.get(
                "author",
                ""
            ),

            "title": document.metadata.get(
                "title",
                ""
            ),

            "creation_date": document.metadata.get(
                "creationDate",
                ""
            )
        }

        document.close()

        return metadata

    except Exception as e:

        print(f"⚠️ Metadata extraction failed: {e}")

        return {
            "page_count": 0,
            "author": "",
            "title": "",
            "creation_date": ""
        }


# ============================================================================
# 🧪 LOCAL TEST
# ============================================================================

if __name__ == "__main__":

    sample_pdf = "sample.pdf"

    print("🔍 Testing PDF extraction...")

    text = extract_pdf_text(sample_pdf)

    metadata = extract_pdf_metadata(sample_pdf)

    print("\n✅ Extraction complete")

    print("\n📑 Metadata:")
    print(metadata)

    print("\n📄 Preview:\n")
    print(text[:1000])