# 05 - Views

## Job

Present the filtered Amazon Bedrock model options as clear decision-support views for an AI product manager choosing a production model.

This piece owns the tables, charts, labels, formatting, and empty states shown **after** the data has been prepared and filtered. It does not download data, parse raw AWS price rows, normalize 1K-token versus 1M-token units, match external benchmark records, or decide which rows pass the filters.

## Contract

### Receives

A filtered table with one comparable Bedrock configuration per row. Each row should already identify, when applicable:

- provider
- model
- AWS region
- inference type / pricing mode
- service tier or feature
- normalized input price in USD per 1 million tokens
- normalized output price in USD per 1 million tokens
- optional external benchmark fields matched to that model/version, such as quality score, output speed, or time to first token

It also receives the current workload assumptions from the shared state/setup, including:

- average input tokens per request
- average output tokens per request
- expected monthly requests
- any additional workload assumptions needed by the selected inference mode, such as cache or batch usage
- any sensitivity scenario values defined by setup

### Produces

Two user-facing views:

1. **Compare** — a table for comparing the currently feasible model-region configurations.
2. **Sensitivity** — a chart showing how workload changes affect estimated cost.

The views do not modify the input table or the active filters.

## Definitions

- **Configuration:** one comparable combination of model, region, inference/pricing mode, and service tier or feature when that field changes the rate.
- **AWS price:** public AWS list-price evidence from the supplied Bedrock price files.
- **External benchmark:** non-AWS evidence such as quality, output speed, or time to first token. Missing benchmark data means unknown, not zero.
- **Estimated cost:** a workload-level calculation based on the normalized AWS rates and the current workload assumptions. It is not a forecast of the customer's final AWS bill.

---

## View 1 — Compare

### Purpose

Answer: **Which currently feasible Bedrock configurations meet the selected constraints, and how do their costs and available performance evidence compare?**

### Table

Show one row per configuration.

Display these fields when available:

| Column | Display rule |
|---|---|
| Provider | Human-readable provider |
| Model | Human-readable model name |
| Region | AWS region code or clear region label |
| Inference / pricing mode | Distinguish standard, batch, flex, priority, global, or other relevant modes |
| Service tier / feature | Show when it changes the meaning or price of the configuration |
| Input $ / 1M tokens | Normalized AWS input-token list price |
| Output $ / 1M tokens | Normalized AWS output-token list price |
| Est. $ / request | Cost for the current workload assumptions |
| Est. $ / 1,000 requests | Same assumptions, scaled to 1,000 requests |
| Est. monthly $ | Same assumptions, scaled to current monthly request volume |
| Quality | External benchmark only when a confident model/version match exists |
| Output speed | External benchmark only when available |
| TTFT / latency | External benchmark only when available |

Default-sort by **estimated monthly cost, lowest first**. Use model name only to break ties.

Above the table, show the number of matching configurations and the workload assumptions currently used for the estimates.

### Visual rules

- Display money in USD.
- Show comparable token prices on the common **per 1 million tokens** basis.
- Keep enough decimal places for per-request cost so a real non-zero value is not displayed as zero.
- Show monthly cost with comma separators and two decimal places.
- Show missing external benchmark values as `Not available`, never `0`.
- Keep AWS pricing columns visually separate from external benchmark columns.
- Do not show raw pricing identifiers such as `SKU`, `RateCode`, or `OfferTermCode` in the main decision table.
- Label workload costs as **estimates based on public AWS list prices**.
- Make the price-list snapshot/version visible in a caption or source note when it is supplied by upstream data.

### Reason

The decision depends on several attributes at once — model, region, serving mode, token price, workload cost, and optional quality/performance evidence — so a comparison table is the clearest primary view.

---

## View 2 — Sensitivity

### Purpose

Answer: **Does the cost ranking remain reasonable when the expected workload changes?**

### Chart

Use a line chart:

- **X-axis:** the workload scenario defined by setup/state, such as monthly request volume
- **Y-axis:** estimated monthly AWS list-price cost
- **One line per compared configuration**
- **Tooltip/label:** model, region, inference mode when relevant, workload value, and estimated monthly cost

Keep all non-varied workload assumptions fixed while changing the sensitivity variable. State next to the chart which variable is changing and which assumptions are being held fixed.

If the filtered set is too large for a readable chart, show a clearly labeled subset of the lowest-cost configurations while keeping the full filtered set in the Compare table. The exact display limit may be chosen by the implementation as a visual-detail decision.

### Reason

The project objective is not only to identify a low-cost option at one workload level, but also to avoid a recommendation that becomes unreasonable when production usage changes.

---

## Shared behavior and edge cases

1. **One active state:** Compare and Sensitivity must reflect the same active filters and workload assumptions.
2. **No raw-row comparison:** Views receive normalized comparable configurations; they must not directly rank raw rows from the two Bedrock source schemas.
3. **Missing benchmark data:** AWS pricing remains usable. Display `Not available` for unmatched external evidence.
4. **No matching rows:** Show `No model configurations match the current filters.` Do not show a misleading empty chart.
5. **Invalid workload input:** If a required workload value is missing or invalid, do not display a calculated cost as if it were valid; identify the input that needs correction.
6. **AWS versus external evidence:** Never label external quality or latency measurements as AWS data.
7. **No automatic “cheapest = best” claim:** Cost may be sorted lowest first, but the view must not claim the cheapest model is the final recommendation when quality, latency, availability, or application testing is unknown.
8. **Traceability:** When source version/effective-date information is available, keep it visible so the user can tell which pricing snapshot supports the displayed costs.

---

## Grounding in the supplied data

The two Bedrock price files describe the same market with different schemas. The Marketplace file uses `serviceName` as the model name and stores important price-dimension details inside `PriceDescription`; its token prices commonly use `1M tokens`. The Amazon-billed Bedrock file has explicit fields such as `Model`, `Provider`, `Inference Type`, `Feature`, and `service_tier`, and its token prices commonly use `1K tokens`.

Therefore, this piece only displays **normalized upstream output**. It does not compare the two raw schemas directly.

AWS price data supports pricing and regional/inference availability. It does not by itself establish application quality or serving performance, so external benchmark evidence is optional and must remain visibly separate.

---

## Checks — done when

| Check | Tiny example | Expected result |
|---|---|---|
| Cost ordering | Model A monthly cost = $120; Model B = $80 | Compare shows B before A |
| Missing benchmark | Model A has AWS prices but no matched quality score | AWS prices remain visible; Quality shows `Not available` |
| Filter consistency | Region filter leaves only `us-west-2` rows | Both Compare and Sensitivity use only `us-west-2` configurations |
| Empty result | Active filters leave 0 configurations | Show the defined no-match message and no sensitivity chart |
| Workload change | Same configuration and rates; monthly request volume increases | Displayed monthly estimate changes consistently with the workload |
| Evidence separation | A row has AWS price plus Artificial Analysis latency | Pricing and external latency are labeled as different evidence sources |

This piece is complete when all six checks pass.
