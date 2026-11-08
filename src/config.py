"""One location for all runtime paths and limits."""
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = Path(os.getenv('AWS_RAW_DATA_DIR', ROOT.parent / 'dataset_aws-price-list' / 'data'))
CLEAN_DIR = Path(os.getenv('AWS_CLEAN_DATA_DIR', ROOT / 'data' / 'snapshot'))
MANIFEST = CLEAN_DIR / 'manifest.json'
MAX_LOADED_ROWS = int(os.getenv('MAX_LOADED_ROWS', '100000'))
SCHEMA_REVISION = 1
TRANSFORM_VERSION = '1.0.0'
