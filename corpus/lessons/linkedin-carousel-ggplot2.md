# LinkedIn carousel: ggplot2 export heuristics

**Source:** tidytuesday `2026_06_16_uk_baby_names` — three-slide carousel + interactive report on GitHub Pages.

## Strategy

| Channel | Format | Strength |
|---------|--------|----------|
| LinkedIn carousel | Static PNG (3–4 slides) | One takeaway per swipe |
| GitHub Pages / Quarto HTML | plotly hover | Exact counts, ranks, extra charts |

LinkedIn cannot embed plotly. Put the **interactive report URL** in the post; slides sell the story, the link rewards the click.

## Chart choice for phone feeds

### Faceted top-N bars (`facet_grid`, `scales = "free"`)

- **Good:** each region/sex panel shows its own count scale — small regions remain visible.
- **Bad on mobile:** six panels, different x-scales — readers compare bar length **within** a panel only.
- **Fix in copy:** state "each region uses its own scale" in post text **and** image alt text.

### Boxplot + jitter + color legend

- **Good in HTML:** hover shows region and year; box summarizes 10-year spread by sex.
- **Bad as static PNG:** cramped legend, overlapping points, **secondary story hidden** (e.g. regional vertical bands) unless caption mentions it.
- **Alternatives for LinkedIn:** `facet_wrap(~ region)` with box or dodged bars; or one number in the post and a simpler chart.

### Line charts with missing years

- When one region lacks 2025 (or latest year), line panels look empty or flat.
- **Slope chart** (rank 2024 → 2025, `facet_wrap(~ Name)`) tells YoY change more directly than sparse multi-region lines.

### Motion (bar chart race GIF)

- GIFs can perform well on LinkedIn, but only if the narrative matches slide 1 — do not build a race and leave it out of the carousel.

## Post copy

- **Hook:** lead with one surprising fact (#1 name, largest jump), not "This week I joined #TidyTuesday".
- **One number per takeaway** when possible (~41% vs ~39% outside top 100).
- **Causation:** soften pop-culture claims when data is partial across regions ("consistent with NRS reported" vs "proves Bridgerton effect").
- **Invite feedback:** one line ("All criticism welcome — charts, copy, or angles I should have explored") if you want comments.
- **Links:** report URL once in body; optional duplicate in first comment for clickability.

## Checklist before posting

1. `run_week()` — regenerate PNGs from current R.
2. Upload slides **in narrative order** (match numbered takeaways).
3. Paste **alt text** per image (LinkedIn image description).
4. Confirm GitHub Pages report matches chart styling.

## Alt text template

Describe chart type, variables, population, year range, and any scale caveat:

> Box plot of the share of births with names outside the top 100, by sex, with points coloured by UK region (2016–2025). Girls consistently have a higher share of less common names.

## Worked example

`../tidytuesday/2026_06_16_uk_baby_names/LINKEDIN.md` — post draft, slide order, alt text  
`../tidytuesday/VIZ_LESSONS.md` — dated lesson log
