# Module 9 Individual Audit — Team 10 Bedrock Cost Comparison

**Auditor:** hsinyuanyu  
**Date:** 2026-10-26  
**Feature audited:** Compare and its linked Sensitivity view  
**Number checked:** Gemma 3 4B estimated monthly cost

## Part 1 — Does the feature help its user?

### User and decision

I acted as an AI product manager at a software company deciding which Amazon Bedrock model and AWS region deserve application testing for a defined workload. I need a comparable cost shortlist, while recognizing that the lowest list price does not establish model quality, latency, or production availability.

### Task and what I saw

I used the app's default workload: `us-east-1`, 1,000 input tokens/request, 1,000 output tokens/request, and 1,000 requests/month, with no budget cap. The Compare view returned **147 eligible configurations**, showed 50 rows per page over three pages, and sorted by exact monthly cost. The table exposed provider, model, region, source, inference mode, serving scope, tier, normalized input/output prices per million tokens, cost/request, cost/1,000 requests, and monthly cost.

The Gemma 3 4B row showed input `$0.0400000000/1M`, output `$0.0800000000/1M`, `$0.0001200000/request`, `$0.1200000000/1,000 requests`, and **`$0.12/month`**. Gemma 3 4B appeared twice at that same cost, with tiers `standard` and `standard (explicit on-demand context)`. The publisher-details expander exposed the source file, offer version, publication date, rate codes, SKUs, and source-row IDs. The snapshot expander identified offer `20261016210806` for `bedrock_service_all.csv` and offer `20261012084008` for `bedrock_foundation_models.csv`.

I also opened Sensitivity. It stated that it plots the lowest-cost 10 configurations from the current base-case shortlist, holding tokens/request and constraints fixed. Its request-volume field accepted `500, 1000, 2000, 5000`; after pressing Enter, the chart updated and included a 5,000-request point. The chart legend distinguished duplicate model rows with short configuration hashes, for example two Gemma 3 4B series ending `59fcf6` and `c4847f`, but did not show their different tier/pricing context.

### What helped, what would help more, and what could mislead

**Helpful:** The cost columns make like-for-like price screening practical, and the workload assumptions are visible above the results. The public-list-price warning is prominent. Snapshot lineage and publisher identifiers support traceability. The Non-AWS evaluation metrics section says quality, speed, and latency are `Not available`, rather than implying that missing evidence is zero. The sensitivity view supports custom request volumes, including the 5,000-request case I tried.

**What would help more:** The table has no control to pin selected configurations for sensitivity analysis. The chart automatically takes the ten lowest-cost configurations, which can omit a more expensive candidate the PM wants to evaluate for quality or other product reasons. Also, when similar configurations appear more than once, short hashes distinguish chart lines technically but do not explain the pricing context that distinguishes them.

**What could mislead:** The 147 count is a configuration count, not a distinct-model count. Gemma 3 4B appears twice at the same cost with different tier context, so a PM could mistake configuration rows for separate model choices. The app mitigates the bigger price-only risk with its warning and explicit unavailable-metrics note; I would still treat the table as a cost filter, not a model recommendation.

## Part 2 — Is the number correct?

### Number and expectation

I checked the app's Gemma 3 4B `us-east-1` standard, on-demand monthly estimate at 1,000 input and 1,000 output tokens/request × 1,000 requests/month. Before calculating, I expected about `$0.10–$0.15/month` (roughly ten cents), since each direction uses one million monthly tokens and the listed per-million rates are only a few cents.

### Independent calculation from the raw AWS data

I ran `check_bedrock_cost.py` against the full raw `bedrock_service_all.csv` from the team's AWS dataset checkout. The separate script skips the five AWS metadata rows, selects exactly one `Gemma 3 4B` input and output row in `us-east-1` with standard tier, OnDemand term, and `1K tokens` unit, then recomputes the total with `Decimal`:

| Direction | Raw AWS rate | Monthly tokens | Charge |
|---|---:|---:|---:|
| Input | `$0.0000400000` per 1K tokens = `$0.04` per 1M | 1,000,000 | `$0.0400000000` |
| Output | `$0.0000800000` per 1K tokens = `$0.08` per 1M | 1,000,000 | `$0.0800000000` |
| **Total** |  |  | **`$0.1200000000` → `$0.12` to cents** |

The raw input row is SKU `9E5YX7K8ZEAFZRC4`, RateCode `9E5YX7K8ZEAFZRC4.JRTCKXETXF.6YS6EN2CT7`; the output row is SKU `ZCDMM2PEJVU7TQQH`, RateCode `ZCDMM2PEJVU7TQQH.JRTCKXETXF.6YS6EN2CT7`. Both are from `bedrock_service_all.csv`, offer `20261016210806`. The calculation is `(1,000,000 / 1,000 × $0.00004) + (1,000,000 / 1,000 × $0.00008) = $0.12`.

### Comparison and diagnosis

The app displayed **`$0.12/month`** and the independent raw-data calculation is **`$0.1200000000`**, which rounds to `$0.12`. They agree. There is no mismatch to diagnose for this configuration and workload.

## Part 3 — Change requests

### CR-05: Let the user pin candidates for sensitivity analysis

- **Part:** Compare shortlist and Sensitivity chart
- **Evidence:** With the default `us-east-1` workload, Compare returned 147 eligible configurations. Sensitivity said it uses the lowest-cost 10 and provided no control to select rows. I expected to stress-test candidates chosen for product evaluation, including a candidate that may not rank in the cheapest ten; the app only plotted its automatic low-cost subset.
- **Change:** Add a user-controlled selection or pin action to Compare and use those selected configurations in Sensitivity. Keep the full Compare results available and state any chart limit.
- **Priority:** medium
- **Status:** open

### CR-06: Allow workload-specific sensitivity volumes — declined after live test

- **Part:** Sensitivity scenario inputs
- **Evidence:** This request was drafted before the professor build was available. Live testing showed that the `Sensitivity requests/month` field accepts custom whole-number volumes: I entered `500, 1000, 2000, 5000`, pressed Enter, and the chart updated through 5,000 requests/month.
- **Change:** No change needed; the requested custom-volume behavior is already present.
- **Priority:** low
- **Status:** declined — live UI test confirmed the feature already exists.

### CR-07: Identify pricing context in Sensitivity series

- **Part:** Sensitivity chart labels and hover details
- **Evidence:** In the default `us-east-1` shortlist, Gemma 3 4B appears as two configurations with the same displayed `$0.12/month` cost but different tier context (`standard` and `standard (explicit on-demand context)`). Sensitivity showed two Gemma 3 4B lines whose labels ended in short hashes `59fcf6` and `c4847f`; the labels and hover details did not identify the tier/context difference. I expected to tell which priced configuration each line represents without matching opaque hashes back to the Compare table.
- **Change:** Include tier and explicit pricing/commitment context in each Sensitivity series label or hover details, while retaining the short configuration ID for exact traceability.
- **Priority:** medium
- **Status:** open
