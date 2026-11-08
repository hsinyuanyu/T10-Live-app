"""Start a Streamlit server on a free port, check HTTP, and always stop it."""
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request


def main():
    with socket.socket() as s:
        s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
    with tempfile.TemporaryFile(mode='w+') as log:
        t=time.perf_counter()
        server=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.headless=true','--server.address=127.0.0.1',f'--server.port={port}','--browser.gatherUsageStats=false'],stdout=log,stderr=subprocess.STDOUT)
        try:
            for _ in range(120):
                if server.poll() is not None: raise RuntimeError('Streamlit exited before health check')
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/_stcore/health',timeout=1) as r:
                        assert r.read()==b'ok'
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}',timeout=1) as r:
                        assert r.status==200 and b'Streamlit' in r.read()
                    print(json.dumps({'port':port,'http_startup_seconds':time.perf_counter()-t,'health':'ok','root_status':200}));return
                except (OSError,AssertionError): time.sleep(.1)
            raise RuntimeError('Streamlit health timed out')
        finally:
            server.terminate()
            try: server.wait(timeout=10)
            except subprocess.TimeoutExpired: server.kill();server.wait(timeout=10)
            if server.returncode not in (0,-15):
                log.seek(0);print(log.read())

if __name__=='__main__': main()
