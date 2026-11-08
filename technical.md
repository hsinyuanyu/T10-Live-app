# Technical Documentation

## Repository purpose

This repository contains documentation, sample files, and a Python script for working with AWS Price List Bulk API offer files. The data covers AWS services including EC2, RDS, S3, Lambda, SageMaker, and Bedrock.

## Intended audiences and decisions

### Audience 1: FinOps analyst at a technology company

This audience needs to choose an AWS region, instance type, operating system, and purchase option for a workload while controlling cloud costs. The dataset can support list-price comparisons using fields such as `Instance Type`, `vCPU`, `Memory`, `Physical Processor`, `Region Code`, `TermType`, `LeaseContractLength`, `PurchaseOption`, `Unit`, and `PricePerUnit`.

The likely product is a comparison view or calculator for comparable EC2 configurations. It should separate on-demand and reserved pricing, normalize units carefully, and show the selected file version and assumptions.

### Audience 2: AI product manager selecting a production model

This audience needs to choose a Bedrock model and region for an application while estimating token costs. The Bedrock files provide model, provider, inference type, region, input-token, output-token, cached-token, and batch-token pricing.

The likely product is a model-and-region comparison that estimates cost for a stated workload. Price alone is not enough to select a model: quality, latency, context limits, availability, and task performance require additional sources or testing.

Both audiences are suitable because they face concrete pricing decisions that this dataset can inform, while neither should treat the published prices as actual customer bills.

## Download and setup result

The repository was connected to the private team repository and the project documentation was pushed successfully. The download workflow is documented in `download_data.py` and `README.md`; downloaded files are stored locally in `data/`.

The repository contains the expected sample files and download script. The local `data/` directory contains the downloaded offer files and is excluded by `.gitignore`. The full download is large, so keeping it local is intentional.

## Blockers and recovery notes

No data-processing blocker is currently known. A Git configuration permission issue initially prevented updating the local remote, but the repository was subsequently connected and the files were pushed successfully. GitHub later reported that the repository had moved to `dso576-project-T10`; the local remote was updated to that canonical URL.

Potential teammate blockers include an unaccepted GitHub invitation, missing push permission, or missing `uv` installation. If cloning or pushing fails, first accept the invitation and authenticate with GitHub, then retry. The browser download route described in the overview is an alternative if the scripted download is blocked by a network.

## Repository contents

- `download_data.py` downloads the full offer files into the local `data/` directory.
- `sample/` contains small CSV samples for inspecting the available tables without downloading the full dataset.
- `data_overview_aws-price-list.md` documents the source, file structure, fields, and known limitations.
- `README.md` provides setup and usage instructions.
- `.gitignore` excludes downloaded data and local Python artifacts from Git.

## Data acquisition

The download script retrieves public AWS offer files over HTTPS. No AWS account, access key, or API credentials are required. Run it from the repository root with:

```bash
uv run python download_data.py
```

The full download is large, so it should remain local. The `data/` directory must not be committed or pushed.

## Checks completed

- Confirmed the repository remote points to the private team repository.
- Confirmed the working tree is clean after pushing the documentation.
- Confirmed `data/` is ignored by `.gitignore` with `git check-ignore`.
- Confirmed only intended Markdown documentation was staged for the documentation commits.
- Reviewed the sample directory and the documented eleven-file download plan.
- Reviewed the data dictionary and limitations in `data_overview_aws-price-list.md`.

## File formats and structure

The downloaded files are primarily CSV files, with JSON index files used to identify available offers and versions. Each CSV row represents a price for one product, purchase term, rate, region, and effective date. Files differ by AWS service and may contain service-specific columns.

Important shared fields include `SKU`, `OfferTermCode`, `TermType`, `EffectiveDate`, `PricePerUnit`, `Unit`, `Currency`, `Location`, `Region Code`, `usageType`, and `serviceName`. The same product can have multiple rows because operating system, region, purchase model, reservation term, and payment option can change the price.

## Recommended analysis workflow

1. Inspect the corresponding file in `sample/` before loading a full file.
2. Read CSV columns as strings initially; parse numeric and date fields explicitly.
3. Filter by service, region, term type, unit, and operating system before comparing prices.
4. Treat `PricePerUnit` as a rate whose meaning depends on `Unit`; do not add values with different units.
5. Preserve the source filename and effective date when combining files or comparing versions.
6. Check missing values and column differences across services and historical versions.

## Technical limitations

These are published list prices, not customer-specific billed prices. Negotiated discounts, credits, taxes, and some AWS pricing products are not represented. Historical files can have different columns, and older EC2 snapshots may not contain `Region Code`; the region may need to be inferred from the filename or `Location`. Comparisons should therefore document the selected file version, region, term, unit, and assumptions.

## Relevant implementation options

- Use the supplied Python downloader and pandas for a reproducible local workflow.
- Start with the sample CSVs for schema exploration, then process only the full files needed for a specific question.
- Build an EC2 regional and purchase-term comparison for the FinOps audience.
- Build a Bedrock token-cost estimator for the AI product audience.
- Keep the two analyses separate unless a clearly defined workload justifies comparing infrastructure cost with model-serving cost.
- Use a database or columnar format for repeated analysis if CSV memory usage becomes a constraint; retain the original files and metadata for traceability.

## Open questions for the team

- Which audience and decision should become the team’s primary project?
- What concrete workload, usage volume, and time horizon will define the cost estimate?
- For EC2, which regions, instance families, operating systems, and commitment terms are comparable?
- For Bedrock, how will the team measure model quality, latency, context limits, and availability in addition to token price?
- Which version stamp and download date should be used as the project’s analytical baseline?
- How should prices with different units, tiers, upfront fees, and hourly charges be normalized?
- What external sources or benchmarks are needed for actual discounts, performance, or model quality?
- How will the team validate results after AWS publishes a new offer version?

## Version-control requirements

Before committing, run:

```bash
git status
git diff --cached --name-only
```

Stage only documentation and source files needed for the project. Confirm that files under `data/` are ignored and absent from the staged-file list. Commit the technical documentation with a descriptive message and push it to the team repository.
