"""Visualize Chroma embeddings with t-SNE (llm_engineering Week 5 Day 2)."""

from __future__ import annotations

from rag._runtime import ensure_project_venv

ensure_project_venv("rag.visualize")

import argparse

import numpy as np
import plotly.graph_objects as go
from langchain_chroma import Chroma
from sklearn.manifold import TSNE

from rag.config import PREPROCESSED_DB, VECTOR_DB, get_embeddings

ROLE_COLORS = {
    "chart_selection": "blue",
    "implementation": "green",
    "style": "orange",
    "theory": "red",
    "recipe": "purple",
    "data_shape": "cyan",
    "caveat": "gray",
}


def visualize(db_name: str = VECTOR_DB, dimensions: int = 2) -> None:
    embeddings = get_embeddings()
    store = Chroma(persist_directory=db_name, embedding_function=embeddings)
    collection = store._collection
    result = collection.get(include=["embeddings", "documents", "metadatas"])
    vectors = np.array(result["embeddings"])
    documents = result["documents"]
    metadatas = result["metadatas"]

    roles = [m.get("role", "unknown") for m in metadatas]
    colors = [ROLE_COLORS.get(r, "black") for r in roles]

    tsne = TSNE(n_components=dimensions, random_state=42)
    reduced = tsne.fit_transform(vectors)

    hover = [
        f"role: {r}<br>path: {m.get('path', '')[:60]}<br>{d[:120]}..."
        for r, m, d in zip(roles, metadatas, documents)
    ]

    if dimensions == 2:
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=reduced[:, 0],
                    y=reduced[:, 1],
                    mode="markers",
                    marker=dict(size=5, color=colors, opacity=0.75),
                    text=hover,
                    hoverinfo="text",
                )
            ]
        )
        fig.update_layout(
            title=f"viz-rag vector store ({db_name}) — 2D t-SNE",
            width=900,
            height=650,
        )
    else:
        fig = go.Figure(
            data=[
                go.Scatter3d(
                    x=reduced[:, 0],
                    y=reduced[:, 1],
                    z=reduced[:, 2],
                    mode="markers",
                    marker=dict(size=4, color=colors, opacity=0.75),
                    text=hover,
                    hoverinfo="text",
                )
            ]
        )
        fig.update_layout(
            title=f"viz-rag vector store ({db_name}) — 3D t-SNE",
            width=950,
            height=750,
        )

    fig.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualize Chroma embeddings")
    parser.add_argument("--db", default=VECTOR_DB, help="Chroma directory")
    parser.add_argument(
        "--preprocessed",
        action="store_true",
        help=f"Use {PREPROCESSED_DB} instead of default",
    )
    parser.add_argument("--3d", dest="three_d", action="store_true", help="3D plot")
    args = parser.parse_args()
    db = PREPROCESSED_DB if args.preprocessed else args.db
    visualize(db_name=db, dimensions=3 if args.three_d else 2)


if __name__ == "__main__":
    main()
