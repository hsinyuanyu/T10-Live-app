# Build report

Status: complete

- Builder model(s): Codex GPT-6.1 (gpt-6.1-sol), medium reasoning, one fresh session; no subagents or model switches. (Coordinator: corrected from "Codex (GPT-6)".)
- Dates and sessions: 2026-10-20, one build session. No separate cross-platform fix session (the build instructions already required macOS/Windows fresh-clone support; see Coordinator).
- App repo: USC-DSO-576-PS/project-prof-build-T10
- Run command (from a fresh clone): `uv sync --locked --python 3.11`, then `uv run streamlit run app.py`. macOS and Windows PowerShell commands are in README.md.

## Outcome

The local Streamlit product runs with a committed full-data Bedrock snapshot, shared Compare/Sensitivity inputs, exact Decimal pricing, inclusive optional budgets, pagination, diagnostic exclusions and auditable source details. No AWS account or raw download is needed for ordinary startup. Complete real sources produce 147 standard configurations in us-east-1 under the default workload. All 41 tests pass. Quality and latency remain Not available. Unsupported dimensions are conservatively excluded, so this is a comparable supported-rate shortlist rather than an exhaustive catalog. Native macOS/Windows execution was unavailable; portable dependencies, code and run instructions are provided. No cloud deployment was requested.

## Asked or guessed

No questions were asked. Higher-priority setup instructions resolve the prompt conflicts below.

