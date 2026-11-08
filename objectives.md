# Objectives

## Team audience statements

**Audience A — FinOps analyst at a technology company:** A FinOps analyst must decide which AWS region, EC2 instance configuration, operating system, and purchase option to use for a defined workload while controlling cloud cost.

**Audience B — AI product manager selecting a production model:** An AI product manager must decide which Amazon Bedrock model and region to use for a defined production application while balancing token cost with model quality and serving performance.

---

## Source-derived facts that frame both decisions

The project uses AWS Price List Bulk API offer files, which are machine-readable **public list prices**, not customer-specific bills. One price-list row represents one product under one purchase term, at one rate, in one region, for the published offer version. The files do not include negotiated enterprise discounts, credits, taxes, or every AWS pricing mechanism, so any recommendation based on them should be described as a **list-price comparison**, not a forecast of an exact invoice. [Source: `data_overview_aws-price-list.md`; `technical.md`]

The current EC2 project data provides detailed fields for comparing instance type, vCPU, memory, processor, operating system, region, tenancy, purchase term, reservation length, purchase option, billing unit, and price. The project download contains EC2 price sheets for **US East (N. Virginia)** and **EU (Ireland)**, while the EC2 version index contains **122 published versions** reaching from December 2015 through September 2026. A reserved purchase can be represented by separate upfront-fee and hourly rows, so effective cost must combine the paired rows correctly. [Source: `data_overview_aws-price-list.md`; `ec2_version_index.csv`]

The newly provided EC2 sample files are appropriate for understanding schema and testing code, but they should **not** be used to report population counts, averages, or effective Reserved Instance rates. Each regional EC2 sample contains only 4,000 randomly selected rows, and random sampling can break the required upfront/hourly reserved-price pair. Final numerical claims should therefore be recomputed on the full EC2 downloads. [Source: `sample/README.md`]

For the AI-product decision, the two provided Bedrock files are complete tables rather than random subsets. `bedrock_foundation_models_sample.csv` contains **5,669 rows covering 53 Marketplace models across 35 regions**, while `bedrock_service_all_sample.csv` contains **11,657 rows covering 86 Amazon-billed models across 36 regions**. The two files use different schemas and billing conventions: the Marketplace file commonly prices in **1M tokens** and encodes the price dimension inside `PriceDescription`, while the Amazon-billed file commonly prices in **1K tokens** and has an explicit `Inference Type` field. The latter also contains multiple inference/service tiers such as standard, flex, priority, batch, and global variants. Any cross-model comparison must normalize those differences before ranking costs. [Source: provided Bedrock CSVs; `data_overview_aws-price-list.md`; `sample/README.md`]

The AWS price files do not directly measure EC2 workload performance or LLM application quality and serving performance. The team's auxiliary-data review identifies AWS Compute Savings Plans and EC2 Spot Price History as useful additions for the FinOps decision, and Artificial Analysis plus LMArena as possible quality/performance evidence for the AI-model decision. [Source: `auxiliary.md`]

---

# Audience A — FinOps analyst at a technology company

## Source-derived facts relevant to the decision

The main EC2 data can support list-price comparisons across `Instance Type`, `vCPU`, `Memory`, `Physical Processor`, `Operating System`, `Region Code`, `TermType`, `LeaseContractLength`, `PurchaseOption`, `Unit`, and `PricePerUnit`. The data supports On-Demand and Reserved pricing directly, but Savings Plans and Spot pricing are outside the provided main price-list files. Only two EC2 regional price sheets are in the current project download, so this dataset can compare those two regions but cannot establish the cheapest AWS region overall without additional regional files. [Source: `technical.md`; `data_overview_aws-price-list.md`]

The main dataset also contains specifications rather than measured application performance. For example, vCPU, memory, processor, and network descriptors can help establish comparable configurations, but they do not prove that one instance will perform better for a specific workload. Public performance benchmark data would be needed for a defensible price-to-performance comparison. [Source: `auxiliary.md`]

## AI-generated hypotheses about what this stakeholder cares about

### Desired outcomes

The FinOps analyst likely wants to choose a configuration that **meets the workload's technical requirements at the lowest reasonable total cost**, rather than simply selecting the cheapest row in the price list. A useful decision should identify an acceptable region, instance type, operating system, and purchase option for a stated workload and time horizon.

