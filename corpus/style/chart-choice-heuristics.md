# Chart choice heuristics (ggplot2 / TidyTuesday)

Original decision notes aligned with [From Data to Viz](https://www.data-to-viz.com) data-shape taxonomy.

## One numeric variable

- Distribution: histogram, density, boxplot, violin.
- Single KPI: big number + context line, or sparkline if time exists elsewhere.

## Two numeric variables

- Relationship: scatter, smooth (loess/linear) if trend is the point.
- If x is time-ordered: line chart, not scatter alone.
- High point count: transparency (`alpha`), hexbin, or 2D density.

## One categorical + one numeric

- Compare groups: bar/column (`geom_col`), ordered by value when rank matters.
- Many categories: horizontal bars (`coord_flip`) or top-N + "Other".
- Distribution within group: boxplot/violin with `x = category`.

## Several categories / facets

- `facet_wrap` or `facet_grid` when the same chart type repeats per region, sex, or year.
- Shared color for the same entity across facets when comparing patterns.

## ggplot faceting gotchas

- `facet_grid` / `facet_wrap` with a **categorical** axis (names, countries, products): by default ggplot shares all category levels across panels. Each panel may only plot top-N items, but the axis still lists every name from every panel — overlapping labels and sparse bars.
- **Fix:** `scales = "free"` (or at least `free_y` for names and `free_x` for counts) when each panel has different categories or value ranges. England & Wales counts are ~6,000; Scotland/NI are ~400 — a shared count axis makes smaller regions invisible.
- **Reorder per panel:** `group_by(region, Sex) |> mutate(Name = fct_reorder(Name, Number))` — not a global `reorder()` across the full dataset.
- **Pattern:** top-N bar charts per region/sex -> `aes(x = Number, y = Name)` + `facet_grid(Sex ~ region, scales = "free")` (horizontal bars without `coord_flip()`).

## Rank data

- Lower rank = more popular: consider `scale_y_reverse()` for rank on y.
- Tile/heatmap when showing rank across two dimensions (region × name).

## Time series

- Line for continuous trends; points for sparse years.
- Highlight one series with color/size if the story is about one group.

## When not to use a chart type

- Pie chart: few slices only; prefer bar for precise comparison.
- Dual y-axis: avoid unless audience is expert; prefer two panels.
- 3D: almost never for 2D data.

## Match data shape to folder names (data_to_viz)

Example filenames like `7_OneCatOneNum.csv` mean one categorical + one numeric — start with bar, boxplot, or ordered dot plot.
