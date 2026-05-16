#!/usr/bin/env python3
"""
LexBridge RAG Retriever

FAISS-based retrieval system for legal knowledge base.

Features:
- semantic similarity search
- lazy loading
- reusable singleton retriever
- metadata-aware retrieval
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

try:
    import faiss

except ImportError as exc:

    raise ImportError(
        "faiss is required.\n"
        "Install using:\n"
        "pip install faiss-cpu"
    ) from exc


# ============================================================================
# ⚖️ LEGAL RETRIEVER
# ============================================================================

class LegalRetriever:
    """
    FAISS-based semantic retriever
    for legal document chunks.
    """

    def __init__(
        self,
        index_path: str = "rag/legal_kb.faiss",
        meta_path: str = "rag/legal_kb_meta.json",
        model_name: str = "all-MiniLM-L6-v2"
    ):

        self.index_path = Path(index_path)

        self.meta_path = Path(meta_path)

        self.model_name = model_name

        # =====================================================================
        # LOAD FAISS INDEX
        # =====================================================================

        if not self.index_path.exists():

            raise FileNotFoundError(
                f"FAISS index not found: {index_path}"
            )

        self.index = faiss.read_index(
            str(self.index_path)
        )

        # =====================================================================
        # LOAD METADATA
        # =====================================================================

        if not self.meta_path.exists():

            raise FileNotFoundError(
                f"Metadata file not found: {meta_path}"
            )

        with open(
            self.meta_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.metadata = json.load(file)

        # =====================================================================
        # LOAD EMBEDDING MODEL
        # =====================================================================

        print(f"📥 Loading retriever model: {model_name}")

        self.model = SentenceTransformer(model_name)

        self.chunks = self.metadata.get(
            "chunks",
            []
        )

        self.chunk_metadata = self.metadata.get(
            "metadata",
            []
        )

    # =========================================================================
    # 🔎 MAIN RETRIEVAL
    # =========================================================================

    def retrieve(
        self,
        query: str,
        top_k: int = 4
    ) -> List[Dict]:
        """
        Retrieve semantically similar chunks.

        Args:
            query: search query
            top_k: number of results

        Returns:
            list of retrieval results
        """

        if not query.strip():

            return []

        # =====================================================================
        # ENCODE QUERY
        # =====================================================================

        query_embedding = self.model.encode(
            [query],
            show_progress_bar=False
        )

        query_vector = np.array(
            query_embedding,
            dtype="float32"
        )

        # =====================================================================
        # SEARCH INDEX
        # =====================================================================

        distances, indices = self.index.search(
            query_vector,
            top_k
        )

        results: List[Dict] = []

        # =====================================================================
        # BUILD RESULTS
        # =====================================================================

        for rank, chunk_index in enumerate(indices[0]):

            if (
                chunk_index < 0
                or chunk_index >= len(self.chunks)
            ):
                continue

            results.append({

                "text": self.chunks[chunk_index],

                "metadata": (
                    self.chunk_metadata[chunk_index]
                    if chunk_index < len(self.chunk_metadata)
                    else {}
                ),

                "score": float(
                    distances[0][rank]
                )
            })

        return results

    # =========================================================================
    # 📄 TEXT-ONLY RETRIEVAL
    # =========================================================================

    def retrieve_text_only(
        self,
        query: str,
        top_k: int = 4
    ) -> List[str]:
        """
        Convenience method:
        returns only retrieved text chunks.
        """

        results = self.retrieve(
            query=query,
            top_k=top_k
        )

        return [
            result["text"]
            for result in results
        ]


# ============================================================================
# 🌍 GLOBAL SINGLETON
# ============================================================================

_retriever_instance: Optional[LegalRetriever] = None


# ============================================================================
# ⚡ QUICK RETRIEVAL FUNCTION
# ============================================================================

def retrieve_rights(
    query: str,
    top_k: int = 4
) -> List[str]:
    """
    Lazy-loaded convenience function.

    Args:
        query: legal query
        top_k: retrieval count

    Returns:
        list of legal context chunks
    """

    global _retriever_instance

    if _retriever_instance is None:

        _retriever_instance = LegalRetriever()

    return _retriever_instance.retrieve_text_only(
        query=query,
        top_k=top_k
    )


# ============================================================================
# 🧪 LOCAL TESTING
# ============================================================================

if __name__ == "__main__":

    print("🔍 Testing legal retriever...")

    try:

        retriever = LegalRetriever()

        query = "tenant eviction notice rights"

        results = retriever.retrieve(
            query=query,
            top_k=3
        )

        print(f"\n✅ Retrieved {len(results)} results")

        for index, result in enumerate(results, start=1):

            print("\n" + "=" * 60)

            print(f"📄 Result {index}")

            print(f"📊 Score: {result['score']:.4f}")

            print(
                f"📑 Source: "
                f"{result['metadata'].get('source', 'unknown')}"
            )

            preview = result["text"][:400]

            print(f"\n{preview}...")

    except Exception as e:

        print(f"\n❌ Retriever test failed: {e}")