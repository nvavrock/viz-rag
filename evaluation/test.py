"""Test questions for viz-rag evaluation."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

TEST_FILE = Path(__file__).parent / "tests.jsonl"


class TestQuestion(BaseModel):
    question: str = Field(description="Question for the RAG system")
    keywords: list[str] = Field(description="Keywords expected in retrieved context")
    reference_answer: str = Field(description="Reference answer for LLM judge")
    category: str = Field(description="Question category")


def load_tests(path: Path | None = None) -> list[TestQuestion]:
    test_path = path or TEST_FILE
    tests: list[TestQuestion] = []
    with test_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                tests.append(TestQuestion(**json.loads(line)))
    return tests
