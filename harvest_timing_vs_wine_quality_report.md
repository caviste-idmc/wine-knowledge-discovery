## Harvest timing (early vs late) and wine quality: direct and indirect effects

This report summarizes research on how **earlier vs later grape harvest** can affect wine “quality” (sensory outcomes, critic scores, and style) **directly** (through grape composition at picking) and **indirectly** (because harvest timing is strongly driven by the same climate conditions that also shape composition and perceived quality).

It is written with your project context in mind: you have a long historical **grape harvest date (GHD)** dataset for European regions (encoded as “days after 31 August”), and modern wine datasets with region and vintage.

---

## 1) What “early” vs “late” harvest means in viticulture

### 1.1 Harvest date is both a decision and a constraint

Harvest timing reflects a mixture of:

- **Grower/winemaker choices**: desired style (fresh vs ripe), capacity constraints, risk management (rain/rot/heat), market goals.
- **Seasonal conditions**: temperature, rainfall, sunlight, vine water status, disease pressure.

Because of this, “early harvest” is not automatically “underripe” and “late harvest” is not automatically “better”. It depends on the vintage conditions and the target wine style.

### 1.2 In the GHD dataset: negative values are valid

In the Daux et al. GHD database, harvest dates are expressed as **number of days after 31 August** (so negative numbers mean harvest happened in August). The dataset description explicitly uses that encoding and treats harvest dates as a climate-sensitive phenological variable.  
Source: Daux et al. (2012) GHD dataset documentation and article summary in Climate of the Past (`https://cp.copernicus.org/articles/8/1403/2012/`) and NOAA text distribution (`https://www.ncei.noaa.gov/pub/data/paleo/historical/europe/europe2012ghd.txt`).

---

## 2) Direct effects: how harvest timing changes grape chemistry and sensory outcomes

“Harvest timing” is essentially choosing a point on the ripening curve. Many key variables move in predictable directions with later picking (though rates vary by cultivar and weather).

### 2.1 Sugar, acidity, pH, alcohol (basic balance)

Across ripening:

- **Sugar increases** (→ higher potential alcohol).
- **Titratable acidity decreases** and **pH tends to increase** (driven especially by malic acid respiration during warm ripening).

Example evidence (Cabernet Sauvignon sequential harvest):
- Grapes from later harvests showed **increased total soluble solids** and **decreased titratable acidity**; wines showed **increased alcoholic strength** and **increased pH** with sequential harvest timing.  
Source: Zhao et al., *Molecules* (2019), “Harvesting at the Right Time…” (`https://www.mdpi.com/1420-3049/24/15/2777`).

Practical sensory implication:
- **Earlier picking** tends to preserve **freshness and acidity**, but risks **thin body / low alcohol** (depending on target style) and may preserve “green” aroma compounds.
- **Later picking** tends toward **richer body / higher alcohol** and softer perceived acidity, but can become unbalanced in warm years (high alcohol + low acidity).

### 2.2 Herbaceous/green vs fresh-fruit vs cooked/overripe aromas

Harvest date can shift aroma profile even over small timing differences.

- A Bordeaux-focused study (Merlot and Cabernet Sauvignon) found that **fine-tuning harvest date modulated herbaceous/vegetal, fresh fruit, and cooked fruit nuances**, and that delaying harvest was necessary to substantially increase cooked-fruit aroma intensity (on the order of about **one week**, depending on vintage/variety).  
Source: Allamy et al., OENO One (harvest-date aroma markers; cooked-fruit molecular markers) (`https://oeno-one.eu/article/view/7458`).

Sequential harvest can also shift volatile composition:
- Several volatile compounds increased when harvest was delayed by about 1–2 weeks in the Cabernet Sauvignon study, and sequential-harvest wines were chemically distinguishable by PCA.  
Source: Zhao et al., *Molecules* (2019) (`https://www.mdpi.com/1420-3049/24/15/2777`).

### 2.3 Phenolic maturity (tannins/anthocyanins) does not perfectly align with “sugar maturity”

Winemakers often distinguish:

- **Technological maturity**: sugar/acidity balance (Brix, TA, pH).
- **Phenolic/aromatic maturity**: tannin ripeness, anthocyanins, aroma precursors.

These can become **decoupled**, especially in warm climates where sugar can accumulate quickly while phenolic maturity lags (and acid drops quickly). This is one reason why harvest decisions are difficult and why “late harvest” isn’t universally “better”: the “best” harvest point is the one that matches the desired balance and the constraints of a given year.

The OENO One study explicitly frames harvest date as a way to manage wine style and highlights that different “maturities” do not coincide and depend on climatic conditions.  
Source: Allamy et al., OENO One (`https://oeno-one.eu/article/view/7458`).

### 2.4 Special case: late-harvest sweet/botrytized wines

“Late harvest” can also mean intentionally harvesting **overripe or botrytized** fruit for sweet wines (e.g., Sauternes, Tokaji). In this case, wine quality may increase *because* noble rot and dehydration create a distinctive metabolome and aroma profile (but this is a different mechanism than “late harvest” for dry table wines).

- Noble rot (Botrytis cinerea) in late ripening stages is used in some regions to produce **high-quality sweet wines** and **alters berry metabolism and composition**, leading to different volatile profiles in wine.  
Source: Negri et al., *Frontiers in Plant Science* (2017) (`https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2017.01002/full`).

---

## 3) Indirect effects: harvest timing as a proxy for climate (and climate also affects “quality”)

### 3.1 Harvest date is strongly driven by temperature

Multiple phenology/climate studies show harvest date is closely tied to spring–summer temperature.

