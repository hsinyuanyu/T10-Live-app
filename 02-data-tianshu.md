# 02 — Bedrock Data Preparation

## Purpose and boundary

Prepare one validated, traceable Bedrock list-price baseline for the AWS Bedrock Model Cost Comparison Tool. The output lets downstream components identify exact, comparable input/output token-rate pairs; it does not recommend a model, calculate workload cost, assess model quality or latency, or fetch data during UI use.

This component uses only:

| Raw file | Source type | Source conventions |
| --- | --- | --- |
| `bedrock_foundation_models.csv` | `marketplace` | Model commonly in `serviceName`; region and price dimension in `PriceDescription`; token unit commonly `1M tokens` |
| `bedrock_service_all.csv` | `amazon_billed` | Model/provider, region, `Inference Type`, `Feature`, and `service_tier` where provided; token unit commonly `1K tokens` |

Published AWS prices are list prices, not customer invoices. Private discounts, credits, taxes, model quality, latency, and actual availability are outside this data contract. Do not infer a cross-source model identity from a similar name.

## Acquisition and immutable source record

Run the course downloader from the dataset repository:

```bash
uv run python download_data.py --small
```

`--small` downloads **nine** files, including both required Bedrock files and unrelated small files. It is the correct Bedrock-only acquisition mode, but this component reads only the two named inputs. The downloader has no two-file mode. Normal mode downloads all eleven files, including two large EC2 CSVs, which this MVP does not require. `--check` downloads nothing. If the downloader fails, use the documented browser fallback to obtain the two named files with their exact filenames.

Raw files remain under the course dataset repository's `data/` directory and are never committed. The team application locates that directory through `AWS_RAW_DATA_DIR`; its default is `../dataset_aws-price-list/data` relative to the team repository. Preparation is explicit and UI startup is read-only.

For each input, capture the five metadata rows plus local acquisition facts before parsing data rows:

```text
source_file, source_url, downloaded_at_utc, format_version, publication_date,
offer_version, offer_code, file_size_bytes, sha256, raw_row_count,
transform_version
```

`current` URLs are mutable. A changed expected checksum or byte count is a warning, not an error, when the received file's metadata and SHA-256 are captured. Never combine files from different source revisions silently.

## Ingestion and lineage

Each full CSV has five metadata rows, its header on row 6, and data from row 7. Read data with the equivalent of:

```python
pd.read_csv(path, skiprows=5, dtype=str, keep_default_na=False, low_memory=False)
```

Rules:

- Preserve raw strings; literal `NA` means “does not apply,” not null.
- Trim whitespace only in derived fields. Retain every raw source field used for a classification.
- Parse `PricePerUnit` to a finite, nonnegative `Decimal`; retain `price_per_unit_raw` separately. Never use binary floating point or replace an absent/malformed price with zero.
- Preserve publisher `RateCode` and `SKU` where present. Create `source_row_id = SHA256(source_file + "|" + offer_version + "|" + original_CSV_data_row_number)` for every raw row.
- Remove only exact duplicates: same publisher identifier and every raw price-defining field. Do not deduplicate by model name, provider, SKU, or rate alone. Log removed rows.
- Every input row has exactly one accounting outcome: clean output, quarantine output, or exact duplicate removed.

## Prepared record contract

`bedrock_prices.parquet` has one row for each nonduplicate raw record. It must contain at least:

```text
source_row_id, source_file, source_type, offer_version, publication_date,
rate_code, sku, model_raw, provider_raw, model_normalized,
region_raw, region_normalized, inference_type_raw, feature_raw,
service_tier_raw, price_dimension_raw, token_direction,
pricing_mode, cache_status, commitment_context, unit_raw,
price_per_unit_raw, price_per_unit_decimal, conversion_multiplier,
price_usd_per_1m_tokens, record_status, flag_reason
```

Allowed `source_type` values are `marketplace` and `amazon_billed`. Allowed terminal `record_status` values are:

