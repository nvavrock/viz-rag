# viz-rag

Personal retrieval corpus and RAG assistant for **ggplot2 / TidyTuesday** visualization work. Separate from [tidytuesday](../tidytuesday).

Built using patterns from [llm_engineering](https://github.com/ed-donner/llm_engineering) Week 5 (RAG): chunk → embed → retrieve → answer, with evaluation and advanced reranking.

## Strategy

| Source | Method |
|--------|--------|
| [data_to_viz](https://github.com/holtzy/data_to_viz) | Git clone → chunk `story/*.Rmd`, caveats, dataset readme |
| [ggplot2](https://github.com/tidyverse/ggplot2) | Git clone → chunk vignettes |
| [VAD](https://www.cs.ubc.ca/~tmm/vadbook/) | Original summary notes in `corpus/notes/` (not book text) |
| FT / Visual Capitalist | Original style heuristics in `corpus/style/` (not scraped) |
| TidyTuesday lessons | `../tidytuesday/VIZ_LESSONS.md` + week `R/*.R` plot recipes |
| Corpus changelog | `corpus/lessons/CHANGELOG.md` — log of what was added and when |

See [ATTRIBUTION.md](ATTRIBUTION.md) for licenses. Lesson history: [corpus/lessons/CHANGELOG.md](corpus/lessons/CHANGELOG.md).

## Setup

```bash
# Python 3.11+
python -m venv .venv

# Windows — PowerShell often blocks `.ps1` scripts (ExecutionPolicy). Prefer:
.venv\Scripts\python.exe -m pip install -e .
# or:
scripts\run.cmd -m pip install -e .
copy .env.example .env

# Optional if ExecutionPolicy allows .ps1:
# .\scripts\run.ps1 -m pip install -e .

# macOS/Linux
# source .venv/bin/activate && pip install -e .
```

**Default:** local Ollama (`ollama run llama3.2`) + HuggingFace embeddings (free).  
Optional: set `LLM_PROVIDER=openai` and `OPENAI_API_KEY` in `.env`.

## Pipeline

### 1. Fetch upstream repos

```bash
bash scripts/fetch_sources.sh
```

### 2. Build chunk file (JSONL)

```bash
python ingest/build_corpus.py
```

Output: `chunks/corpus.jsonl` — one JSON object per line with `text`, `source`, `role`, `package`.

### 3. Embed into Chroma (local HuggingFace embeddings)

```bash
.venv\Scripts\python.exe -m rag.ingest
# or: scripts\run.cmd -m rag.ingest
```

Uses `all-MiniLM-L6-v2` locally (no API key). Long sections are split with overlap automatically.

**Optional — LLM chunk preprocessing** (headline + summary per chunk, slow):

```bash
python -m rag.ingest --preprocess
```

Stores in `preprocessed_db/` instead of `vector_db/`.

### 4. Chat (Gradio)

```bash
.venv\Scripts\python.exe -m rag.app
# or: scripts\run.cmd -m rag.app
```

**Optional — advanced RAG** (query rewrite + reranking):

```bash
python -m rag.app --advanced
python -m rag.app --advanced --preprocessed   # if you used --preprocess
```

### 5. Visualize embeddings (optional)

```bash
python -m rag.visualize
python -m rag.visualize --3d
python -m rag.visualize --preprocessed
```

### 6. Fetch context from the command line (optional)

```bash
python -m rag.retrieve "how do I use facet_wrap for small multiples?"
python -m rag.retrieve "geom_line time series" --advanced
```

### 7. Evaluate retrieval and answers (optional)

Requires Ollama or OpenAI for the LLM judge:

```bash
python -m evaluation.eval 0              # one test by index
python -m evaluation.eval --all --limit 5   # summary over first N tests
```

## Chunk schema

```json
{
  "id": "1",
  "source": "data_to_viz",
  "path": ".../story/TwoNum.Rmd",
  "section": "Introduction",
  "text": "...",
  "language": "r",
  "role": "chart_selection",
  "package": "ggplot2"
}
```

## Layout

```
viz-rag/
├── corpus/style/       # FT-inspired + chart-choice notes
├── corpus/notes/       # VAD-style framework summaries
├── corpus/lessons/     # changelog + dated lesson log
├── sources/            # cloned repos (gitignored)
├── chunks/             # generated JSONL (gitignored)
├── vector_db/          # Chroma index (gitignored)
├── preprocessed_db/    # optional LLM-preprocessed index (gitignored)
├── ingest/             # build_corpus.py / .R
├── rag/                # ingest, answer, app, visualize, preprocess
├── evaluation/         # tests.jsonl + eval metrics
└── scripts/            # fetch_sources.sh
```

## Configuration (.env)

| Variable | Default | Purpose |
|----------|---------|---------|
| `LLM_PROVIDER` | `ollama` | `ollama` or `openai` for chat / rerank / eval |
| `OLLAMA_MODEL` | `llama3.2` | Local chat model |
| `OPENAI_MODEL` | `gpt-4.1-nano` | Used when `LLM_PROVIDER=openai` |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local HuggingFace embeddings |

## Cursor

Use this repo as context when working on R viz projects. The Gradio app is for interactive Q&A; for Cursor, `@` mention files or wire an MCP tool against `fetch_context()` in `rag/answer.py`.
