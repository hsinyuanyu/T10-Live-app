import json
import pandas as pd
import pytest
from src.loader import available_regions,load_slice,LoadRequest,_regions,_slice
from src.filter import COLUMNS
from src.data import prepare
from conftest import write_sources,raw_row

def test_projection_regions_and_empty_schema(snapshot):
    assert available_regions(snapshot)==('eu-west-1','us-east-1')
    req=LoadRequest('bedrock',('us-east-1',),('region_normalized','token_direction'))
    l=load_slice(snapshot,req)
    assert len(l.rows)==2 and set(l.rows.region_normalized)=={'us-east-1'}
    assert l.provenance.source_file.is_unique
    assert set(l.rows.columns)=={'region_normalized','token_direction','source_row_id','source_file','offer_version','publication_date','record_status','flag_reason'}
    empty=load_slice(snapshot,LoadRequest('bedrock',('eu-west-1',),('model_raw',)))
    assert len(empty.rows)==1
    with pytest.raises(ValueError,match='Unknown region'):load_slice(snapshot,LoadRequest('bedrock',('bad',),COLUMNS))
    with pytest.raises(ValueError,match='Unknown columns'):load_slice(snapshot,LoadRequest('bedrock',(),('oops',)))
    # A known region can have no rows in a column/context query; internal empty slices retain columns.
    from src.loader import key,validate
    e=_slice(key(snapshot,validate(snapshot)),('zz-empty-1',),('source_row_id','record_status'),'comparison',100)
    assert e.empty and list(e.columns)==['source_row_id','record_status']

@pytest.mark.parametrize('damage',['missing','hash','revision','schema','qa'])
def test_fail_closed(snapshot,damage):
    m=json.loads(snapshot.read_text())
    if damage=='missing': (snapshot.parent/'bedrock_prices.parquet').unlink()
    if damage=='hash':
        p=snapshot.parent/'bedrock_prices.parquet';p.write_bytes(p.read_bytes()+b'corrupt')
    if damage=='revision':m['dataset_revision']='bad'
    if damage=='schema':m['schema_revision']=99
    if damage=='qa':m['quality_checks']['passed']=False
    snapshot.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='Dataset activation failed'):available_regions(snapshot)

def test_region_discovery_cache_and_ineligible(tmp_path):
    a=raw_row();write_sources(tmp_path/'raw',amazon=[a,a,raw_row(SKU='other',RateCode='other',**{'Region Code':'ap-south-1','Unit':'hour'})])
    prepare(tmp_path/'raw',tmp_path/'clean');p=tmp_path/'clean/manifest.json'
    before=_regions.cache_info();assert available_regions(p)==('eu-west-1','us-east-1');assert available_regions(p)==('eu-west-1','us-east-1')
    after=_regions.cache_info();assert after.misses-before.misses==1 and after.hits-before.hits==1

def test_zero_regions(tmp_path):
    write_sources(tmp_path/'raw',amazon=[raw_row(Unit='hour')],market=[raw_row(serviceName='M',Unit='hour',PriceDescription='AWS Marketplace software usage|us-east-1|Unknown')])
    prepare(tmp_path/'raw',tmp_path/'clean');assert available_regions(tmp_path/'clean/manifest.json')==()

def test_row_safety_limit(snapshot,monkeypatch):
    import src.loader as loader
    monkeypatch.setattr(loader,'MAX_LOADED_ROWS',1)
    with pytest.raises(ValueError,match='narrow'):load_slice(snapshot,LoadRequest('bedrock',(),COLUMNS))

def test_copy_cache_and_inspection(snapshot):
    req=LoadRequest('bedrock',(),COLUMNS)
    a=load_slice(snapshot,req);a.rows.loc[:,'model_raw']='mutated'
    b=load_slice(snapshot,req);assert 'mutated' not in set(b.rows.model_raw)
    assert len(load_slice(snapshot,LoadRequest('bedrock',(),('record_status',),'inspection')).rows)>=len(b.rows)
