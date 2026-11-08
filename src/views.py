"""Rendering receives already-calculated amounts; money is only formatted here."""
from decimal import Decimal, localcontext
import pandas as pd
import plotly.express as px
import streamlit as st
from src.filter import EMPTY_MESSAGE

def money(value, monthly=False):
    with localcontext() as ctx:
        ctx.prec = 100
        if monthly: return f'${value:,.2f}'
        return '$' + format(value, 'f')

def compare(result):
    st.metric('Eligible configurations', result.total)
    if not result.total: st.info(EMPTY_MESSAGE); return
    names = {'provider':'Provider','model':'Model','region':'Region','source':'Source','pricing_mode':'Inference mode',
             'serving_scope':'Serving scope','tier':'Tier','input_usd_per_1m':'Input USD/1M tokens', 'output_usd_per_1m':'Output USD/1M tokens',
             'per_request_cost_usd':'USD/request','per_1000_requests_usd':'USD/1,000 requests','monthly_cost_usd':'Monthly USD'}
    records = [{label: money(c[k], k=='monthly_cost_usd') if isinstance(c[k],Decimal) else c[k] for k,label in names.items()} for c in result.page]
    st.dataframe(pd.DataFrame(records), hide_index=True, width='stretch')
    st.caption(f'Page {result.page_number} of {max(1,(result.total+49)//50)} · 50 configurations per page. Sorted by exact monthly cost, then configuration ID.')
    with st.expander('Publisher identifiers and offer details for this page'):
        for c in result.page:
            st.markdown(f'**{c["model"]} · {c["region"]} · {c["serving_scope"]}**')
            st.json({k:c[k] for k in ['configuration_id','source_file','offer_version','publication_date','input_rate_code','output_rate_code','input_sku','output_sku','input_source_row_id','output_source_row_id']})
    with st.expander('Non-AWS evaluation metrics'):
        st.write('Model quality: Not available · Output speed: Not available · TTFT/latency: Not available')

def sensitivity(result):
    if not result.total: st.info(EMPTY_MESSAGE); return
    st.caption('Lowest-cost 10 configurations in the current base-case shortlist. Tokens/request and all constraints stay fixed; the base-case budget is not reapplied at each scenario.')
    chart = pd.DataFrame(result.scenarios)
    # Float conversion is for Plotly rendering only, after Decimal calculations.
    chart['Estimated monthly USD'] = chart.monthly_cost_usd.map(float)
    chart['Exact USD'] = chart.monthly_cost_usd.map(str)
    fig = px.line(chart,x='requests',y='Estimated monthly USD',color='label',markers=True,
                  labels={'requests':'Monthly requests','label':'Model · region · source · scope'},hover_data=['Exact USD'])
    fig.update_layout(legend=dict(orientation='h',y=-.3),margin=dict(t=20))
    st.plotly_chart(fig,use_container_width=True)
