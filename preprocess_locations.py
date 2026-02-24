"""
Preprocess all wine datasets for location-level joins and harvest enrichment.

What this script does:
1) Standardizes region and country names across GHD, WineDataset, and XWines.
2) Aggregates duplicate GHD regions (example: Champagne 1 + Champagne 2 -> Champagne).
   - Coordinates are averaged.
   - Harvest values are summed by year.
3) Finds the global oldest vintage in WineDataset + XWines.
4) Computes average harvest per region from start_year..2007.
5) Adds harvest columns to WineDataset and XWines (without overwriting originals).
"""

from __future__ import annotations

import ast
import csv
import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
OUT_DIR = ROOT_DIR / "data_preprocessed"
HARVEST_END_YEAR = 2007


# Conservative aliases only for clearly equivalent names.
COUNTRY_ALIASES = {
    "usa": "United States",
    "us": "United States",
    "u.s.a.": "United States",
    "u.s.": "United States",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
}


# Region aliases to improve matching while staying on region-level.
REGION_ALIASES = {
    "bourgogne": "Burgundy",
    "burgundy": "Burgundy",
    "champagne": "Champagne",
    "champagne 1": "Champagne",
    "champagne 2": "Champagne",
    "northern rhone valley": "Northern Rhone Valley",
    "northern rhône valley": "Northern Rhone Valley",
    "southern rhone valley": "Southern Rhone Valley",
    "southern rhône valley": "Southern Rhone Valley",
    "ile de france": "Ile de France",
    "ile-de-france": "Ile de France",
}


# Countries for GHD regional composites.
GHD_REGION_COUNTRY = {
    "Alsace": "France",
    "Auvergne": "France",
    "Auxerre-Avalon": "France",
    "Beaujolais and Maconnais": "France",
    "Bordeaux": "France",
    "Burgundy": "France",
    "Champagne": "France",
    "Gaillac- South-West": "France",
    "Germany": "Germany",
    "High Loire Valley": "France",
    "Ile de France": "France",
    "Jura": "France",
    "Languedoc": "France",
    "Low Loire Valley": "France",
    "Luxembourg": "Luxembourg",
    "Maritime alps": "France",
    "Northern Italy": "Italy",
    "Northern Lorraine": "France",
    "Northern Rhone Valley": "France",
    "Savoie": "France",
    "Spain": "Spain",
    "Southern Lorraine": "France",
    "Southern Rhone Valley": "France",
    "Switzerland (Leman Lake)": "Switzerland",
    "Various South-East": "France",
    "Vendée - Poitou Charente": "France",
}


def normalize_space(value: str) -> str:
    """Collapse repeated whitespace."""
    return re.sub(r"\s+", " ", value or "").strip()


def strip_accents(text: str) -> str:
    """Remove accents for robust key comparisons."""
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def normalize_key(text: str) -> str:
    """Lowercase key with accents and punctuation removed."""
    text = strip_accents(normalize_space(text)).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return normalize_space(text)


def standardize_country(country: str) -> str:
    """Standardize countries while preserving unknown values."""
    text = normalize_space(country)
    if not text:
        return ""
    return COUNTRY_ALIASES.get(text.lower(), text)


def standardize_region(region: str) -> str:
    """Standardize region names with conservative aliasing."""
    text = normalize_space(region)
    if not text:
        return ""
    alias_key = normalize_key(text)
    return REGION_ALIASES.get(alias_key, text)


def location_key(country: str, region: str) -> str:
    """Join key for matching across datasets."""
    return f"{normalize_key(country)}|{normalize_key(region)}"


def parse_decimal(value: str) -> Optional[float]:
    """Parse decimal values that may use comma separators."""
    text = normalize_space(value)
    if not text:
        return None
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return None


def parse_wine_vintage(value: str) -> Optional[int]:
    """
    Parse the first 4-digit year from WineDataset vintage field.
    Examples: NV -> None, 2022 -> 2022, 2020/21 -> 2020.
    """
    if not value:
        return None
    match = re.search(r"(19\d{2}|20\d{2})", value)
    return int(match.group(1)) if match else None


def parse_xwine_vintages(value: str) -> List[int]:
    """Parse the integer years from XWines Vintages list."""
    if not value:
        return []
    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return []
    years: List[int] = []
    if not isinstance(parsed, list):
        return years
    for item in parsed:
        if isinstance(item, int):
            years.append(item)
        elif isinstance(item, str):
            match = re.fullmatch(r"(19\d{2}|20\d{2})", item.strip())
            if match:
                years.append(int(match.group(1)))
    return years


def read_csv(path: Path, delimiter: str = ",") -> Tuple[List[str], List[Dict[str, str]]]:
    """Read CSV as header + list of dict rows."""
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)
        fields = list(reader.fieldnames or [])
    return fields, rows


