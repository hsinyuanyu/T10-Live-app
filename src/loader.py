"""Validated revision caches and bounded DuckDB projection/predicate loading."""
import json
import hashlib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal
import duckdb
import pandas as pd
from src.config import MAX_LOADED_ROWS, SCHEMA_REVISION
from src.data import sha

@dataclass(frozen=True)
class LoadRequest:
    service: Literal['bedrock']
    regions: tuple[str, ...]
    columns: tuple[str, ...]
    purpose: Literal['comparison', 'inspection'] = 'comparison'

@dataclass
class LoadedSlice:
    rows: pd.DataFrame
    provenance: pd.DataFrame
    quality_summary: dict
    dataset_revision: str
    is_sample: bool

AUDIT = ('source_row_id','source_file','offer_version','publication_date','record_status','flag_reason')

def validate(path):
    path = Path(path)
    try:
        m = json.loads(path.read_text(encoding='utf-8'))
        expected_revision = hashlib.sha256((m['transform_version'] + ''.join(s['sha256'] for s in m['sources'])).encode()).hexdigest()
        if m['dataset_revision'] != expected_revision: raise ValueError('Invalid dataset revision')
        if len(m['sources']) != 2 or len({s['source_file'] for s in m['sources']}) != 2: raise ValueError('Expected exactly two source offers')
        if m['schema_revision'] != SCHEMA_REVISION or not m['quality_checks']['passed']: raise ValueError('Invalid schema or quality checks')
        for name in ('bedrock_prices.parquet','quarantine.parquet','provenance.json','quality.json'):
            item = m['outputs'][name]
            if item['path'] != name: raise ValueError('Unexpected output path')
            p = path.parent / name
            if not p.is_file(): raise ValueError(f'Missing output {name}')
        signatures = tuple((n, (path.parent/n).stat().st_size, (path.parent/n).stat().st_mtime_ns, (path.parent/n).stat().st_ctime_ns) for n in m['outputs'])
        _hash_check(str(path.parent.resolve()), json.dumps(m, sort_keys=True), signatures)
        return m
    except (OSError, KeyError, json.JSONDecodeError, ValueError) as e:
        raise ValueError(f'Dataset activation failed: {e}. Run uv run python -m src.data prepare --raw-dir data/raw --out-dir data/snapshot') from e

@lru_cache(maxsize=8)
def _hash_check(directory, manifest_json, signatures):
    m = json.loads(manifest_json)
    for name, item in m['outputs'].items():
        if sha(Path(directory)/name) != item['sha256']: raise ValueError(f'Hash mismatch: {name}; re-prepare the complete snapshot')
    q = json.loads((Path(directory)/'quality.json').read_text())
    p = json.loads((Path(directory)/'provenance.json').read_text())
    if not q['passed'] or p != m['sources']: raise ValueError('Provenance or QA mismatch')
    return True

def key(path, m):
    return (str(Path(path).resolve()), m['dataset_revision'], m['schema_revision'], json.dumps(m['outputs'], sort_keys=True))

@lru_cache(maxsize=8)
def _regions(k):
    with duckdb.connect(config={'threads': 1}) as db:
        return tuple(r[0] for r in db.execute("SELECT DISTINCT region_normalized FROM read_parquet(?) WHERE record_status='comparison_eligible' AND region_normalized <> '' ORDER BY 1", [str(Path(k[0]).parent/'bedrock_prices.parquet')]).fetchall())

def available_regions(manifest_path, service='bedrock'):
    if service != 'bedrock': raise ValueError('Only Bedrock is supported')
    m = validate(manifest_path)
    return _regions(key(manifest_path, m))

@lru_cache(maxsize=16)
def _slice(k, regions, columns, purpose, limit):
    path = Path(k[0]).parent/'bedrock_prices.parquet'
    with duckdb.connect(config={'threads': 1}) as db:
        known = {r[0] for r in db.execute('DESCRIBE SELECT * FROM read_parquet(?)', [str(path)]).fetchall()}
        if set(columns)-known: raise ValueError(f'Unknown columns: {sorted(set(columns)-known)}')
        conditions = ["record_status='comparison_eligible'"] if purpose == 'comparison' else []
        params = [str(path)]
        if regions:
            conditions.append('region_normalized IN (' + ','.join('?' for _ in regions) + ')'); params.extend(regions)
        sql = 'SELECT '+','.join('"'+c+'"' for c in columns)+' FROM read_parquet(?)'
        if conditions: sql += ' WHERE '+' AND '.join(conditions)
        rows = db.execute(sql + f' LIMIT {limit+1}', params).fetchdf()
        if len(rows) > limit: raise ValueError(f'More than MAX_LOADED_ROWS={limit}; narrow the selected regions')
        return rows

def load_slice(manifest_path, request):
    if request.service != 'bedrock' or request.purpose not in ('comparison','inspection'): raise ValueError('Invalid service or purpose')
    m = validate(manifest_path); k = key(manifest_path, m)
    if set(request.regions)-set(_regions(k)): raise ValueError('Unknown region; select an available region code')
    columns = tuple(dict.fromkeys(request.columns + AUDIT))
    rows = _slice(k, tuple(sorted(set(request.regions))), columns, request.purpose, MAX_LOADED_ROWS).copy(deep=True)
    return LoadedSlice(rows, pd.DataFrame(m['sources']).copy(), json.loads((Path(manifest_path).parent/'quality.json').read_text()), m['dataset_revision'], m['is_sample'])
