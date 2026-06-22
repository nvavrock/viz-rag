# VAD framework notes (original summary)

Concepts from Tamara Munzner, *Visualization Analysis and Design* — paraphrased for retrieval, not reproduced from the book.
Book: https://www.cs.ubc.ca/~tmm/vadbook/

## Data abstraction (what)

- **Tables**: items + attributes (most TidyTuesday sets).
- **Networks**: nodes + links (use graph layouts, not force scatter).
- **Spatial**: geometry + attributes (maps, choropleth).
- **Fields**: samples in continuous domain (heatmaps, contours).

Ask: is each row an observation, a relationship, or a location?

## Task abstraction (why)

Common tasks:

- **Lookup**: read a single value.
- **Compare**: which is larger, which changed more.
- **Identify**: find outliers or matches.
- **Summarize**: distribution, trend, aggregate.

Match chart to task, not to aesthetics first.

## Marks and channels

- **Marks**: points, lines, areas, bars, text.
- **Channels**: position (strongest), length, angle, area, color, shape.

Prefer position and length for magnitude. Use color for categories or a single highlight.

## Arrange (ggplot2 mapping)

- **Tables** → `geom_col`, `geom_point`, `geom_boxplot`, facets for subgroups.
- **Time** → `geom_line`, ordered x.
- **Many categories** → facet, filter to top-N, or small multiples.

## Reduce and embed

- **Reduce**: filter, aggregate, sample — simplify before plotting.
- **Facet**: split views instead of one overcrowded panel.
- **Focus+context**: highlight one series or period in color/size.

## Validation mindset

Does the chart answer the stated task? Would a table be clearer? Can a reader state the takeaway in one sentence after reading the title?
