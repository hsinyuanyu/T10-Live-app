# Change requests

Our team's log of what we found and what should change, kept in the top folder of our team repo
from Module 9 to Module 13. Pull before you edit it and push soon after.

- For each finding, copy the request template below to the end of this file, give it the next
  number and fill in every field.
- Never delete a request. When it is built, set its status to `built` with the commit; when the
  team decides against it, `declined` with the reason.
- When this file gets long, ask Codex to move the built and declined requests into a dated file
  in `change-requests-archive/` (for example `change-requests-archive/2026-11-02.md`) and leave
  only the open ones here. Numbers continue; never reuse one.

Request template:

```markdown
### CR-NN: short title

- **From:** name, YYYY-MM-DD
- **Part:** the feature, number or function
- **Evidence:** what you did and saw: the input, what you expected, what the tool gave
- **Change:** what should change, in a sentence or two
- **Priority:** high, medium or low
- **Status:** open
```

A filled request (from the class lottery app):

```markdown
### CR-01: chance above 100% with two slots

- **From:** Ana, 2026-10-21
- **Part:** `odds` (the chance of selection by wage level)
- **Evidence:** one person at Level I and one at Level IV, two slots. Both must be selected,
  so each chance is 1. `odds` gave 0.4 and 1.6.
- **Change:** select each person at most once (without replacement), so no chance passes 1.
- **Priority:** high
- **Status:** open
```

## Requests

<!-- Add new requests below this comment, at the end of the file, newest last. -->

### CR-01: Show unique-model count separately from eligible configurations

- **From:** tianshuhuang, 2026-10-25
- **Part:** Compare results summary
- **Evidence:** With the default workload, the app showed 147 eligible configurations in
  `us-east-1` and 150 in `us-west-2`. Some model names appeared multiple times because they had
  different configurations or tiers, but the summary displayed only the configuration count.
- **Change:** Display both the number of eligible configurations and the number of distinct
  models so users can understand their actual model choices.
- **Priority:** medium
- **Status:** open

### CR-02: Summarize model availability differences between regions

- **From:** tianshuhuang, 2026-10-25
- **Part:** Region selection and Compare results
- **Evidence:** When switching from `us-east-1` to `us-west-2`, the configuration count changed
  from 147 to 150, but the app did not summarize which models were unique to either region.
- **Change:** When comparing selected regions, show models shared between them and models
  available only in each specific region.
- **Priority:** medium
- **Status:** open

### CR-03: Show maximum monthly requests supported by the budget

- **From:** Siyao, 2026-10-26
- **Part:** Maximum monthly USD filter and Compare results
- **Evidence:** In us-east-1 with 1,000 input and 1,000 output tokens/request, 1,000 requests/month, Nova Micro's independently verified cost is $0.175/month. Budgets $0.17, $0.175 and $0.18 returned 5, 6 and 6 configurations respectively. The filter evaluates the entered request volume, but the result table provides no maximum request capacity for the entered budget. I want to know how much usage a fixed budget can support. At $0.18 and the same tokens/request, Nova Micro supports 1,028 whole requests: 1,028 cost $0.1799, while 1,029 cost $0.180075.
- **Change:** Add maximum whole monthly requests supported by the entered budget for each displayed configuration, using its exact unrounded per-request cost and rounding down. Keep tokens/request fixed and show the assumptions. Handle zero per-request cost explicitly rather than dividing by zero; a missing budget should leave capacity unset. This is an enhancement, not a correction to the verified cost calculation.
- **Priority:** medium
- **Status:** open

### CR-04: Show a traceable monthly token and cost breakdown

- **From:** Siyao, 2026-10-26
- **Part:** Compare monthly USD and calculation details
- **Evidence:** The Compare table shows normalized input/output rates and the final monthly amount. Its publisher details expose rate identifiers and offer metadata, but do not show monthly input/output token totals and the two component charges. During my Nova Micro check, I initially confused per-token and per-million units and estimated $175,000, then corrected my expectation to $0.175 before running the independent check. The check confirmed 1,000,000 input tokens costing $0.035 plus 1,000,000 output tokens costing $0.140; the displayed total is $0.18. I found this calculation breakdown useful for understanding the number.
- **Change:** Add per-configuration calculation details showing requests/month times input/output tokens per request, both monthly token totals, rates with explicit units, separate input/output charges, and the exact total alongside the rounded displayed total. Use the same active workload and preserve exact monetary values so users can trace unit conversion and reproduce the estimate.
- **Priority:** medium
- **Status:** open

### CR-05: Let the user pin candidates for sensitivity analysis

- **From:** hsinyuanyu, 2026-10-26
- **Part:** Compare shortlist and Sensitivity chart
- **Evidence:** With the default `us-east-1` workload, Compare returned 147 eligible configurations. Sensitivity said it uses the lowest-cost 10 and provided no control to select rows. I expected to stress-test candidates chosen for product evaluation, including a candidate that may not rank in the cheapest ten; the app only plotted its automatic low-cost subset.
- **Change:** Add a user-controlled selection or pin action to Compare and use those selected configurations in Sensitivity. Keep the full Compare results available and state any chart limit.
- **Priority:** medium
- **Status:** open

### CR-06: Allow workload-specific sensitivity volumes

- **From:** hsinyuanyu, 2026-10-26
- **Part:** Sensitivity scenario inputs
- **Evidence:** This request was drafted before the professor build was available. Live testing showed that the `Sensitivity requests/month` field accepts custom whole-number volumes: I entered `500, 1000, 2000, 5000`, pressed Enter, and the chart updated through 5,000 requests/month.
- **Change:** No change needed; the requested custom-volume behavior is already present.
- **Priority:** low
- **Status:** declined — live UI test confirmed the feature already exists.

### CR-07: Identify pricing context in Sensitivity series

- **From:** hsinyuanyu, 2026-10-26
- **Part:** Sensitivity chart labels and hover details
- **Evidence:** In the default `us-east-1` shortlist, Gemma 3 4B appears as two configurations with the same displayed `$0.12/month` cost but different tier context (`standard` and `standard (explicit on-demand context)`). Sensitivity showed two Gemma 3 4B lines whose labels ended in short hashes `59fcf6` and `c4847f`; the labels and hover details did not identify the tier/context difference. I expected to tell which priced configuration each line represents without matching opaque hashes back to the Compare table.
- **Change:** Include tier and explicit pricing/commitment context in each Sensitivity series label or hover details, while retaining the short configuration ID for exact traceability.
- **Priority:** medium
- **Status:** open