A second desired outcome is **financial flexibility**. The analyst may prefer a higher On-Demand rate when demand is uncertain, but may accept a one- or three-year commitment when the workload is stable enough for a Reserved Instance or Savings Plan to create meaningful savings.

A third outcome is **traceability**. The analyst should be able to explain the recommendation using a reproducible set of assumptions: workload requirements, AWS region, operating system, tenancy, billing unit, commitment length, payment option, price-list version, and the method used to combine upfront and hourly costs.

### What could go badly if the wrong decision is made

The analyst could choose an instance that is inexpensive on paper but does not meet CPU, memory, architecture, compatibility, or performance needs. That would create a false economy because the application might need a larger instance, more instances, or a redesign later.

The analyst could also **over-commit** to a one- or three-year term when demand changes, or remain entirely On-Demand when a stable workload could have justified a commitment. Either mistake can raise the effective cost of the workload.

A third risk is an invalid comparison. Mixing Linux and Windows, different tenancy or capacity states, different units, or unmatched Reserved Instance fee components can create a ranking that looks precise but is economically meaningless. Treating public list prices as the company's realized bill could also overstate expected savings because negotiated discounts and credits are absent.

### Tradeoffs

The main tradeoff is **cost versus flexibility**. On-Demand pricing has little commitment; Reserved pricing can lower list cost in exchange for a longer commitment and particular payment structure. Compute Savings Plans would add another commitment option if the team incorporates the auxiliary source.

There is also a **cost versus performance** tradeoff. A lower-priced instance family, processor, or region may not deliver the same workload performance. The available main data can establish hardware and price comparability, but measured price-to-performance requires workload benchmarks or direct testing.

Region choice introduces a further tradeoff between price and operational requirements. The cheapest of the two available regions may not be acceptable if the company has latency, data-residency, disaster-recovery, or architecture constraints.

### Constraints

The comparison must be limited to **comparable EC2 configurations**. Operating system, tenancy, capacity status, preinstalled software, instance characteristics, term type, and billing unit should be held constant or explicitly normalized before costs are compared.

Reserved pricing must combine the upfront and hourly components correctly. The random sample files cannot reliably do this because the pair may be split by sampling, so final cost calculations must use the full regional files.

The analysis must record the selected AWS price-list version because the `current` offer can change when AWS republishes prices. The current project data also covers only two EC2 regions and excludes Savings Plans, Spot prices, private discounts, credits, and actual usage history.

### Evidence needs / evidence that would change the decision

The recommendation would become more credible with the following evidence:

- the stakeholder's actual workload requirements: vCPU, memory, architecture, operating system, runtime pattern, expected utilization, and acceptable regions;
- full EC2 price-list rows for all configurations being compared, including correctly paired Reserved Instance fee components;
- the company's expected hours of use and commitment horizon;
- Compute Savings Plans pricing if commitment flexibility matters;
- Spot Price History if the workload is interruption-tolerant;
- performance benchmark or direct workload-test results when two instances have different processors or generations; and
- the company's negotiated AWS pricing or existing commitments if the goal is to estimate realized rather than list cost.

A recommendation should change if any of this evidence materially changes the ordering of total cost, makes an option operationally infeasible, or shows that a more expensive option delivers meaningfully better price-to-performance.

### Measures of success

The project would be successful for this audience if it produces a reproducible comparison in which the recommended configuration:

- meets the stakeholder-defined technical and regional requirements;
- has the lowest or near-lowest **normalized list cost** among feasible alternatives;
- quantifies the dollar and percentage difference from a clearly defined baseline;
- shows how the answer changes under different utilization or commitment assumptions;
- documents the price-list version, region, operating system, term, purchase option, billing unit, and normalization method; and
- makes clear which costs are known from AWS list prices and which would require customer-specific data.

## Questions that require a real stakeholder

1. What exact workload is being deployed, and what are its minimum CPU, memory, architecture, operating-system, storage, network, and performance requirements?
2. Which AWS regions are operationally acceptable, and are there latency, compliance, data-residency, or disaster-recovery constraints?
3. How many hours per month will the workload run, and how stable is that demand over one to three years?
4. How much commitment risk is acceptable? Is flexibility more important than the lowest possible committed list price?
5. Does the company already have Reserved Instances, Savings Plans, enterprise discounts, credits, or contract pricing that should affect the comparison?
6. Is Spot capacity acceptable, and what interruption risk can the workload tolerate?
7. What should define success: lowest monthly cost, savings versus the current configuration, price-to-performance, budget predictability, or another business metric?

---

# Audience B — AI product manager selecting a production model

## Source-derived facts relevant to the decision

The complete Bedrock tables provide broad pricing coverage for production-model comparison. The Marketplace table contains 53 model names across 35 regions, and the Amazon-billed Bedrock table contains 86 model names across 36 regions. The pricing dimensions include input and output tokens as well as variants such as batch, cache-related, flex, priority, and other service-specific rates. [Source: provided Bedrock CSVs]

However, the two Bedrock tables cannot be compared naively. They have different schemas, different model-name conventions, and different dominant token units. The Marketplace file encodes important pricing information inside `PriceDescription`, while the Amazon-billed file has explicit fields such as `Model`, `Provider`, `Inference Type`, `service_tier`, and `Feature`. A valid comparison therefore requires a normalized model identifier, region, inference type, service tier, and cost unit. [Source: `data_overview_aws-price-list.md`; provided Bedrock CSVs]

The AWS price files are strong evidence for **AWS list price**, but they are not sufficient evidence for production-model quality. They do not directly establish task accuracy, hallucination/error rate, output speed, time to first token, context-window suitability, or application-specific quality. The auxiliary review identifies Artificial Analysis as the strongest proposed source for benchmark and serving-performance data and LMArena as a secondary human-preference signal. [Source: `auxiliary.md`]

## AI-generated hypotheses about what this stakeholder cares about

### Desired outcomes

The AI product manager likely wants to select a Bedrock model and region that **meets a minimum quality and serving-performance standard at an acceptable production cost**. The right objective is therefore not “pick the cheapest model,” but “find the lowest-cost option that still meets the product's requirements.”

A useful output should translate AWS token rates into a workload-level metric such as **cost per request, cost per 1,000 requests, or monthly inference cost**. That estimate should use the expected mix of input tokens, output tokens, caching, batch inference, service tier, and region rather than comparing one isolated price row.

The product manager also likely values **robustness**. The recommendation should remain reasonable if token volume, input/output ratio, cache usage, or production traffic changes within a plausible range.

### What could go badly if the wrong decision is made

A model with the lowest token price could fail the application's quality threshold, leading to poor user outcomes, rework, manual review, or reputational risk. Conversely, selecting the most capable or premium model without considering usage volume could create unsustainable unit economics at scale.

A model may also look inexpensive but fail latency, throughput, context, modality, regional-availability, or reliability requirements. Price alone cannot establish those characteristics.

There is also a data-processing risk. The two Bedrock files use different units and field structures. Failing to convert 1K-token and 1M-token rates to a common basis, or mixing input, output, cache, batch, flex, priority, or provisioned-throughput rates, could produce a misleading cost ranking.

### Tradeoffs

The central tradeoff is **cost versus model capability**. A lower-cost model may be sufficient for a narrow extraction or classification task but inadequate for a demanding reasoning or long-context use case. A more expensive model may be justified if its quality materially reduces product errors or downstream human review.

A second tradeoff is **cost versus serving performance**. Standard, flex, priority, batch, and other service options may price the same model differently while providing different operational behavior. The cheapest inference mode may not meet an interactive product's latency expectations, while a batch-oriented product may benefit from lower-cost batch rates.

There can also be a **region and availability tradeoff**. A preferred model or inference mode may not be available in every acceptable region, so the lowest listed token price is not automatically a feasible production choice.

### Constraints

All compared rates must be normalized to the same cost basis, such as dollars per one million input tokens and dollars per one million output tokens. Model name, provider, model/version variant, region, inference type, feature, and service tier should be aligned before any ranking is produced.

A realistic cost model also requires a defined workload: expected input-token volume, output-token volume, number of requests, cache behavior, batch usage, and traffic pattern. Without that information, a single “cheapest model” result would not answer the production decision.

The main dataset cannot prove model quality or latency. A production recommendation therefore needs external benchmark evidence, application-specific evaluation, or both. External benchmark records also need careful provider/model/version matching because there is no guaranteed shared stable model ID between Bedrock and the proposed auxiliary sources.

### Evidence needs / evidence that would change the decision

The recommendation would become more credible with:

