"""Cross-platform measurements and an independent raw-pair audit; raw data stays local."""
import argparse
import csv
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from decimal import Decimal
import pandas as pd
import psutil
from streamlit.testing.v1 import AppTest
from src.config import MANIFEST, ROOT
from src.loader import available_regions, load_slice, LoadRequest
from src.filter import COLUMNS, evaluate


def measure_child(command):
    with tempfile.TemporaryFile(mode='w+') as output:
        start = time.perf_counter()
        child = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT)
        peak = 0
        while child.poll() is None:
            try:
                proc = psutil.Process(child.pid)
                peak = max(peak, proc.memory_info().rss + sum(p.memory_info().rss for p in proc.children(recursive=True)))
            except (psutil.NoSuchProcess, psutil.AccessDenied): pass
            time.sleep(.02)
        seconds=time.perf_counter()-start
        output.seek(0)
        if child.returncode: raise RuntimeError(output.read())
        return seconds,peak/1e6


def main():
    p=argparse.ArgumentParser();p.add_argument('--raw-dir',type=Path,default=ROOT/'data/raw');a=p.parse_args()
    with tempfile.TemporaryDirectory(prefix='t10-benchmark-') as scratch:
        prep, prep_peak=measure_child([sys.executable,'-m','src.data','prepare','--raw-dir',str(a.raw_dir),'--out-dir',str(Path(scratch)/'clean')])
    start=time.perf_counter();regions=available_regions(MANIFEST);loaded=load_slice(MANIFEST,LoadRequest('bedrock',('us-east-1',),COLUMNS));r=evaluate(loaded.rows,['us-east-1']);cold=time.perf_counter()-start
    timings=[]
    for i in range(30):
        t=time.perf_counter();load_slice(MANIFEST,LoadRequest('bedrock',('us-east-1',),COLUMNS));evaluate(loaded.rows,['us-east-1'],requests=500+i*100,budget='100');timings.append(time.perf_counter()-t)
    # Independent comparison: original CSV rows, actual metadata and original unit prices.
    candidate=r.rows[0]
    raw_path=a.raw_dir/candidate['source_file']
    raw=pd.read_csv(raw_path,skiprows=5,dtype=str,keep_default_na=False)
    with raw_path.open(newline='',encoding='utf-8') as f:
        reader=csv.reader(f);meta=dict(next(reader) for _ in range(5))
    assert candidate['offer_version']==meta['Version'] and candidate['publication_date']==meta['Publication Date']
    audit=[]
    for direction in ('input','output'):
        rr=raw[raw.RateCode==candidate[direction+'_rate_code']]
        assert len(rr)==1;row=rr.iloc[0]
        import hashlib
        expected_id=hashlib.sha256(f'{candidate["source_file"]}|{meta["Version"]}|{int(rr.index[0])+1}'.encode()).hexdigest()
        assert expected_id==candidate[direction+'_source_row_id']
        assert row['Region Code']=='us-east-1'
        assert row['Model']==candidate['model_raw']
        assert direction in row['Inference Type'].lower()
        rate=Decimal(row.PricePerUnit)*({'1K tokens':Decimal(1000),'1M tokens':Decimal(1)}[row.Unit])
        assert rate==candidate[direction+'_usd_per_1m']
        audit.append(dict(direction=direction,rate_code=row.RateCode,sku=row.SKU,unit=row.Unit,raw_rate=row.PricePerUnit,normalized_rate=str(rate),inference_type=row['Inference Type'],tier=row.service_tier))
    proc=psutil.Process();peak=[proc.memory_info().rss];stop=threading.Event()
    def sample():
        while not stop.wait(.02): peak[0]=max(peak[0],proc.memory_info().rss)
    sampler=threading.Thread(target=sample);sampler.start()
    t=time.perf_counter();app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run();ui=time.perf_counter()-t
    assert not app.exception
    # A real UI volume change exercises cached loading and both shared views.
    t=time.perf_counter();app.text_input[2].set_value('2000').run();interaction=time.perf_counter()-t
    assert not app.exception
    stop.set();sampler.join()
    m=json.loads(MANIFEST.read_text());q=loaded.quality_summary
    result=dict(preparation_seconds=prep,preparation_peak_mb=prep_peak,cold_loader_filter_seconds=cold,warm_median_seconds=statistics.median(timings),warm_max_seconds=max(timings),
        ui_startup_seconds=ui,ui_volume_update_seconds=interaction,ui_process_peak_mb=peak[0]/1e6,loaded_rows=len(loaded.rows),matches=r.total,regions=len(regions),
        source_rows=sum(x['raw'] for x in q['sources'].values()),raw_bytes=sum(s['byte_size'] for s in m['sources']),audit_model=candidate['model'],audit_source=candidate['source_file'],audit=audit,
        dataset_revision=m['dataset_revision'],sources=m['sources'],quality=q)
    (ROOT/'reports/measurements.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('sources','quality')},indent=2))

if __name__=='__main__': main()
