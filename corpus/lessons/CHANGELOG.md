# viz-rag corpus changelog

Log of lessons and corpus updates. Rebuild after changes:

```bash
python ingest/build_corpus.py
.venv\Scripts\python.exe -m rag.ingest
```

| Date | Change |
|------|--------|
| 2026-06-21 | Initial corpus: data_to_viz, ggplot2 vignettes, FT style notes, VAD summary, tidytuesday R recipes |
| 2026-06-22 | **ggplot faceting gotchas** in `corpus/style/chart-choice-heuristics.md` (shared categorical axis, `scales = "free"`, per-panel `fct_reorder`) |
| 2026-06-22 | Eval test: overlapping `facet_grid` name labels |
| 2026-06-22 | Ingest `corpus/lessons/` and `../tidytuesday/VIZ_LESSONS.md` as `role: lesson` |
| 2026-06-22 | tidytuesday UK baby names polish ingested (horizontal bars, captions, slope chart, Okabe–Ito palettes) |
| 2026-06-22 | Ingest all tidytuesday week folders (`../tidytuesday/*/R/*.R`) instead of one hardcoded week |
| 2026-06-22 | **Gapminder**: `corpus/style/gapminder-bubble-charts.md` + `sources/gapminder` docs (README, vignette, man/*.Rd); raw data skipped |
| 2026-06-22 | **Cursor MCP** (`viz_rag_mcp`): `search_viz_corpus` + agent rule — retrieval through Cursor chat, not Gradio |
| 2026-06-23 | tidytuesday `VIZ_LESSONS.md`: gganimate bar race, gifski pixels, ggplotly line fix, discrete heatmap legend, facet spacing |
| 2026-06-24 | **corpus/lessons/**: plotly PNG export (webshot2), ggplotly boxplot+jitter legend, LinkedIn carousel heuristics, baby-name diversity metrics |
| 2026-06-24 | tidytuesday `VIZ_LESSONS.md`: same topics + `save_interactive_png` / `as_interactive` legend fixes |
