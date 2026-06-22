"""Optional LLM chunk preprocessing (headline + summary + original text)."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from litellm import completion
from pydantic import BaseModel, Field
from tqdm import tqdm

from rag.config import PREPROCESS_AVERAGE_CHUNK_SIZE, litellm_model
from rag.documents import prepare_documents


class Chunk(BaseModel):
    headline: str = Field(
        description="Brief heading for this chunk, most likely to surface in a query"
    )
    summary: str = Field(
        description="A few sentences summarizing this chunk for common ggplot2/viz questions"
    )
    original_text: str = Field(
        description="The original chunk text exactly as provided, unchanged"
    )

    def as_document(self, metadata: dict) -> Document:
        content = f"{self.headline}\n\n{self.summary}\n\n{self.original_text}"
        return Document(page_content=content, metadata=dict(metadata))


class Chunks(BaseModel):
    chunks: list[Chunk]


def _prompt(doc: Document) -> str:
    meta = doc.metadata
    how_many = (len(doc.page_content) // PREPROCESS_AVERAGE_CHUNK_SIZE) + 1
    return f"""
You split documents into overlapping chunks for a ggplot2 / data visualization knowledge base.

Source: {meta.get("source", "")}
Path: {meta.get("path", "")}
Section: {meta.get("section", "")}
Role: {meta.get("role", "")}

A chatbot will use these chunks to answer questions about chart choice, ggplot2, and visualization best practices.
Split the document sensibly. The entire document must appear across chunks — leave nothing out.
This document should probably split into about {how_many} chunks, with ~25% overlap where helpful.

For each chunk provide: headline, summary, and original_text (exact original text for that chunk).

Document:

{doc.page_content}

Respond with the chunks.
"""


def preprocess_document(doc: Document) -> list[Document]:
    response = completion(
        model=litellm_model(),
        messages=[{"role": "user", "content": _prompt(doc)}],
        response_format=Chunks,
    )
    parsed = Chunks.model_validate_json(response.choices[0].message.content)
    return [chunk.as_document(doc.metadata) for chunk in parsed.chunks]


def preprocess_documents(documents: list[Document], parallel: bool = False) -> list[Document]:
    if parallel:
        from multiprocessing import Pool

        with Pool() as pool:
            nested = pool.map(preprocess_document, documents)
        return [doc for group in nested for doc in group]

    result: list[Document] = []
    for doc in tqdm(documents, desc="LLM preprocessing"):
        result.extend(preprocess_document(doc))
    return result


def preprocess_from_jsonl(jsonl_path: Path | None = None) -> list[Document]:
    base = prepare_documents(jsonl_path)
    # Preprocess at section level before secondary splitting for long sections
    from rag.documents import load_jsonl_chunks

    raw = load_jsonl_chunks(jsonl_path)
    return preprocess_documents(raw)
