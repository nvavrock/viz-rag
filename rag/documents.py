"""Load JSONL chunks as LangChain documents with optional long-chunk splitting."""

from __future__ import annotations

import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.config import (
    JSONL_PATH,
    LONG_CHUNK_THRESHOLD,
    SPLIT_CHUNK_OVERLAP,
    SPLIT_CHUNK_SIZE,
)


def load_jsonl_chunks(jsonl_path: Path | None = None) -> list[Document]:
    path = jsonl_path or JSONL_PATH
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {path}. Run: python ingest/build_corpus.py"
        )

    docs: list[Document] = []
    for line in path.open(encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        docs.append(
            Document(
                page_content=row["text"],
                metadata={
                    "chunk_id": row.get("id", ""),
                    "source": row.get("source", ""),
                    "path": row.get("path", ""),
                    "section": row.get("section", ""),
                    "role": row.get("role", ""),
                    "package": row.get("package", ""),
                    "language": row.get("language", ""),
                },
            )
        )
    return docs


def split_long_chunks(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=SPLIT_CHUNK_SIZE,
        chunk_overlap=SPLIT_CHUNK_OVERLAP,
    )
    result: list[Document] = []
    for doc in documents:
        if len(doc.page_content) <= LONG_CHUNK_THRESHOLD:
            result.append(doc)
            continue
        for sub in splitter.split_documents([doc]):
            sub.metadata = dict(doc.metadata)
            sub.metadata["split"] = "true"
            result.append(sub)
    return result


def prepare_documents(jsonl_path: Path | None = None) -> list[Document]:
    docs = load_jsonl_chunks(jsonl_path)
    return split_long_chunks(docs)
