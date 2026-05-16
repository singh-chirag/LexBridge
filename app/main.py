#!/usr/bin/env python3
"""
LexBridge FastAPI Backend
Production-ready API server for legal document analysis.
"""

import os
import tempfile
from typing import Dict, List, Optional

from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    HTTPException,
    UploadFile
)

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.graph import app as agent_graph


# ============================================================================
# 🚀 FASTAPI APP
# ============================================================================

app = FastAPI(
    title="LexBridge API",
    description="AI legal aid agent for document analysis",
    version="1.0.0"
)


# ============================================================================
# 🌐 CORS
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# 📦 REQUEST / RESPONSE MODELS
# ============================================================================

class AnalysisRequest(BaseModel):
    file_path: str
    language: Optional[str] = None


class AnalysisResponse(BaseModel):
    doc_type: str
    language: str

    risks: List[Dict]
    plain_explanations: List[Dict]
    legal_rights: List[str]
    action_plan: List[Dict]

    response_letter: Optional[str]
    urgency: str


# ============================================================================
# 🧹 TEMP FILE CLEANUP
# ============================================================================

def cleanup_temp_file(path: str):

    try:

        if os.path.exists(path):
            os.unlink(path)

    except Exception as e:

        print(f"Cleanup error: {e}")


# ============================================================================
# 🧠 BUILD INITIAL STATE
# ============================================================================

def create_initial_state(
    file_path: str,
    language: str = ""
):

    return {
        "file_path": file_path,
        "raw_text": "",
        "doc_type": "",
        "language": language,

        "risks": [],
        "plain_explanations": [],
        "legal_rights": [],
        "action_plan": [],

        "response_letter": None,
        "urgency": "MEDIUM"
    }


# ============================================================================
# 📄 ANALYZE EXISTING FILE
# ============================================================================

@app.post(
    "/analyze",
    response_model=AnalysisResponse
)

async def analyze_document(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):

    if not os.path.exists(request.file_path):

        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    try:

        initial_state = create_initial_state(
            file_path=request.file_path,
            language=request.language or ""
        )

        result = agent_graph.invoke(initial_state)

        background_tasks.add_task(
            cleanup_temp_file,
            request.file_path
        )

        return AnalysisResponse(**result)

    except Exception as e:

        background_tasks.add_task(
            cleanup_temp_file,
            request.file_path
        )

        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


# ============================================================================
# 📤 ANALYZE UPLOADED FILE
# ============================================================================

@app.post(
    "/analyze/upload",
    response_model=AnalysisResponse
)

async def analyze_uploaded_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):

    allowed_types = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/jpg",
        "text/plain"
    ]

    if file.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )

    suffix = os.path.splitext(file.filename)[1]

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            content = await file.read()

            temp_file.write(content)

            temp_path = temp_file.name

        initial_state = create_initial_state(
            file_path=temp_path
        )

        result = agent_graph.invoke(initial_state)

        background_tasks.add_task(
            cleanup_temp_file,
            temp_path
        )

        return AnalysisResponse(**result)

    except Exception as e:

        if "temp_path" in locals():
            cleanup_temp_file(temp_path)

        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


# ============================================================================
# ❤️ HEALTH CHECK
# ============================================================================

@app.get("/health")

async def health_check():

    return {
        "status": "ok",
        "service": "lexbridge-api"
    }


# ============================================================================
# 🏠 ROOT ENDPOINT
# ============================================================================

@app.get("/")

async def root():

    return {
        "message": "LexBridge API Running",
        "docs": "/docs",
        "health": "/health"
    }


# ============================================================================
# ▶️ LOCAL DEVELOPMENT
# ============================================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )