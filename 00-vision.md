# Team T10 — Project Vision

## AWS Bedrock Model Cost Comparison Tool

**Audience:** AI product managers at software companies choosing a production Amazon Bedrock model and AWS deployment region.

**Vision:** We aim to build a decision-support tool that helps AI product managers compare Amazon Bedrock models and deployment regions based on pricing and workload requirements. Users can specify their expected token usage, monthly request volume, and budget, then explore comparable models through interactive tables and sensitivity analysis. The tool helps users identify cost-effective configurations while maintaining transparency about pricing assumptions and data limitations.

## Decision and value

The user's decision is **which Bedrock model–region configuration deserves further evaluation for a defined workload**. Today, prices are scattered across AWS price sheets that use different model labels, units, serving modes, and regional conventions; manually joining and calculating them is error-prone. Our tool makes like-for-like *published list-price* comparisons reproducible, exposes assumptions and source versions, and shows whether cost rankings change as request volume changes.

The user cares about **estimated cost, budget fit, service/region availability, traceability, and the risk of making a price-only decision**. The tool does **not** claim that the cheapest model is the best choice: application quality, latency, private discounts, and real-world availability require additional evidence.

## Concrete user flows

| User selects / enters | Tool shows | Decision supported |
| --- | --- | --- |
| Region(s), 1,000 input tokens/request, 1,000 output tokens/request, 1,000 monthly requests | Comparable, standard, uncached Bedrock configurations ranked by estimated monthly USD cost; input/output list rates and source versions | Which model–region configurations to shortlist for testing |
| A maximum workload budget, e.g. $50 | The count and table of configurations within the budget, with explicit no-match feedback | Which options meet a cost constraint |
| Sensitivity volumes of 500, 1,000, and 2,000 requests/month | A line chart of each shortlisted configuration's estimated monthly USD cost while holding tokens/request fixed | Whether the shortlist stays affordable as traffic changes |

## Product boundary and evidence

- **In scope (MVP):** Amazon Bedrock published pricing from the two course-provided Bedrock price sheets; normalized input/output token prices; exact, unambiguous standard-inference configurations; workload estimates, region/budget filters, a Compare table, and a Sensitivity chart.
- **Out of scope (MVP):** EC2 Reserved Instance recommendations, catalog-drift analysis, model-quality or latency claims without separately verified benchmarks, inferred cross-source model identity, private AWS bills, and automated purchasing.
- **Evidence rule:** List prices are not actual invoices. Keep marketplace and Amazon-billed sources identifiable; show the price-file version and missing or excluded evidence. Do not merge distinct service tiers, caching modes, or model versions just because their names resemble one another.

**Team project repository:** https://github.com/mumaniu3/dso576-project-T10

**Course dataset repository:** https://github.com/USC-DSO-576-PS/dataset_aws-price-list
