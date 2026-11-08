"""Read-only setup orchestration with one shared request state."""
from src.filter import COLUMNS, evaluate, integer, budget_value
from src.loader import LoadRequest, load_slice

def run_comparison(manifest, regions, inputs):
    # Validate even when selection is empty; never dispatch loader's all-regions sentinel.
    integer(inputs['input_tokens'], 'Input tokens/request')
    integer(inputs['output_tokens'], 'Output tokens/request')
    integer(inputs['requests'], 'Requests/month')
    budget_value(inputs.get('budget'))
    if not regions: return None
    loaded = load_slice(manifest, LoadRequest('bedrock',tuple(regions),COLUMNS))
    return loaded, evaluate(loaded.rows,regions,**inputs)
