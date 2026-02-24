# Symbolic KD Conclusions on Raw `data/` Datasets

This report summarizes the rerun based on:
- `data/WineDataset.csv`
- `data/XWines_Test_100_wines.csv`

with outputs in:
- `outputs/wine_symbolic_kd_raw_light/`
- `outputs/xwine_symbolic_kd_raw_light/`

and notebooks:
- `WineDataset_symbolic_kd_raw.ipynb`
- `XWine_symbolic_kd_raw.ipynb`

## 1) WineDataset (raw)

### Main feature signals

Top symbolic features (importance):
- `Closure_Natural Cork`
- `region_clean_Other`
- `Type_White`
- `Type_Red`
- `abv_num_low`

Interpretation:
- The structure is now much more domain-oriented (closure, type, style, ABV, country/region) than the previous enrichment-driven run.

### Concepts (stable / high-support)

Top stable concepts include:
- `{Closure_Natural Cork}`
- `{region_clean_Other}`
- `{Type_White}`
- `{abv_num_low}`

Interpretation:
- Core axes of variation in this raw wine dataset are closure, broad geography bucket, type, and ABV tier.

### Interesting implications (examples)

Highlighted rules include:
1. `{char::Black Fruit, region_clean_Other} -> {Type_Red}`
2. `{Style_Savoury & Full Bodied} -> {Type_Red}`
3. `{Country_France, Type_White, price_num_high} -> {Closure_Natural Cork}`
4. `{Country_France, vintage_year_low, price_num_high} -> {Closure_Natural Cork}`
5. `{Closure_Screwcap, char::Lemon} -> {Type_White}`

Interpretation:
- These implications are now meaningful wine-style and market-structure associations rather than mostly missing-data relations.

## 2) XWine (raw)

### Main feature signals

Top symbolic features:
- `region_clean_Other`
- `Type_Red`
- `food::Beef`
- `Elaborate_Varietal/100%`
- `latest_vintage_low`

Interpretation:
- The strongest structure combines wine type, elaboration style, food pairing tags, and vintage-based attributes.

### Concepts (stable / high-support)

Top stable concepts include:
- `{region_clean_Other}`
- `{region_clean_Other, Elaborate_Varietal/100%}`
- `{Acidity_Medium, region_clean_Other}`
- `{abv_num_low, region_clean_Other}`

Interpretation:
- Regional bucket + stylistic descriptors (elaboration, acidity, ABV) define coherent conceptual groupings.

### Interesting implications (examples)

Highlighted rules include:
1. `{food::Game Meat} -> {Type_Red}`
2. `{food::Lamb} -> {food::Beef}`
3. `{vintage_span_high} -> {oldest_vintage_low}`
4. `{oldest_vintage_high} -> {vintage_span_low}`
5. `{Body_Full-bodied, food::Beef} -> {Type_Red}`

Interpretation:
- XWine produces clear and intuitive food-body-type symbolic links.

## 3) Subgroups and Target Design

Binary targets used:
- WineDataset: `high_price_quartile`
- XWine: `high_abv_quartile`

Year grouping decision:
- Broad eras (e.g. `<=2010` vs `>2010`) are preferred over adjacent-year pairs.
- Rationale: broader bins reduce sparsity and improve interpretability/stability.

Current subgroup quality in lightweight run:
- Top precision values are around `0.30`, indicating weak discrimination under strict runtime constraints.

Interpretation:
- Subgroup results are exploratory and should be treated as preliminary.
- For stronger subgroup discovery, increase pattern-space budget (sample size / search depth).

## 4) Final takeaway

Switching to raw `data/` substantially improved interpretability:
- fewer missingness-driven artifacts
- more domain-relevant implications and concepts
- better basis for qualitative wine knowledge discussion

The generated notebooks are valid for reporting FCA/SKD findings, with a clear note that subgroup quality is limited by the lightweight computational setting.
