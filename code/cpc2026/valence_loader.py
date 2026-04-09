"""Download and merge Warriner et al. (2013) valence norms onto SWOW-EN nodes."""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile
import urllib.request
import zipfile

import pandas as pd

from common import (
    CPC_RESULTS_DIR,
    DEFAULT_SEED,
    SWOW_VALENCE_CSV,
    VALENCE_COVERAGE_JSON,
    ensure_directory,
    load_swow_en_graph,
    normalize_token,
    save_json,
    seed_everything,
)


WARRINER_ZIP_URL = (
    "https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-012-0314-x/"
    "MediaObjects/13428_2012_314_MOESM1_ESM.zip"
)
WARRINER_CSV_FALLBACK_URL = "https://crr.ugent.be/papers/Ratings_Warriner_et_al.csv"


def download_url(url: str, destination: Path) -> Path:
    """Download a remote file to a local destination."""

    ensure_directory(destination.parent)
    with urllib.request.urlopen(url, timeout=60) as response:
        destination.write_bytes(response.read())
    return destination


def resolve_warriner_csv(work_dir: Path) -> Path:
    """Fetch the Warriner table, preferring the original supplementary ZIP."""

    zip_path = work_dir / "warriner_2013.zip"
    csv_path = work_dir / "Ratings_Warriner_et_al.csv"

    try:
        download_url(WARRINER_ZIP_URL, zip_path)
        with zipfile.ZipFile(zip_path) as archive:
            csv_candidates = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csv_candidates:
                raise FileNotFoundError("No CSV found inside the Warriner supplementary ZIP.")
            csv_name = sorted(csv_candidates)[0]
            archive.extract(csv_name, path=work_dir)
            extracted = work_dir / csv_name
            extracted.replace(csv_path)
            return csv_path
    except Exception:
        download_url(WARRINER_CSV_FALLBACK_URL, csv_path)
        return csv_path


def build_valence_table(output_path: Path = SWOW_VALENCE_CSV) -> pd.DataFrame:
    """Merge Warriner valence norms onto the validated SWOW-EN node set."""

    graph = load_swow_en_graph()
    swow_nodes = pd.DataFrame({"node": sorted(graph.nodes())})
    swow_nodes["match_key"] = swow_nodes["node"].map(normalize_token)

    with tempfile.TemporaryDirectory(prefix="warriner_2013_") as temp_dir:
        csv_path = resolve_warriner_csv(Path(temp_dir))
        warriner = pd.read_csv(csv_path)

    expected_columns = {"Word", "V.Mean.Sum", "A.Mean.Sum", "D.Mean.Sum"}
    missing = expected_columns.difference(warriner.columns)
    if missing:
        raise ValueError(f"Warriner table is missing expected columns: {sorted(missing)}")

    warriner = warriner.rename(
        columns={
            "Word": "word",
            "V.Mean.Sum": "valence_raw",
            "A.Mean.Sum": "arousal_raw",
            "D.Mean.Sum": "dominance_raw",
        }
    )
    warriner["match_key"] = warriner["word"].map(normalize_token)
    warriner = (
        warriner.loc[warriner["match_key"] != ""]
        .sort_values("valence_raw", ascending=False)
        .drop_duplicates("match_key")
        .loc[:, ["match_key", "word", "valence_raw", "arousal_raw", "dominance_raw"]]
    )

    merged = swow_nodes.merge(warriner, on="match_key", how="left")
    merged["matched_warriner"] = merged["valence_raw"].notna()
    merged["valence_raw"] = merged["valence_raw"].fillna(5.0).astype(float)
    merged["arousal_raw"] = merged["arousal_raw"].fillna(5.0).astype(float)
    merged["dominance_raw"] = merged["dominance_raw"].fillna(5.0).astype(float)
    merged["valence_centered"] = ((merged["valence_raw"] - 5.0) / 4.0).clip(-1.0, 1.0)

    coverage = float(merged["matched_warriner"].mean())
    coverage_payload = {
        "seed": DEFAULT_SEED,
        "n_nodes": int(len(merged)),
        "matched_nodes": int(merged["matched_warriner"].sum()),
        "coverage_fraction": coverage,
        "coverage_percent": 100.0 * coverage,
        "neutral_fill_value": 0.0,
        "sources": {
            "primary": WARRINER_ZIP_URL,
            "fallback": WARRINER_CSV_FALLBACK_URL,
        },
    }

    ensure_directory(output_path.parent)
    merged.loc[
        :,
        [
            "node",
            "word",
            "matched_warriner",
            "valence_raw",
            "valence_centered",
            "arousal_raw",
            "dominance_raw",
        ],
    ].to_csv(output_path, index=False)
    save_json(VALENCE_COVERAGE_JSON, coverage_payload)
    return merged


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=SWOW_VALENCE_CSV, help="Output CSV path.")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run a minimal download-and-merge smoke test and print a short summary.",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for valence download and merge."""

    seed_everything(DEFAULT_SEED)
    args = parse_args()
    merged = build_valence_table(output_path=args.output)
    if args.smoke_test:
        print(
            merged.loc[:, ["node", "matched_warriner", "valence_centered"]]
            .head(5)
            .to_string(index=False)
        )
        return

    print(
        f"Saved {len(merged)} SWOW-EN valence rows to {args.output} "
        f"(coverage={merged['matched_warriner'].mean():.1%})."
    )


if __name__ == "__main__":
    main()
