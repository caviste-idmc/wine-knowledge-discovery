import argparse
import json
from pathlib import Path


KEYWORDS = (
    "caspailleur",
    "paspailleur",
    "formal",
    "context",
    "concept",
    "stability",
    "implic",
    "subgroup",
    "pattern",
    "cluster",
)


def summarize_notebook(path: Path) -> None:
    nb = json.loads(path.read_text(encoding="utf-8"))
    print(f"\n=== {path} ===")
    cells = nb.get("cells", [])
    print(f"Cells: {len(cells)}")

    for idx, cell in enumerate(cells):
        source = cell.get("source", "")
        src = source if isinstance(source, str) else "".join(source)
        stripped = src.strip()
        first = stripped.splitlines()[0] if stripped else ""
        cell_type = cell.get("cell_type", "")
        if cell_type == "markdown" and first.startswith("#"):
            print(f"{idx:03d} | MD   | {first[:140]}")
            continue
        if cell_type == "code":
            lowered = src.lower()
            if any(k in lowered for k in KEYWORDS):
                short = first[:140] if first else "<empty>"
                print(f"{idx:03d} | CODE | {short}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Print compact notebook outline.")
    parser.add_argument("notebooks", nargs="+", help="Notebook paths")
    args = parser.parse_args()
    for notebook in args.notebooks:
        summarize_notebook(Path(notebook))


if __name__ == "__main__":
    main()