- a representative evaluation set from the actual product use case;
- a stakeholder-defined minimum quality threshold or error tolerance;
- expected monthly requests and input/output token distributions;
- latency, output-speed, or time-to-first-token requirements;
- required context length, modality, safety, privacy, or compliance constraints;
- region and availability requirements;
- Artificial Analysis benchmark and serving-performance evidence matched to the exact model/version where possible; and
- LMArena or another secondary quality signal as a cross-check rather than the sole evaluation criterion.

The model choice should change if application-specific testing shows that a cheaper option does not meet quality or latency requirements, or if another model reaches the same quality threshold at materially lower normalized cost.

### Measures of success

The project would be successful for this audience if it identifies one or more models that:

- meet a stakeholder-defined minimum quality threshold on the target task;
- satisfy latency or serving-performance requirements;
- are available in an acceptable AWS region and inference mode;
- minimize or reasonably control **cost per request and expected monthly cost** for the defined workload;
- remain competitive under reasonable sensitivity tests for input/output token volume, caching, and batch usage;
- normalize all Bedrock prices to a common unit before comparison; and
- clearly separate AWS pricing evidence from external benchmark evidence and stakeholder assumptions.

## Questions that require a real stakeholder

1. What exact product task will the model perform—for example, summarization, extraction, coding, search, customer support, or reasoning?
2. What does “good enough” quality mean for this task, and what evaluation metric or acceptance threshold will be used?
3. What latency, time-to-first-token, throughput, or user-experience requirement must the model meet?
4. What are the expected monthly number of requests and the distributions of input and output tokens per request?
5. Will the product use prompt caching, batch inference, priority/flex tiers, provisioned throughput, or only standard on-demand inference?
6. Which AWS regions are required or prohibited?
7. What context length, modality, safety, privacy, or compliance requirements matter?
8. What maximum cost per request, per 1,000 requests, per user, or per month is acceptable?

---

# Comparison of the two audiences

## Source-supported comparison

Both audiences face concrete decisions that the AWS pricing data can inform, and both require a fixed price-list version, normalized units, and explicit assumptions. Both must also distinguish **public list price** from actual realized cost.

The **FinOps analyst** is more directly supported by the main data for the pricing portion of the decision because EC2 exposes hardware attributes, region, operating system, term type, commitment length, purchase option, and price. The largest evidence gaps are customer-specific pricing, Savings Plans, Spot pricing, and measured workload performance.

The **AI product manager** has unusually broad Bedrock pricing coverage—the two complete tables together contain 139 model entries across many regions—but the decision itself depends on dimensions that the AWS price files do not measure, especially quality and serving performance. This audience therefore requires more external evidence or direct product testing before a recommendation can be defended.

The sample design also differs between the two paths. The Bedrock “sample” files are complete tables and can support exact counts and price parsing for their publication versions. The EC2 regional samples are random subsets intended for schema exploration, so final EC2 statistics and effective Reserved Instance calculations must return to the full downloads. [Source: `sample/README.md`]

## AI-generated comparison / hypotheses to test

The FinOps path may be easier to make **feasible** with the main dataset because the decision can be narrowed to comparable configurations and normalized list costs. Its main challenge is making sure the workload assumptions and commitment choices are realistic.

The AI-product path may be more decision-rich but is harder to defend from the AWS data alone. Its strongest version would combine Bedrock cost with external capability and latency evidence and then evaluate the cost-quality-performance frontier for a specific product task.

Neither audience should be selected only because its raw data is larger or easier to analyze. The final project audience should be the one for which the team can define a concrete stakeholder decision, obtain enough evidence to test the important tradeoffs, and produce a result that would actually change what the stakeholder does.

---

## Sources used

- `data_overview_aws-price-list.md` — AWS Price List dataset context, data dictionary, full-file counts, known findings, and limitations.
- `technical.md` — team audience framing, decision variables, technical limitations, and open questions.
- `auxiliary.md` — proposed supplementary sources for Savings Plans, Spot prices, EC2 performance, Artificial Analysis, and LMArena.
- `sample/README.md` / `README(4).md` — explains which files are random samples versus complete tables and the limitations of using EC2 samples for final statistics.
- `ec2_version_index.csv` — complete index of 122 EC2 price-list versions.
- `bedrock_foundation_models_sample.csv` — complete Marketplace Bedrock pricing table for the supplied publication version.
- `bedrock_service_all_sample.csv` — complete Amazon-billed Bedrock pricing table for the supplied publication version.
- `ec2_us-east-1_sample.csv` and `ec2_eu-west-1_sample.csv` — schema/testing samples only; not used for population statistics.

