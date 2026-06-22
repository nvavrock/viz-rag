"""Gradio chat UI for viz-rag."""

from __future__ import annotations

from rag._runtime import ensure_project_venv

ensure_project_venv("rag.app")

import argparse

import gradio as gr

from rag import answer as basic
from rag import answer_advanced as advanced
from rag.config import PREPROCESSED_DB, VECTOR_DB


def chat_basic(message: str, history: list[dict]) -> str:
    response, _ = basic.answer_question(message, history)
    return response


def chat_advanced(message: str, history: list[dict], preprocessed: bool) -> str:
    db = advanced.default_db_for_mode(preprocessed)
    response, _, query = advanced.answer_question(message, history, db_name=db)
    return f"*{query}*\n\n{response}"


def main() -> None:
    parser = argparse.ArgumentParser(description="viz-rag Gradio chat")
    parser.add_argument(
        "--advanced",
        action="store_true",
        help="Use query rewrite + reranking (Week 5 Day 5)",
    )
    parser.add_argument(
        "--preprocessed",
        action="store_true",
        help=f"Query {PREPROCESSED_DB} (requires rag.ingest --preprocess)",
    )
    args = parser.parse_args()

    if args.advanced:
        fn = lambda msg, hist: chat_advanced(msg, hist, args.preprocessed)
        title = "viz-rag (advanced RAG)"
    else:
        fn = chat_basic
        title = "viz-rag (basic RAG)"

    gr.ChatInterface(
        fn,
        type="messages",
        title=title,
        description="Ask about ggplot2, chart choice, TidyTuesday viz, or FT-style principles.",
    ).launch()


if __name__ == "__main__":
    main()