| # | Prompt text (quote, with section) | What the builder did | Effect on the app | Cause (PROMPT / BUILD / UNSURE) |
|---|---|---|---|---|
| 1 | Data integration: “Use `data/cleaned/` only for generated local outputs and keep it in `.gitignore`.” User: “Commit ... only the condensed data files the app reads.” | Keep generated `data/cleaned/` ignored; copy its complete validated output set to committed `data/snapshot/`, the configured app default. | Fresh clone runs without downloading; CLI still defaults to the prescribed integration directory. | BUILD (coordinator retag: the conflict comes from the build protocol's commit-the-condensed-data rule, not the prompt) |
| 2 | Data acquisition: “Raw sources stay in the dataset repo”; “Use the course downloader ... (or ... browser-download fallback).” User: “Keep raw downloads in `data/raw/` (git-ignored).” | Import the course downloader from the provided sibling repo and invoke its original download function/URLs for only the two Bedrock files, saving to ignored app `data/raw/`. | No sibling writes, EC2 or unrelated downloads; app itself never downloads. | BUILD (coordinator retag: raw-in-`data/raw/` is a build-protocol rule; the prompt puts raw files in the dataset repo) |
| 3 | Matching: “compare only explicitly identifiable context”; “compatible standard tier/feature context.” | Recognized Marketplace standard/token dimensions and explicit on-demand Feature support standard context; Amazon uses explicit standard tier or on-demand Feature. Preserve exact feature/tier and global/regional/unspecified serving scope in pairing keys; reject unsupported contexts. | Conservative pair matching; no priority/batch/flex/global-region merges. Blank providers display Not available. Coordinator: because Amazon-billed rows with `service_tier=standard` (the `*-mantle-*-standard` usage types) and rows with `Feature=On-demand Inference` are kept as separate contexts, 33 Amazon-billed models show up twice in the 147 us-east-1 rows (66 rows) at identical prices. The two rows differ only in the Tier column and the publisher IDs, and both lines can appear in the top-10 Sensitivity chart. | PROMPT |
| 4 | Normalization: “Unrecognized dimensions are flagged rather than guessed.” | Whitelist documented generic input/output/response token patterns, including documented Batch prefix; retain cache, long-context, underscore, Token Count and modality variants as noncomparable if not explicitly supported. | Some valid AWS prices are omitted with visible reasons. No fuzzy matching or invented rates. | PROMPT |
| 5 | Compare: “monthly figures rounded to 2 decimals only for display”; first-open inputs and scenarios listed without widget design. | Use text controls to preserve Decimal budget and integer validation; comma-separated scenario input; default Decimal display rounding, exact digits for smaller money. Validate field values and remove calculated views on errors. | Exact budget boundaries and no misleading small-cost zeros. | PROMPT |
| 6 | Loader: “MAX_LOADED_ROWS=100000”; “small bounded cache.” | Set 16 read-only slice entries and 8 manifest/region entries, DuckDB one thread; validate output fingerprints/hashes before reuse. | Token/budget changes reuse Parquet slices; no raw reads on reruns. | PROMPT |
| 7 | “benchmark memory on actual data”; “reliably on a laptop.” | Use cross-platform psutil sampled RSS and Streamlit AppTest for measured UI timings; separately run a free-port HTTP server and stop it. | Actual shared-host measurements, with sampling and browser/native-platform limits disclosed. | PROMPT |

## Use cases

| # | Use case | Result (works / partly / fails) | Cause (PROMPT / BUILD / UNSURE / —) | Evidence |
|---|---|---|---|---|
| 1 | Shortlist: us-east-1, 1K input + 1K output, 1K monthly requests | works | — | 147 complete configurations ranked by exact monthly cost; UI table, details and chart verified with AppTest. |
| 2 | Constrain: optional maximum monthly cost | works | — | $3.99 excludes synthetic $4 cost; $4 includes it. Real UI zero budget shows exact no-match message. Invalid input clears results. |
| 3 | Stress-test: 500/1K/2K requests with fixed tokens | works | — | Synthetic $2/$4/$8 verified, with $4 base-case budget still allowing the $8 scenario. Real UI chart uses the lowest-cost 10 current configurations. |

## The prompt's "done when" checks

| Check | Result | Note |
|---|---|---|
| 1 Actual headers/metadata + tiny fixture | PASS | Inspected both full headers, five metadata rows and field distributions; missing-column diagnostic fixture. |
| 2 1K normalization / priority | PASS | Exact 0.2625000 Decimal; priority retained. |
| 3 Non-token, duplicate, unknown, accounting | PASS | hour/TextUnit/TPM, invalid prices, raw accounting and duplicate tests; full-source counts reported. |
| 4 Manifest and loader | PASS | Projection, regions, provenance uniqueness, empty schema, unknown column/region, missing/hash errors. |
| 5 Pair matching | PASS | Complete pair survives; incomplete, mismatched tiers/modes/scopes/sources and ambiguous inputs excluded. |
| 6 Money and scenarios | PASS | Exact $4/$0.004/$4; scenarios $2/$4/$8. |
| 7 Budget, empty, pagination | PASS | Inclusive unrounded boundaries, zero use, 51 rows into 50+1, exact empty text. |
| 8 Setup/cache | PASS | No Loader call for empty selection; volume/budget updates reuse one slice; both views share calculated state. |
| 8a Region discovery | PASS | Sorted unique eligible codes, cache one discovery per revision, no full-table materialization, no-region UI. |
| 9 Snapshot/sample safety | PASS | Broken hashes/revision/schema/quality fail closed, mixed offers rejected, SAMPLE blocks comparisons. |
| 10 Real data/UI/performance | PASS | Raw rate IDs, unit normalization, model/region, metadata and row hashes independently audited; AppTest + HTTP smoke; measured performance below. |

## Real-world operation

- Data size used (rows, MB) and whether it is the full real size: 20,341 raw rows, 9.381 MB, both full Bedrock offers (not samples). 863 eligible US-East rates loaded; 36 available eligible-rate regions. 11,540 eligible rates and 8,801 retained noncomparable records across all regions.
- Start-up time: 0.642 s Streamlit in-process UI harness; 0.194 s cold loader/filter. Actual HTTP readiness 1.132 s on free port 50331; server stopped.
- Slowest interaction, and how slow: 0.127 s maximum of 30 warm workload/budget updates (median 0.124 s); UI request-volume change 0.236 s. Preparation 2.689 s.
- Memory at peak: preparation child sampled RSS 386.4 MB; UI/benchmark process 226.4 MB (20 ms psutil sampling, may miss instantaneous spikes). Measurements made on shared Linux host; native macOS/Windows and browser paint timing unmeasured.

## Data

- Raw source: provided course dataset repo's downloader and its public AWS URLs for AmazonBedrockFoundationModels and AmazonBedrock; full CSVs saved only to ignored `data/raw/`. Offer versions 20261012084008 (published 2026-10-12T08:40:08Z) and 20261016210806 (published 2026-10-16T21:08:06Z). Actual newer AWS hashes differ from course September reference; lineage is preserved.
- Condensed files committed (name, rows, MB):
  - `data/snapshot/bedrock_prices.parquet`: 20341 rows, 5.593584 MB.
  - `data/snapshot/manifest.json`: metadata rows, 0.003028 MB.
  - `data/snapshot/provenance.json`: metadata rows, 0.002046 MB.
  - `data/snapshot/quality.json`: metadata rows, 0.002038 MB.
  - `data/snapshot/quarantine.parquet`: 0 rows, 0.014347 MB.
- `data/raw/` deleted: no; intentionally kept locally per user instruction, git-ignored and not committed. Generated `data/cleaned/` also ignored.

## Build problems not caused by the prompt

- The first `uv run` happened before local project configuration existed and selected an ancestor environment with read-only files. No data was downloaded in that attempt. Creating the project-local pyproject/venv resolved it.
- A tiny Marketplace test fixture initially disagreed between its pipe-delimited region and explicit Region Code; the newly added conflict flag correctly excluded it. Fixed the fixture to agree.
- A display edit briefly introduced Python 3.11 f-string quote syntax incompatibility; the UI test caught it and it was corrected. A Plotly width keyword warning was corrected using the pinned Streamlit API.
- Fresh-clone verification passed in a new TMPDIR checkout: locked dependency install, all 41 tests (3.40 s), healthy HTTP server (0.612 s, free port 41905, stopped), and 147 real configurations without raw or generated cleaned inputs. Only the committed snapshot was used. No verified product blocker remains.

## Coordinator

- Fresh clone starts: yes. Checked on 2026-10-20 with `git -c core.symlinks=false clone` (the way Windows clones) into a clean directory on Linux: `uv sync --locked --python 3.11` worked and 41/41 tests passed (3.3 s). `uv run streamlit run app.py --server.port 8600` returned `/_stcore/health` ok, then the server was stopped. Streamlit AppTest showed the title, the exact list-price banner, offer versions and dates, the region selector (36 regions, default us-east-1), Compare/Sensitivity tabs, the table and the Plotly chart. The app needs neither the dataset repo nor raw files.
- Use cases re-walked: 3/3 work. (1) Shortlist with the defaults: 147 us-east-1 configurations (101 Amazon-billed, 46 Marketplace), shown 50 per page over 3 pages and sorted by exact monthly cost. 564 rate rows were excluded as nonstandard and 5 configurations as incomplete. Spot checks against the raw CSVs and their hashes matched the manifest: DeepSeek v3.2 0.00062/0.00185 per 1K → 0.62/1.85 per 1M; Llama 3.3 70B 0.72/0.72; Nova Pro 0.80/3.20; Claude Haiku 4.5 Marketplace global 1.00/5.00 and regional 1.10/5.50 per 1M. (2) Constrain: a $0.50 budget leaves 32 rows and a $0 budget shows exactly "No model configurations match the current filters." with no chart. A negative budget and a non-integer request count give field errors and the table disappears. Clearing the regions shows no matches. Three regions give 4 pages. (3) Stress-test: the chart has 10 lines at x = 500/1000/2000 (Voxtral Mini 0.04/0.08/0.16 USD), and the $1 base budget is not reapplied. Custom scenarios (100, 5000) re-plot.
- Data used vs the prompt: the two Bedrock CSVs the prompt names, fetched fresh through the course downloader's functions and URLs (AmazonBedrockFoundationModels offer 20261012084008, 2026-10-12, and AmazonBedrock offer 20261016210806, 2026-10-16). These are newer than the course's September reference, so their hashes differ from the dataset repo's expected values; the prompt allows a newer offer, and the raw hashes match the build's manifest. Full size, not samples: 20,341 raw rows (9.4 MB) → 11,540 eligible rates and 8,801 retained noncomparable records, 0 quarantined. EC2 was not downloaded.
- Size: the largest committed file is `data/snapshot/bedrock_prices.parquet` at 5.6 MB (the cleaned, typed form of all 20,341 rows, not the raw CSVs); the git pack is 4.05 MiB. No raw CSVs or `data/raw/` in git, and no tokens, credentials, emails or personal paths. `one-shot-prompt.md` is byte-identical to the team's prompt; `change-requests.md` is the unchanged template.
- Build-setup notes that affected entries: Asked-or-guessed #1 and #2 are tagged BUILD because the build setup requires committing the condensed data the app reads (here `data/snapshot/`; `data/cleaned/` stays ignored as the prompt says) and keeping raw downloads in the app's git-ignored `data/raw/` (the prompt says raw files stay in the dataset repo). The dataset repo was cloned as the sibling `../dataset_<slug>` the prompt expects. The builder model name was corrected to Codex GPT-6.1 (gpt-6.1-sol), medium reasoning.
- Cross-platform: the build instructions already required a fresh clone to install and run on macOS and Windows, so there was no separate cross-platform fix session and nothing was changed afterwards. Current main has no symlinks, no Linux-only modules (systemd, cgroup, /proc, fcntl, resource) in the app, tests or scripts, memory sampling uses cross-platform psutil, and README has macOS and Windows PowerShell run commands. Verified on Linux with symlinks disabled as above; native macOS and Windows runs were not done by the coordinator.
- Finding for the team to audit: 33 Amazon-billed models appear twice in the 147 us-east-1 rows (66 rows) at identical prices. The app keeps two SKU families as separate contexts: rows with `service_tier=standard` (the `*-mantle-*-standard` usage types) and rows with `Feature=On-demand Inference`. The two rows of each pair differ only in the Tier column and the publisher IDs, and both can take a line in the top-10 Sensitivity chart. This follows the prompt's rule to preserve tier/feature contexts and not deduplicate by model name (Asked-or-guessed #3); the team may want to decide whether the two families are the same standard context.
