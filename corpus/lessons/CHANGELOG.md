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
