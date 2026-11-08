"""Explicit, source-aware preparation; never imported to download at UI runtime."""
import argparse
import csv
import hashlib
import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
import pandas as pd
from src.config import RAW_DIR, ROOT, SCHEMA_REVISION, TRANSFORM_VERSION

SOURCES = {'bedrock_foundation_models.csv': ('marketplace', 'AmazonBedrockFoundationModels'),
           'bedrock_service_all.csv': ('amazon_billed', 'AmazonBedrock')}

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()

def normalize(raw, filename, metadata, number):
    r = {k: str(v) for k, v in raw.items()}
    get = lambda k: r.get(k, '').strip()
    market = SOURCES[filename][0] == 'marketplace'
    desc = get('PriceDescription')
    parts = desc.split('|')
    region = parts[1].strip() if market and len(parts) == 3 else get('Region Code') if not market else ''
    dimension = parts[2].strip() if market and len(parts) == 3 else get('Inference Type') if not market else ''
    model = get('serviceName') if market else get('Model')
    feature, tier = get('Feature'), get('service_tier').lower()
    context = ' '.join([dimension, feature, tier, get('Batch')]).lower()
    # Whitelist text token dimensions: other modalities never become text comparisons.
    token_text = re.sub(r'\s+', ' ', dimension.lower())
    token_text = re.sub(r'^(million )batch ', r'\1', token_text) if market else token_text
    direction = 'unknown'
    if re.fullmatch(r'(million )?(input|output|response) tokens?(?:[ ,\-]+(?:standard|global|regional|priority|flex|batch))*', token_text):
        direction = 'input' if 'input' in token_text else 'output'
    cache = 'cache' if 'cache' in context else 'uncached'
    mode = next((v for v in ('batch', 'priority', 'flex') if v in context), '')
    if not mode:
        if 'standard' in context or feature.lower() == 'on-demand inference' or (market and direction != 'unknown'):
            mode = 'standard'
        else: mode = 'unknown'
    scope = 'global' if 'global' in context else 'regional' if 'regional' in context else 'unspecified'
    commitment = get('TermType') + '|' + (feature if 'provision' in feature.lower() else '')
    reasons = []
    quarantine = False
    try:
        price = Decimal(get('PricePerUnit'))
        if not price.is_finite() or price < 0: raise InvalidOperation
    except InvalidOperation:
        price = None; reasons.append('invalid_price'); quarantine = True
    multiplier = {'1K tokens': 1000, '1M tokens': 1}.get(get('Unit'))
    if not multiplier: reasons.append('unsupported_unit')
    if direction == 'unknown': reasons.append('unrecognized_dimension')
    if not model: reasons.append('missing_model')
    if market and get('Region Code') and get('Region Code') != region: reasons.append('region_conflict')
    if not re.fullmatch(r'[a-z]{2}(?:-[a-z]+)+-\d+', region): reasons.append('missing_or_invalid_region')
    if not (get('RateCode') and get('SKU')): reasons.append('missing_publisher_id'); quarantine = True
    if get('Currency') != 'USD': reasons.append('non_usd'); quarantine = True
    if get('StartingRange') != '0' or get('EndingRange') != 'Inf': reasons.append('ranged_price')
    if 'provision' in context or get('TermType') != 'OnDemand': reasons.append('commitment')
    # Preserve all original fields in JSON, keeping literal NA and source whitespace.
    return dict(source_row_id=hashlib.sha256(f'{filename}|{metadata["Version"]}|{number}'.encode()).hexdigest(),
        source_file=filename, source_type=SOURCES[filename][0], offer_version=metadata['Version'],
        publication_date=metadata['Publication Date'], rate_code=get('RateCode'), sku=get('SKU'),
        model_raw=r.get('serviceName' if market else 'Model', ''), provider_raw=r.get('Provider', ''),
        model_normalized=model, region_raw=r.get('Region Code', ''), region_normalized=region,
        inference_type_raw=r.get('Inference Type', ''), feature_raw=r.get('Feature', ''), service_tier_raw=r.get('service_tier', ''),
        price_dimension_raw=dimension, token_direction=direction, pricing_mode=mode, serving_scope=scope,
        cache_status=cache, commitment_context=commitment, unit_raw=r.get('Unit', ''),
        price_per_unit_raw=r.get('PricePerUnit', ''), price_per_unit_decimal=str(price) if price is not None else '',
        conversion_multiplier=str(multiplier or ''), price_usd_per_1m_tokens=str(price * multiplier) if price is not None and multiplier else '',
        record_status='quarantined' if quarantine else 'retained_noncomparable' if reasons else 'comparison_eligible',
        flag_reason=';'.join(reasons), original_row_number=str(number), raw_attributes=json.dumps(r, sort_keys=True))

