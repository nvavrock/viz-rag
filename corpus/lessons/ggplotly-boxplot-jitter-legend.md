# ggplotly: boxplot + jitter legend and tooltips

**Source:** tidytuesday `2026_06_16_uk_baby_names` — share of births outside top 100 by sex, points colored by UK region.

## ggplot pattern

Sex on x-axis; distribution summarized with a neutral box; individual years/regions as colored jitter.

```r
ggplot(recent, aes(x = Sex, y = pct_outside_top100)) +
  geom_boxplot(fill = "grey85", color = "grey50", outlier.shape = NA, alpha = 0.5) +
  geom_jitter(aes(color = region, text = hover), width = 0.12, size = 2, alpha = 0.85) +
  scale_color_manual(values = REGION_COLORS) +
  theme(legend.position = "right", plot.margin = margin(5.5, 80, 5.5, 5.5))
```

Build `hover` as a plain string column (`paste0(region, ", ", Year, "<br>", ...)`) and map `text = hover` on jitter only.

## Symptoms after `ggplotly()`

1. **Duplicate legend entries** — one per box trace and one per jitter trace.
2. **Box traces in legend** labeled `"1"`, `"2"` (useless).
3. **Jitter trace names** like `"1, England & Wales"` instead of region alone.
4. **Invisible jitter points** — `null` or `NA` in trace data from plotly's box/jitter split.
5. **Legend clipped** in PNG export — legend sits outside plot area.

## Fixes in `as_interactive()` (post-`ggplotly`)

### 1. Hide box traces from legend

```r
if (identical(trace$type, "box")) {
  trace$showlegend <- FALSE
  return(trace)
}
```

### 2. Clean jitter/scatter trace names → region

ggplotly often encodes jitter groups as `"<x>, <group>"`:

```r
if (grepl(",", trace_name, fixed = TRUE)) {
  region_label <- trimws(sub(".*,", "", trace_name))
  trace$name <- region_label
  trace$legendgroup <- region_label
}
```

### 3. Dedupe legend by `legendgroup`

Keep `showlegend = TRUE` only for the first trace per `legendgroup`.

### 4. Drop NA coordinates

Filter `trace$x`, `trace$y`, and `trace$text` with `keep <- !is.na(x) & !is.na(y)`.

### 5. Layout for export

```r
plotly::layout(
  hovermode = "closest",
  legend = list(orientation = "v", x = 1.02, y = 1, xanchor = "left", yanchor = "top")
)
```

Pair with ggplot `plot.margin` right padding so the legend is not cropped in `webshot2` PNGs.

## Convert call

```r
ggplotly(plot, tooltip = "text")
```

Use `tooltip = "text"` so only the custom hover column appears, not redundant aes fields.

## Static vs interactive

- **HTML report:** full `as_interactive()` pipeline.
- **LinkedIn PNG:** same pipeline, then `save_interactive_png()` (see `plotly-static-png-export.md`).
- If you only need a feed-friendly static chart, a dodged bar chart (`x = Sex, fill = region`) may read faster than box + jitter without hover.

## Worked example

`../tidytuesday/2026_06_16_uk_baby_names/R/02_name_uniqueness.R` — `plot_uniqueness_by_sex`  
`../tidytuesday/2026_06_16_uk_baby_names/R/load_data.R` — `as_interactive`
