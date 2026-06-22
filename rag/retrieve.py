"""CLI to fetch RAG context (useful for scripts and Cursor workflows)."""

from __future__ import annotations

from rag._runtime import ensure_project_venv

ensure_project_venv("rag.retrieve")

import argparse

from rag import answer as basic
from rag import answer_advanced as advanced


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch viz-rag context for a question")
    parser.add_argument("question", help="Question to search")
    parser.add_argument("--advanced", action="store_true", help="Query rewrite + rerank")
    parser.add_argument("--preprocessed", action="store_true", help="Use preprocessed_db")
    parser.add_argument("-k", type=int, default=None, help="Number of chunks")
    args = parser.parse_args()

    if args.advanced:
        db = advanced.default_db_for_mode(args.preprocessed)
        if args.k:
            docs = advanced.fetch_context(args.question, db_name=db, k=args.k)
        else:
            docs = advanced.fetch_context(args.question, db_name=db)
    else:
        k = args.k or 10
        docs = basic.fetch_context(args.question, k=k)

    for i, doc in enumerate(docs, 1):
        path = doc.metadata.get("path", "")
        role = doc.metadata.get("role", "")
        print(f"--- Chunk {i} [{role}] {path} ---")
        print(doc.page_content[:2000])
        if len(doc.page_content) > 2000:
            print("...")
        print()


if __name__ == "__main__":
    main()
