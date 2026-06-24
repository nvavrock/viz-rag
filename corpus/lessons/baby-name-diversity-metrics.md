# Baby name diversity metrics (ggplot2 captions)

**Source:** tidytuesday `2026_06_16_uk_baby_names` — uniqueness charts by region, year, and sex.

## Two complementary metrics

Computed per **region × year × sex** from raw name registration rows (`Year`, `Sex`, `Name`, `Number`, `Rank`):

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| `names_per_1000_births` | `n_distinct(Name) / sum(Number) * 1000` | How many unique names appear per 1,000 births |
| `pct_outside_top100` | `sum(Number[Rank > 100 \| is.na(Rank)]) / sum(Number) * 100` | Share of babies **not** given a top-100 name |

Higher values = more naming diversity / less concentration in ultra-common names.

## Definitions that matter in captions

- **Top 100 is per region per year** — ranks are not pooled across England & Wales, Scotland, and Northern Ireland.
- **Unranked names** (`is.na(Rank)`) count as outside the top 100 (typically rare spellings).
- **England & Wales** is one region in the dataset (ONS combined), not separate countries.

## Chart pairing

| Story | Chart | Y-axis |
|-------|-------|--------|
| Diversity trend over time | `facet_wrap(~ region)` lines | `names_per_1000_births` |
| Girls vs boys + regional spread | boxplot by `Sex`, jitter colored by `region` | `pct_outside_top100` |

Regional level differences (E&W > Scotland > NI) can appear in jitter color even when the headline is sex — mention in text or facet by region.

## Population size caveat

`% outside top 100` is already a **within-group proportion**, so it is comparable across regions without normalizing by population. Population size affects raw distinct-name counts more than this percentage.

Do not claim population alone explains regional gaps without other evidence (culture, ethnicity, reporting).

## R implementation

```r
compute_uniqueness <- function(names) {
  names |>
    filter(!is.na(Number), Number > 0) |>
    group_by(region, Year, Sex) |>
    summarise(
      total_births = sum(Number),
      distinct_names = n_distinct(Name),
      births_outside_top100 = sum(Number[Rank > 100 | is.na(Rank)]),
      .groups = "drop"
    ) |>
    mutate(
      names_per_1000_births = distinct_names / total_births * 1000,
      pct_outside_top100 = births_outside_top100 / total_births * 100
    )
}
```

## Worked example

`../tidytuesday/2026_06_16_uk_baby_names/R/02_name_uniqueness.R`
