"""Shared configuration for viz-rag RAG pipeline."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

ROOT = Path(__file__).resolve().parent.parent
JSONL_PATH = ROOT / "chunks" / "corpus.jsonl"
VECTOR_DB = str(ROOT / "vector_db")
PREPROCESSED_DB = str(ROOT / "preprocessed_db")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")

RETRIEVAL_K = 10
RETRIEVAL_K_ADVANCED = 20
LONG_CHUNK_THRESHOLD = 2000
SPLIT_CHUNK_SIZE = 1000
SPLIT_CHUNK_OVERLAP = 200
PREPROCESS_AVERAGE_CHUNK_SIZE = 500

SYSTEM_PROMPT = """
You are an expert R visualization assistant specializing in ggplot2 and TidyTuesday workflows.
You are helping a user make better charts with accurate, practical advice.
Use the retrieved context to answer. Prefer ggplot2 code examples when relevant.
If the context does not cover the question, say so — do not invent APIs or functions.
When helpful, mention the source path of the material you used.

Context:
{context}
"""

SYSTEM_PROMPT_ADVANCED = """
You are an expert R visualization assistant specializing in ggplot2 and TidyTuesday workflows.
Your answer will be evaluated for accuracy, relevance, and completeness.
Answer only what was asked; be precise and practical.
If you don't know, say so.
For context, here are extracts from the knowledge base that may be relevant:
{context}

With this context, answer the user's question. Be accurate, relevant, and complete.
"""


def litellm_model() -> str:
    if LLM_PROVIDER == "openai":
        return OPENAI_MODEL
    return f"ollama/{OLLAMA_MODEL}"


def get_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def get_llm():
    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(temperature=0, model=OPENAI_MODEL)
    from langchain_ollama import ChatOllama

    return ChatOllama(model=OLLAMA_MODEL, temperature=0)
