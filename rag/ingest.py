"""Embed corpus chunks into Chroma using local HuggingFace embeddings."""

from __future__ import annotations

from rag._runtime import ensure_project_venv

ensure_project_venv("rag.ingest")

import argparse
from pathlib import Path

from langchain_chroma import Chroma

from rag.config import PREPROCESSED_DB, VECTOR_DB, get_embeddings
from rag.documents import prepare_documents
from rag.preprocess import preprocess_from_jsonl


def create_vectorstore(
    chunks,
    db_name: str,
    *,
    reset: bool = True,
) -> Chroma:
    embeddings = get_embeddings()
    db_path = Path(db_name)

    if reset and db_path.exists():
        Chroma(persist_directory=db_name, embedding_function=embeddings).delete_collection()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=db_name,
    )

    collection = vectorstore._collection
    count = collection.count()
    sample = collection.get(limit=1, include=["embeddings"])["embeddings"][0]
    print(f"Vector store at {db_name}: {count:,} vectors, {len(sample):,} dimensions")
    return vectorstore


def ingest(*, preprocess: bool = False, db_name: str | None = None) -> Chroma:
    if preprocess:
        chunks = preprocess_from_jsonl()
        target = db_name or PREPROCESSED_DB
    else:
        chunks = prepare_documents()
        target = db_name or VECTOR_DB

    print(f"Embedding {len(chunks):,} chunks...")
    return create_vectorstore(chunks, target)


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed viz-rag corpus into Chroma")
    parser.add_argument(
        "--preprocess",
        action="store_true",
        help="Use LLM to add headline/summary to each chunk (slow; requires Ollama/OpenAI)",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Chroma persist directory (default: vector_db or preprocessed_db)",
    )
    args = parser.parse_args()
    ingest(preprocess=args.preprocess, db_name=args.db)
    print("Ingestion complete")


if __name__ == "__main__":
    main()