- Burgundy grape harvest date is **mainly influenced by local April–August temperature** (interannual), with additional winter-temperature effects on longer time scales.  
Source: Krieger et al., *Climate of the Past* (2011) (`https://cp.copernicus.org/articles/7/425/2011/`).

- The Daux et al. GHD database paper emphasizes a **strong link between harvest dates and growing-season temperature** and uses that relationship as a core quality check of the series.  
Source: Daux et al., *Climate of the Past* (2012) (`https://cp.copernicus.org/articles/8/1403/2012/`).

Interpretation:
- In many traditional regions, an “early harvest year” often indicates a **warmer-than-usual growing season**.

### 3.2 Climate affects composition and wine style (even at the same “harvest timing”)

Climate shapes:
- rate of sugar accumulation and acid degradation,
- water stress and berry size (dilution vs concentration),
- disease/rot pressure,
- heat damage/sunburn risk,
- aromatic precursor formation.

Recent synthesis:
- A major review summarizes that rising temperatures have advanced harvest dates by **~2–3 weeks over the past ~40 years**, shifting ripening into a warmer part of summer, thereby changing grape composition and wine style.  
Source: van Leeuwen et al., *Nature Reviews Earth & Environment* (2024) (`https://www.nature.com/articles/s43017-024-00521-5`).

### 3.3 Wine “quality” scores also respond to weather (so harvest date can be confounded)

If critics’ scores (or price) respond to weather, and harvest date also responds to weather, then a correlation between harvest date and “quality” can appear even if harvest date itself isn’t the causal driver.

Evidence example (Bordeaux):
- A large open-access analysis links critic scores to weather variables; in continuous-time models the authors report higher quality in years with certain temperature/rainfall patterns and describe higher quality in years with “earlier, shorter seasons” alongside other weather characteristics.  
Source: Wood et al., *iScience* (2023) open access via PMC (`https://pmc.ncbi.nlm.nih.gov/articles/PMC10638477/`).

Practical interpretation:
- An observed relationship “earlier harvest → higher scores” could actually mean “warmer/drier ripening conditions → higher scores” (with harvest date being one of several correlated outcomes).
- The sign can vary by region and era because “warm” can be beneficial up to a point and harmful beyond it (extreme heat can reduce quality or shift style away from what critics prefer).

---

## 4) What you can reasonably conclude from early vs late harvest (for your project)

### 4.1 Style expectations (direct signals)

When you match a wine’s region+vintage to a harvest-date metric (like GHD days-after-31-Aug):

- **Lower GHD (earlier harvest)** tends to signal:
  - higher acidity / lower pH (all else equal),
  - lower sugar / lower alcohol potential (all else equal),
  - more herbaceous/“green” risk if too early,
  - in many regions, a warmer year (so *composition can still be ripe* even if harvest is earlier).

- **Higher GHD (later harvest)** tends to signal:
  - lower acidity / higher pH,
  - higher sugar / higher alcohol potential,
  - riper fruit character; risk of cooked/overripe notes and/or rot depending on conditions,
  - in some cases: intentional late-harvest/botrytis styles (sweet wines).

### 4.2 The key modeling caveat (indirect/confounding)

Harvest date is a **proxy variable** for climate and for human choices. If you treat it as purely causal, you will likely over-interpret it.

For analysis, consider:
- **Harvest date as an intermediate** between climate → grape composition → wine quality/style.
- **Harvest date as a summary indicator** of ripening-season warmth (especially in GHD datasets), but not the only one.

### 4.3 Practical suggestions for analysis design

If you plan statistical modeling:

- **Separate “direct” vs “indirect” hypotheses**:
  - Direct: later harvest changes sugar/acids/aroma precursors (supported by composition studies).
  - Indirect: harvest date summarizes climate conditions that influence wine quality ratings (supported by climate/quality studies).

- **Be cautious with cross-region comparisons**:
  - A given GHD value can mean different physiological maturity depending on cultivar, viticulture, and baseline climate.

- **Check non-linearity**:
  - “Warmer/earlier” can improve quality up to an optimum, after which heat can harm quality and typicity (suggested broadly in climate adaptation literature).

---

## 5) References (sources used)

- Daux, V. et al. (2012). *An open-access database of grape harvest dates for climate research: data description and quality assessment.* Climate of the Past. `https://cp.copernicus.org/articles/8/1403/2012/`
- NOAA distribution of the Daux et al. GHD dataset (text file, includes encoding description). `https://www.ncei.noaa.gov/pub/data/paleo/historical/europe/europe2012ghd.txt`
- Krieger, M. et al. (2011). *Seasonal climate impacts on the grape harvest date in Burgundy (France).* Climate of the Past. `https://cp.copernicus.org/articles/7/425/2011/`
- Wood, A. et al. (2023). *Seasonal weather impacts wine quality in Bordeaux.* iScience (open access via PMC). `https://pmc.ncbi.nlm.nih.gov/articles/PMC10638477/`
- van Leeuwen, C. et al. (2024). *Climate change impacts and adaptations of wine production.* Nature Reviews Earth & Environment. `https://www.nature.com/articles/s43017-024-00521-5`
- Zhao, T. et al. (2019). *Harvesting at the Right Time: Maturity and its Effects on the Aromatic Characteristics of Cabernet Sauvignon Wine.* Molecules. `https://www.mdpi.com/1420-3049/24/15/2777`
- Allamy, L. et al. (OENO One). *Impact of harvest date on aroma compound composition…* `https://oeno-one.eu/article/view/7458`
- Negri, S. et al. (2017). *The Induction of Noble Rot (Botrytis cinerea) Infection…* Frontiers in Plant Science. `https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2017.01002/full`

