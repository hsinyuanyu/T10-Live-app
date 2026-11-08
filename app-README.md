# Bedrock cost comparison app

Run from the team repository root:

```bash
uv sync --locked
uv run streamlit run app.py
```

The committed `data/snapshot/` contains the activated, validated AWS Bedrock price snapshot, so the app starts without a raw-data download or AWS credentials. The app compares standard, uncached token pricing only; it labels missing quality, speed, and latency evidence as `Not available`.

To run the checks:

```bash
uv run pytest -q
python3 09-audit/check_bedrock_cost.py
```

Refresh pricing only through the explicit preparation commands in `scripts/` and review the new snapshot and manifest before activating it.
