# 03 - Loader and Data Access

## Purpose

Load the validated AWS pricing relations defined in `02-data.md` and supply bounded, reproducible DataFrames to the filters and views. Support both EC2 and Bedrock without mixing their schemas or pricing units. This is a component specification for Handout 8, not an implemented loader.

## Design and responsibilities

- Prepare and validate data ahead of time; load only the requested service, source versions, regions and columns at startup or when setup changes. Large EC2 files must not be reread on each click.
- Use DuckDB to select rows and columns from prepared Parquet, then return the selected rows as pandas DataFrames. Parquet supports column selection and preserves typed fields; pandas supports the downstream in-memory filters and view calculations.
- Keep file access in this component. Filters and views receive data rather than opening files themselves.
- Preserve decimal prices, source identifiers, quality status and provenance. Do not download, clean, normalize prices again, rank products or draw UI controls here.

## Input and handoff contract

Consume the five logical outputs of `02-data.md`: `ec2_prices_clean`, `bedrock_prices_clean`, `source_provenance`, `data_quality_report`, and `quarantine_records`. The Data component owns their generation and validation. A clean output row represents one source price record after exact-duplicate handling, not one unique instance or model.

Proposed physical handoff for team agreement: prepared price relations and quarantine records as Parquet under `data/cleaned/`; provenance and quality reports as JSON. Keep raw CSVs untouched under `data/`. `02-data.md` currently leaves storage unresolved, so confirm this mapping with its owner before implementation and reconcile it during 8.7. Store the mapping in one loader configuration; no downstream component may hard-code paths.

The prepared-data manifest must identify the paths, dataset revision, schema revision, sample/full designation, per-source offer versions, transformation version and prepared-file hashes. Treat it as the explicit selected baseline; never fetch the mutable AWS `current` URLs during loading. Publish a completed manifest only after all referenced outputs are complete.

## Public interface

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import pandas as pd

@dataclass(frozen=True)
class LoadRequest:
    service: Literal["ec2", "bedrock"]
    regions: tuple[str, ...]  # empty means all available in selected service
    columns: tuple[str, ...]
    purpose: Literal["comparison", "inspection"] = "comparison"

@dataclass
class LoadedSlice:
    rows: pd.DataFrame
    provenance: pd.DataFrame
    quality_summary: dict
    dataset_revision: str
    is_sample: bool

def load_slice(manifest_path: Path, request: LoadRequest) -> LoadedSlice: ...
```

The manifest selects the source versions; the request selects the service, regions and columns. Return exactly the requested columns plus mandatory traceability fields: `source_file`, `offer_version`, `publication_date`, `record_status`, `flag_reason`, and the agreed stable source-row identifier. Include applicable provenance records and quality counts separately from price rows. Do not join provenance in a way that multiplies rows.

## Selection and correctness rules

| Rule | Required behavior |
|---|---|
| Service | Query the EC2 or Bedrock relation separately; do not concatenate unrelated schemas. |
| Region | EC2 uses `region_code`; Bedrock uses `region_normalized`. Preserve the stored labels; no inferred region fallback. |
| Comparison | Include only `record_status == "comparison_eligible"`. This denotes data eligibility, not a final stakeholder recommendation. |
| Inspection | Allow retained noncomparable records with their status and reasons. Quarantine remains a separate diagnostic relation. |
| Identifiers | Preserve every selected rate record; never deduplicate by SKU, instance type or model name. |
| Prices | Preserve decimal values and nulls exactly. Never cast prices to binary floats, fill missing prices with zero, or repeat token-unit conversion. |
| EC2 Reserved | Preserve upfront and hourly components. Do not apply an hourly-unit-only filter before downstream pairing; request all fields and components needed for the selected term. |
| Bedrock | Preserve source type, model/version context, token direction, pricing mode, cache status, commitment context and raw service tier when needed. Do not merge tiers or infer cross-source model equivalence. |
| Samples | Permit sample data for development/inspection only; reject sample EC2 data for final comparisons and effective Reserved rates. |

Validate requested columns against the selected relation before querying. Use parameterized values and schema-validated column identifiers. Apply stakeholder-specific constraints and cost calculations in downstream components, using the definitions agreed by the team.

## Runtime, caching and errors

1. At startup, validate the manifest, required schema, quality report and referenced files for the requested service. Verify source revisions and hashes once per activated dataset revision. Refuse a baseline with failed required validation checks.
2. Query only needed columns and rows. Before materializing a large selection, estimate its result size and enforce a configurable memory budget; if exceeded, ask the setup layer to narrow it rather than attempting an unbounded load. Determine the budget using a measured laptop run before final submission.
3. Cache a small bounded number of slices keyed by dataset/schema revisions, file fingerprints and the canonical request. Region order must not create duplicate cache entries. Do not hash a whole DataFrame on each click.
4. Sidebar changes and chart clicks operate on the loaded slice in memory. A setup change that requires rows or columns outside it creates another load request.
5. An explicit dataset refresh validates a new manifest and invalidates affected cached results; it never combines old and new outputs silently. Downstream code must not mutate cached frames.
6. A valid query matching no rows returns an empty DataFrame with the correct schema. Missing/corrupt files, missing fields, invalid requests and failed quality checks raise actionable errors naming the affected input. Never silently substitute samples or another version.

## Build order and done-when checks

First agree on the physical handoff and stable row identifiers with Data; implement validation and one-service loading on tiny fixtures; add the second service, cache behavior and a measured full-data run.

| Check | Expected result |
|---|---|
| Tiny EC2 fixture: eligible US-East hourly and upfront rows, an eligible Ireland row, and a noncomparable US-East row | A US-East comparison request returns both eligible US-East components only. |
| Tiny Bedrock fixture: an eligible input rate of decimal 0.2625000 per 1M tokens and a non-token hourly record | Comparison returns the token rate unchanged; inspection retains the hourly record with its noncomparable status. |
| Independent full-data reconciliation | Per-source selected row counts and decimal rate sums grouped by unit match a separate direct query under identical predicates. Never sum across incompatible units. |
| Provenance | Each returned source/version has exactly one matching provenance record; row counts are unchanged by provenance lookup. |
| Empty selection and broken input | Empty matches preserve schema; missing file/column and failed validation produce distinct errors. |
| Cache lifecycle | Repeated request and sidebar-only interaction perform no additional data read; a new activated revision forces revalidation and a fresh result. |
| Sample safeguard | Sample EC2 cannot produce final comparison results; development outputs identify themselves as samples. |
| Real size | Record selected rows, load time, repeat-request time and peak memory on the target laptop; confirm selections stay within the configured budget. |

## Team decisions to settle before combining

Confirm the physical paths/formats, manifest and quality-report schema, stable source-row identifiers, EC2 eligibility/baseline flag name, initial load range, required columns and measured memory budget. Reserved pairing and amortization, workload assumptions, cross-source model matching and final rankings belong to the relevant downstream specification; they must be agreed before those features are enabled.

## Local use and later deployment

Resolve local paths relative to the repository, not a teammate-specific absolute path. A later cloud deployment can replace the path configuration with object-storage locations while keeping the DataFrame contract; dataset revisions, memory limits and per-session selections still apply.

## References

- `02-data.md`: authoritative cleaning, normalization, quality-status and logical handoff definitions.
- `objectives.md` and `technical.md`: AWS project decisions and limitations.
- Handout 8.4-8.6: independent pieces, explicit contracts, real-size operation and component checks.
