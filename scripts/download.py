"""Use the course downloader, selecting only the two required Bedrock files."""
import argparse
import importlib.util
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--dataset-repo', type=Path, default=Path('../dataset_aws-price-list'))
p.add_argument('--out-dir', type=Path, default=Path('data/raw'))
a = p.parse_args()
s = importlib.util.spec_from_file_location('course_downloader', a.dataset_repo / 'download_data.py')
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
a.out_dir.mkdir(parents=True, exist_ok=True)
for name, url, size, digest, _ in m.FILES:
    if name in ('bedrock_foundation_models.csv', 'bedrock_service_all.csv'):
        if not m.download_one(url, a.out_dir / name, size, digest):
            raise SystemExit(f'Download failed: {name}')
