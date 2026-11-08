# AWS Bedrock Model Cost Comparison

A local Streamlit shortlist for AI product managers comparing public AWS Bedrock token list prices. Set regions, tokens per request, request volume, and an optional budget. Compare complete standard input/output configurations and stress-test the current shortlist at other volumes. Price is not evidence of quality or latency.

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/); uv installs Python 3.11+ if needed. The committed `data/snapshot/` contains a complete, validated condensed Bedrock snapshot; no AWS account, credentials, sibling checkout, or network download is needed after dependency installation.

## Run on macOS

```bash
git clone https://github.com/USC-DSO-576-PS/project-prof-build-T10.git
cd project-prof-build-T10
uv run streamlit run app.py
```

## Run on Windows PowerShell

```powershell
git clone https://github.com/USC-DSO-576-PS/project-prof-build-T10.git
Set-Location project-prof-build-T10
uv run streamlit run app.py
```

Streamlit prints a local browser URL. Stop the server with Ctrl+C. Choose a free port with `--server.port 8517` if the default is occupied. Startup never downloads or prepares prices.

## Refresh explicitly

The snapshot stays fixed until you deliberately replace it. These commands work in macOS shells and PowerShell, from the app directory:

```text
git clone https://github.com/USC-DSO-576-PS/dataset_aws-price-list.git ../dataset_aws-price-list
uv run python scripts/download.py
uv run python -m src.data prepare --raw-dir data/raw
uv run python -m src.data prepare --raw-dir data/raw --out-dir data/snapshot
```

Reuse the sibling repository if already cloned. `scripts/download.py` invokes the course downloader's original function and URL list, selecting only the two required Bedrock sources. It saves downloads under ignored `data/raw/`; it never fetches EC2. Source URLs, actual hashes, sizes, acquisition times and the five metadata rows are preserved. Changes from the course's expected hashes are normal when AWS republishes. Re-running download may retrieve a newer offer: preparation is the explicit activation boundary.

The first preparation command creates the prompt's ignored `data/cleaned/` integration outputs for review. The second explicitly activates the app's portable, committed snapshot. Do not run two preparations against the same directory at once. Outputs replace atomically with the manifest published last; readers reject inconsistent outputs rather than using stale prices. Review `quality.json` and changes before committing a refreshed snapshot.

For sources already downloaded by `uv run python download_data.py --small` in the dataset repo:

```text
uv run python -m src.data prepare --raw-dir ../dataset_aws-price-list/data --out-dir data/snapshot
```

Without `--raw-dir`, preparation uses `AWS_RAW_DATA_DIR`, defaulting to the sibling dataset's `data/`. Without `--out-dir`, it uses `data/cleaned/`. App paths and row limits live in `src/config.py`. To inspect a different activated directory, set `AWS_CLEAN_DATA_DIR` before starting:

macOS:

```bash
export AWS_CLEAN_DATA_DIR="$PWD/data/cleaned"
uv run streamlit run app.py
```

PowerShell:

```powershell
$env:AWS_CLEAN_DATA_DIR = Join-Path $PWD 'data/cleaned'
uv run streamlit run app.py
```

A missing or corrupt manifest shows repair commands. A sample snapshot is labeled SAMPLE and cannot produce a production shortlist. Missing rates never become zero. Keep both full source files from each intended preparation together; each service legitimately publishes its own offer version, and they are never paired across services.

## Verify

```text
uv run pytest -q
uv run python -m scripts.benchmark --raw-dir data/raw
```

Tests use tiny synthetic source-aware fixtures plus the committed real snapshot. The benchmark requires the full raw downloads, writes local `reports/measurements.json`, samples process RSS with cross-platform psutil, audits a real raw pair and runs Streamlit's UI harness. Scratch uses Python's platform temporary directory (`TMPDIR`/`TEMP` may override). No Linux-only process or filesystem facilities are used in application or test code. See [validation results](reports/validation.md) and [build report](BUILD_REPORT.md).

## Reading results

Default workload: 1,000 input and 1,000 output tokens/request × 1,000 requests/month in `us-east-1`. The optional budget compares **unrounded Decimal** amounts inclusively. Tables round monthly USD to two decimals only for display; all other money retains decimal digits. Equal prices use a stable configuration ID for ordering. Pages contain 50 configurations; sensitivity uses the first 10 in the full base-case shortlist, keeping the budget fixed at the base case. Clearing regions means no matches. Loader's internal empty-region sentinel means all regions and is never sent for an empty UI selection.

Identity preserves exact source file/type, offer, model name/version, provider, region, standard inference context, serving scope, feature, tier and commitment. Only one input and one output publisher record may form a pair; ambiguous and incomplete groups are counted and excluded. Global/regional serving scopes are distinct. Unrecognized dimensions (including unsupported modality and long-context dimensions) stay in diagnostics rather than being inferred. The conservative parser can omit valid AWS rates; this is a supported-rate shortlist, not every available Bedrock purchasing option. The region selector indicates eligible rate rows, not guaranteed complete pairs. Details expose publisher IDs and offer stamps. Quality, output speed and latency are `Not available`.

`src/data.py` owns preparation and lineage; `src/loader.py` validates hashes and performs bounded DuckDB queries; `src/filter.py` owns matching and every money calculation; `src/setup.py` connects shared state; `src/views.py` formats prepared results. Revision-keyed bounded caches avoid repeated Parquet queries when workload or budget changes. Initial projection is limited to 100,000 rows (configurable with `MAX_LOADED_ROWS`); requests over the cap ask for narrower regions.

Published AWS list-price estimates only — not your actual bill; discounts, credits, taxes, quality and latency are excluded. No purchasing, authentication, cloud deployment or actual bill calculation is provided. A future hosted version would use read-only versioned object storage, a separate preparation job, appropriate access control, and per-user session state with revision-keyed shared caches.
