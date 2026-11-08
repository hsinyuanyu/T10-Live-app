# 06 — Setup, Defaults, and Application Wiring

## Purpose

Define the **first-run experience, user inputs, shared state, local startup, and module handoffs** for the AWS public-price comparison tool. This is a **component specification**, not implemented application code. It connects the team's existing pieces without taking over their responsibilities:

| Piece | Owns | Setup's relationship |
| --- | --- | --- |
| `02-data-tianshu.md` | Download, standardization, data quality, published price versions | Specify where to find the selected prepared-data manifest; never clean or download on a UI click |
| `03-loader-siyao.md` | Manifest validation, bounded DuckDB/Parquet reads, DataFrame slices, caching | Issue a validated `LoadRequest`; consume `LoadedSlice` |
| `04-filter-tianna.md` | Eligible offerings, Decimal cost calculations, constraints, ranking and pagination | Supply regions, budget and workload assumptions; never recalculate prices in setup |
| `05-views-alicia.md` | Bedrock Compare and Sensitivity presentations | Pass filtered configurations and the same active workload state to both views |

**Product decision to resolve at integration:** Data, Loader and Filter describe **both EC2 and Bedrock**, but the supplied Views specification defines **Bedrock only**. This setup specifies Bedrock as the **currently complete user-facing path**. Do not display an EC2 route as working until the team assigns and specifies an EC2 results view. If the team selects EC2-only or dual-service as its final vision, reconcile this setup and `05-views-alicia.md` together; do not silently substitute a different product.

## Design principles

1. **One state, one interpretation.** Setup is the sole owner of user-entered assumptions; Filter and Views use those exact values instead of defining competing defaults.
2. **Reproducibility.** Every result belongs to one explicitly selected prepared-data revision and published AWS offer version. The app never silently switches to a new `current` price sheet.
3. **Separation of jobs.** Setup validates controls and coordinates calls; Data cleans, Loader reads, Filter calculates, and Views renders.
4. **Safe by default.** Only public AWS list prices are shown. Missing data, unresolved Bedrock price pairs and development samples are not silently converted into production comparisons.
5. **Fast interactions.** Changes to workload or budget reuse the loaded slice; only a changed service, region, required column set or dataset revision can trigger another Loader request.

## First screen and default state

For the current **Bedrock user-facing path**, the opening screen shows:

- Product title and purpose: compare public Amazon Bedrock model/region token costs for a specified workload.
- A persistent notice: **“Estimates use published AWS list prices, not your actual bill; discounts, credits, taxes, model quality and latency are not included.”**
- The activated dataset revision, publisher offer version(s), acquisition/publication date if available, and a conspicuous **SAMPLE / DEVELOPMENT** label for sample data.
- A Setup panel for service, region(s), optional budget, workload and sensitivity assumptions, followed by the existing **Compare** and **Sensitivity** views.
- If there is no validated full-data manifest, a setup/error screen with the exact missing path and recovery steps—not invented pricing or a usable-looking example recommendation.

| User control | Default | Validation and meaning |
| --- | --- | --- |
| Service | Bedrock | EC2 is not offered as a complete route until an EC2 view is specified and built |
| Region(s) | `us-east-1` | Region must occur in the selected service's eligible prepared data; no selection means **no matches**, not “all regions” |
| Maximum estimated cost (USD) | Unset | Optional `Decimal >= 0`; unset means no budget limit |
| Inference context | Standard, uncached, non-batch, non-provisioned | Keep source/mode/tier identities separate; only unambiguous compatible input/output price pairs may be estimated |
| Average input tokens/request | `1,000` | Nonnegative integer |
| Average output tokens/request | `1,000` | Nonnegative integer |
| Expected monthly requests | `1,000` | Nonnegative integer; zero is a valid zero-usage scenario |
| Sensitivity requests/month | `500`, `1,000`, `2,000` | Nonnegative integer scenarios; hold tokens per request and selected configurations constant |
| Dataset version | The validated prepared manifest | Display read-only; switching revisions requires explicit activation and revalidation |

