#!/usr/bin/env python3
"""
LexBridge Agent - Production-Ready LangGraph Pipeline
AI legal document analysis with OCR, RAG grounding, and action planning.
"""
from dotenv import load_dotenv

load_dotenv()

import json
import os
import re
from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from parsers.doc_classifier import classify_document
from parsers.pdf_parser import extract_pdf_text
from rag.retriever import retrieve_rights


# ============================================================================
# ✅ ENVIRONMENT VALIDATION
# ============================================================================

if not os.getenv("GROQ_API_KEY"):
    raise EnvironmentError(
        "GROQ_API_KEY not found in environment variables."
    )


# ============================================================================
# 📦 STATE DEFINITION
# ============================================================================

class LexState(TypedDict):
    file_path: str
    raw_text: str
    doc_type: str
    language: str

    risks: List[Dict[str, Any]]
    plain_explanations: List[Dict[str, Any]]
    legal_rights: List[str]
    action_plan: List[Dict[str, Any]]

    response_letter: Optional[str]
    urgency: str


# ============================================================================
# 📝 PROMPTS
# ============================================================================

RISK_PROMPT = """
You are a legal document analyst.

DOCUMENT TYPE:
{doc_type}

DOCUMENT TEXT:
{text}

Extract ALL:
- risks
- deadlines
- obligations
- penalties
- waived rights

For each issue provide:
- risk_type
- severity (CRITICAL/HIGH/MEDIUM/LOW)
- quote
- plain_issue

Respond ONLY as JSON array.
"""

STRATEGY_PROMPT = """
You are a legal aid assistant.

DOCUMENT TYPE:
{doc_type}

RISKS:
{risks}

LEGAL RIGHTS:
{rag_context}

Generate a practical action plan.

Rules:
1. Only use retrieved rights
2. Never predict legal outcomes
3. Suggest legal aid consultation
4. Translate to: {language}

Respond ONLY as JSON:
{{
  "action_plan": []
}}
"""

DRAFT_PROMPT = """
Document type:
{doc_type}

Top risks:
{top_risks}

Legal rights:
{rights}

Draft a professional response letter template.

Requirements:
- formal tone
- placeholders where needed
- request written confirmation
- include legal rights clearly

Language:
{language}
"""


# ============================================================================
# 🤖 LLM INITIALIZATION
# ============================================================================

llm = ChatGroq(
    model=os.getenv("MODEL_NAME", "llama-3.3-70b-versatile"),
    temperature=float(os.getenv("TEMPERATURE", 0.1)),
    groq_api_key=os.getenv("GROQ_API_KEY")
)


# ============================================================================
# 🔧 HELPERS
# ============================================================================

def extract_json(response_text: str) -> Any:
    """
    Safely parse JSON from LLM response.
    Handles markdown code blocks.
    """

    text = response_text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        match = re.search(
            r"(\[.*\]|\{.*\})",
            text,
            re.DOTALL
        )

        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None

    return None


# ============================================================================
# 📄 NODE 1 — DOCUMENT PARSING
# ============================================================================

def document_parser_node(state: LexState) -> LexState:

    raw_text = extract_pdf_text(state["file_path"])

    classification = classify_document(
        raw_text[:2000],
        llm
    )

    return {
        **state,
        "raw_text": raw_text,
        "doc_type": classification.get("doc_type", "other"),
        "language": classification.get("language", "en")
    }


# ============================================================================
# ⚠️ NODE 2 — RISK EXTRACTION
# ============================================================================

def risk_extraction_node(state: LexState) -> LexState:

    prompt = RISK_PROMPT.format(
        doc_type=state["doc_type"],
        text=state["raw_text"][:8000]
    )

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    risks = extract_json(response.content) or []

    severities = [
        r.get("severity", "MEDIUM")
        for r in risks
    ]

    if "CRITICAL" in severities:
        urgency = "CRITICAL"

    elif "HIGH" in severities:
        urgency = "HIGH"

    elif severities.count("MEDIUM") >= 2:
        urgency = "MEDIUM"

    else:
        urgency = "LOW"

    return {
        **state,
        "risks": risks,
        "urgency": urgency
    }


# ============================================================================
# 🗣️ NODE 3 — PLAIN LANGUAGE EXPLANATION
# ============================================================================

