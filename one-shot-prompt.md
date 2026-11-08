# Team T10 — One-Shot Product Build Prompt

**Product:** AWS Bedrock Model Cost Comparison Tool  
**Team repository:** https://github.com/mumaniu3/dso576-project-T10  
**Dataset repository:** https://github.com/USC-DSO-576-PS/dataset_aws-price-list

## Agent mandate and product vision

Build a **locally runnable, testable Streamlit application** from this prompt, the course dataset repository, and the public internet alone. The target user is an **AI product manager** selecting a production Amazon Bedrock model and AWS region for a known request workload. Give the user a reproducible shortlist of *like-for-like public list-price* configurations, not a claim about model quality or an actual AWS invoice.

The user sets region(s), typical input/output tokens per request, monthly request volume, and an optional maximum workload cost. The app shows comparable model–region prices, the eligible count and cost-ranked table, and a sensitivity chart across monthly request volumes. Its advantage over consulting AWS CSVs manually is source-aware normalization, unambiguous comparisons, consistent cost calculations, and visible price-version assumptions.

**Use cases (every feature must support one):**

1. **Shortlist:** choose `us-east-1`, 1,000 input and 1,000 output tokens per request, 1,000 requests/month → see standard, uncached, unambiguous model–region configurations ranked by monthly cost → select candidates for quality/latency testing.
2. **Constrain:** enter a maximum estimated workload budget → see only qualifying configurations and a matching count, with an explanation if none qualify → narrow the shortlist without assuming missing rates are zero.
3. **Stress-test:** compare 500, 1,000, and 2,000 requests/month → see monthly-cost lines for the current shortlist, holding tokens/request fixed → judge whether cost rankings remain acceptable as usage changes.

**Scope decision:** **Bedrock only in the user-facing MVP.** The course repository also contains EC2, and the team drafted general-purpose EC2 data/loader/filter designs. Do not build an EC2 screen, Reserved Instance recommender, ten-year catalog-drift engine, or a second FinOps product for this deliverable. Reusable ingestion/loader code may be service-extensible, but the Bedrock workflow is the only release requirement. Similarly, do not present model quality, output speed, or latency as known unless independently joined, source-dated evidence is available; for this MVP display `Not available`, not a fake value. No purchasing, authentication, customer bills, AWS credentials, predictive model, or cloud deployment is required.

## Design principles and component map (big picture before details)

1. **One decision and one state:** a shared set of selected inputs drives both views; no view-specific pricing or filter defaults.
2. **Comparable and auditable:** distinguish AWS source, region, model/version, inference mode, tier, token direction, and published offer version. Never join on fuzzy names.
3. **Separate pieces:** acquisition/cleaning → bounded loading → calculations/filters → displays, orchestrated by setup. Each piece has a testable input/output contract and can fail in isolation.
4. **Reliable on a laptop:** prepare Parquet once; load needed columns/regions with DuckDB; perform small in-memory calculations with pandas and `Decimal`; cache read-only results by revision and request.
5. **No false precision:** show list-price caveats, validation errors, sample status, and missing data. No silent fallback to stale quotes or synthetic prices.

| Piece (suggested file) | Owns / input | Output passed forward |
| --- | --- | --- |
| **02 Data** (`src/data.py`) | Raw AWS CSVs and metadata; classification, units, QA, lineage | Clean typed Bedrock Parquet + provenance/QA JSON + atomic manifest |
| **03 Loader** (`src/loader.py`) | Manifest, requested service/regions/columns | Bounded pandas price rows + provenance + dataset revision |
| **04 Filter** (`src/filter.py`) | Loaded Bedrock rows, active regions, total tokens, optional budget | One unambiguous input/output pair per configuration, Decimal costs, sorted/paginated results and reasons for exclusions |
| **05 Views** (`src/views.py`) | Filtered configurations, prepared scenario costs, source metadata | Compare table, Sensitivity Plotly chart, empty/error states; no repricing |
| **06 Setup** (`src/setup.py`, `app.py`) | Local config, user inputs, manifest validation | One validated session state and calls to Loader → Filter → Views |

The component titles mirror the team's modules; **this prompt is self-contained** and must remain sufficient even when the team's separately drafted module documents are unavailable. Put configuration/path choices in one location rather than duplicating them.

## Data acquisition, preparation, and contracts

**Required MVP sources:**