The default workload therefore has **1,000,000 total input tokens** and **1,000,000 total output tokens**. This deliberately matches the default total-token assumptions in `04-filter-tianna.md` while supplying the **per-request** inputs required by `05-views-alicia.md`.

If the team implements EC2 views later, its setup defaults must match `04-filter-tianna.md`: `instance_count = 1`, `hours_per_month = 730`, optional budget unset, and `us-east-1` selected from the two supported EC2 regions (`us-east-1`, `eu-west-1`). Allow a positive integer count and hours in `[0, 744]`. This baseline concerns **On-Demand** Linux/shared/used/no-preinstalled-software compute; do not imply Reserved effective-cost calculations are already implemented.

## State contract and derived values

Store only **per-session user input** as mutable UI state. Treat loader results as read-only cached data keyed by manifest revision and canonical `LoadRequest`. A Python typing sketch, not a requirement to duplicate state across modules:

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

@dataclass(frozen=True)
class SetupSelection:
    service: Literal["bedrock", "ec2"] = "bedrock"
    regions: tuple[str, ...] = ("us-east-1",)
    maximum_budget_usd: Decimal | None = None
    avg_input_tokens_per_request: int = 1000
    avg_output_tokens_per_request: int = 1000
    monthly_requests: int = 1000
    sensitivity_monthly_requests: tuple[int, ...] = (500, 1000, 2000)
    instance_count: int = 1
    hours_per_month: int = 730
```

`dataset_revision`, `is_sample`, provenance and offer versions come **from the Loader's `LoadedSlice`**, not from editable user controls. The manifest path is supplied by local configuration.

Use these exact shared calculations:

```text
monthly_input_tokens  = avg_input_tokens_per_request  * monthly_requests
monthly_output_tokens = avg_output_tokens_per_request * monthly_requests
monthly_estimated_bedrock_usd =
    (monthly_input_tokens * input_usd_per_1m_tokens
   + monthly_output_tokens * output_usd_per_1m_tokens) / 1_000_000
