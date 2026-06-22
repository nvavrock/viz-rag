"""Advanced RAG: query rewriting + reranking (llm_engineering Week 5 Day 5)."""

from __future__ import annotations

from langchain_core.documents import Document
from litellm import completion
from pydantic import BaseModel, Field

from rag.answer import get_vectorstore
from rag.config import (
    PREPROCESSED_DB,
    RETRIEVAL_K_ADVANCED,
    SYSTEM_PROMPT_ADVANCED,
    VECTOR_DB,
    get_embeddings,
    get_llm,
    litellm_model,
)

_llm = get_llm()


class RankOrder(BaseModel):
    order: list[int] = Field(
        description="Chunk ids from most to least relevant (1-based), include all ids"
    )


def rewrite_query(question: str, history: list[dict] | None = None) -> str:
    history = history or []
    history_text = "\n".join(
        f"{m.get('role', 'user')}: {m.get('content', '')}" for m in history
    )
    message = f"""
You are helping search a ggplot2 / data visualization knowledge base.

Conversation so far:
{history_text or "(none)"}

User question:
{question}

Respond with ONE short search query most likely to surface relevant chunks.
Focus on chart types, ggplot2 functions, data shapes, or viz principles.
Do not mention "ggplot2" unless the question is general.
Respond ONLY with the search query, nothing else.
"""
    response = completion(
        model=litellm_model(),
        messages=[{"role": "user", "content": message}],
    )
    return response.choices[0].message.content.strip()


def fetch_context_unranked(
    question: str,
    *,
    db_name: str | None = None,
    k: int = RETRIEVAL_K_ADVANCED,
) -> list[Document]:
    db = db_name or VECTOR_DB
    embeddings = get_embeddings()
    store = get_vectorstore(db)
    collection = store._collection
    query_embedding = embeddings.embed_query(question)
    results = collection.query(query_embeddings=[query_embedding], n_results=k)
    docs: list[Document] = []
    for text, meta in zip(results["documents"][0], results["metadatas"][0]):
        docs.append(Document(page_content=text, metadata=meta))
    return docs


def rerank(question: str, chunks: list[Document]) -> list[Document]:
    if not chunks:
        return []

    system_prompt = """
You are a document re-ranker for a ggplot2 / visualization knowledge base.
Rank the provided chunks by relevance to the question, most relevant first.
Reply only with ranked chunk ids. Include every chunk id you were given.
"""
    user_prompt = f"Question:\n{question}\n\nRank these chunks:\n\n"
    for index, chunk in enumerate(chunks):
        path = chunk.metadata.get("path", "")
        user_prompt += f"# CHUNK ID: {index + 1} ({path}):\n\n{chunk.page_content[:1500]}\n\n"
    user_prompt += "Reply only with the list of ranked chunk ids."

    response = completion(
        model=litellm_model(),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=RankOrder,
    )
    order = RankOrder.model_validate_json(response.choices[0].message.content).order
    return [chunks[i - 1] for i in order if 1 <= i <= len(chunks)]


def fetch_context(
    question: str,
    *,
    db_name: str | None = None,
    k: int = RETRIEVAL_K_ADVANCED,
) -> list[Document]:
    chunks = fetch_context_unranked(question, db_name=db_name, k=k)
    return rerank(question, chunks)


def answer_question(
    question: str,
    history: list[dict] | None = None,
    *,
    db_name: str | None = None,
    use_rewrite: bool = True,
) -> tuple[str, list[Document], str]:
    from langchain_core.messages import HumanMessage, SystemMessage, convert_to_messages

    history = history or []
    search_query = rewrite_query(question, history) if use_rewrite else question
    chunks = fetch_context(search_query, db_name=db_name)
    context_with_sources = "\n\n".join(
        f"Extract from {c.metadata.get('path', 'unknown')}:\n{c.page_content}"
        for c in chunks[:10]
    )
    system_prompt = SYSTEM_PROMPT_ADVANCED.format(context=context_with_sources)
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(convert_to_messages(history))
    messages.append(HumanMessage(content=question))
    response = _llm.invoke(messages)
    return response.content, chunks, search_query


def default_db_for_mode(preprocessed: bool) -> str:
    return PREPROCESSED_DB if preprocessed else VECTOR_DB
