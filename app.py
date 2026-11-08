import streamlit as st
from src.config import MANIFEST
from src.loader import available_regions, validate
from src.setup import run_comparison
from src.filter import EMPTY_MESSAGE, integer
from src.views import compare, sensitivity

st.set_page_config(page_title='Bedrock Model Cost Comparison',page_icon='☁️',layout='wide')
st.title('AWS Bedrock Model Cost Comparison')
st.write('Shortlist model–region configurations for a known workload, then stress-test monthly request volume.')
st.warning('Published AWS list-price estimates only — not your actual bill; discounts, credits, taxes, quality and latency are excluded.')
try:
    regions = available_regions(MANIFEST,'bedrock')
    manifest = validate(MANIFEST)
except ValueError as e:
    st.error(str(e)); st.code('uv sync\nuv run python scripts/download.py\nuv run python -m src.data prepare --raw-dir data/raw --out-dir data/snapshot\nuv run streamlit run app.py'); st.stop()
if manifest['is_sample']: st.error('SAMPLE dataset — inspection only. Prepare both full AWS sources to enable production comparisons.'); st.stop()
st.caption(f'Activated dataset {manifest["dataset_revision"]} · Schema {manifest["schema_revision"]} · Read-only snapshot; refresh only with explicit preparation.')
with st.expander('Price snapshots and lineage'):
    for s in manifest['sources']:
        st.write(f'{s["source_file"]} · Offer {s["offer_version"]} · Published {s["publication_date"]}')
        st.markdown(f'[AWS source]({s["source_url"]})'); st.caption(f'SHA-256 {s["sha256"]} · Acquired {s["download_timestamp"]}')
if not regions: st.error('No valid regions exist in this dataset. Prepare a full source with eligible token rates.'); st.stop()
st.caption('Bedrock only · Standard, uncached, non-batch, non-provisioned pricing. Global and regional serving contexts remain separate.')
selected = st.multiselect('Region(s)',regions,default=['us-east-1'] if 'us-east-1' in regions else [])
a,b,c,d = st.columns(4)
it = a.text_input('Input tokens/request','1000')
ot = b.text_input('Output tokens/request','1000')
volume = c.text_input('Requests/month','1000')
budget = d.text_input('Maximum monthly USD (optional)','')
scenarios = st.text_input('Sensitivity requests/month (comma-separated)','500, 1000, 2000')
page = st.number_input('Compare page',min_value=1,value=1,step=1)
try:
    scenario_values = [integer(v.strip(),'Sensitivity scenarios') for v in scenarios.split(',')]
    inputs = dict(input_tokens=it,output_tokens=ot,requests=volume,budget=budget,scenarios=scenario_values,page=page)
    response = run_comparison(MANIFEST,selected,inputs)
except ValueError as e: st.error(str(e)); st.stop()
if response is None: st.info(EMPTY_MESSAGE); st.stop()
loaded,result = response
st.caption(f'Active workload: {integer(it,"Input tokens/request"):,} input + {integer(ot,"Output tokens/request"):,} output tokens/request × {integer(volume,"Requests/month"):,} requests/month. Budget: {budget or "unset"} USD.')
comparison_tab, sensitivity_tab = st.tabs(['Compare','Sensitivity'])
with comparison_tab: compare(result)
with sensitivity_tab: sensitivity(result)
with st.expander('Exclusions and preparation diagnostics'):
    st.write('Pairing/filter exclusions in the selected regions'); st.json(result.excluded)
    st.write('Source-level accounting, excluded-rate reasons and detected columns'); st.json(loaded.quality_summary)
    st.caption(f'{len(loaded.rows):,} eligible rate rows loaded. A region with eligible rates may still lack a complete standard pair.')