```

**Ownership:** Setup computes the two integer **token totals**, then passes them to Filter. Filter performs the Decimal money calculation, budget test and sorting. Views receives the same per-request assumptions and Filter's already-calculated results; it must not compute a different base-case monthly cost. For Sensitivity, Filter (or a shared pure cost-calculation function owned by Filter) recomputes each requested monthly-volume scenario, holding every other assumption constant. No separate formula in Setup or Views.

## Interaction and module handoff

1. **Startup:** Read the configured manifest location. Ask Loader to validate manifest/schema/file hashes, report sample/full status and return eligible regions for the active service. No network download at app startup.
2. **Validate input:** Parse region selection, Decimal budget and nonnegative integer workload fields. Show field-level errors and mark previous results stale when inputs are invalid. Do not show earlier estimates as current.
3. **Load once per relevant slice:** For a nonempty valid region selection, call `load_slice(manifest_path, LoadRequest(service="bedrock", regions=..., columns=..., purpose="comparison"))`. The requested columns include those used by Filter/Views: source type, model/provider/version, `region_normalized`, token direction, normalized rate, pricing mode, cache/tier/commitment context and any required offering identifiers. Loader adds required provenance/status fields. The column set is agreed with the Loader owner rather than hard-coded in two places.
4. **Important empty-region rule:** `03-loader-siyao.md` defines `LoadRequest(regions=())` as **all available**, while `04-filter-tianna.md` defines an empty UI region selection as **no matches**. Setup must **short-circuit** an empty UI selection: show a prompt to select a region and do not call Loader with an empty region tuple. An explicit “All regions” control must expand into the available region codes.
5. **Filter:** Pass the loaded slice, selected regions, total input/output tokens and optional budget to Filter. It constructs eligible, unambiguous model configurations and returns filtered results and counts. Setup does not pair Bedrock price rows or convert token units.
6. **Display:** Pass the same filtered result, active assumptions and version metadata to both Compare and Sensitivity. Preserve missing external quality/latency evidence as `Not available`. Do not claim cheapest means best.
7. **Reactivity:** Changes to budget, token counts, monthly requests or sensitivity scenarios require **no raw-file read**. A region/service change can request another cached slice; explicit revision activation revalidates and refreshes the cache. Never combine rows from separate revisions silently.

The `04-filter-tianna.md` budget is based on the **total entered workload**. In Bedrock, Setup derives that total from per-request tokens and expected monthly requests; do **not** treat “1,000 tokens/request” as “1,000 total tokens.”

## Local environment and run contract

The coding agent builds the local runnable entry point after the team approves this specification. Required stack follows the existing component plans: **Python 3.11, `uv`, pandas, DuckDB, PyArrow/Parquet, Streamlit, Plotly**, plus a test runner such as pytest. Define dependencies once in the team repository (`pyproject.toml` and lockfile). The app needs no AWS account or API credentials to download the published public offers; access to the private GitHub repositories does require the user's own GitHub permissions.

From a laptop, the documented first-time sequence is:

```bash
mkdir -p ~/dso576
cd ~/dso576
# Skip either clone if the directory is already present.
git clone https://github.com/mumaniu3/dso576-project-T10.git
git clone https://github.com/USC-DSO-576-PS/dataset_aws-price-list.git
cd dataset_aws-price-list
uv run python download_data.py
```

The course downloader fetches **11 files**, but Data only prepares the **four** in-scope price CSVs specified in `02-data-tianshu.md`. Raw files remain local and are not committed. Do not run `--small` for final EC2 work or fetch the huge all-region EC2 sheet. If the download script fails, use the dataset README's browser route. If a clone already exists, update or reuse it rather than cloning into an occupied path.

**Proposed integration convention (must be agreed with Data and Loader owners):** Set `AWS_RAW_DATA_DIR` to `~/dso576/dataset_aws-price-list/data`, and point `AWS_PREPARED_MANIFEST` to the manifest created by the Data pipeline, proposed as `~/dso576/dso576-project-T10/data/cleaned/manifest.json`. The Data component—not Setup—converts the four raw CSVs to the prepared Parquet/JSON outputs and atomically publishes a validated manifest. Configure both paths in one application configuration; do not hard-code a teammate's home directory. File naming/manifest schema are pending agreement in `02-data-tianshu.md` and `03-loader-siyao.md`.

Once the coding agent has produced the app, the proposed launch/test commands **from the team repository** are:

```bash
uv sync
uv run python -m pytest -q
uv run streamlit run app.py
```

`app.py`, `pyproject.toml`, the manifest builder and the test suite are **implementation deliverables to create**, not files asserted to exist now. The app must show actionable setup guidance when dependencies, manifest or prepared outputs are missing. Do not automatically perform multi-hundred-MB downloads merely because someone opens the page.

## Edge cases and safety

| Situation | Required setup behavior |
| --- | --- |
| No selected regions | Prompt to select a region; no Loader query and no fabricated results |
| Selected region not in the prepared baseline | Explain unavailable region, preserve other controls, no silent replacement |
| Negative/noninteger tokens or requests; negative/unparseable budget | Field-level error; no current estimates until corrected |
| Valid zero token usage or zero budget | Accept; Filter may return legitimate `$0` results or no matches |
| No eligible Bedrock input/output pair | Show excluded/unresolved count and a no-match explanation; do not guess the missing direction |
| Sample data | Prominent development label; never present sample EC2 prices as final Reserved/population results |
| Missing/invalid manifest or mismatch of dataset revisions | Stop comparison and display the exact setup/validation error; never switch to synthetic production-style prices |
| New AWS `current` publication appears | Keep the activated, traceable snapshot until a user explicitly runs the data refresh/pipeline |
| Missing benchmark quality/latency | Keep the AWS price comparison; show `Not available` for outside evidence |
| Large request | Respect Loader's memory budget and its suggestion to narrow region or columns |

## Build order and “done when” tests

Build this component **after agreeing on the Data-to-Loader manifest contract**, and before wiring the full application:

1. Implement configuration discovery, manifest error messages and immutable prepared-source selection.
2. Implement `SetupSelection`, defaults, field-level validation and token-total derivation.
3. Wire Loader → Filter → Views using one shared state, with the empty-region short-circuit.
4. Add refresh/cache coordination and setup/validation recovery screens.
5. Run the independent checks below on tiny **explicitly marked synthetic fixtures**, then test a complete full-data baseline. Synthetic fixtures are for tests only, never normal production results.

| Independent check | Expected result |
| --- | --- |
| Opening Bedrock defaults | Region `us-east-1`, budget unset, `1,000` requests/month and `1,000` tokens each direction per request; Filter receives `1,000,000` input and `1,000,000` output tokens |
| Two matching Bedrock rates: input `$1/1M`, output `$3/1M` | Filter computes `$4.00` for the default month; a `$3.99` budget excludes it and `$4.00` includes it |
| Double monthly requests to `2,000` | Totals become `2,000,000` each and monthly cost becomes `$8.00`, with no raw-file reload; both views agree |
| Sensitivity at `500`, `1,000`, `2,000` requests | With the same rates/tokens per request, expected monthly costs are `$2`, `$4`, `$8` |
| Clear all selected regions | Zero matches; no call with `LoadRequest(regions=())` |
| Re-select unchanged region and adjust budget only | Loader uses existing slice; Filter and displayed matching count update consistently |
| Invalid or missing manifest | Clear failure and recovery message; no normal result/table falsely presented |
| Sample revision and source version | Sample label and exact source version are displayed; no mixed-version output |
| No matching configurations | Compare shows its no-match message; Sensitivity shows no misleading chart |
| Source consistency | Provenance/version details agree with Loader; no per-view refresh or separate price computation |
| Full local run | Record load time, repeated-interaction time and peak memory; confirm no reparse of raw EC2 CSV on every click |

## Later cloud deployment

Keep the same component interfaces. Replace local manifest and Parquet paths with authenticated, read-only object-storage paths; pin an immutable dataset revision for each deployment. Publish new validated revisions through a separate data pipeline, then explicitly activate them. Isolate UI session state per user and use revision-keyed read-only caches. Restrict data-upload access and never place private customer usage exports, AWS secrets, or raw data in the public app/repository. Cloud hosting is a **later plan**, not required for this component specification to run locally.

## Open integration decisions (assign before the final one-shot prompt)

1. **Team product scope:** Bedrock-only MVP, EC2-only MVP, or both? `05-views-alicia.md` currently covers Bedrock; any EC2 UI must be added or deliberately excluded from the final vision.
2. **Manifest contract:** Data currently leaves output filenames unresolved; Loader proposes Parquet plus JSON metadata. Agree on the schema, exact location and owner of the manifest before claiming a runnable workflow.
3. **Bedrock eligible modes:** Confirm final standard/uncached/source/tier filters with Filter and Views; do not merge mismatched modes or model versions.
4. **Views' scenario costs:** Agree that Filter's pure cost-calculation function supplies both base-case and Sensitivity values, so Views has no independent financial formula.
5. **Documentation references:** The Loader document refers to `02-data.md`; the actual team's file is named `02-data-tianshu.md`. Keep references or integration filenames consistent.

**Completion criterion:** A fresh coding agent can open the app with a validated manifest, see exactly one selected published price baseline, enter a workload, and obtain consistent Bedrock Compare/Sensitivity outputs without guessing UI defaults, reading raw files on every interaction, or inventing missing prices.
