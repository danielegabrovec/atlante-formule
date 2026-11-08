import json
import os
from pathlib import Path
import subprocess
import tempfile
import sys
ROOT=Path(__file__).resolve().parents[1]
exe=ROOT/'dist/AtlanteFormule/AtlanteFormule.exe'
scale=sys.argv[1] if len(sys.argv)>1 else '1'
report=ROOT/('verifiche/package-smoke.json' if scale=='1' else 'verifiche/package-smoke-dpi150.json')
env=os.environ.copy();win=os.environ.get('SystemRoot',r'C:\Windows');env['PATH']=str(Path(win)/'System32')+';'+win;env['QT_SCALE_FACTOR']=scale;env.pop('PYTHONPATH',None)
with tempfile.TemporaryDirectory(prefix='atlante-portable-') as cwd:
    env['ATLANTE_DATA_DIR']=str(Path(cwd)/'profile')
    result=subprocess.run([str(exe),'--qa-report',str(report)],cwd=cwd,env=env,timeout=65,creationflags=subprocess.CREATE_NO_WINDOW)
    log=Path(cwd)/'profile/avvio.log'
    (ROOT/f'verifiche/exe-startup-{scale}.log').write_text(log.read_text(encoding='utf-8') if log.exists() else '',encoding='utf-8')
    assert result.returncode==0,f'Exit code {result.returncode}'
data=json.loads(report.read_text(encoding='utf-8'))
assert data['ok'],data
print(json.dumps(data,ensure_ascii=False,indent=2))
print('EXE verificato da cartella di lavoro estranea, con PATH privo di Python.')
