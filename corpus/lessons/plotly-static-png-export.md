# Plotly static PNG export (ggplot2 → LinkedIn)

**Source:** tidytuesday `2026_06_16_uk_baby_names` — uniqueness-by-sex chart with region-colored jitter and hover tooltips.

## Problem

Interactive Quarto reports use `ggplotly()` for hover. LinkedIn carousels need **static PNGs**. A plain `ggsave()` on the ggplot loses plotly-specific behavior (custom hover strings, legend cleanup). You want one ggplot object that renders both ways.

## Pattern: `save_interactive_png()`

1. Build ggplot with `aes(text = hover)` on layers that need tooltips.
2. Wrap with `as_interactive()` (plotly conversion + trace fixes).
3. Save self-contained HTML via `htmlwidgets::saveWidget()`.
4. Screenshot with `webshot2::webshot()` to PNG.

```r
save_interactive_png <- function(plot, path, width = 960, height = 720, zoom = 2) {
  if (!requireNamespace("webshot2", quietly = TRUE) ||
      !requireNamespace("htmlwidgets", quietly = TRUE)) {
    ggplot2::ggsave(path, plot, width = width / 150, height = height / 150, dpi = 150)
    return(invisible(path))
  }
  px <- as_interactive(plot) |> plotly::config(displayModeBar = FALSE, displaylogo = FALSE)
  tmp <- tempfile("plotly_widget_")
  dir.create(tmp)
  on.exit(unlink(tmp, recursive = TRUE), add = TRUE)
  html_path <- file.path(tmp, "chart.html")
  htmlwidgets::saveWidget(px, html_path, selfcontained = FALSE)
  webshot2::webshot(html_path, path, vwidth = width, vheight = height, zoom = zoom)
  invisible(path)
}
```

## Dependencies

- **webshot2** — add to project `install_packages.R`.
- webshot2 needs a headless browser (bundled Chromium on most setups).
- **Fallback:** if webshot2/htmlwidgets missing, `ggsave()` still writes a usable static chart.

## When to use

| Export | Tool |
|--------|------|
| LinkedIn / slides / README | `save_interactive_png()` for charts with jitter hover + plotly legend fixes |
| Simple geoms (bars, lines, facets) | `ggsave()` is enough |
| Full interactivity | `analysis.html` via Quarto + `as_interactive()` in document only |

## Gotchas

- `selfcontained = FALSE` + temp dir: widget assets must resolve for webshot; clean up temp with `on.exit(unlink(...))`.
- Set `zoom = 2` (or higher) for retina-sharp PNGs at modest `vwidth`/`vheight`.
- Do not use `ggrepel` on the same plot you plan to screenshot with plotly — repel labels often break in `ggplotly()`.

## Worked example

`../tidytuesday/2026_06_16_uk_baby_names/R/load_data.R` — `save_interactive_png`, `as_interactive`  
`../tidytuesday/2026_06_16_uk_baby_names/run.R` — `save_interactive_png(p_unique_sex, "output/04_uniqueness_by_sex.png")`