def prepare(raw_dir=RAW_DIR, out_dir=ROOT / 'data/cleaned', is_sample=False):
    started = time.perf_counter(); out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    clean, quarantine, sources, counts = [], [], [], {}
    for filename, (_, service) in SOURCES.items():
        path = Path(raw_dir) / filename
        if not path.exists(): raise ValueError(f'Missing required full source: {path}. Run uv run python scripts/download.py')
        with path.open(newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f); metadata_rows = [next(reader) for _ in range(5)]
            metadata = {row[0]: row[1] for row in metadata_rows if len(row) >= 2}
        if not all(metadata.get(k) for k in ('Version', 'Publication Date')): raise ValueError(f'{filename}: missing five-row offer metadata')
        table = pd.read_csv(path, skiprows=5, dtype=str, keep_default_na=False, low_memory=False)
        required = {'SKU','RateCode','Unit','PricePerUnit','Currency','PriceDescription','TermType','StartingRange','EndingRange'} | ({'serviceName'} if service.endswith('FoundationModels') else {'Model','Provider','Region Code','Inference Type','Feature','service_tier'})
        if required - set(table.columns): raise ValueError(f'{filename}: missing source columns {sorted(required-set(table.columns))}')
        c = Counter(raw=len(table), clean=0, quarantine=0, exact_duplicate_removed=0); seen = set(); reasons = Counter()
        for number, raw in enumerate(table.to_dict('records'), 1):
            identity = tuple(raw.items())
            if identity in seen: c['exact_duplicate_removed'] += 1; continue
            seen.add(identity)
            row = normalize(raw, filename, metadata, number)
            if row['record_status'] == 'quarantined': quarantine.append(row); c['quarantine'] += 1
            else: clean.append(row); c['clean'] += 1
            reasons.update(filter(None, row['flag_reason'].split(';')))
        assert c['raw'] == c['clean'] + c['quarantine'] + c['exact_duplicate_removed']
        counts[filename] = dict(c, reasons=dict(reasons), columns=list(table.columns))
        sources.append(dict(source_file=filename, source_url=f'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/{service}/current/index.csv',
            sha256=sha(path), byte_size=path.stat().st_size, download_timestamp=datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            metadata_rows=metadata_rows, offer_version=metadata['Version'], publication_date=metadata['Publication Date']))
    revision = hashlib.sha256((TRANSFORM_VERSION + ''.join(s['sha256'] for s in sources)).encode()).hexdigest()
    quality = dict(passed=True, sources=counts, status_counts=dict(Counter(r['record_status'] for r in clean + quarantine)))
    frame = pd.DataFrame(clean + quarantine)
    outputs = {}
    for name, obj in [('bedrock_prices.parquet', frame[frame.record_status != 'quarantined']), ('quarantine.parquet', frame[frame.record_status == 'quarantined']), ('provenance.json', sources), ('quality.json', quality)]:
        tmp = out_dir / (name + '.tmp')
        if name.endswith('parquet'):
            obj.to_parquet(tmp, index=False)
            assert len(pd.read_parquet(tmp)) == len(obj)
        else: tmp.write_text(json.dumps(obj, indent=2), encoding='utf-8')
        tmp.replace(out_dir / name); outputs[name] = dict(path=name, sha256=sha(out_dir / name))
    manifest = dict(schema_revision=SCHEMA_REVISION, transform_version=TRANSFORM_VERSION, dataset_revision=revision,
        is_sample=is_sample, sources=sources, outputs=outputs, quality_checks={'passed': True})
    tmp = out_dir / 'manifest.json.tmp'; tmp.write_text(json.dumps(manifest, indent=2), encoding='utf-8'); tmp.replace(out_dir / 'manifest.json')
    return {'seconds': time.perf_counter()-started, 'revision': revision, 'quality': quality}

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('command', choices=['prepare']); p.add_argument('--raw-dir', type=Path, default=RAW_DIR); p.add_argument('--out-dir', type=Path, default=ROOT/'data/cleaned'); p.add_argument('--sample', action='store_true')
    a = p.parse_args(); print(json.dumps(prepare(a.raw_dir, a.out_dir, a.sample), indent=2))
