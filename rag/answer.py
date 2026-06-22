"""Basic RAG: retriever + LLM (llm_engineering Week 5 Day 3)."""

from __future__ import annotations

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage, convert_to_messages

from rag.config import (
    RETRIEVAL_K,
    SYSTEM_PROMPT,
    VECTOR_DB,
    get_embeddings,
    get_llm,
)

_embeddings = get_embeddings()
_vectorstore: Chroma | None = None
_llm = get_llm()


def get_vectorstore(db_name: str | None = None) -> Chroma:
    global _vectorstore
    target = db_name or VECTOR_DB
    if db_name is None and _vectorstore is not None:
        return _vectorstore
    store = Chroma(persist_directory=target, embedding_function=_embeddings)
    if db_name is None:
        _vectorstore = store
    return store


def get_retriever(db_name: str | None = None, k: int = RETRIEVAL_K, role: str | None = None):
    store = get_vectorstore(db_name)
    kwargs: dict = {"k": k}
    if role:
        kwargs["filter"] = {"role": role}
    return store.as_retriever(search_kwargs=kwargs)


def fetch_context(question: str, *, db_name: str | None = None, k: int = RETRIEVAL_K) -> list[Document]:
    retriever = get_retriever(db_name=db_name, k=k)
    return retriever.invoke(question)


def combined_question(question: str, history: list[dict] | None = None) -> str:
    history = history or []
    prior = "\n".join(m["content"] for m in history if m.get("role") == "user")
    if prior:
        return prior + "\n" + question
    return question


def format_context(docs: list[Document]) -> str:
    parts = []
    for doc in docs:
        path = doc.metadata.get("path", "")
        section = doc.metadata.get("section", "")
        header = f"[{path} — {section}]" if section else f"[{path}]"
        parts.append(f"{header}\n{doc.page_content}")
    return "\n\n".join(parts)


def answer_question(
    question: str,
    history: list[dict] | None = None,
    *,
    db_name: str | None = None,
) -> tuple[str, list[Document]]:
    history = history or []
    combined = combined_question(question, history)
    docs = fetch_context(combined, db_name=db_name)
    context = format_context(docs)
    system_prompt = SYSTEM_PROMPT.format(context=context)
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(convert_to_messages(history))
    messages.append(HumanMessage(content=question))
    response = _llm.invoke(messages)
    return response.content, docs
