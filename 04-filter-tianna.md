# Tianna — Price filter

## Purpose and design

Help users find EC2 configurations and Bedrock model offerings within a budget and inspect the matching data. Use separate EC2 and Bedrock results because their cost measures differ. Compare AWS public list-price estimates in USD; customer discounts, credits, taxes, and unmodeled charges are excluded.

Calculate comparable costs before filtering. Keep cost calculation and filtering independent of the screen so the same rules can be checked without opening the app. The filter must consume prepared data rather than reload or clean raw CSVs on each interaction.

## Starting view and controls

| Setting | EC2 | Bedrock |
| --- | --- | --- |
| Cost measure | Estimated monthly compute cost | Estimated total token cost for the entered workload |
| Usage inputs | Instance count: 1; hours per month: 730 | Total input tokens: 1,000,000; total output tokens: 1,000,000 |
| Editable assumptions | Positive integer instance count; hours from 0 through 744 | Nonnegative integer input/output token totals; these are workload totals, not tokens per request |
| Budget | Optional nonnegative maximum in USD; initially unset, so all eligible estimates appear | Same |
| Region | Initially us-east-1; allow either supplied EC2 region or both | Initially us-east-1; allow regions present in eligible prepared data |
| Comparable offering | On-Demand, Linux, Shared tenancy, Used capacity, no preinstalled software, Compute Instance, Hrs unit | Uncached, non-batch, non-provisioned standard token inference; input and output must have matching model/version, region, source, and pricing context |

Use numeric inputs for usage and budget. Label the Bedrock estimate as the entered workload total, with no implied monthly period. Show the assumptions beside each result. EC2 estimates cover compute only, excluding storage and network charges. Reserved EC2 offers are outside this filter's initial scope because they require paired upfront/hourly costs and commitment assumptions.

## Calculation and filter contract

The preparation component supplies source-aware, validated decimal prices and provenance using the fields in `02-data.md`. The calculation component returns eligible offering records with a stable offering identifier, comparable dimensions, assumptions, and an unrounded decimal `estimated_cost_usd`:

- EC2: hourly USD rate × instance count × hours per month. Preserve instance type, region, operating system, purchase term, tenancy, capacity status, software, rate identifier, and source version.
- Bedrock: `(input_tokens × input_usd_per_1m + output_tokens × output_usd_per_1m) / 1,000,000`. Use normalized per-million rates. Pair directions only within an explicitly matching model/version, region, source, tier, mode, and commitment context. Do not join offerings by approximate model names or mix the two source schemas without an approved identity mapping. Require one unambiguous input/output rate pair; retain unresolved offerings in the preparation report and exclude them from estimates.

The filter receives eligible offering records, selected regions, and an optional decimal maximum budget. Return the records whose region is selected and whose `estimated_cost_usd <= maximum_budget_usd`; an unset budget imposes no price restriction. Apply all constraints with AND; multiple selected regions match with OR. Return matching count and records in ascending unrounded cost, breaking ties by stable offering identifier. Do not mutate the source records.

Use decimal arithmetic from raw decimal strings. Compare the unrounded estimate to the budget; display estimates with at least two decimal places and enough additional precision to distinguish small nonzero costs. Show raw and normalized rates in the result details.

## Matching data shown

Show a matching-offering count and a paginated table of 50 records per page. Paginate after filtering and sorting; the count covers every match.

| Result | Columns |
| --- | --- |
| EC2 | Instance type, region, vCPU, memory, operating system, purchase term, hourly USD rate, instance count, monthly hours, estimated monthly USD cost |
| Bedrock | Model/version, provider if available, region, source, tier/mode, input and output USD per million tokens, entered input/output totals, estimated total USD cost |

Expose source filename, publisher rate identifiers, and offer version in row details for auditability. Model cost results do not establish model quality or performance. The view renders the returned records; it does not recalculate costs or independently implement the budget rule.

## Edge cases

- Empty matches: show zero matches, an empty table, and “No offerings match these selections.” Keep controls available for adjustment.
- Empty region selection: show no matches and prompt the user to select a region; do not silently interpret it as all regions.
- Missing, negative, or unparseable rates and unresolved units: exclude from estimates and report the excluded count/reasons from preparation; do not substitute zero.
- Valid zero rates and zero usage: retain zero-cost estimates and allow a zero budget.
- Negative budgets, invalid counts, or out-of-range hours: show validation beside the control; do not display a new estimate until corrected. Clear or mark prior results as stale.
- Missing Bedrock directions, ambiguous pairs, cache/batch/provisioned rates, or unresolved tiers: exclude and report; do not infer a substitute rate. A zero price is different from a missing price.
- No eligible prepared data: explain the missing input and show no estimates; never silently substitute sample data. Samples may support parsing checks, but production results use full in-scope source files.

## Build order and done-when checks

Build against the prepared-data contract first, then decimal cost calculations, then filtering/sorting, then controls and results. Use tiny invented fixtures for the following independent expected results:

| Check | Expected result |
| --- | --- |
| EC2 rates $0.02/hour and $0.10/hour, one instance, 730 hours | Estimates $14.60 and $73.00; a $20 maximum returns only the first |
| EC2 $0.02/hour, two instances, 100 hours | Estimate $4.00 |
| Bedrock input $1/million and output $3/million; 2 million input and 0.5 million output | Estimated total $3.50 |
| Maximum budget equals $3.50 | The $3.50 offering is included; a $3.5001 offering is excluded |
| No budget; two selected regions | All eligible offerings from those regions remain, ordered by cost |
| Valid zero price and a missing price | Zero is eligible; missing is excluded and reported |
| Bedrock input/output rows have different tiers or ambiguous duplicate directions | No combined estimate; exclusion reason is reported |
| 51 matching offerings | Count is 51; first page shows 50, second shows 1 |
| No matches or invalid controls | Empty-state or validation behavior matches the rules above |

For source-data verification, manually trace one eligible EC2 estimate and one unambiguous Bedrock input/output pair to their full raw source rows and recorded versions, and independently recompute their costs. Confirm that changing the budget updates both count and table consistently without rereading raw CSVs.
