import argparse
import ast
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import caspailleur as csp
import numpy as np
import pandas as pd
import paspailleur as psp


def parse_number(text: Any) -> float:
    if pd.isna(text):
        return np.nan
    if isinstance(text, (int, float, np.number)):
        return float(text)
    match = re.search(r"[-+]?\d*\.?\d+", str(text).replace(",", ""))
    return float(match.group()) if match else np.nan


def parse_vintage_year(value: Any) -> float:
    if pd.isna(value):
        return np.nan
    match = re.search(r"(19|20)\d{2}", str(value))
    return float(match.group()) if match else np.nan


def split_multivalue(value: Any) -> list[str]:
    if pd.isna(value):
        return []
    if isinstance(value, (list, tuple, set)):
        raw_items = list(value)
    else:
        text = str(value).strip()
        if not text:
            return []
        if text.startswith("[") and text.endswith("]"):
            try:
                parsed = ast.literal_eval(text)
                if isinstance(parsed, (list, tuple, set)):
                    raw_items = list(parsed)
                else:
                    raw_items = [text]
            except (ValueError, SyntaxError):
                raw_items = re.split(r"[;,|]", text)
        else:
            raw_items = re.split(r"[;,|]", text)

    cleaned = []
    for item in raw_items:
        token = str(item).strip().strip("'").strip('"')
        if token and token.lower() not in {"nan", "none", "n.v.", "nv"}:
            cleaned.append(token)
    return cleaned


def cap_categories(series: pd.Series, top_k: int = 8) -> pd.Series:
    values = series.astype(str).fillna("Unknown")
    top = set(values.value_counts(dropna=False).head(top_k).index)
    return values.apply(lambda v: v if v in top else "Other")


def qcut_labels(series: pd.Series, labels: list[str]) -> pd.Series:
    clean = series.astype(float)
    valid = clean.dropna()
    if valid.empty:
        return pd.Series(["missing"] * len(series), index=series.index)
    q = min(len(labels), valid.nunique())
    if q < 2:
        out = pd.Series(["single_bin"] * len(series), index=series.index)
        out[clean.isna()] = "missing"
        return out
    binned, bins = pd.qcut(valid, q=q, retbins=True, duplicates="drop")
    n_bins = max(1, len(bins) - 1)
    used_labels = labels[:n_bins]
    # Re-label intervals to stable low/mid/high tags even if qcut reduced bins.
    binned_valid = pd.Categorical.from_codes(binned.cat.codes, categories=used_labels, ordered=True)
    out = pd.Series(index=series.index, dtype=object)
    out.loc[valid.index] = binned_valid.astype(str)
    out.loc[clean.isna()] = "missing"
    return out.fillna("missing")


def build_wine_dataframe(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path).copy()
    df["price_num"] = df["Price"].apply(parse_number)
    df["abv_num"] = df["ABV"].apply(parse_number)
    df["vintage_year"] = df["Vintage"].apply(parse_vintage_year)
    if "region_std" in df.columns:
        df["region_clean"] = df["region_std"].fillna(df["Region"]).fillna("Unknown")
    else:
        df["region_clean"] = df["Region"].fillna("Unknown")
    df["grape_tokens"] = df["Grape"].apply(split_multivalue)
    df["char_tokens"] = df["Characteristics"].apply(split_multivalue)
    return df


def build_xwine_dataframe(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path).copy()
    df["abv_num"] = df["ABV"].apply(parse_number)
    if "region_std" in df.columns:
        df["region_clean"] = df["region_std"].fillna(df["RegionName"]).fillna("Unknown")
    else:
        df["region_clean"] = df["RegionName"].fillna("Unknown")
    df["grape_tokens"] = df["Grapes"].apply(split_multivalue)
    df["harmonize_tokens"] = df["Harmonize"].apply(split_multivalue)
    vintages = df["Vintages"].apply(split_multivalue)
    vintage_numbers = vintages.apply(lambda arr: [int(v) for v in arr if str(v).isdigit()])
    df["latest_vintage"] = vintage_numbers.apply(lambda arr: max(arr) if arr else np.nan)
    df["oldest_vintage"] = vintage_numbers.apply(lambda arr: min(arr) if arr else np.nan)
    df["vintage_span"] = df["latest_vintage"] - df["oldest_vintage"]
    df["has_non_vintage"] = df["Vintages"].astype(str).str.contains("N\\.V\\.", case=False, na=False)
    return df


