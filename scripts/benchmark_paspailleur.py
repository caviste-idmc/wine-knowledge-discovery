from pathlib import Path
import time

from run_symbolic_kd_analysis import build_wine_dataframe, build_xwine_dataframe, run_paspailleur


def bench(name: str, builder, dataset_key: str, sizes: list[int]) -> None:
    df = builder(Path(name)).reset_index(drop=True)
    df.index = [f"{dataset_key}_{i:04d}" for i in range(len(df))]
    for n in sizes:
        sample = df.head(min(n, len(df)))
        t0 = time.time()
        result = run_paspailleur(sample, dataset_key)
        dt = time.time() - t0
        print(
            f"{dataset_key} n={len(sample)} shape={result['pattern_shape']} "
            f"concepts={len(result['pattern_concepts'])} implications={len(result['pattern_implications'])} "
            f"seconds={dt:.2f}"
        )


if __name__ == "__main__":
    bench("data_preprocessed/WineDataset_enriched.csv", build_wine_dataframe, "wine", [80, 120, 180])
    bench("data_preprocessed/XWines_Test_100_wines_enriched.csv", build_xwine_dataframe, "xwine", [80, 100])
