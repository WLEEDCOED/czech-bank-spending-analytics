"""Download the Berka / PKDD'99 financial dataset, clean it, and save a
deterministic sample (seed 42, 100k rows) to data/bank_transactions.csv.

Source: PKDD'99 Discovery Challenge, prepared by Petr Berka.
Internet Archive copy of the original distribution:
https://web.archive.org/web/20070214120527/http://lisp.vse.cz/pkdd99/DATA/data_berka.zip
"""
import os
import urllib.request
import zipfile
import tempfile

import numpy as np
import pandas as pd

URL = "https://web.archive.org/web/20070214120527/http://lisp.vse.cz/pkdd99/DATA/data_berka.zip"
SEED = 42
N_SAMPLE = 100_000
CHUNK = 100_000

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUT_CSV = os.path.join(TARGET, "bank_transactions.csv")


def download_extract(dest_dir: str) -> str:
    """Download the zip and extract it. Returns path to the extracted dir."""
    os.makedirs(dest_dir, exist_ok=True)
    zip_path = os.path.join(dest_dir, "data_berka.zip")
    print(f"Downloading {URL} ...")
    urllib.request.urlretrieve(URL, zip_path)
    print(f"Extracting {zip_path} ...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(dest_dir)
    os.remove(zip_path)
    return dest_dir


def clean_and_sample(src_path: str, out_path: str) -> None:
    """Read trans.asc in chunks, apply basic cleaning, deterministically
    sample N_SAMPLE rows (seed 42) and write to CSV."""
    chunks = []
    n_read = 0
    for chunk in pd.read_csv(src_path, sep=";", header=0, chunksize=CHUNK):
        chunk = chunk.rename(columns={c: c.strip('"') for c in chunk.columns})
        # parse date YYMMDD -> datetime; drop rows we cannot parse
        chunk["date"] = pd.to_datetime(
            chunk["date"].astype(str).str.strip('"'), format="%y%m%d", errors="coerce"
        )
        # drop rows with missing/non-positive amount
        n_read += len(chunk)
        chunk = chunk[chunk["amount"].fillna(0) > 0]
        chunk = chunk[chunk["date"].notna()]
        chunks.append(chunk)

    df = pd.concat(chunks, ignore_index=True)
    print(f"Rows read: {n_read:,} | rows after cleaning: {len(df):,}")

    rng = np.random.default_rng(SEED)
    n = min(N_SAMPLE, len(df))
    idx = rng.choice(len(df), size=n, replace=False)
    sample = df.iloc[np.sort(idx)].reset_index(drop=True)

    for c in ("type", "operation", "k_symbol", "bank", "account"):
        if c in sample.columns:
            sample[c] = sample[c].astype(str).str.strip('"').replace('""', "", regex=False)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sample.to_csv(out_path, index=False)
    print(f"Wrote {len(sample):,} rows x {len(sample.columns)} cols -> {out_path}")


def main() -> None:
    tmp = tempfile.mkdtemp(prefix="berka_")
    extracted = download_extract(tmp)
    src = None
    for root, _dirs, files in os.walk(extracted):
        if "trans.asc" in files:
            src = os.path.join(root, "trans.asc")
            break
    if src is None:
        raise FileNotFoundError("trans.asc not found in the downloaded archive")
    clean_and_sample(src, OUT_CSV)


if __name__ == "__main__":
    main()
