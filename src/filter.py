"""Pure matching, Decimal money, budget filtering and scenario preparation."""
import hashlib
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext
import pandas as pd

PAIR_KEY = ['source_type','source_file','offer_version','model_raw','provider_raw','region_normalized',
            'pricing_mode','serving_scope','feature_raw','service_tier_raw','cache_status','commitment_context']
COLUMNS = tuple(dict.fromkeys(PAIR_KEY + ['model_normalized','token_direction','price_usd_per_1m_tokens',
    'rate_code','sku','source_row_id','publication_date','record_status','flag_reason']))
EMPTY_MESSAGE = 'No model configurations match the current filters.'

def integer(value, field):
    try:
        n = Decimal(str(value))
        if not n.is_finite() or n < 0 or n != n.to_integral_value(): raise InvalidOperation
        return int(n)
    except (InvalidOperation, ValueError): raise ValueError(f'{field}: enter a nonnegative integer')

def budget_value(value):
    if value is None or str(value).strip() == '': return None
    try:
        n = Decimal(str(value).strip())
        if not n.is_finite() or n < 0: raise InvalidOperation
        return n
    except (InvalidOperation, ValueError): raise ValueError('Budget: enter a finite nonnegative USD amount')

def cost(input_total, output_total, input_rate, output_rate):
    with localcontext() as ctx:
        rates = (Decimal(input_rate), Decimal(output_rate))
        ctx.prec = max(100, len(str(input_total)) + len(str(output_total)) + sum(len(r.as_tuple().digits) + abs(r.as_tuple().exponent) for r in rates) + 10)
        return (Decimal(input_total)*rates[0]+Decimal(output_total)*rates[1])/Decimal(1000000)

def configurations(rows):
    reasons = Counter(); result = []
    if rows.empty: return result, reasons
    valid = rows[(rows.record_status == 'comparison_eligible') & (rows.pricing_mode == 'standard') &
                 (rows.cache_status == 'uncached') & rows.token_direction.isin(['input','output']) &
                 rows.service_tier_raw.str.lower().isin(['','standard','global-standard']) &
                 rows.feature_raw.str.lower().isin(['','on-demand inference'])]
    reasons['nonstandard_or_incompatible_rate_rows'] = len(rows)-len(valid)
    for identity, group in valid.groupby(PAIR_KEY, dropna=False, sort=True):
        if group.offer_version.nunique() != 1: raise ValueError('Mixed offer versions')
        directions = {d: group[group.token_direction == d] for d in ('input','output')}
        if any(len(v) > 1 for v in directions.values()): reasons['ambiguous_configurations'] += 1; continue
        if any(len(v) == 0 for v in directions.values()): reasons['incomplete_or_mismatched_configurations'] += 1; continue
        a, b = directions['input'].iloc[0], directions['output'].iloc[0]
        config = {k: a[k] for k in PAIR_KEY}
        config.update(configuration_id=hashlib.sha256('|'.join(str(v) for v in identity).encode()).hexdigest(),
            provider=a.provider_raw or 'Not available', model=a.model_normalized, region=a.region_normalized,
            source=a.source_type, tier=a.service_tier_raw or 'standard (explicit on-demand context)',
            input_usd_per_1m=Decimal(a.price_usd_per_1m_tokens), output_usd_per_1m=Decimal(b.price_usd_per_1m_tokens),
            input_rate_code=a.rate_code, output_rate_code=b.rate_code, input_sku=a.sku, output_sku=b.sku,
            input_source_row_id=a.source_row_id, output_source_row_id=b.source_row_id, publication_date=a.publication_date,
            quality='Not available', output_speed='Not available', latency='Not available')
        result.append(config)
    return result, reasons

@dataclass
class Result:
    rows: list
    total: int
    page: list
    scenarios: list
    excluded: dict
    page_number: int

def evaluate(rows, regions, input_tokens=1000, output_tokens=1000, requests=1000, budget=None, scenarios=(500,1000,2000), page=1):
    it = integer(input_tokens,'Input tokens/request'); ot = integer(output_tokens,'Output tokens/request')
    volume = integer(requests,'Requests/month'); cap = budget_value(budget)
    volumes = sorted(set(integer(v,'Sensitivity scenarios') for v in scenarios))
    if not volumes: raise ValueError('Sensitivity scenarios: enter at least one request volume')
    if len(volumes)>30: raise ValueError('Sensitivity scenarios: use at most 30 request volumes')
    if not regions: return Result([],0,[],[],{},1)
    selected = rows[rows.region_normalized.isin(regions)]
    # A source baseline cannot contain two offers for the same source file.
    if any(g.offer_version.nunique()>1 for _,g in selected.groupby('source_file')): raise ValueError('Mixed offer versions in source baseline; prepare one revision')
    configs, reasons = configurations(selected)
    priced = []
    for c in configs:
        c = c.copy(); c['monthly_cost_usd'] = cost(it*volume, ot*volume, c['input_usd_per_1m'], c['output_usd_per_1m'])
        c['per_request_cost_usd'] = cost(it,ot,c['input_usd_per_1m'],c['output_usd_per_1m'])
        c['per_1000_requests_usd'] = cost(it*1000,ot*1000,c['input_usd_per_1m'],c['output_usd_per_1m'])
        if cap is None or c['monthly_cost_usd'] <= cap: priced.append(c)
        else: reasons['over_budget_configurations'] += 1
    priced.sort(key=lambda c:(c['monthly_cost_usd'],c['configuration_id']))
    page = max(1,min(integer(page,'Page'),max(1,(len(priced)+49)//50)))
    series = [dict(configuration_id=c['configuration_id'], label=f'{c["model"]} · {c["region"]} · {c["source"]} · {c["serving_scope"]} · {c["configuration_id"][:6]}',
                   requests=v, monthly_cost_usd=cost(it*v,ot*v,c['input_usd_per_1m'],c['output_usd_per_1m'])) for c in priced[:10] for v in volumes]
    return Result(priced,len(priced),priced[(page-1)*50:page*50],series,dict(reasons),page)
