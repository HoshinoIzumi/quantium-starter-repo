#!/usr/bin/env python3
"""
Build a single formatted output file from Soul Foods morsel transaction CSVs.

Rules:
1) Keep only rows where product == "pink morsel"
2) Create Sales = quantity * price
3) Keep Date and Region unchanged
4) Output contains exactly 3 fields: Sales, Date, Region
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from typing import List

import pandas as pd


REQUIRED_COLUMNS = {"product", "quantity", "price", "date", "region"}


def find_csv_files(data_dir: str) -> List[str]:
    pattern = os.path.join(data_dir, "*.csv")
    return sorted(glob.glob(pattern))


def load_and_validate_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"CSV '{path}' is missing required columns: {sorted(missing)}. "
            f"Found columns: {list(df.columns)}"
        )

    # Clean & convert numeric fields
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

    # price values look like "$3.00" -> remove $ and commas before converting
    df["price"] = (
        df["price"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # normalize product text a bit (helps avoid hidden whitespace issues)
    df["product"] = df["product"].astype(str).str.strip()

    return df


def build_output(data_dir: str) -> pd.DataFrame:
    files = find_csv_files(data_dir)
    if not files:
        raise FileNotFoundError(f"No CSV files found in '{data_dir}'.")

    df = pd.concat([load_and_validate_csv(f) for f in files], ignore_index=True)

    # Filter product (dataset uses lowercase "pink morsel")
    df = df[df["product"] == "pink morsel"].copy()

    # Drop rows with invalid numerics before sales calc
    df = df.dropna(subset=["quantity", "price"])

    # Compute Sales
    df["Sales"] = df["quantity"] * df["price"]

    # Output fields
    out = df[["Sales", "date", "region"]].copy()
    out.columns = ["Sales", "Date", "Region"]

    # Keep date as-is per instructions (optional normalization disabled)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Combine Soul Foods CSVs into a single formatted output file (Sales, Date, Region)."
    )
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--output", default="output.csv")
    args = parser.parse_args()

    try:
        out = build_output(args.data_dir)
        out.to_csv(args.output, index=False)
        print(f"✅ Wrote {len(out):,} rows to '{args.output}'")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
