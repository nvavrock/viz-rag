# FT-inspired chart principles (original summary)

Summarized from public FT data-viz journalism practice — not copied from FT articles.
References: [FT Chart Doctor](https://www.ft.com/chart-doctor), [FT on data visualization](https://professional.ft.com/en-gb/blog/data-visualisation-ft-what-makes-it-unique/).

## Communication first

- A chart should carry information like a paragraph: readers should learn something concrete, not just see decoration.
- Title and subtitle state the takeaway. The chart proves it.
- If the title is vague, the chart is probably vague.

## Titles and labels

- Use a headline-style title: what happened or what matters.
- Subtitle: scope, time range, units, or caveats ("England & Wales through 2024").
- Label axes in plain language; avoid jargon when the audience is general.
- Directly label series when there are few lines/bars; avoid legend hunting.

## Accessibility

- Do not rely on color alone. Use position, labels, or pattern when categories must be distinguished.
- Check palettes for colorblind safety (viridis, Okabe–Ito, or tested corporate palettes).
- Sufficient contrast for text on backgrounds.

## Density and time

- Many readers skim. One strong message per chart beats three weak ones.
- Small multiples beat overloaded single panels when comparing regions or groups.
- Truncate y-axis only when the baseline is meaningful and distortion is obvious — default to zero for counts.

## ggplot2 habits that match this style

- `labs(title = ..., subtitle = ..., caption = "Source: ...")`
- `theme_minimal()` or a restrained custom theme; avoid chartjunk.
- `scale_*` with readable breaks (`scales::comma`, `scales::percent`).
- Put source and notes in `caption`, not buried in body text.
