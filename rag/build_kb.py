#!/usr/bin/env python3
"""
LexBridge Knowledge Base Builder

Builds a FAISS vector database from legal source documents
for Retrieval-Augmented Generation (RAG).

Features:
- document chunking
- embedding generation
- FAISS indexing
- metadata persistence
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

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
# ✂️ TEXT CHUNKING
# ============================================================================

def chunk_text(
    text: str,
    chunk_size: int = 300,
    overlap: int = 50
) -> List[Tuple[str, int]]:
    """
    Split text into overlapping chunks.

    Args:
        text: source text
        chunk_size: words per chunk
        overlap: overlap between chunks

    Returns:
        list of (chunk, start_position)
    """

    words = text.split()

    chunks: List[Tuple[str, int]] = []

    step = chunk_size - overlap

    for index in range(0, len(words), step):

        chunk_words = words[index:index + chunk_size]

        if not chunk_words:
            continue

        chunk = " ".join(chunk_words)

        chunks.append((chunk, index))

    return chunks


# ============================================================================
# 🏗️ KNOWLEDGE BASE BUILDER
# ============================================================================

def build_knowledge_base(
    sources_dir: str = "rag/sources",
    output_dir: str = "rag",
    model_name: str = "all-MiniLM-L6-v2"
) -> Dict:
    """
    Build FAISS vector knowledge base.

    Args:
        sources_dir: legal text files
        output_dir: save location
        model_name: embedding model

    Returns:
        build statistics
    """

    print(f"\n🔨 Building knowledge base from: {sources_dir}")

    # =========================================================================
    # LOAD EMBEDDING MODEL
    # =========================================================================

    print(f"📥 Loading embedding model: {model_name}")

    model = SentenceTransformer(model_name)

    all_chunks: List[str] = []

    metadata: List[Dict] = []

    sources_path = Path(sources_dir)

    if not sources_path.exists():

        raise FileNotFoundError(
            f"Sources directory not found: {sources_dir}"
        )

    text_files = list(
        sources_path.glob("*.txt")
    )

    if not text_files:

        raise ValueError(
            f"No .txt files found in {sources_dir}"
        )

    # =========================================================================
    # PROCESS DOCUMENTS
    # =========================================================================

    for file_path in text_files:

        print(f"📄 Processing: {file_path.name}")

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                text = file.read()

            chunks = chunk_text(text)

            for chunk_index, (chunk, position) in enumerate(chunks):

                all_chunks.append(chunk)

                metadata.append({
                    "source": file_path.name,
                    "chunk_id": chunk_index,
                    "position": position,
                    "source_url": ""
                })

        except Exception as e:

            print(f"⚠️ Failed processing {file_path.name}: {e}")

    print(f"\n📊 Total chunks created: {len(all_chunks)}")

    if not all_chunks:

        raise ValueError(
            "No chunks generated from source files."
        )

    # =========================================================================
    # GENERATE EMBEDDINGS
    # =========================================================================

    print("\n🧠 Generating embeddings...")

    embeddings = model.encode(
        all_chunks,
        show_progress_bar=True,
        batch_size=32
    )

    embeddings = np.array(
        embeddings,
        dtype="float32"
    )

    # =========================================================================
    # BUILD FAISS INDEX
    # =========================================================================

    print("\n🗃️ Building FAISS index...")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    # =========================================================================
    # SAVE INDEX + METADATA
    # =========================================================================

    output_path = Path(output_dir)

    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    index_path = output_path / "legal_kb.faiss"

    metadata_path = output_path / "legal_kb_meta.json"

    faiss.write_index(
        index,
        str(index_path)
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "chunks": all_chunks,
                "metadata": metadata,
                "model": model_name,
                "chunk_count": len(all_chunks)
            },
            file,
            indent=2,
            ensure_ascii=False
        )

    # =========================================================================
    # SUMMARY
    # =========================================================================

    print("\n✅ Knowledge base built successfully!")

    print(f"📦 Index saved: {index_path}")

    print(f"📑 Metadata saved: {metadata_path}")

    return {
        "chunks_created": len(all_chunks),
        "sources_processed": len(text_files),
        "index_path": str(index_path),
        "metadata_path": str(metadata_path),
        "embedding_model": model_name
    }


# ============================================================================
# 🧪 CLI ENTRYPOINT
# ============================================================================

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Build LexBridge legal knowledge base"
    )

    parser.add_argument(
        "--sources",
        default="rag/sources",
        help="Directory containing legal .txt files"
    )

    parser.add_argument(
        "--output",
        default="rag",
        help="Directory to save FAISS index"
    )

    parser.add_argument(
        "--model",
        default="all-MiniLM-L6-v2",
        help="SentenceTransformer model"
    )

    args = parser.parse_args()

    stats = build_knowledge_base(
        sources_dir=args.sources,
        output_dir=args.output,
        model_name=args.model
    )

    print("\n📈 Build Summary:\n")

    print(
        json.dumps(
            stats,
            indent=2
        )
    )