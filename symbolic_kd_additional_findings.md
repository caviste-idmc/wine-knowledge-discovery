# Additional Symbolic KD Findings (Lightweight Run)

This note complements:
- `WineDataset_symbolic_kd.ipynb`
- `XWine_symbolic_kd.ipynb`

## Why lightweight?

To keep runtime practical, the workflow uses:
- full FCA mining on binary contexts with `caspailleur` (fast enough)
- sampled pattern-space exploration with `paspailleur` for subgroup analysis

This follows the logic of the reference notebooks while avoiding heavy exhaustive search.

## Subgroups: what they are and why binary target?

A subgroup is a pattern that describes a subset of wines where a binary target is concentrated.

Chosen binary targets:
- WineDataset: `high_price_quartile` (price in top 25%)
- XWine: `high_abv_quartile` (ABV in top 25%)

Reason:
- easy to interpret
- actionable for market/product segmentation
- balanced enough for quick exploratory subgroup mining

## Time-based subgrouping decision

For year-based grouping, broad eras are preferred over adjacent-year pairs:
- Preferred: `<= 2010` vs `> 2010`
- Avoided: `2001-2002`, `2002-2003`, ...

Justification:
- adjacent-year bins are sparse and unstable
- broad eras produce more robust and interpretable symbolic patterns

## Highlighted implications (top examples)

### WineDataset

From `outputs/wine_symbolic_kd_light/interesting_implications.csv`:
1. `{'avg_harvest_start_to_2007_missing'} -> {'harvest_for_vintage_missing'}`
2. `{'region_clean_Other'} -> {'harvest_for_vintage_missing'}`
3. `{'price_num_low'} -> {'harvest_for_vintage_missing'}`
4. `{'Type_White', 'abv_num_low'} -> {'harvest_for_vintage_missing'}`
5. `{'Closure_Screwcap'} -> {'harvest_for_vintage_missing'}`

Interpretation note: these are strong metadata-completeness implications and useful for data quality diagnostics.

### XWine

From `outputs/xwine_symbolic_kd_light/interesting_implications.csv`:
1. `{'food::Beef'} -> {'avg_harvest_start_to_2007_missing'}`
2. `{'Type_Red'} -> {'avg_harvest_start_to_2007_missing'}`
3. `{'abv_num_low'} -> {'avg_harvest_start_to_2007_missing'}`
4. `{'Acidity_High'} -> {'avg_harvest_start_to_2007_missing'}`
5. `{'food::Game Meat'} -> {'avg_harvest_start_to_2007_missing', 'Type_Red'}`

Interpretation note: these implications highlight interactions between food-pairing descriptors, style/type, and missing harvest-derived variables.

## Suggested next step (optional)

If you later want deeper subgroup quality:
- increase `paspailleur` sample size and subgroup search depth
- keep the same targets to preserve comparability