| Status | Meaning |
| --- | --- |
| `comparison_eligible` | Valid, explicitly identified token rate; eligible for Loader's comparison slice, but not automatically a complete input/output configuration |
| `retained_noncomparable` | Valid published row that is not an eligible token rate, such as an hourly provisioned-throughput rate |
| `quarantined` | Row cannot safely be parsed or classified; write it to `quarantine.parquet` with a reason |

`model_normalized` is a display/search aid only. It is never a cross-source join key. A `comparison_eligible` row requires a nonblank model, normalized region, rate identifier, recognized token direction, exactly recognized token unit, and finite nonnegative decimal price.

## Bedrock normalization rules

### Marketplace source

Preserve complete `PriceDescription`, then cautiously split only its pipe-delimited prefix, region, and remaining price description. A missing region segment is flagged; do not infer region from a model name.

Classify only an approved, clearly labelled price dimension. Grounded examples from the course sample are:

| `PriceDescription` remainder | Derived meaning |
| --- | --- |
| `Million Input Tokens Global` | input, global |
| `Output Tokens - Standard, Global` | output, standard, global |
| `Cache Read Tokens - Standard, Global` | cache-read, standard, global |
| `Million Batch Response Tokens Global` | output, batch, global |

`Per Hour per 1K Input TPM Reserved 3 Month Regional` with unit `1M TPM Hour`, and `Provisioned Throughput Hourly Price (6 Months Commit)` with unit `hour`, are retained non-token rates. They receive no per-million-token price. An unapproved or ambiguous description is quarantined as `unrecognized_price_description`; do not use a heuristic to guess direction, tier, cache, commitment, or region.

### Amazon-billed source

Use explicit `Model`, `Provider`, `Region Code`, `Inference Type`, `Feature`, and `service_tier` values where present. Keep their raw values and derive context only when explicit labels support it.

| Sample label/context | Derived meaning |
| --- | --- |
| `Input tokens priority` | input, priority |
| `output tokens batch` | output, batch |
| `Output tokens` + `service_tier=standard` | output, standard |
| `Prompt cache read input tokens` | cache-read-input, separate cache rate |
| `Input tokens` + `Feature=Batch Inference` | input, batch |

Blank `Inference Type` is not evidence of input or output. For example, a `1K tokens` row with `service_tier=global-flex` and blank inference type is retained_noncomparable with `flag_reason=missing_token_direction`. Units such as `hour`, `TextUnit`, `Custom Model Unit per Min`, and `1M TPM Hour` are retained_noncomparable with `flag_reason=non_token_unit`.

Do not merge standard, priority, flex, batch, global, cache, provisioned-throughput, or differing commitment contexts. Do not infer missing provider, model, region, tier, or token direction.

### Token-unit conversion

Normalize only a recognized input or output token rate with one of these exact units:

| `unit_raw` | `conversion_multiplier` | `price_usd_per_1m_tokens` |
| --- | ---: | --- |
| `1K tokens` | 1000 | `price_per_unit_decimal * 1000` |
| `1M tokens` | 1 | `price_per_unit_decimal` |

Keep input, output, cache-read, and batch prices distinct. A token-rate row is not `comparison_eligible` when it is cache, batch, nonstandard, provisioned, or otherwise incompatible with the MVP's required standard, uncached, non-batch, non-provisioned pairing context; retain it with its explicit context and status/reason. The Filter component, not this component, pairs exactly one compatible input and output rate and calculates cost.

## Required local outputs and publication

Write generated outputs under the team repository's ignored `data/cleaned/` directory:

| Path | Contents |
| --- | --- |
| `data/cleaned/bedrock_prices.parquet` | Typed prepared records using the contract above |
| `data/cleaned/quarantine.parquet` | Quarantined source rows, `source_row_id`, raw fields needed for diagnosis, and reason code |
| `data/cleaned/provenance.json` | Per-source acquisition and five-line metadata records |
| `data/cleaned/quality.json` | Counts, validation results, duplicate/parsing/exclusion reasons, and sample/full state |
| `data/cleaned/manifest.json` | The sole selected baseline for Loader |

