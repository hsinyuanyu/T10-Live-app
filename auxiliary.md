# Auxiliary Data

## Scope

This file covers **Role 4: Auxiliary Data only**. Its purpose is to identify outside data that could add decision-relevant information to the AWS Price List dataset for the team's two candidate audiences. It does not replace the main dataset, define the project objective, evaluate the main dataset in full, or document the technical download path.

The two candidate audiences are:

1. A **FinOps analyst at a technology company** choosing an AWS region, instance type, operating system, and purchase option while controlling cloud costs.
2. An **AI product manager selecting a production model** choosing an Amazon Bedrock model and region while estimating token costs.

---

## Audience 1: FinOps analyst at a technology company

The main AWS Price List is strong for comparing published On-Demand and Reserved prices and EC2 product attributes. However, several decision-relevant pricing and performance signals sit outside the provided files.

### Candidate A — AWS Compute Savings Plans price lists

**Why it is useful**

The provided AWS Price List files do not include Savings Plans. This matters because a FinOps analyst choosing a purchase option should not compare only On-Demand and Reserved pricing if a Savings Plan may be a realistic commitment option.

**Source**

AWS Price List Bulk API for Savings Plans  
Documentation:  
https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-the-aws-price-list-bulk-api-fetching-price-list-files-manually.html

Current Compute Savings Plans index:  
https://pricing.us-east-1.amazonaws.com/savingsPlan/v1.0/aws/AWSComputeSavingsPlan/current/index.json

**What the auxiliary data contains**

AWS documents Savings Plan price-list files in CSV and JSON formats. They contain metadata, product attributes, purchase-option information, and pricing terms. The documentation gives examples of attributes such as `Instance Type`, `Location Type`, and `Purchase Option`.

**How it could connect to the main dataset**

There is not a guaranteed cross-service SKU that can simply be joined to the EC2 file. The safer approach would be to align comparable workload attributes such as region/location, instance family or type when applicable, usage/operation, and purchase-term information.

**What it would enable**

It would extend the purchase-option comparison from:

- On-Demand
- Reserved

to a broader comparison that also considers:

- Compute Savings Plans

This would make the FinOps decision closer to the actual set of AWS commitment choices.

**Limitations**

- Savings Plans have their own pricing structure, so they should not be treated as a simple one-to-one row join with EC2 prices.
- Commitment terms and payment options must be normalized before comparison.
- These are still public list rates, not a company's negotiated or realized bill.

**Priority: HIGH**

This is the strongest auxiliary source for Audience 1 because it directly fills a pricing option that is missing from the provided dataset and is available from an official public AWS source.

---

### Candidate B — Amazon EC2 Spot Price History

**Why it is useful**

Spot pricing is also excluded from the provided AWS Price List files. A FinOps analyst may care about Spot for flexible or interruption-tolerant workloads because it introduces another cost option beyond On-Demand and long-term commitments.

**Source**

AWS EC2 `DescribeSpotPriceHistory` API:  
https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeSpotPriceHistory.html

**What the auxiliary data contains**

The AWS API returns Spot price history with fields including:

- `InstanceType`
- `ProductDescription`
- `SpotPrice`
- `AvailabilityZone`
- `Timestamp`

**How it could connect to the main dataset**

A practical match would use:

- Spot `InstanceType` ↔ main `Instance Type`
- Spot `ProductDescription` ↔ main `Operating System`
- Spot `AvailabilityZone` mapped to the corresponding AWS region ↔ main `Region Code`

Because Spot prices change over time, a timestamp or time window must also be defined before comparing them with a current list-price snapshot.

**What it would enable**

The team could compare the current public On-Demand/Reserved list-price picture with observed Spot price history for the same instance types and regions.

**Limitations**

- The API is time-varying rather than a static price catalog.
- Retrieving it through the EC2 API requires AWS authentication/permissions.
- Price alone does not measure interruption risk or availability, so Spot should not automatically be treated as the "best" option when it is cheapest.

**Priority: HIGH, but secondary to Savings Plans**

It is highly relevant to FinOps, but it adds more acquisition and interpretation complexity than the public Savings Plans price-list files.

---

### Candidate C — EC2 performance benchmark results

**Why it is useful**

The AWS Price List contains specifications such as vCPU, memory, processor, and network descriptions, but specifications are not the same as measured workload performance. Performance data would help an analyst compare value rather than price alone.

**Possible source**

OpenBenchmarking.org / Phoronix Test Suite EC2 results. One public example compares AWS Graviton EC2 instance types:  
https://openbenchmarking.org/result/2405291-NE-2308110NE13

**How it could connect to the main dataset**

The natural linking field is EC2 instance type (for example, `m7g.16xlarge`), with benchmark name, operating system, test date, and configuration retained so that unlike tests are not mixed together.

