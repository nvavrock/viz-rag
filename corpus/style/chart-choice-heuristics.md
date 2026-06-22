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