Use schema revision `1`. `manifest.json` must include `dataset_revision` derived from source SHA-256 values and transform version, schema revision, `is_sample`, source offer versions/metadata, exact relative output paths, each output's SHA-256, and quality-check pass/fail results. Write and validate each output at a temporary path, then atomically publish the manifest **last**. Loader must reject a missing, mismatched, partially published, failed-quality, or mixed-revision manifest.

## Validation and acceptance criteria

The preparation run passes only when all of the following are true:

1. Both required files exist, are nonempty, and each has exactly one provenance record.
2. Each full source has five metadata rows and all columns used by its transform; a missing/renamed required column fails that source rather than invoking a fallback name.
3. Every loaded row has one terminal accounting outcome, and for each source:

   ```text
   raw_rows = clean_rows + quarantined_rows + exact_duplicates_removed
   clean_rows = comparison_eligible_rows + retained_noncomparable_rows
   ```

4. Any `comparison_eligible` row has all required fields, unit exactly `1K tokens` or `1M tokens`, a recognized input/output direction, and a finite nonnegative `Decimal` price.
5. Every nonnull normalized rate equals `price_per_unit_decimal × conversion_multiplier`, with multiplier exactly 1000 or 1. Non-token/unresolved rows have null normalized token price and a reason code.
6. Exact-duplicate removals, parse failures, unknown units, unrecognized Marketplace descriptions, missing regions, missing direction, and non-token rates are counted by source in `quality.json`.
7. Manifest paths and SHA-256 values match the published output files, and both source files share the manifest's activated revision.
8. Sample runs are labelled conspicuously `SAMPLE` in quality/manifest metadata and must not be presented as a complete production baseline.

### Small test cases

| Input | Expected result |
| --- | --- |
| Amazon-billed row: `Inference Type="Input tokens priority"`, `Unit="1K tokens"`, `PricePerUnit="0.0002625000"`, valid model/region/rate identifier | `token_direction=input`, `pricing_mode=priority`, multiplier `1000`, normalized rate `0.2625000`; preserve priority rather than relabeling it standard |
| Row: `Unit="hour"`, `Feature="Provisioned Throughput Inference - 6 months"` | null normalized rate, `retained_noncomparable`, `flag_reason=non_token_unit` |
| Marketplace row: `Output Tokens - Standard, Global`, `Unit="1M tokens"`, `PricePerUnit="25.0000000000"` | output/standard/global; multiplier `1`; normalized rate `25.0000000000` |

## Downstream handoff and ownership

Loader reads only the validated manifest and Parquet outputs, requests bounded columns/regions with DuckDB, and returns `comparison_eligible` records plus provenance/status fields. Filter owns exact pairing of one input and one output rate within the same explicit source/file/version, model identity/version, region, standard context, and commitment context; it owns Decimal workload-cost, budget, sorting, and pagination calculations. Views display Filter results and never normalize raw rows or reprice them. Setup owns user input and never downloads or prepares data on a click.

## Integration flags

- The authoritative one-shot prompt is Bedrock-only and defines the physical output contract above. Existing `03-loader-siyao.md`, `04-filter-tianna.md`, and `06-setup-tony.md` still contain EC2 routes or references; they should be reconciled before implementation, but are not changed by this component.
- This file, `02-data-tianshu.md`, is the authoritative Bedrock-only data specification. Some team documents still refer to `02-data.md`; reconcile those references before implementation.
- The one-shot prompt requires standard, uncached, non-batch, non-provisioned full configurations, but it does not define every acceptable Marketplace string or all compatible standard tier/feature combinations. Maintain an explicit approved mapping and quarantine unrecognized cases; do not invent additional parsing or pairing rules.

## Sources consulted

- `00-vision.md`
- `one-shot-prompt.md`
- `download_data.py`
- `03-loader-siyao.md`, `04-filter-tianna.md`, `05-views-alicia.md`, and `06-setup-tony.md`