**What it would enable**

Instead of only asking "Which EC2 instance is cheaper?", the team could ask which comparable instance offers stronger **price-to-performance** for a defined workload.

**Limitations**

- Public benchmark coverage is uneven across instance families.
- Tests may have been run under different operating systems, software versions, storage configurations, and dates.
- A benchmark result is not a complete current catalog of EC2 performance.

**Priority: MEDIUM / OPTIONAL**

Useful if the team narrows the FinOps question to price-to-performance, but it is less clean and complete than the two AWS pricing sources above.

---

## Audience 2: AI product manager selecting a production model

The Bedrock files provide model identity and token-price information, but a production-model decision cannot be made from price alone. The important missing dimensions are model quality and service performance.

### Candidate D — Artificial Analysis model benchmark and performance data

**Why it is useful**

Artificial Analysis publishes independent model benchmarking data and a structured Data API. Its language-model data includes model identity, benchmark evaluations, pricing fields, and performance metrics such as output speed and time to first token.

**Source**

Artificial Analysis Data API documentation:  
https://artificialanalysis.ai/data-api/docs

Methodology:  
https://artificialanalysis.ai/methodology/intelligence-benchmarking

**Relevant fields**

Useful fields for this project include:

- model name
- model creator/provider
- benchmark/evaluation scores
- output tokens per second
- time to first token
- release date

The AWS Bedrock file should remain the authoritative source for the AWS token prices used in the project; the Artificial Analysis pricing fields could be used only as a cross-check if needed.

**How it could connect to the main dataset**

There is no shared stable ID between the Bedrock price file and Artificial Analysis. The likely matching method is a normalized combination of:

- provider / model creator
- model name
- model version where available

A manual mapping table would probably be needed for naming differences such as date suffixes, reasoning variants, or Bedrock-specific display names.

**What it would enable**

The analysis could move from:

"Which Bedrock model has the lowest token price?"

to:

"Which Bedrock model offers the strongest trade-off between AWS token cost, model capability, and serving performance?"

That is more useful for an AI product manager selecting a production model.

**Limitations**

- Coverage must be checked against the specific Bedrock models in the AWS file; not every Bedrock model is guaranteed to have a matching benchmark record.
- Benchmark scores summarize standardized tasks and may not predict performance on the product manager's exact application.
- The API requires an API key. Artificial Analysis documents a free API tier with rate limits.
- Model names and benchmark methodologies change over time, so versions should be recorded.

**Priority: VERY HIGH**

This is the strongest auxiliary source for Audience 2 because it adds the quality and latency/speed dimensions that token-price data alone cannot provide.

---

### Candidate E — LMArena text-model leaderboard

**Why it is useful**

LMArena provides model-level scores based on human preference comparisons and reports the number of votes for models. It includes many proprietary models, including some Anthropic and Amazon models.

**Source**

LMArena text leaderboard:  
https://lmarena.ai/leaderboard/text

**How it could connect to the main dataset**

The likely match is again a normalized provider + model-name mapping.

**What it would enable**

It could provide a second, user-preference-oriented signal of model quality to compare with Bedrock token prices.

**Limitations**

- Coverage of the exact Bedrock model versions may be incomplete.
- Arena preference is not the same as performance on a specific production workload.
- Model aliases and dated versions create matching problems.
- It is better used as a secondary quality signal than as the sole basis for a production decision.

**Priority: MEDIUM / SECONDARY**

Useful as a cross-check, but Artificial Analysis is more directly structured for a cost-quality-performance comparison.

---

## Recommended auxiliary-data plan

| Audience | Recommended primary auxiliary data | Secondary data | Main value added |
|---|---|---|---|
| FinOps analyst | AWS Compute Savings Plans price lists | EC2 Spot Price History | Expands the purchase-option comparison beyond On-Demand and Reserved |
| AI product manager | Artificial Analysis Data API | LMArena leaderboard | Adds model quality and serving-performance evidence to Bedrock token prices |

If the project later narrows to **Audience 1**, Role 4 should prioritize the public Compute Savings Plans files first and then consider Spot price history. If it narrows to **Audience 2**, Role 4 should prioritize Artificial Analysis and build a small model-name mapping to the Bedrock models.

---

## Role 4 conclusion

The most useful auxiliary data should add information that the provided AWS Price List intentionally does not contain rather than duplicate columns already present in it.

For the **FinOps analyst**, the largest immediate gap is additional AWS purchasing options, especially Savings Plans and Spot pricing. For the **AI product manager**, the largest gap is model quality and serving performance. These auxiliary sources would allow the final analysis to support a more realistic decision than a list-price ranking alone.

The next step, after the team chooses its final audience, is to test overlap between the selected auxiliary source and the relevant AWS records before committing to a combined analysis.