def plain_language_node(state: LexState) -> LexState:

    if not state["risks"]:
        return {
            **state,
            "plain_explanations": []
        }

    explanations = []

    for risk in state["risks"]:

        prompt = f"""
Rewrite this legal clause in simple language.

Translate explanation to:
{state["language"]}

Original:
"{risk.get('quote', '')}"

Issue:
{risk.get('plain_issue', '')}

Respond ONLY as JSON:
{{
  "plain_language": "",
  "translation": ""
}}
"""

        try:

            response = llm.invoke([
                HumanMessage(content=prompt)
            ])

            parsed = extract_json(response.content) or {}

            explanations.append({
                "original_clause": risk.get("quote", ""),
                "plain_language": parsed.get(
                    "plain_language",
                    risk.get("plain_issue", "")
                ),
                "translation": parsed.get(
                    "translation",
                    risk.get("plain_issue", "")
                )
            })

        except Exception as e:

            print(f"Plain-language node error: {e}")

            explanations.append({
                "original_clause": risk.get("quote", ""),
                "plain_language": risk.get("plain_issue", ""),
                "translation": risk.get("plain_issue", "")
            })

    return {
        **state,
        "plain_explanations": explanations
    }


# ============================================================================
# ⚖️ NODE 4 — RIGHTS + ACTION PLAN
# ============================================================================

def strategy_rights_node(state: LexState) -> LexState:

    top_risks = state["risks"][:3]

    query_parts = [
        f"{state['doc_type']} rights"
    ] + [
        r.get("plain_issue", "")
        for r in top_risks
    ]

    query = " | ".join(
        filter(None, query_parts)
    )

    rag_chunks = retrieve_rights(
        query,
        top_k=4
    )

    rag_context = "\n\n---\n\n".join(rag_chunks)

    prompt = STRATEGY_PROMPT.format(
        doc_type=state["doc_type"],
        risks=json.dumps(state["risks"], indent=2),
        rag_context=rag_context,
        language=state["language"]
    )

    try:

        response = llm.invoke([
            HumanMessage(content=prompt)
        ])

        parsed = extract_json(response.content)

        action_plan = (
            parsed.get("action_plan", [])
            if isinstance(parsed, dict)
            else []
        )

    except Exception as e:

        print(f"Strategy node error: {e}")

        action_plan = [{
            "priority": "DO TODAY",
            "action": "Consult a legal aid professional",
            "reason": "AI outputs may contain errors",
            "deadline": "As soon as possible"
        }]

    return {
        **state,
        "legal_rights": rag_chunks,
        "action_plan": action_plan
    }


# ============================================================================
# 📝 NODE 5 — RESPONSE LETTER
# ============================================================================

def draft_response_node(state: LexState) -> LexState:

    needs_response = state["doc_type"] in [
        "eviction",
        "debt",
        "summons",
        "immigration"
    ]

    if not needs_response or not state["risks"]:

        return {
            **state,
            "response_letter": None
        }

    top_risks = [
        r.get("plain_issue", "")
        for r in state["risks"][:3]
    ]

    prompt = DRAFT_PROMPT.format(
        doc_type=state["doc_type"],
        top_risks=json.dumps(top_risks),
        rights="\n".join(
            f"- {r}"
            for r in state["legal_rights"][:3]
        ),
        language=state["language"]
    )

    try:

        response = llm.invoke([
            HumanMessage(content=prompt)
        ])

        letter = (
            "[TEMPLATE ONLY — review with legal professional]\n\n"
            + response.content.strip()
        )

    except Exception as e:

        print(f"Draft node error: {e}")

        letter = None

    return {
        **state,
        "response_letter": letter
    }


# ============================================================================
# 🕸️ GRAPH DEFINITION
# ============================================================================

def build_graph():

    graph = StateGraph(LexState)

    graph.add_node(
        "parse",
        document_parser_node
    )

    graph.add_node(
        "extract",
        risk_extraction_node
    )

    graph.add_node(
        "explain",
        plain_language_node
    )

    graph.add_node(
        "strategy",
        strategy_rights_node
    )

    graph.add_node(
        "draft",
        draft_response_node
    )

    graph.set_entry_point("parse")

    graph.add_edge("parse", "extract")
    graph.add_edge("extract", "explain")
    graph.add_edge("explain", "strategy")
    graph.add_edge("strategy", "draft")
    graph.add_edge("draft", END)

    return graph.compile()


# ============================================================================
# 🚀 COMPILED APP
# ============================================================================

app = build_graph()


# ============================================================================
# 🧪 LOCAL TEST
# ============================================================================

if __name__ == "__main__":

    print("🔍 LexBridge Local Test")

    test_state = {
        "file_path": "",
        "raw_text": "",
        "doc_type": "",
        "language": "",

        "risks": [],
        "plain_explanations": [],
        "legal_rights": [],
        "action_plan": [],

        "response_letter": None,
        "urgency": "MEDIUM"
    }

    try:

        result = app.invoke(test_state)

        print("\n✅ Pipeline completed")
        print(f"📄 Type: {result['doc_type']}")
        print(f"🌐 Language: {result['language']}")
        print(f"⚠️ Risks: {len(result['risks'])}")
        print(f"⚡ Urgency: {result['urgency']}")

    except Exception as e:

        print(f"\n❌ Test failed: {e}")