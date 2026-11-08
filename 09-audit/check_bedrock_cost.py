#!/usr/bin/env python3
"""Recompute Gemma 3 4B monthly cost directly from the AWS Bedrock CSV."""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from pathlib import Path


def default_source() -> Path:
    candidates = (
        Path.home() / "Desktop/dso576/dataset_aws-price-list/data/bedrock_service_all.csv",
        Path(__file__).resolve().parent.parent / "data/bedrock_service_all.csv",
        Path(__file__).resolve().parent.parent / "sample/bedrock_service_all_sample.csv",
        Path.home() / "dso576-project-T10/sample/bedrock_service_all_sample.csv",
    )
    return next((p for p in candidates if p.is_file()), candidates[-1])


def rows_after_metadata(source: Path):
    """Yield rows after five AWS metadata lines, or read a header-first sample."""
    with source.open(newline="", encoding="utf-8") as f:
        first = f.readline()
        f.seek(0)
        if first.startswith('"FormatVersion"') or first.startswith("FormatVersion,"):
            for _ in range(5):
                next(f)
        yield from csv.DictReader(f)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=str(default_source()),
        help="Path to the raw bedrock_service_all.csv or its supplied sample",
    )
    args = parser.parse_args()
    source = Path(args.csv_path)
    selected: dict[str, list[dict[str, str]]] = {"input": [], "output": []}

    for row in rows_after_metadata(source):
        if (
            (row.get("Model") or "").strip() != "Gemma 3 4B"
            or (row.get("Region Code") or "").strip() != "us-east-1"
            or (row.get("service_tier") or "").strip().lower() != "standard"
            or (row.get("TermType") or "").strip() != "OnDemand"
            or (row.get("Unit") or "").strip() != "1K tokens"
        ):
            continue
        direction = (row.get("Inference Type") or "").strip().lower()
        kind = "input" if direction == "input tokens" else "output" if direction == "output tokens" else None
        if kind:
            selected[kind].append(row)

    for kind, matches in selected.items():
        if len(matches) != 1:
            raise SystemExit(f"Expected exactly one {kind} rate, found {len(matches)} in {source}")

    input_row, output_row = selected["input"][0], selected["output"][0]
    input_rate = Decimal(input_row["PricePerUnit"])
    output_rate = Decimal(output_row["PricePerUnit"])
    requests_per_month = 1_000
    input_tokens = 1_000 * requests_per_month
    output_tokens = 1_000 * requests_per_month
    input_cost = input_rate * Decimal(input_tokens) / Decimal(1_000)
    output_cost = output_rate * Decimal(output_tokens) / Decimal(1_000)
    total = input_cost + output_cost

    print(f"Source: {source.resolve()}")
    print("Configuration: Google Gemma 3 4B, us-east-1, standard, OnDemand")
    print(f"Input row:  SKU={input_row['SKU']} RateCode={input_row['RateCode']} ${input_rate}/1K tokens")
    print(f"Output row: SKU={output_row['SKU']} RateCode={output_row['RateCode']} ${output_rate}/1K tokens")
    print(f"Workload: {input_tokens:,} input + {output_tokens:,} output tokens/month")
    print(f"Input charge:  ${input_cost}")
    print(f"Output charge: ${output_cost}")
    print(f"Total:         ${total} (displayed to cents: ${total.quantize(Decimal('0.01'))})")


if __name__ == "__main__":
    main()
