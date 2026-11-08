from decimal import Decimal
import pandas as pd
import pytest
from src.data import normalize
from src.filter import evaluate,configurations,cost
from conftest import raw_row
META={'Version':'v1','Publication Date':'2026-10-01'}

def pair(model='Test',**changes):
    return [normalize(raw_row(Model=model,SKU=d,RateCode=d,PricePerUnit=p,**{'Inference Type':d+' tokens'},**changes),'bedrock_service_all.csv',META,i) for i,(d,p) in enumerate([('input','0.001'),('output','0.003')],1)]

def test_money_budget_scenarios():
    frame=pd.DataFrame(pair());r=evaluate(frame,['us-east-1'])
    assert r.total==1
    assert [r.rows[0][k] for k in ('monthly_cost_usd','per_request_cost_usd','per_1000_requests_usd')]==[Decimal('4'),Decimal('.004'),Decimal('4')]
    assert [s['monthly_cost_usd'] for s in r.scenarios]==[Decimal('2'),Decimal('4'),Decimal('8')]
    assert evaluate(frame,['us-east-1'],budget='3.99').total==0
    r=evaluate(frame,['us-east-1'],budget='4');assert r.total==1 and r.scenarios[-1]['monthly_cost_usd']==8
    assert evaluate(frame,[]).total==0
    assert evaluate(frame,['us-east-1'],input_tokens=0,output_tokens=0,budget=0).rows[0]['monthly_cost_usd']==0
    assert cost(1000000,1000000,'0','0')==0
    assert evaluate(frame,['us-east-1'],budget='3.99999999999999999999999999999999999999').total==0

def test_matching_exclusions():
    good=pair();incomplete=pair('Missing')[:1];ambiguous=pair('Ambiguous');ambiguous.append(ambiguous[0]|{'rate_code':'second','price_usd_per_1m_tokens':'9'})
    priority=pair('Mode');priority[0]['pricing_mode']='priority'
    tier=pair('Tier');tier[0]['service_tier_raw']='flex'
    rows,reasons=configurations(pd.DataFrame(good+incomplete+ambiguous+priority+tier))
    assert len(rows)==1 and reasons['ambiguous_configurations']==1
    assert reasons['incomplete_or_mismatched_configurations']==3 and reasons['nonstandard_or_incompatible_rate_rows']==2

def test_no_fuzzy_or_cross_source_merge():
    rows=pair();rows[1]['model_raw']='Test v2'
    assert configurations(pd.DataFrame(rows))[0]==[]
    rows=pair();rows[1]['source_type']='marketplace'
    assert configurations(pd.DataFrame(rows))[0]==[]
    rows=pair();rows[1]['serving_scope']='global'
    assert configurations(pd.DataFrame(rows))[0]==[]

def test_versions_and_pagination():
    frame=pd.DataFrame(sum((pair(f'Test {i}') for i in range(51)),[]))
    a=evaluate(frame,['us-east-1']);b=evaluate(frame,['us-east-1'],page=2)
    assert a.total==b.total==51 and len(a.page)==50 and len(b.page)==1 and len(a.scenarios)==30
    assert len(set(r['configuration_id'] for r in a.page+b.page))==51
    frame.loc[0,'offer_version']='new'
    with pytest.raises(ValueError,match='Mixed offer versions'):evaluate(frame,['us-east-1'])

@pytest.mark.parametrize('field,value',[('input_tokens',-1),('output_tokens','1.5'),('requests','NaN'),('budget','-0.1'),('budget','Infinity'),('budget','nope'),('scenarios',[-1])])
def test_invalid_inputs(field,value):
    with pytest.raises(ValueError):evaluate(pd.DataFrame(pair()),['us-east-1'],**{field:value})
