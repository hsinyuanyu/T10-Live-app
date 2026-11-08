from decimal import Decimal
import json
import pandas as pd
import pytest
from src.data import normalize, prepare, sha
from conftest import raw_row,write_sources
META={'Version':'20261001000000','Publication Date':'2026-10-01'}

def test_priority_conversion_and_raw_preservation():
    row=normalize(raw_row(PricePerUnit='0.0002625000',Provider='NA',**{'Inference Type':'Input tokens priority'}),'bedrock_service_all.csv',META,1)
    assert Decimal(row['price_usd_per_1m_tokens']) == Decimal('0.2625000')
    assert row['pricing_mode']=='priority' and row['record_status']=='comparison_eligible'
    assert row['provider_raw']=='NA' and row['price_per_unit_raw']=='0.0002625000'

@pytest.mark.parametrize('dimension,direction,mode,cache',[('Million Input Tokens Global','input','standard','uncached'),('Output Tokens - Standard, Global','output','standard','uncached'),('Million Batch Response Tokens Global','output','batch','uncached'),('Cache Read Tokens - Standard, Global','unknown','standard','cache')])
def test_market_dimensions(dimension,direction,mode,cache):
    r=normalize(raw_row(serviceName='Example',PriceDescription='AWS Marketplace software usage|us-east-1|'+dimension,Unit='1M tokens'),'bedrock_foundation_models.csv',META,1)
    assert (r['token_direction'],r['pricing_mode'],r['cache_status'])==(direction,mode,cache)

@pytest.mark.parametrize('unit',['hour','TextUnit','1M TPM Hour'])
def test_non_token(unit):
    r=normalize(raw_row(Unit=unit),'bedrock_service_all.csv',META,1)
    assert r['record_status']=='retained_noncomparable' and 'unsupported_unit' in r['flag_reason']

@pytest.mark.parametrize('price',['','NaN','Infinity','-1','bad'])
def test_invalid_price(price):
    assert normalize(raw_row(PricePerUnit=price),'bedrock_service_all.csv',META,1)['record_status']=='quarantined'

def test_accounting_duplicates_and_diagnostic(tmp_path):
    a=raw_row();write_sources(tmp_path/'raw',amazon=[a,a,raw_row(SKU='hour',RateCode='hour',Unit='hour'),raw_row(SKU='bad',RateCode='bad',PricePerUnit='bad'),raw_row(SKU='unparsed',RateCode='unparsed',**{'Inference Type':''})])
    result=prepare(tmp_path/'raw',tmp_path/'clean')
    c=result['quality']['sources']['bedrock_service_all.csv']
    assert c['raw']==5 and c['clean']==3 and c['quarantine']==1 and c['exact_duplicate_removed']==1
    assert c['reasons']['unsupported_unit']==1 and c['reasons']['unrecognized_dimension']==1
    assert len(pd.read_parquet(tmp_path/'clean/quarantine.parquet'))==1
    f=tmp_path/'raw/bedrock_service_all.csv';f.write_text(f.read_text().replace('Inference Type','Unsupported Header'))
    with pytest.raises(ValueError,match='missing source columns'):prepare(tmp_path/'raw',tmp_path/'other')

def test_revision_deterministic_and_sample(tmp_path):
    write_sources(tmp_path/'raw');a=prepare(tmp_path/'raw',tmp_path/'a');b=prepare(tmp_path/'raw',tmp_path/'b',True)
    assert a['revision']==b['revision']
    assert json.loads((tmp_path/'b/manifest.json').read_text())['is_sample'] is True
