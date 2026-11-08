"""Crea ZIP e manifest SHA256, senza includere ambiente o dati personali."""
from pathlib import Path
import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
bundle=ROOT/'dist/AtlanteFormule'
if not (bundle/'AtlanteFormule.exe').exists():raise SystemExit('EXE mancante: eseguire Build.ps1.')
results=ET.parse(ROOT/'verifiche/test-results.xml')
assert all(int(suite.get('failures',0))==int(suite.get('errors',0))==0 for suite in results.iter('testsuite')),'La suite di verifica contiene errori.'
for name in ('package-smoke.json','package-smoke-dpi150.json'):
    p=ROOT/'verifiche'/name
    assert p.stat().st_mtime>=(bundle/'AtlanteFormule.exe').stat().st_mtime,'Ripetere la verifica EXE dopo la compilazione.'
    assert json.loads(p.read_text(encoding='utf-8')).get('ok'),f'Verifica EXE non superata: {name}'
for name in ('GUIDA.md','VERIFICHE.md','AUDIT_FORMULE.md','MATERIE.md','CONSEGNA.md','requirements-lock.txt'):
    import shutil
    shutil.copy2(ROOT/name,bundle/name)
evidence=bundle/'verifiche';evidence.mkdir(exist_ok=True)
for name in ('test-results.xml','tests.log','audit-formule.json','fonti-online.json','package-smoke.json','package-smoke-dpi150.json'):
    shutil.copy2(ROOT/'verifiche'/name,evidence/name)
manifest={str(p.relative_to(bundle)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in bundle.rglob('*') if p.is_file() and p.name!='SHA256.json'}
(bundle/'SHA256.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
out=ROOT/'dist/AtlanteFormule-Windows-x64.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in bundle.rglob('*'):
        if p.is_file():z.write(p,'AtlanteFormule/'+p.relative_to(bundle).as_posix())
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for relative,digest in manifest.items():assert hashlib.sha256(z.read('AtlanteFormule/'+relative)).hexdigest()==digest
sources=ROOT/'dist/AtlanteFormule-Sorgenti.zip'
with zipfile.ZipFile(sources,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for dirname in ('atlante','contenuti','tools','tests','LICENZE','verifiche'):
        for p in (ROOT/dirname).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and not any(part.endswith('-profile') for part in p.parts) and p.suffix not in ('.db','.sqlite3'):
                z.write(p,p.relative_to(ROOT).as_posix())
    for name in ('LICENSE','COPYRIGHT.md','THIRD_PARTY.md','main.py','README.md','CONSEGNA.md','GUIDA.md','VERIFICHE.md','AUDIT_FORMULE.md','MATERIE.md','Build.ps1','Avvia.cmd','requirements.txt','requirements-dev.txt','requirements-lock.txt','pytest.ini','vendor/package.json','vendor/package-lock.json'):
        z.write(ROOT/name,name)
    for p in (ROOT/'vendor/node_modules').rglob('*'):
        if p.is_file():z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(sources) as z:
    assert z.testzip() is None
    for member in z.infolist():
        original=ROOT/member.filename
        assert original.is_file() and hashlib.sha256(z.read(member.filename)).digest()==hashlib.sha256(original.read_bytes()).digest(),member.filename
(ROOT/'dist/SHA256SUMS.txt').write_text('\n'.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}' for p in (out,sources))+'\n',encoding='utf-8')
print('ZIP verificati:',out.name,sources.name)
