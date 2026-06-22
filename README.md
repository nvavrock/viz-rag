# viz-rag

Personal retrieval corpus for **ggplot2 / TidyTuesday** visualization work. Separate from [tidytuesday](../tidytuesday).

## Strategy

| Source | Method |
|--------|--------|
| [data_to_viz](https://github.com/holtzy/data_to_viz) | Git clone → chunk `story/*.Rmd`, caveats, dataset readme |
| [ggplot2](https://github.com/tidyverse/ggplot2) | Git clone → chunk vignettes |
| [VAD](https://www.cs.ubc.ca/~tmm/vadbook/) | Original summary notes in `corpus/notes/` (not book text) |
| FT / Visual Capitalist | Original style heuristics in `corpus/style/` (not scraped) |
| Your projects | Optional ingest from `../tidytuesday/.../R/*.R` |

See [ATTRIBUTION.md](ATTRIBUTION.md) for licenses.

## Quick start

### 1. Fetch upstream repos

```bash
# Git Bash or WSL
bash scripts/fetch_sources.sh
```

### 2. Build chunk file (JSONL)

**Python** (no R required):

```bash
python ingest/build_corpus.py
```

**R** (RStudio):

```r
source("ingest/build_corpus.R")
build_corpus()
```

Output: `chunks/corpus.jsonl` — one JSON object per line, ready for embedding.

### 3. Embed (your choice of tool)

Point your embedder at `chunks/corpus.jsonl` fields: `text`, `source`, `role`, `package`.

Examples: OpenAI embeddings, `text-embeddings-inference`, Chroma, LanceDB, or Cursor MCP with a local index.

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
├── corpus/style/     # FT-inspired + chart-choice notes (yours)
├── corpus/notes/     # VAD-style framework summaries (yours)
├── sources/          # cloned repos (gitignored)
├── chunks/           # generated JSONL (gitignored)
├── ingest/           # build_corpus.R
└── scripts/          # fetch_sources.sh
```

## Cursor

Use this repo as context when working on any R viz project. Wire an MCP retrieval tool later that searches `chunks/` or a vector index built from it.