def list_token_features(series: pd.Series, min_support: int, top_k: int) -> list[str]:
    counter = Counter()
    for values in series:
        counter.update(set(values))
    return [token for token, cnt in counter.most_common(top_k) if cnt >= min_support]


def build_binary_context(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    n_rows = len(df)
    token_min_support = max(3, int(0.05 * n_rows))
    context = pd.DataFrame(index=df.index)

    if dataset_name == "wine":
        for col in ["Type", "Country", "region_clean", "Style", "Closure"]:
            mapped = cap_categories(df[col].fillna("Unknown"), top_k=7)
            dummies = pd.get_dummies(mapped, prefix=col, dtype=bool)
            context = pd.concat([context, dummies], axis=1)

        numeric_cols = ["price_num", "abv_num", "vintage_year"]
        if "harvest_for_vintage" in df.columns:
            numeric_cols.append("harvest_for_vintage")
        if "avg_harvest_start_to_2007" in df.columns:
            numeric_cols.append("avg_harvest_start_to_2007")
        for col in numeric_cols:
            bins = qcut_labels(df[col], labels=["low", "mid", "high"])
            dummies = pd.get_dummies(bins, prefix=col, dtype=bool)
            context = pd.concat([context, dummies], axis=1)

        for token in list_token_features(df["grape_tokens"], token_min_support, top_k=10):
            context[f"grape::{token}"] = df["grape_tokens"].apply(lambda arr: token in arr)
        for token in list_token_features(df["char_tokens"], token_min_support, top_k=12):
            context[f"char::{token}"] = df["char_tokens"].apply(lambda arr: token in arr)

    else:
        for col in ["Type", "Elaborate", "Country", "region_clean", "Body", "Acidity"]:
            mapped = cap_categories(df[col].fillna("Unknown"), top_k=7)
            dummies = pd.get_dummies(mapped, prefix=col, dtype=bool)
            context = pd.concat([context, dummies], axis=1)

        numeric_cols = ["abv_num", "latest_vintage", "oldest_vintage", "vintage_span"]
        if "avg_harvest_start_to_2007" in df.columns:
            numeric_cols.append("avg_harvest_start_to_2007")
        for col in numeric_cols:
            bins = qcut_labels(df[col], labels=["low", "mid", "high"])
            dummies = pd.get_dummies(bins, prefix=col, dtype=bool)
            context = pd.concat([context, dummies], axis=1)

        context["has_non_vintage"] = df["has_non_vintage"].fillna(False).astype(bool)
        for token in list_token_features(df["grape_tokens"], token_min_support, top_k=12):
            context[f"grape::{token}"] = df["grape_tokens"].apply(lambda arr: token in arr)
        for token in list_token_features(df["harmonize_tokens"], token_min_support, top_k=12):
            context[f"food::{token}"] = df["harmonize_tokens"].apply(lambda arr: token in arr)

    context = context.loc[:, context.sum(axis=0) > 0]
    return context.astype(bool)


def rowset(obj: Any) -> set[str]:
    if isinstance(obj, set):
        return obj
    if isinstance(obj, (list, tuple)):
        return set(obj)
    return set()


def run_caspailleur(context: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    min_support_concepts = max(5, int(0.04 * len(context)))
    min_support_imp = max(4, int(0.03 * len(context)))
    concepts = csp.mine_concepts(
        context,
        to_compute=["extent", "intent", "support", "delta_stability"],
        min_support=min_support_concepts,
        sort_by_descending="delta_stability",
    ).reset_index(drop=True)
    implications = csp.mine_implications(
        context,
        basis_name="Canonical Direct",
        to_compute=["premise", "conclusion", "support", "delta_stability"],
        min_support=min_support_imp,
    ).reset_index(drop=True)
    return concepts, implications


def mine_feature_importance(context: pd.DataFrame, concepts: pd.DataFrame, implications: pd.DataFrame) -> pd.DataFrame:
    concept_weight = defaultdict(float)
    implication_weight = defaultdict(float)

    for _, row in concepts.iterrows():
        intent = rowset(row["intent"])
        weight = float(row["delta_stability"]) * (float(row["support"]) / max(1, len(context)))
        for attr in intent:
            concept_weight[attr] += weight

    for _, row in implications.iterrows():
        premise = rowset(row["premise"])
        conclusion = rowset(row["conclusion"])
        weight = float(row["support"]) / max(1, len(context))
        for attr in premise:
            implication_weight[attr] += 1.2 * weight
        for attr in conclusion:
            implication_weight[attr] += 0.8 * weight

    records = []
    for attr in context.columns:
        support = float(context[attr].mean())
        score = support + concept_weight[attr] + implication_weight[attr]
        records.append(
            {
                "feature": attr,
                "support_ratio": support,
                "concept_weight": concept_weight[attr],
                "implication_weight": implication_weight[attr],
                "importance_score": score,
            }
        )

    out = pd.DataFrame(records).sort_values("importance_score", ascending=False).reset_index(drop=True)
    return out


def serialise_pattern_dict(pattern_map: dict[Any, Any], total_objects: int) -> pd.DataFrame:
    rows = []
    for premise, conclusion in pattern_map.items():
        rows.append(
            {
                "premise": str(premise),
                "conclusion": str(conclusion),
                "premise_size": len(premise),
                "conclusion_size": len(conclusion),
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.sort_values(["premise_size", "conclusion_size"], ascending=[True, False]).reset_index(drop=True)


def make_bounds(values: pd.Series, n_quantiles: int = 5) -> tuple[float, ...]:
    valid = values.dropna().astype(float)
    if valid.empty:
        return (0.0, 1.0)
    quantiles = np.linspace(0, 1, n_quantiles)
    bounds = sorted(set(float(valid.quantile(q)) for q in quantiles))
    if len(bounds) == 1:
        return (bounds[0] - 1.0, bounds[0], bounds[0] + 1.0)
    return tuple(bounds)


def build_pattern_structure_input(df: pd.DataFrame, dataset_name: str) -> tuple[Any, pd.DataFrame]:
    p_df = pd.DataFrame(index=df.index)
    pattern_types = {}

    if dataset_name == "wine":
        p_df["Type"] = cap_categories(df["Type"].fillna("Unknown"), top_k=6)
        p_df["Country"] = cap_categories(df["Country"].fillna("Unknown"), top_k=8)
        p_df["ABV"] = df["abv_num"].fillna(df["abv_num"].median())
        p_df["Price"] = df["price_num"].fillna(df["price_num"].median())
        p_df["Vintage"] = df["vintage_year"].fillna(df["vintage_year"].median())

    else:
        p_df["Type"] = cap_categories(df["Type"].fillna("Unknown"), top_k=6)
        p_df["Country"] = cap_categories(df["Country"].fillna("Unknown"), top_k=8)
        p_df["Body"] = cap_categories(df["Body"].fillna("Unknown"), top_k=5)
        p_df["ABV"] = df["abv_num"].fillna(df["abv_num"].median())
        p_df["LatestVintage"] = df["latest_vintage"].fillna(df["latest_vintage"].median())

    for col in p_df.columns:
        if pd.api.types.is_numeric_dtype(p_df[col]):
            pattern_types[col] = psp.pattern_factory("ClosedIntervalPattern", BoundsUniverse=make_bounds(p_df[col], 6))
        else:
            universe = tuple(sorted(p_df[col].astype(str).unique()))
            pattern_types[col] = psp.pattern_factory("CategorySetPattern", Universe=universe)
            p_df[col] = p_df[col].astype(str)

    class DynamicPattern(psp.bip.CartesianPattern):
        DimensionTypes = pattern_types

    return DynamicPattern, p_df


def choose_subgroup_targets(df: pd.DataFrame, dataset_name: str) -> dict[str, tuple[pd.Series, str]]:
    targets = {}
    if dataset_name == "wine":
        high_price_cut = df["price_num"].quantile(0.75)
        targets["high_price_quartile"] = (
            df["price_num"] >= high_price_cut,
            f"Price in top quartile (>= {high_price_cut:.2f}) captures commercially premium wines.",
        )
        targets["older_vintage_pre2011"] = (
            df["vintage_year"] <= 2010,
            "A split at 2010 yields interpretable pre-2011 vs modern wines and avoids tiny year-by-year groups.",
        )
    else:
        high_abv_cut = df["abv_num"].quantile(0.75)
        targets["high_abv_quartile"] = (
            df["abv_num"] >= high_abv_cut,
            f"ABV top quartile (>= {high_abv_cut:.2f}) isolates stronger wine profiles.",
        )
        targets["older_latest_vintage_pre2011"] = (
            df["latest_vintage"] <= 2010,
            "Using <=2010 for latest known vintage creates stable temporal subgroups instead of sparse consecutive-year bins.",
        )
    return targets


def run_paspailleur(df: pd.DataFrame, dataset_name: str) -> dict[str, Any]:
    pattern_type, p_df = build_pattern_structure_input(df, dataset_name)
    if len(p_df) > 10:
        # Paspailleur is computationally expensive; use a representative sample for exploratory subgroup mining.
        p_df = p_df.sample(n=10, random_state=42)
    ps = psp.PatternStructure(pattern_type)
    ps.fit(p_df.to_dict("index"), min_atom_support=max(2, int(0.25 * len(p_df))))

    concepts = ps.mine_concepts(min_support=max(2, int(0.3 * len(p_df))), min_delta_stability=0.02)

    subgroup_frames = {}
    subgroup_rationale = {}
    targets = choose_subgroup_targets(df.loc[p_df.index], dataset_name)

    atoms = list(ps.atomic_patterns.keys())[:12]
    for target_name, (mask, rationale) in targets.items():
        goal_objects = set(p_df.index[mask.fillna(False)])
        if len(goal_objects) < 3:
            continue
        subgroup_rationale[target_name] = rationale

        candidates = []
        for p in atoms:
            candidates.append((str(p), p))
        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):
                joined = atoms[i] | atoms[j]
                candidates.append((str(joined), joined))

        rows = []
        fallback_rows = []
        for descr, pattern in candidates:
            extent = set(ps.extent(pattern))
            support = len(extent)
            if support < 1:
                continue
            tp = len(extent & goal_objects)
            fp = support - tp
            quality = tp / support if support else 0.0
            fallback_rows.append(
                {
                    "description": descr,
                    "quality": float(quality),
                    "tp": int(tp),
                    "fp": int(fp),
                    "support": int(support),
                }
            )
            if quality < 0.4:
                continue
            rows.append(
                {
                    "description": descr,
                    "quality": float(quality),
                    "tp": int(tp),
                    "fp": int(fp),
                    "support": int(support),
                }
            )
        subgroup_df = pd.DataFrame(rows)
        if subgroup_df.empty:
            fallback_df = pd.DataFrame(fallback_rows)
            if fallback_df.empty:
                subgroup_frames[target_name] = pd.DataFrame(columns=["description", "quality", "tp", "fp", "support"])
            else:
                subgroup_frames[target_name] = (
                    fallback_df.drop_duplicates(subset=["description"])
                    .sort_values(["quality", "support"], ascending=[False, False])
                    .head(8)
                    .reset_index(drop=True)
                )
        else:
            subgroup_frames[target_name] = (
                subgroup_df.drop_duplicates(subset=["description"])
                .sort_values(["quality", "support"], ascending=[False, False])
                .reset_index(drop=True)
            )

    concept_rows = []
    for concept in concepts:
        concept_rows.append(
            {
                "intent": str(concept.intent),
                "support": int(len(concept.extent)),
                "delta_stability": np.nan,
            }
        )
    concepts_df = pd.DataFrame(concept_rows).sort_values(
        ["delta_stability", "support"], ascending=[False, False]
    ).reset_index(drop=True)

    return {
        "pattern_concepts": concepts_df,
        "pattern_implications": pd.DataFrame(columns=["premise", "conclusion", "premise_size", "conclusion_size"]),
        "subgroups": subgroup_frames,
        "subgroup_rationale": subgroup_rationale,
        "pattern_shape": ps.shape,
    }


def pick_interesting_implications(implications: pd.DataFrame, max_n: int = 5) -> pd.DataFrame:
    if implications.empty:
        return implications
    scored = implications.copy()
    scored["premise_len"] = scored["premise"].apply(lambda x: len(rowset(x)))
    scored["conclusion_len"] = scored["conclusion"].apply(lambda x: len(rowset(x)))
    scored["interesting_score"] = (
        scored["support"] * (1 + 0.2 * scored["premise_len"] + 0.15 * scored["conclusion_len"])
    )
    scored = scored.sort_values("interesting_score", ascending=False)
    return scored.head(max_n).reset_index(drop=True)


def run_analysis(dataset_name: str, input_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    if dataset_name == "wine":
        df = build_wine_dataframe(input_path)
    else:
        df = build_xwine_dataframe(input_path)

    df = df.reset_index(drop=True)
    df.index = [f"{dataset_name}_{i:04d}" for i in range(len(df))]

    context = build_binary_context(df, dataset_name)
    concepts, implications = run_caspailleur(context)
    feature_importance = mine_feature_importance(context, concepts, implications)
    top_implications = pick_interesting_implications(implications, max_n=5)

    psp_results = run_paspailleur(df, dataset_name)

    context.astype(int).to_csv(output_dir / "binary_context.csv", index=True)
    concepts.to_csv(output_dir / "caspailleur_concepts.csv", index=False)
    implications.to_csv(output_dir / "caspailleur_implications.csv", index=False)
    feature_importance.to_csv(output_dir / "feature_importance.csv", index=False)
    top_implications.to_csv(output_dir / "interesting_implications.csv", index=False)
    psp_results["pattern_concepts"].to_csv(output_dir / "paspailleur_concepts.csv", index=False)
    psp_results["pattern_implications"].to_csv(output_dir / "paspailleur_implications.csv", index=False)

    subgroup_files = {}
    for target_name, subgroup_df in psp_results["subgroups"].items():
        file_name = f"subgroups_{target_name}.csv"
        subgroup_df.to_csv(output_dir / file_name, index=False)
        subgroup_files[target_name] = file_name

    summary = {
        "dataset": dataset_name,
        "n_objects": int(len(df)),
        "n_binary_features": int(context.shape[1]),
        "caspailleur_concepts": int(len(concepts)),
        "caspailleur_implications": int(len(implications)),
        "pattern_structure_shape": [int(psp_results["pattern_shape"][0]), int(psp_results["pattern_shape"][1])],
        "subgroup_files": subgroup_files,
        "subgroup_rationale": psp_results["subgroup_rationale"],
        "year_grouping_justification": (
            "Year-based subgrouping uses broader eras (<=2010 vs >2010) instead of consecutive pairs "
            "to reduce sparsity and improve interpretability."
        ),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run symbolic knowledge discovery analysis.")
    parser.add_argument("--dataset", choices=["wine", "xwine"], required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--input-path", required=False)
    args = parser.parse_args()

    default_input = {
        "wine": Path("data_preprocessed/WineDataset_enriched.csv"),
        "xwine": Path("data_preprocessed/XWines_Test_100_wines_enriched.csv"),
    }
    input_path = Path(args.input_path) if args.input_path else default_input[args.dataset]
    run_analysis(args.dataset, input_path=input_path, output_dir=Path(args.output_dir))


if __name__ == "__main__":
    main()