def write_csv(path: Path, fieldnames: List[str], rows: List[Dict[str, str]], delimiter: str = ",") -> None:
    """Write rows to CSV with controlled column order."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def load_ghd_data() -> Tuple[Dict[str, Dict[int, float]], Dict[str, str]]:
    """
    Read GHD harvest table and aggregate region aliases.
    Returns:
      - harvest_by_region[region_std][year] = summed harvest
      - original_to_std mapping for source headers
    """
    input_path = DATA_DIR / "europe2012ghd(GHD Data).csv"

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        matrix = list(csv.reader(f, delimiter=";"))

    if len(matrix) < 2:
        raise ValueError("GHD data file must contain header and data rows.")

    header = matrix[0]
    source_regions = header[1:]  # Skip 'year'
    source_to_std: Dict[str, str] = {}
    for source_region in source_regions:
        source_to_std[source_region] = standardize_region(source_region)

    harvest_by_region: Dict[str, Dict[int, float]] = {}
    for row in matrix[1:]:
        if not row:
            continue
        try:
            year = int(normalize_space(row[0]))
        except ValueError:
            # Skip abbreviation row "Abb." and any malformed rows.
            continue
        for idx, source_region in enumerate(source_regions, start=1):
            value = parse_decimal(row[idx]) if idx < len(row) else None
            if value is None:
                continue
            region_std = source_to_std[source_region]
            harvest_by_region.setdefault(region_std, {})
            harvest_by_region[region_std][year] = harvest_by_region[region_std].get(year, 0.0) + value
    return harvest_by_region, source_to_std


def preprocess_ghd_locations(
    harvest_by_region: Dict[str, Dict[int, float]],
    source_to_std: Dict[str, str],
    start_year: int,
) -> Dict[str, float]:
    """
    Standardize and aggregate GHD locations.
    For merged regions (e.g. Champagne 1/2), coordinates are averaged.
    Adds average harvest between start_year and HARVEST_END_YEAR.
    """
    fields, rows = read_csv(DATA_DIR / "europe2012ghd(Locations).csv", delimiter=";")

    # Collect coordinates per standardized region.
    coord_bucket: Dict[str, List[Tuple[float, float]]] = {}
    for row in rows:
        source_region = normalize_space(row.get("Location", ""))
        region_std = source_to_std.get(source_region, standardize_region(source_region))

        lat = parse_decimal(row.get("Latitude", ""))
        lon = parse_decimal(row.get("Longitude", ""))
        if lat is not None and lon is not None:
            coord_bucket.setdefault(region_std, []).append((lat, lon))

    output_rows: List[Dict[str, str]] = []
    average_harvest_by_region: Dict[str, float] = {}

    for region_std in sorted(coord_bucket.keys()):
        coords = coord_bucket[region_std]
        avg_lat = sum(x for x, _ in coords) / len(coords)
        avg_lon = sum(y for _, y in coords) / len(coords)

        country_std = GHD_REGION_COUNTRY.get(region_std, "")
        years = harvest_by_region.get(region_std, {})
        in_range_values = [
            years[y] for y in sorted(years.keys()) if start_year <= y <= HARVEST_END_YEAR
        ]
        avg_harvest = sum(in_range_values) / len(in_range_values) if in_range_values else None
        if avg_harvest is not None:
            average_harvest_by_region[region_std] = avg_harvest

        output_rows.append(
            {
                "Location": region_std,
                "Latitude": f"{avg_lat:.5f}",
                "Longitude": f"{avg_lon:.5f}",
                "country_std": country_std,
                "region_std": region_std,
                "location_key": location_key(country_std, region_std),
                "avg_harvest_start_to_2007": f"{avg_harvest:.4f}" if avg_harvest is not None else "",
            }
        )

    out_fields = fields + ["country_std", "region_std", "location_key", "avg_harvest_start_to_2007"]
    write_csv(OUT_DIR / "europe2012ghd_locations_standardized.csv", out_fields, output_rows, delimiter=";")
    return average_harvest_by_region


def preprocess_ghd_data(harvest_by_region: Dict[str, Dict[int, float]]) -> None:
    """Write an aggregated GHD harvest table by standardized region."""
    all_years: List[int] = sorted({year for years in harvest_by_region.values() for year in years.keys()})
    regions: List[str] = sorted(harvest_by_region.keys())

    rows: List[Dict[str, str]] = []
    for year in all_years:
        row: Dict[str, str] = {"year": str(year)}
        for region in regions:
            value = harvest_by_region[region].get(year)
            row[region] = f"{value:.4f}" if value is not None else ""
        rows.append(row)

    write_csv(
        OUT_DIR / "europe2012ghd_data_standardized.csv",
        ["year"] + regions,
        rows,
        delimiter=";",
    )


def oldest_vintage_from_wine_dataset(rows: Iterable[Dict[str, str]]) -> Optional[int]:
    """Get oldest available numeric vintage from WineDataset."""
    years = [parse_wine_vintage(row.get("Vintage", "")) for row in rows]
    years = [year for year in years if year is not None]
    return min(years) if years else None


def oldest_vintage_from_xwines(rows: Iterable[Dict[str, str]]) -> Optional[int]:
    """Get oldest available numeric vintage from XWines."""
    candidates: List[int] = []
    for row in rows:
        candidates.extend(parse_xwine_vintages(row.get("Vintages", "")))
    return min(candidates) if candidates else None


def harvest_for_region_year(
    harvest_by_region: Dict[str, Dict[int, float]],
    region_std: str,
    year: int,
) -> Optional[float]:
    """Lookup harvested value for a standardized region and year."""
    return harvest_by_region.get(region_std, {}).get(year)


def enrich_wine_dataset(
    harvest_by_region: Dict[str, Dict[int, float]],
    avg_harvest_by_region: Dict[str, float],
) -> None:
    """Add standardized location and harvest columns to WineDataset."""
    fields, rows = read_csv(DATA_DIR / "WineDataset.csv")
    out_rows: List[Dict[str, str]] = []

    for row in rows:
        country_std = standardize_country(row.get("Country", ""))
        region_std = standardize_region(row.get("Region", ""))
        loc_key = location_key(country_std, region_std)

        vintage_year = parse_wine_vintage(row.get("Vintage", ""))
        harvest_value = None
        if vintage_year is not None and region_std:
            harvest_value = harvest_for_region_year(harvest_by_region, region_std, vintage_year)
        avg_harvest = avg_harvest_by_region.get(region_std)

        row["country_std"] = country_std
        row["region_std"] = region_std
        row["location_key"] = loc_key
        row["harvest_for_vintage"] = f"{harvest_value:.4f}" if harvest_value is not None else ""
        row["avg_harvest_start_to_2007"] = f"{avg_harvest:.4f}" if avg_harvest is not None else ""
        out_rows.append(row)

    out_fields = fields + [
        "country_std",
        "region_std",
        "location_key",
        "harvest_for_vintage",
        "avg_harvest_start_to_2007",
    ]
    write_csv(OUT_DIR / "WineDataset_enriched.csv", out_fields, out_rows)


def enrich_xwines_file(
    input_filename: str,
    output_filename: str,
    harvest_by_region: Dict[str, Dict[int, float]],
    avg_harvest_by_region: Dict[str, float],
) -> None:
    """Add standardized location and harvest columns to an XWines file."""
    fields, rows = read_csv(DATA_DIR / input_filename)
    out_rows: List[Dict[str, str]] = []

    for row in rows:
        country_std = standardize_country(row.get("Country", ""))
        region_std = standardize_region(row.get("RegionName", ""))
        loc_key = location_key(country_std, region_std)

        vintages = parse_xwine_vintages(row.get("Vintages", ""))
        harvest_values: List[str] = []
        for year in vintages:
            harvest_value = harvest_for_region_year(harvest_by_region, region_std, year)
            harvest_values.append(f"{harvest_value:.4f}" if harvest_value is not None else "")

        avg_harvest = avg_harvest_by_region.get(region_std)

        row["country_std"] = country_std
        row["region_std"] = region_std
        row["location_key"] = loc_key
        row["harvest_for_vintages"] = json.dumps(harvest_values, ensure_ascii=True)
        row["avg_harvest_start_to_2007"] = f"{avg_harvest:.4f}" if avg_harvest is not None else ""
        out_rows.append(row)

    out_fields = fields + [
        "country_std",
        "region_std",
        "location_key",
        "harvest_for_vintages",
        "avg_harvest_start_to_2007",
    ]
    write_csv(OUT_DIR / output_filename, out_fields, out_rows)


def main() -> None:
    """Run full preprocessing pipeline and write all outputs to data_preprocessed."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    wine_fields, wine_rows = read_csv(DATA_DIR / "WineDataset.csv")
    del wine_fields
    xw_fields, xw_rows = read_csv(DATA_DIR / "XWines_Slim_1K_wines.csv")
    del xw_fields

    oldest_wine = oldest_vintage_from_wine_dataset(wine_rows)
    oldest_xwine = oldest_vintage_from_xwines(xw_rows)
    available_oldest = [year for year in [oldest_wine, oldest_xwine] if year is not None]
    if not available_oldest:
        raise ValueError("No numeric vintage year found in WineDataset and XWines.")
    start_year = min(available_oldest)

    harvest_by_region, source_to_std = load_ghd_data()
    avg_harvest_by_region = preprocess_ghd_locations(harvest_by_region, source_to_std, start_year=start_year)
    preprocess_ghd_data(harvest_by_region)

    enrich_wine_dataset(harvest_by_region, avg_harvest_by_region)
    enrich_xwines_file(
        "XWines_Slim_1K_wines.csv",
        "XWines_Slim_1K_wines_enriched.csv",
        harvest_by_region,
        avg_harvest_by_region,
    )
    enrich_xwines_file(
        "XWines_Test_100_wines.csv",
        "XWines_Test_100_wines_enriched.csv",
        harvest_by_region,
        avg_harvest_by_region,
    )

    print(f"Done. Start year used for averages: {start_year}.")
    print(f"Output folder: {OUT_DIR}")


if __name__ == "__main__":
    main()
