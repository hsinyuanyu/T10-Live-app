# Validation — 2026-10-20

41 pytest checks passed. Fixtures are explicitly synthetic; UI checks use the full real committed snapshot. Tests and measurements ran on this shared Linux build host with Python 3.11.15. macOS and Windows were not available for native execution; both have documented run commands and a cross-platform dependency lock. No Linux-specific facilities or symlinks are committed.

## Required checks

| Prompt check | Result / evidence |
|---|---|
| 1 | PASS — Actual metadata and headers inspected before preparation. Source-aware fixture checks missing Inference Type gives a diagnostic. |
| 2 | PASS — Priority 0.0002625000 per 1K normalizes exactly to Decimal 0.2625000 per 1M and remains priority. |
| 3 | PASS — hour/TextUnit/1M TPM Hour excluded; bad prices quarantined, exact duplicate counted, raw accounting asserted per source. |
| 4 | PASS — Region and column projection, unique source provenance, empty slice schema, bad regions/columns and missing/hash failures verified. |
| 5 | PASS — Only a complete source-aware standard pair survives incomplete/mode/tier/ambiguous cases; exact model/source/scope boundaries tested. |
| 6 | PASS — $1/$3 per 1M gives $4 monthly, $0.004/request and $4/1K requests; scenarios give $2/$4/$8. |
| 7 | PASS — $3.99 excludes and $4 includes; unrounded boundary, genuine zero usage/prices and 51 rows paginated 50+1 verified. |
| 8 | PASS — Empty UI selection never calls Loader. Workload/budget changes yield one Parquet slice cache miss then two hits. Shared UI state has no stale table after invalid input. |
| 8a | PASS — Distinct eligible regions sorted; duplicate and ineligible rows do not add regions. One discovery query per revision; zero regions shows error without a default. |
| 9 | PASS — Corrupt hashes/revisions/schema/quality and mixed source-file offers fail closed. SAMPLE is conspicuous and cannot display comparisons. |
| 10 | PASS — Full real data prepared and raw pair independently audited. Streamlit UI harness verifies title/banner/controls/table/chart and empty/error states. Actual server health and root HTTP 200 passed (1.132s startup, port 50331, server stopped). |

## Actual sources and accounting

Dataset revision: `25cea5fdf07ef420553666eb8e58b38949adbc48291ae24b6bc1c234af737d0d`. Full sources: 20,341 rows, 9.381 MB; not a sample. 36 eligible-rate regions. 863 eligible US-East rows loaded, yielding 147 complete standard configurations. No cross-source joins.

| Source | Offer / publication | Raw | Clean | Quarantine | Duplicates |
|---|---|---:|---:|---:|---:|
| bedrock_foundation_models.csv | 20261012084008 / 2026-10-12T08:40:08Z | 7026 | 7026 | 0 | 0 |
| bedrock_service_all.csv | 20261016210806 / 2026-10-16T21:08:06Z | 13315 | 13315 | 0 | 0 |

Both downloads differ from the course downloader’s September fingerprints because AWS published newer offers. Source metadata, actual hashes and acquisition timestamps are in the snapshot manifest and provenance.

Status counts: {'retained_noncomparable': 8801, 'comparison_eligible': 11540}. Reason counts overlap; a row can have several flags.

**bedrock_foundation_models.csv exclusion flags:** unrecognized_dimension=4573, unsupported_unit=1431, commitment=1242.

**bedrock_service_all.csv exclusion flags:** unrecognized_dimension=4124, unsupported_unit=835, missing_model=854, commitment=122.

Detected schema variants: Marketplace now also includes explicit Model/Provider/Feature/Inference Type fields, but its documented pipe-delimited PriceDescription and serviceName remain authoritative for normalization. Amazon-billed contains explicit Model, Provider, Region Code, Inference Type, Feature and service_tier. Both have five metadata rows. Raw blank tiers, priority/flex/batch/global-standard tiers, cache dimensions, provisioned units, multiple modalities, and long-context/underscore/Token Count dimensions exist. Unsupported text variants and modalities are deliberately flagged; the shortlist is conservative and does not claim exhaustive purchasing coverage. Full observed column lists and exclusion counts are in quality.json.

## Independent real-pair audit

Model: **Voxtral Mini 1.0**, us-east-1, bedrock_service_all.csv, standard tier. The benchmark independently reads the full raw CSV and its five metadata rows, finds each exact RateCode, verifies Model/Region/Inference Type, normalizes the original unit price with Decimal, checks offer/publication and independently reconstructs the immutable row hashes.

| Direction | Rate code | Original USD / unit | USD / 1M |
|---|---|---|---|
| input | `WS67YY6G4ZQ6H736.JRTCKXETXF.6YS6EN2CT7` | 0.0000400000 / 1K tokens | 0.0400000000 |
| output | `7CBDMBCVMEJYUJB8.JRTCKXETXF.6YS6EN2CT7` | 0.0000400000 / 1K tokens | 0.0400000000 |

This pair costs exactly $0.08/month at the default workload, $0.00008/request, and $0.08/1K requests. Public AWS identifiers and metadata appear in app details; no model performance is inferred.

## Measured performance

| Measurement | Observed |
|---|---|
| Preparation wall time (child including interpreter) | 2.689 s |
| Cold region discovery + bounded load + filter | 0.194 s |
| Warm load/filter median (30 varying workloads/budgets) | 0.124 s |
| Warm load/filter slowest (30 updates) | 0.127 s |
| UI startup in Streamlit AppTest | 0.642 s |
| UI volume change in AppTest | 0.236 s |
| Preparation child sampled peak RSS | 386.4 MB |
| UI/benchmark process sampled peak RSS | 226.4 MB |

RSS was sampled every 20 ms with psutil, not a guaranteed instantaneous maximum. UI startup is in-process harness rendering, distinct from HTTP server readiness; browser paint/network time is not measured. Warm update maximum is under the 3-second preference on this host. Run `uv run python -m scripts.benchmark --raw-dir data/raw` to reproduce measurements; generated measurements.json is ignored. Raw inputs are required only for re-preparation/audit, never normal UI reruns.

## Fresh-clone verification

PASS: cloned the committed repository into a new directory under TMPDIR using `git clone --no-hardlinks`, ran `uv sync --locked --python 3.11` (44 packages installed in 38.01 s), and ran all 41 tests (3.40 s). A fresh server returned health `ok` and HTTP 200 in 0.612 s on free port 41905 and was stopped. Confirmed there was no `data/raw/` or `data/cleaned/` directory and that the committed snapshot alone yields 147 real US-East configurations. No Git symlinks or raw downloads are tracked. This verifies a clean Linux checkout; macOS/Windows execution remains unmeasured.
