import json
import argparse
from pathlib import Path


def md_cell(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip("\n").split("\n")],
    }


def code_cell(code: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in code.strip("\n").split("\n")],
    }


def build_notebook(dataset_key: str, output_dir: str, title: str, notebook_path: Path) -> None:
    summary_path = Path(output_dir) / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    subgroup_files = summary.get("subgroup_files", {})
    subgroup_list = ", ".join(subgroup_files.values()) if subgroup_files else "None"
    subgroup_rationale = summary.get("subgroup_rationale", {})

    cells = [
        md_cell(
            f"""
# {title}

This notebook follows the workflow style from:
- `resources/FCA_From_Scratch_SymbolicKD.ipynb`
- `resources/SymbolicKD_Pattern_Mining_+_Clustering.ipynb`

The run is intentionally lightweight to avoid computationally heavy processing:
- full binary-context mining with `caspailleur`
- sampled pattern-space mining with `paspailleur` for subgroup exploration
"""
        ),
        code_cell(
            f"""
import json
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = Path("{output_dir}")
summary = json.loads((OUTPUT_DIR / "summary.json").read_text(encoding="utf-8"))
summary
"""
        ),
        md_cell(
            """
## 1) Context and Dataset Overview

We mine a binary context for FCA (caspailleur) and a compact multi-dimensional pattern structure for subgroup-oriented exploration (paspailleur).
"""
        ),
        code_cell(
            """
context = pd.read_csv(OUTPUT_DIR / "binary_context.csv")
concepts = pd.read_csv(OUTPUT_DIR / "caspailleur_concepts.csv")
implications = pd.read_csv(OUTPUT_DIR / "caspailleur_implications.csv")
feature_importance = pd.read_csv(OUTPUT_DIR / "feature_importance.csv")
interesting_implications = pd.read_csv(OUTPUT_DIR / "interesting_implications.csv")
paspailleur_concepts = pd.read_csv(OUTPUT_DIR / "paspailleur_concepts.csv")

print("Context shape:", context.shape)
print("Caspailleur concepts:", len(concepts))
print("Caspailleur implications:", len(implications))
print("Paspailleur concepts (sampled pattern structure):", len(paspailleur_concepts))
"""
        ),
        md_cell(
            """
## 2) Feature Importance (more important vs less important)

Importance combines:
- binary support (frequency)
- stability-weighted concept participation
- implication participation weight
"""
        ),
        code_cell(
            """
top_features = feature_importance.head(15).copy()
low_features = feature_importance.tail(15).copy()

display(top_features)
display(low_features)

plt.figure(figsize=(10, 5))
plt.barh(top_features["feature"][::-1], top_features["importance_score"][::-1])
plt.title("Top 15 features by symbolic importance score")
plt.xlabel("importance_score")
plt.tight_layout()
plt.show()
"""
        ),
        md_cell(
            """
## 3) Concepts (including cool/stable concepts)

`caspailleur` returns concept intents/extents with support and delta stability.
We inspect high-support and high-stability concepts.
"""
        ),
        code_cell(
            """
stable_concepts = concepts.sort_values(["delta_stability", "support"], ascending=[False, False]).head(20)
support_concepts = concepts.sort_values("support", ascending=False).head(20)

display(stable_concepts)
display(support_concepts)
"""
        ),
        md_cell(
            """
## 4) Implications (highlight interesting ones)

The table below shows a compact ranked set of implications to discuss (3-5 most interesting).
"""
        ),
        code_cell(
            """
display(interesting_implications.head(5))

if len(interesting_implications) > 0:
    plt.figure(figsize=(8, 4))
    plt.bar(range(len(interesting_implications.head(5))), interesting_implications.head(5)["interesting_score"])
    plt.title("Interesting implication scores (top 5)")
    plt.xlabel("Implication rank")
    plt.ylabel("interesting_score")
    plt.tight_layout()
    plt.show()
"""
        ),
        md_cell(
            f"""
## 5) Subgroups (binary targets + rationale)

Subgroups are mined as patterns that are highly precise for a **binary target**.

Detected subgroup files: `{subgroup_list}`.

Rationale used in this run:
{chr(10).join([f"- `{k}`: {v}" for k, v in subgroup_rationale.items()]) if subgroup_rationale else "- No subgroup target generated in this run."}

Temporal-grouping policy:
- Prefer broad eras (e.g. <=2010 vs >2010) rather than tiny year-pairs (2001-2002, 2002-2003, ...)
- Reason: broader bins reduce sparsity and improve subgroup interpretability/stability
"""
        ),
        code_cell(
            """
for csv_file in sorted(OUTPUT_DIR.glob("subgroups_*.csv")):
    print("\\n===", csv_file.name, "===")
    df = pd.read_csv(csv_file)
    display(df.head(15))
"""
        ),
        md_cell(
            """
## 6) Paspailleur Pattern Concepts (sampled run)

This section mirrors the pattern-mining spirit from the resource notebook but under lightweight constraints.
"""
        ),
        code_cell(
            """
display(paspailleur_concepts.head(20))
"""
        ),
        md_cell(
            """
## 7) Practical Interpretation Notes

- Use top symbolic features as candidate explanatory variables for recommendation/ranking models.
- Validate highlighted implications with domain experts (oenologists/sommeliers).
- Subgroups should be re-mined on larger compute budgets if exhaustive subgroup quality optimization is required.
"""
        ),
    ]

    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    notebook_path.write_text(json.dumps(nb, ensure_ascii=True, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate symbolic KD notebooks from output directories.")
    parser.add_argument("--wine-output-dir", default="outputs/wine_symbolic_kd_light")
    parser.add_argument("--xwine-output-dir", default="outputs/xwine_symbolic_kd_light")
    parser.add_argument("--wine-notebook", default="WineDataset_symbolic_kd.ipynb")
    parser.add_argument("--xwine-notebook", default="XWine_symbolic_kd.ipynb")
    parser.add_argument("--title-suffix", default="")
    args = parser.parse_args()

    suffix = f" ({args.title_suffix})" if args.title_suffix else ""

    build_notebook(
        dataset_key="wine",
        output_dir=args.wine_output_dir,
        title=f"Symbolic Knowledge Discovery - WineDataset{suffix}",
        notebook_path=Path(args.wine_notebook),
    )
    build_notebook(
        dataset_key="xwine",
        output_dir=args.xwine_output_dir,
        title=f"Symbolic Knowledge Discovery - XWine Dataset{suffix}",
        notebook_path=Path(args.xwine_notebook),
    )


if __name__ == "__main__":
    main()
