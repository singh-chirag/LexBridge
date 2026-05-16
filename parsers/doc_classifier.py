#!/usr/bin/env python3
"""
Document classification utilities for LexBridge.
Detects:
- document type
- language
using Gemini + fallback heuristics.
"""

import json
import re
from typing import Dict

from langchain_core.messages import HumanMessage


# ============================================================================
# 📝 CLASSIFICATION PROMPT
# ============================================================================

CLASSIFY_PROMPT = """
You are a legal document classifier.

Analyze the document excerpt below.

Tasks:
1. Detect document type:
   - eviction
   - contract
   - summons
   - debt
   - employment
   - immigration
   - other

2. Detect language using ISO 639-1 code:
   - en
   - es
   - fr
   - hi
   - ar
   - zh
   etc.

DOCUMENT:
{text}

Respond ONLY as valid JSON.

Example:
{{
  "doc_type": "eviction",
  "language": "en"
}}
"""


# ============================================================================
# 🧠 MAIN CLASSIFIER
# ============================================================================

def classify_document(
    text: str,
    llm,
    max_chars: int = 2000
) -> Dict[str, str]:
    """
    Classify legal document type and language.

    Args:
        text: document text
        llm: LangChain LLM instance
        max_chars: max chars sent to model

    Returns:
        {
            "doc_type": "...",
            "language": "..."
        }
    """

    excerpt = text[:max_chars]

    prompt = CLASSIFY_PROMPT.format(
        text=excerpt
    )

    try:

        response = llm.invoke([
            HumanMessage(content=prompt)
        ])

        content = response.content.strip()

        # Remove markdown JSON blocks
        if content.startswith("```"):

            content = re.sub(
                r"^```(?:json)?\n?",
                "",
                content
            )

            content = re.sub(
                r"\n?```$",
                "",
                content
            )

        parsed = json.loads(content)

        return {
            "doc_type": parsed.get(
                "doc_type",
                "other"
            ),
            "language": parsed.get(
                "language",
                "en"
            )
        }

    except Exception as e:

        print(f"⚠️ Classification failed: {e}")

        return fallback_classification(text)


# ============================================================================
# 🛟 FALLBACK CLASSIFIER
# ============================================================================

def fallback_classification(
    text: str
) -> Dict[str, str]:
    """
    Lightweight fallback classifier
    using regex + keyword heuristics.
    """

    text_lower = text.lower()


    # =========================================================================
    # 📄 DOCUMENT TYPE DETECTION
    # =========================================================================

    if any(
        keyword in text_lower
        for keyword in [
            "eviction",
            "notice to quit",
            "pay or quit",
            "tenant eviction"
        ]
    ):

        doc_type = "eviction"

    elif any(
        keyword in text_lower
        for keyword in [
            "lease agreement",
            "rental agreement",
            "contract",
            "terms and conditions"
        ]
    ):

        doc_type = "contract"

    elif any(
        keyword in text_lower
        for keyword in [
            "summons",
            "court order",
            "defendant",
            "plaintiff"
        ]
    ):

        doc_type = "summons"

    elif any(
        keyword in text_lower
        for keyword in [
            "debt collection",
            "creditor",
            "outstanding balance",
            "payment due"
        ]
    ):

        doc_type = "debt"

    elif any(
        keyword in text_lower
        for keyword in [
            "employment",
            "termination",
            "employee",
            "non-compete"
        ]
    ):

        doc_type = "employment"

    elif any(
        keyword in text_lower
        for keyword in [
            "uscis",
            "visa",
            "immigration",
            "green card"
        ]
    ):

        doc_type = "immigration"

    else:

        doc_type = "other"


    # =========================================================================
    # 🌐 LANGUAGE DETECTION
    # =========================================================================

    if re.search(r"[\u0600-\u06FF]", text):

        language = "ar"

    elif re.search(r"[\u4E00-\u9FFF]", text):

        language = "zh"

    elif re.search(r"[\u0900-\u097F]", text):

        language = "hi"

    elif any(
        char in text_lower
        for char in "áéíóúñü"
    ):

        language = "es"

    elif any(
        char in text_lower
        for char in "àâçéèêëîïôùûüÿ"
    ):

        language = "fr"

    else:

        language = "en"


    return {
        "doc_type": doc_type,
        "language": language
    }