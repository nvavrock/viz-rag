"""Evaluate viz-rag retrieval and answer quality (llm_engineering Week 5 Day 4)."""

from __future__ import annotations

from rag._runtime import ensure_project_venv

ensure_project_venv("evaluation.eval")

import argparse
import math
import sys

from litellm import completion
from pydantic import BaseModel, Field

from evaluation.test import TestQuestion, load_tests
from rag.answer import answer_question, fetch_context
from rag.config import litellm_model


class RetrievalEval(BaseModel):
    mrr: float
    ndcg: float
    keywords_found: int
    total_keywords: int
    keyword_coverage: float


class AnswerEval(BaseModel):
    feedback: str
    accuracy: float
    completeness: float
    relevance: float


def calculate_mrr(keyword: str, retrieved_docs: list) -> float:
    keyword_lower = keyword.lower()
    for rank, doc in enumerate(retrieved_docs, start=1):
        if keyword_lower in doc.page_content.lower():
            return 1.0 / rank
    return 0.0


def calculate_dcg(relevances: list[int], k: int) -> float:
    dcg = 0.0
    for i in range(min(k, len(relevances))):
        dcg += relevances[i] / math.log2(i + 2)
    return dcg


def calculate_ndcg(keyword: str, retrieved_docs: list, k: int = 10) -> float:
    keyword_lower = keyword.lower()
    relevances = [
        1 if keyword_lower in doc.page_content.lower() else 0
        for doc in retrieved_docs[:k]
    ]
    dcg = calculate_dcg(relevances, k)
    idcg = calculate_dcg(sorted(relevances, reverse=True), k)
    return dcg / idcg if idcg > 0 else 0.0


def evaluate_retrieval(test: TestQuestion, k: int = 10) -> RetrievalEval:
    retrieved_docs = fetch_context(test.question, k=k)
    mrr_scores = [calculate_mrr(kw, retrieved_docs) for kw in test.keywords]
    ndcg_scores = [calculate_ndcg(kw, retrieved_docs, k) for kw in test.keywords]
    keywords_found = sum(1 for score in mrr_scores if score > 0)
    total = len(test.keywords)
    return RetrievalEval(
        mrr=sum(mrr_scores) / len(mrr_scores) if mrr_scores else 0.0,
        ndcg=sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0,
        keywords_found=keywords_found,
        total_keywords=total,
        keyword_coverage=(keywords_found / total * 100) if total else 0.0,
    )


def evaluate_answer(test: TestQuestion) -> tuple[AnswerEval, str, list]:
    generated_answer, retrieved_docs = answer_question(test.question)
    judge_messages = [
        {
            "role": "system",
            "content": (
                "You evaluate RAG answers about ggplot2 and data visualization. "
                "Only give 5/5 for perfect answers."
            ),
        },
        {
            "role": "user",
            "content": f"""Question:
{test.question}

Generated Answer:
{generated_answer}

Reference Answer:
{test.reference_answer}

Score accuracy, completeness, and relevance from 1 to 5.
If the answer is wrong, accuracy must be 1.""",
        },
    ]
    judge_response = completion(
        model=litellm_model(),
        messages=judge_messages,
        response_format=AnswerEval,
    )
    answer_eval = AnswerEval.model_validate_json(judge_response.choices[0].message.content)
    return answer_eval, generated_answer, retrieved_docs


def run_cli(test_number: int) -> None:
    tests = load_tests()
    if test_number < 0 or test_number >= len(tests):
        print(f"Error: test index must be 0–{len(tests) - 1}")
        sys.exit(1)

    test = tests[test_number]
    print(f"\n{'=' * 80}\nTest #{test_number}\n{'=' * 80}")
    print(f"Question: {test.question}")
    print(f"Keywords: {test.keywords}")
    print(f"Category: {test.category}")

    retrieval = evaluate_retrieval(test)
    print(f"\nRetrieval — MRR: {retrieval.mrr:.4f}, nDCG: {retrieval.ndcg:.4f}")
    print(f"Keywords found: {retrieval.keywords_found}/{retrieval.total_keywords}")

    answer_eval, generated, _ = evaluate_answer(test)
    print(f"\nGenerated:\n{generated}")
    print(f"\nFeedback: {answer_eval.feedback}")
    print(
        f"Scores — accuracy: {answer_eval.accuracy}, "
        f"completeness: {answer_eval.completeness}, "
        f"relevance: {answer_eval.relevance}"
    )


def run_summary(limit: int | None = None) -> None:
    tests = load_tests()
    if limit:
        tests = tests[:limit]

    mrrs, ndcgs, acc, comp, rel = [], [], [], [], []
    for test in tests:
        r = evaluate_retrieval(test)
        mrrs.append(r.mrr)
        ndcgs.append(r.ndcg)
        a, _, _ = evaluate_answer(test)
        acc.append(a.accuracy)
        comp.append(a.completeness)
        rel.append(a.relevance)
        print(f"✓ {test.question[:60]}…")

    n = len(tests)
    print(f"\n{'=' * 80}")
    print(f"Summary over {n} tests")
    print(f"  Retrieval MRR:  {sum(mrrs) / n:.3f}")
    print(f"  Retrieval nDCG: {sum(ndcgs) / n:.3f}")
    print(f"  Answer accuracy:    {sum(acc) / n:.2f}/5")
    print(f"  Answer completeness:{sum(comp) / n:.2f}/5")
    print(f"  Answer relevance:   {sum(rel) / n:.2f}/5")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate viz-rag")
    parser.add_argument("test_index", nargs="?", type=int, help="Run one test by index")
    parser.add_argument("--all", action="store_true", help="Run all tests (slow)")
    parser.add_argument("--limit", type=int, default=None, help="Limit tests with --all")
    args = parser.parse_args()

    if args.all:
        run_summary(limit=args.limit)
    elif args.test_index is not None:
        run_cli(args.test_index)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
