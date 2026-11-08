from unittest.mock import patch
from pathlib import Path
from streamlit.testing.v1 import AppTest
from src.setup import run_comparison
from src.loader import _slice
from src.config import MANIFEST

APP=Path(__file__).resolve().parents[1]/'app.py'


def test_empty_selection_never_loads(snapshot):
    with patch('src.setup.load_slice') as loader:
        assert run_comparison(snapshot,[],dict(input_tokens=1000,output_tokens=1000,requests=1000)) is None
        loader.assert_not_called()

def test_money_updates_reuse_slice(snapshot):
    before=_slice.cache_info()
    for volume,budget in [(1000,None),(2000,'10'),(500,'4')]:
        run_comparison(snapshot,['us-east-1'],dict(input_tokens=1000,output_tokens=1000,requests=volume,budget=budget))
    after=_slice.cache_info()
    assert after.misses-before.misses==1 and after.hits-before.hits==2

def test_real_ui():
    assert MANIFEST.exists()
    app=AppTest.from_file(APP,default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value=='AWS Bedrock Model Cost Comparison'
    assert 'Published AWS list-price' in app.warning[0].value
    assert len(app.tabs)==2 and app.metric[0].value!='0' and len(app.dataframe)==1 and len(app.get('plotly_chart'))==1
    app.text_input[3].set_value('0').run()
    assert not app.exception and any(i.value=='No model configurations match the current filters.' for i in app.info)
    app.multiselect[0].set_value([]).run()
    assert not app.exception and any(i.value=='No model configurations match the current filters.' for i in app.info)
    app.multiselect[0].set_value(['us-east-1']);app.text_input[0].set_value('-1').run()
    assert not app.exception and 'Input tokens/request' in app.error[0].value and len(app.dataframe)==0


def test_manifest_ui_errors_and_sample(snapshot):
    import json
    with patch('src.config.MANIFEST',snapshot):
        m=json.loads(snapshot.read_text());m['is_sample']=True;snapshot.write_text(json.dumps(m))
        app=AppTest.from_file(APP,default_timeout=30).run()
        assert not app.exception and 'SAMPLE' in app.error[0].value and len(app.dataframe)==0
        snapshot.unlink()
        app=AppTest.from_file(APP,default_timeout=30).run()
        assert not app.exception and 'activation failed' in app.error[0].value and len(app.code)==1


def test_zero_region_ui(tmp_path):
    from conftest import write_sources,raw_row
    from src.data import prepare
    write_sources(tmp_path/'raw',amazon=[raw_row(Unit='hour')],market=[raw_row(serviceName='M',Unit='hour',PriceDescription='Unknown')])
    prepare(tmp_path/'raw',tmp_path/'clean')
    with patch('src.config.MANIFEST',tmp_path/'clean/manifest.json'):
        app=AppTest.from_file(APP,default_timeout=30).run()
        assert not app.exception and 'No valid regions' in app.error[0].value and len(app.multiselect)==0