| Local file | AWS service | Grain / important source conventions |
| --- | --- | --- |
| `bedrock_foundation_models.csv` | AmazonBedrockFoundationModels (Marketplace) | One published rate row; model commonly in `serviceName`, pricing meaning and region in `PriceDescription`, token unit commonly `1M tokens` |
| `bedrock_service_all.csv` | AmazonBedrock (Amazon-billed) | One published rate row; model/provider, region, `Inference Type`, `Feature`, `service_tier` explicitly where provided; token unit commonly `1K tokens` |

Use the course downloader `download_data.py` in the dataset repository (or its README's browser-download fallback), **not** a guessed schema. For the selected Bedrock-only scope, `uv run python download_data.py --small` includes both required Bedrock CSVs; it also downloads unrelated small files. The normal mode additionally downloads large EC2 files, which are **not required for the Bedrock MVP**. Use only the two named Bedrock inputs; do not download the all-region EC2 price sheet. Raw downloads reside locally under the dataset repo's `data/` and are not committed. Point the team app to the raw directory with `AWS_RAW_DATA_DIR` (default: adjacent `../dataset_aws-price-list/data` relative to team repo). Do not contact AWS on ordinary UI reruns.

Each CSV has **five metadata rows**, then a header and data. Capture those metadata rows (especially publication date, offer version/code), download timestamp, source URL, byte size and SHA-256. Parse the table using the equivalent of `pd.read_csv(path, skiprows=5, dtype=str, keep_default_na=False, low_memory=False)`; stream/chunk if required by actual size. Preserve original strings, especially literal `NA`; trim derived values only. Keep raw `PricePerUnit` separately from a finite, nonnegative `Decimal` rate. Never convert USD rates to binary floating point for calculation or set missing prices to zero.

For each price record, preserve the publisher's rate/SKU identifier where present; additionally create immutable `source_row_id = SHA256(source_file + '|' + offer_version + '|' + original_CSV_data_row_number)` to trace back to input rows. Remove **only exact duplicates** across publisher identifier and every raw price-defining attribute, recording removals. Do **not** deduplicate by model name. The prepared Bedrock schema must expose at least:

```text
source_row_id, source_file, source_type [marketplace|amazon_billed],
offer_version, publication_date, rate_code, sku,
model_raw, provider_raw, model_normalized, region_raw, region_normalized,
inference_type_raw, feature_raw, service_tier_raw, price_dimension_raw,
token_direction [input|output|other|unknown], pricing_mode,
cache_status, commitment_context, unit_raw, price_per_unit_raw,
price_per_unit_decimal, conversion_multiplier, price_usd_per_1m_tokens,
record_status [comparison_eligible|retained_noncomparable|quarantined],
flag_reason
```

Normalize only when the **source explicitly supports** the transformation:

- Marketplace: preserve and cautiously parse pipe-delimited `PriceDescription` into region and price dimension. Known examples: `Million Input Tokens Global` = input/global; `Output Tokens - Standard, Global` = output/standard/global; `Cache Read Tokens - Standard, Global` = cache-read; `Million Batch Response Tokens Global` = output/batch. Do not invent a region from a model name. Unrecognized dimensions are flagged rather than guessed.
- Amazon-billed: use explicit `Model`, `Provider`, `Region Code`, `Inference Type`, `Feature`, and `service_tier`. For example, `Input tokens priority` is **priority**, `output tokens batch` is **batch**, `Output tokens` with `service_tier=standard` is **standard** output, and `Prompt cache read input tokens` is a separate cache rate. An empty `Inference Type` does **not** prove a token direction.
- Normalize only recognized token units: `1K tokens` → `price_usd_per_1m_tokens = Decimal(PricePerUnit) * 1000`; `1M tokens` → unchanged, using multiplier 1. A source price `0.0002625000` per `1K tokens` must become exactly `0.2625000` per 1M. Do not treat `hour`, `TextUnit`, `1M TPM Hour`, or provisioned-throughput commitments as token rates.
- Preserve different source types, inference modes (`standard`, `batch`, `priority`, `flex`, `global`, etc.), cache status, serving tier, model versions, regions and commitments. **A comparison-eligible normalized rate is not automatically an eligible full model configuration.**

Each input record has exactly one accounting outcome: cleaned, quarantined, or exact duplicate removed. A cleaned row is either `comparison_eligible` (recognized direction and token unit, valid model/region/id/price) or `retained_noncomparable`. Produce source-level counts, parsing failures, reasons for exclusions, hashes and versions; assert `raw = clean + quarantine + exact_duplicate_removed`. Block use of invalid manifest revisions. Dev samples may be used for tests/inspection with a conspicuous `SAMPLE` label but must never masquerade as complete production comparisons.

**Chosen physical integration format (resolves the team's draft ambiguity):** create `data/cleaned/bedrock_prices.parquet`, `data/cleaned/quarantine.parquet`, `data/cleaned/provenance.json`, `data/cleaned/quality.json`, and `data/cleaned/manifest.json` in the **team working directory**. Use `data/cleaned/` only for generated local outputs and keep it in `.gitignore`. Use fixed schema revision `1`. The manifest contains a stable `dataset_revision` derived from source-file hashes + transform version, `schema_revision`, `is_sample`, source metadata and offer versions, exact relative output paths, output file SHA-256 hashes, and quality-check pass/fail results. Write each output to a temporary path, validate, then atomically publish the manifest **last**. Loader must reject missing, mismatched or partially updated outputs. Never silently merge two source revisions into one published baseline. Raw sources stay in the dataset repo; transformed data stays in the team working dir.

## Loader contract and budget

Implement these interfaces or behaviorally equivalent ones:

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import pandas as pd

@dataclass(frozen=True)
class LoadRequest:
    service: Literal["bedrock"]
    regions: tuple[str, ...]  # empty means all available TO THE LOADER ONLY
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

Query Parquet using **DuckDB** projection and region predicates, materializing only bounded pandas slices. For `comparison`, retain records with `record_status='comparison_eligible'`; `inspection` may expose retained noncomparable records, with quarantine in diagnostics only.

For `purpose="comparison"`, return the union of `request.columns` and the mandatory comparison columns below, in a deterministic order. Keep this required-column definition in one shared contract used by Loader and Filter:

- Identity and matching: `source_row_id`, `source_file`, `source_type`, `offer_version`, `model_raw`, `region_normalized`, `pricing_mode`, `service_tier_raw`, `feature_raw`, `cache_status`, `commitment_context`, `rate_code`, `sku`.
- Rates: `token_direction`, `price_usd_per_1m_tokens`.
- Audit: `publication_date`, `record_status`, `flag_reason`.

Mandatory columns cannot be dropped by a display-only projection. Validate their presence before returning the slice; if the prepared schema lacks one, reject the comparison load with an actionable schema error. Never replace an absent matching field or rate with an assumed default. Presence checks do not make ambiguous values eligible: Filter must still enforce the existing exact-pair rules. For `inspection`, return requested columns plus `source_row_id`, `source_file`, `offer_version`, `publication_date`, `record_status`, and `flag_reason`.

Do not multiply rows while attaching provenance. Reject unknown requested columns, invalid regions and broken hashes with actionable messages. For a valid zero-match request, return an empty DataFrame with the same required schema.

Done when: (1) a comparison request asking only for `model_raw` still returns every mandatory comparison field; (2) removing `token_direction` or `price_usd_per_1m_tokens` from the prepared schema raises a clear error before Filter runs; (3) a valid zero-match comparison preserves the required columns. Use the existing source-aware matching fixture to confirm that the returned slice can be passed directly to Filter without guessed fields.

Cache read-only slices on `(dataset_revision, schema_revision, file_hashes, sorted(regions), columns, purpose)` with a small bounded cache. Changes to token usage, budget or chart scenarios must not reopen raw files or rescan Parquet. Set a configurable `MAX_LOADED_ROWS=100000` safety limit initially; show a request-to-narrow message if exceeded, and benchmark memory on actual data instead of assuming safety. An explicit prepare/activate action alone can change the dataset revision.

## User setup, matching, pricing and filters

**First screen:** title and purpose; persistent banner **“Published AWS list-price estimates only — not your actual bill; discounts, credits, taxes, quality and latency are excluded.”** Show the dataset/offer versions and publication dates. Controls appear above **Compare** and **Sensitivity** tabs. When required full-price data or the manifest is missing, show exact preparation steps rather than a plausible example recommendation.

| Control | First-open value and validation |
| --- | --- |
| Service | Bedrock only (no unimplemented EC2 tab) |
| Region(s) | `us-east-1`; must exist in eligible records; clearing region means **no matches** |
| Budget | Unset; optional nonnegative USD `Decimal`; tests compare unrounded numbers |
| Pricing context | Standard, uncached, non-batch, non-provisioned; compare only explicitly identifiable context |
| Input tokens/request | `1,000`, integer ≥ 0 |
| Output tokens/request | `1,000`, integer ≥ 0 |
| Requests/month | `1,000`, integer ≥ 0 |
| Sensitivity request scenarios | `500, 1,000, 2,000`, integer ≥ 0; fix other inputs |
| Activated dataset version | Manifest-selected and read-only; no auto-refresh |

Important interface reconciliation: **Loader interprets `regions=()` as all regions; Filter/UI interprets zero selected regions as zero matches.** Setup **must not call Loader** for an empty user selection. If an explicit “All regions” action exists, expand it to the nonempty known region codes before loading.

Prepare comparable configurations **only** from unambiguous input and output price records with the same explicit source type/file and version, exact source model identity/version, known identical region, pricing mode `standard`, compatible standard tier/feature context, uncached and non-batch/non-provisioned status, and the same commitment context. Require **exactly one distinct input and one distinct output rate** for the complete configuration. Exclude and count incomplete, ambiguous or mismatched pairs; do not average duplicate rates, guess an identity across the two Bedrock sources, merge global/regional modes, or combine a priority input with a standard output. Retain both publisher IDs, source file and offer version for audit. `model_normalized` is a display/search aid, **not a cross-source join key**. Model quality/latency/throughput are **not** determined by these price lists; use `Not available` for such fields unless independently verified evidence is subsequently added.

For every surviving configuration, the **Filter** module must create one deterministic `configuration_id`. Define it from the exact comparison identity, not from display labels: `source_file`, `offer_version`, exact source model identity/version, `region_normalized`, `pricing_mode`, standard tier/feature context, `cache_status`, `commitment_context`, plus the two paired publisher rate identifiers (input first, output second). Encode the values in a fixed field order and hash that canonical string with SHA-256. The same pair under the same dataset revision must always produce the same ID. Views may display a shorter human-readable label, but pagination, row identity, tie-breaking, and sensitivity-series joins must use `configuration_id`.

The **Filter** module owns every money calculation, using `Decimal`:

```text
monthly_input_tokens  = input_tokens_per_request  * requests_per_month
monthly_output_tokens = output_tokens_per_request * requests_per_month
cost(input_total, output_total) =
    (Decimal(input_total) * input_usd_per_1m + Decimal(output_total) * output_usd_per_1m)
    / Decimal(1_000_000)
monthly_cost_usd        = cost(monthly_input_tokens, monthly_output_tokens)
per_request_cost_usd    = cost(input_tokens_per_request, output_tokens_per_request)
per_1000_requests_usd   = per_request_cost_usd * Decimal(1000)
```

These token totals are **workload totals**, not per-request totals. Apply selected-region and optional monthly budget conditions with `AND` (multiple selected regions use `OR`), always test unrounded `monthly_cost_usd <= budget` (inclusive), and sort qualifying configurations by unrounded monthly cost ascending, then `configuration_id`. The full filtered match count is returned independently of pagination; paginate **50 rows** per page. Preserve genuine zero price/zero usage. Reject negative or nonintegral token/request inputs and invalid budgets with field-level errors; don't show stale calculated numbers while inputs are invalid.

**Sensitivity:** For each configuration in the **current base-case filtered shortlist**, Filter's same pure cost function computes monthly costs at 500, 1,000, and 2,000 requests. Hold per-request tokens, rates and all model/region/mode constraints fixed. Do **not** reapply the base-case budget separately at each scenario; the chart deliberately shows when a currently affordable option becomes more expensive as volume grows. Plotly has X = monthly requests, Y = estimated monthly USD cost, one line per displayed configuration; label series by model+region+source. If the shortlist is large, limit chart to lowest-cost 10 configurations (all remain in the full Compare table) and state that rule. Views receive already-priced base rows and scenario series and never recompute amounts independently.

**Compare view:** display match count, active workload assumptions and a table with provider, model, region, source, standard inference mode/tier, normalized input and output USD/1M tokens, per-request USD, per-1,000 USD, estimated monthly USD, and in expandable row details the publisher identifiers and offer version. Keep AWS list prices visually separate from optional non-AWS metrics; show `Not available` for absent quality, output speed, TTFT/latency. Show money in USD; monthly figures rounded to 2 decimals **only for display**, very small nonzero per-request costs with enough digits not to render falsely as zero. Empty result: exactly `No model configurations match the current filters.` and no misleading chart. Show counts/reasons for excluded invalid/ambiguous records and price snapshot stamps.

## Local run, cloud path, and completion checks

**Stack:** Python 3.11, `uv`, pandas, DuckDB, PyArrow, Streamlit, Plotly, pytest. Define pinned dependencies in `pyproject.toml` / `uv.lock` and use one app configuration for paths. Never embed personal absolute directories, credentials or raw downloads in Git. The agent must create the needed application and test files; they are not asserted to exist beforehand.

**Reproducible commands** (from `~/dso576`, reusing any existing checkout):

```bash
mkdir -p ~/dso576 && cd ~/dso576
git clone https://github.com/USC-DSO-576-PS/dataset_aws-price-list.git
cd dataset_aws-price-list
uv run python download_data.py --small  # includes both Bedrock inputs
cd ..
# Work in an existing team checkout if accessible; otherwise create a local project.
mkdir -p dso576-project-T10
cd dso576-project-T10
# Agent first creates pyproject.toml, app.py, src/, and tests/ as specified.
uv sync
uv run python -m src.data prepare --raw-dir ../dataset_aws-price-list/data
uv run pytest -q
uv run streamlit run app.py
```

The prep command is an **implementation requirement**, not a claim that it already exists. CLI should accept `--raw-dir` and `--out-dir` with documented defaults. Preparation is explicit; app startup is read-only and must not download anything. The private **team repository is an optional destination**, not a build-time input: if it is inaccessible, build in the local project directory created above and explain how to copy or commit the artifacts later. Only the **course dataset repository** is required; if its access is unavailable, report the exact blocker and do not fabricate real pricing. Ignore `data/`, `.venv/`, `.streamlit/secrets.toml` and generated caches. Commit only if actual Git permissions are available; never demand credentials. In future cloud deployment, move versioned Parquet/manifest to read-only object storage, run a separate scheduled preparation job, place Streamlit behind suitable access controls, and preserve per-user session state plus revision-keyed shared caches. Cloud deployment is **not** required now.

**Build order and independent “done when” tests:**

| Order | Piece / fixture | Expected outcome |
| --- | --- | --- |
| 1 | Inspect actual dataset CSV headers and metadata, prepare one tiny source-aware fixture | Exact source columns checked; an unsupported or absent column produces a documented diagnostic, not invented data |
| 2 | Data unit test: `0.0002625000` per `1K tokens`, priority input | Decimal per-1M rate is exactly `0.2625000`; status/context remains **priority**, never treated as standard |
| 3 | Data quality: `hour`/`TextUnit` vs token rate; duplicate/unparsed cases | Non-token rate is excluded from comparison and counted; raw = clean + quarantine + dedup for each file; 1K/1M conversion checked |
| 4 | Manifest and loader: US-East eligible input/output + another-region row + noncomparable row | Only requested region and needed eligible rows load, provenance unique; missing file/hash/column gives useful error; empty selection preserves schema |
| 5 | Matching: 1 unambiguous standard pair; unmatched direction and mismatched mode/tier; 2 ambiguous input rates | Only the complete matched pair survives; excluded count/reasons reflect each other case; no fuzzy merging |
| 6 | Pricing: rates `$1/1M` input and `$3/1M` output under default 1K+1K tokens/request ×1K requests | Month `$4.00`; per request `$0.004`; per 1K requests `$4`; scenarios 500/1000/2000 → `$2/$4/$8` |
| 7 | Budget/empty/pagination: `$3.99` vs `$4.00` budget; 51 qualifying configurations | `$3.99` excludes and `$4.00` includes default example; full count 51, pages 50+1; no-match message is shown |
| 8 | Setup/cache: remove selected regions, then change volume/budget only | Empty UI selection does **not** call Loader with `()`; changes recompute costs without raw-read or duplicate Parquet scan; both views share state |
| 9 | Snapshot/sample safety: corrupt manifest hash, old/new offer versions, sample-only data | Fail closed with actionable message; no mixed version or production-looking sample comparison |
| 10 | Real Bedrock data and UI smoke run | Independently verify one input/output pair against full raw rows and offer metadata; record preparation time, warm filter response time, loaded rows and peak memory; app starts with title, banner, controls, table and chart/empty state |

Report test pass/fail, detected schema variants, excluded-rate counts, actual dataset versions and measured performance in `reports/validation.md`. Prefer warm filter updates under 3 seconds on the test laptop, but report actual measurements; never invent a benchmark or source statistic. The final team repository should contain the code, tests, `README.md`, `00-vision.md`, and this prompt; no raw AWS files, private datasets, local caches or secrets. If any core feature is blocked by verified data limitations, show its precise limitation and preserve a non-misleading read-only app rather than quietly fabricating prices.
