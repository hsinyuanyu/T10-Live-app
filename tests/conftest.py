import csv
import pytest
from src.data import prepare

BASE = dict(SKU='sku',RateCode='rate',TermType='OnDemand',StartingRange='0',EndingRange='Inf',Currency='USD',
            PriceDescription='USD price',Unit='1K tokens',PricePerUnit='0.001',Model='Test 1.0',Provider='Test',
            **{'Region Code':'us-east-1','Inference Type':'Input tokens','Feature':'On-demand Inference','service_tier':'standard'})

def raw_row(**changes):
    return BASE | changes

def write_sources(directory, amazon=None, market=None):
    directory.mkdir(parents=True,exist_ok=True)
    if amazon is None: amazon = [raw_row(),raw_row(SKU='out',RateCode='out',PricePerUnit='0.003',**{'Inference Type':'Output tokens'})]
    if market is None: market = [raw_row(SKU='market',RateCode='market',serviceName='Marketplace Test',PriceDescription='AWS Marketplace software usage|eu-west-1|Million Input Tokens Global',Unit='1M tokens',**{'Region Code':'eu-west-1'})]
    for filename,rows in [('bedrock_service_all.csv',amazon),('bedrock_foundation_models.csv',market)]:
        with (directory/filename).open('w',newline='',encoding='utf-8') as f:
            w=csv.writer(f);w.writerows([['FormatVersion','v1.0'],['Disclaimer','Test fixture only'],['Publication Date','2026-10-01T00:00:00Z'],['Version','20261001000000'],['OfferCode','test']])
            writer=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for row in rows for k in row)));writer.writeheader();writer.writerows(rows)

@pytest.fixture
def snapshot(tmp_path):
    write_sources(tmp_path/'raw');prepare(tmp_path/'raw',tmp_path/'clean')
    return tmp_path/'clean'/'manifest.json'
