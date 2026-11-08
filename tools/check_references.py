"""Verifica l'accessibilità degli URL, senza scaricare libri o materiali didattici."""
import concurrent.futures
import json
from datetime import datetime,timezone
from pathlib import Path
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'atlante/data/catalog.json').read_text(encoding='utf-8'))
urls={s['url'] for c in data['cards'] for s in c['sources']}
urls.update(c['source'] for c in data.get('courses',[]))
def check(url):
    row={'url':url}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (AtlanteFormule reference availability check)'})
        with urllib.request.urlopen(req,timeout=12) as response:
            row.update(status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type',''),accessible=200<=response.status<400)
    except urllib.error.HTTPError as exc:row.update(status=exc.code,accessible=False,error=str(exc))
    except Exception as exc:row.update(status=None,accessible=False,error=str(exc))
    return row
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(check,sorted(urls)))
report={'checked_utc':datetime.now(timezone.utc).isoformat(),'note':'Un HTTP 200 verifica l’accesso alla pagina, non certifica le formule. Timeout e blocchi non dimostrano che un riferimento sia inesistente.','results':results}
(ROOT/'verifiche/fonti-online.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'total':len(results),'accessible':sum(r['accessible'] for r in results),'unconfirmed':[r for r in results if not r['accessible']]},ensure_ascii=True,indent=2))
