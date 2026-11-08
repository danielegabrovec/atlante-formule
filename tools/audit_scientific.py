"""Registro riproducibile della revisione; non una certificazione matematica."""
import hashlib
import importlib.util
import json
import math
import sys
import subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atlante.engine import calculate,dimensional_result,units
from atlante.logic import logic_lab
from tools.revise_legacy import CHANGES

ROOT=Path(__file__).resolve().parents[1]
FIELDS=('title','latex','explanation','conditions','example','symbols','calculator','logic','code_example','kind')
MANUAL_UNITS={
 'termo-014':'Conversione affine Celsius→kelvin: unità del dato Celsius e offset esplicitati nella scheda.',
 'moderna-015':'La costante numerica −13.6 contiene implicitamente eV; formula energetica di Bohr approssimata.',
}
UNIT_ALIASES={'bit logico':'','bit':'','byte':'','pagine':'','host':'','sottoreti':'','bit/s':'1/s','byte/s':'1/s','risultati/s':'1/s'}
FLOAT_ZERO_TOLERANCE={'trigonometria-009':2e-15,'onde-011':2e-16}

def load_references():
    spec=importlib.util.spec_from_file_location('engineering_reference_cases',ROOT/'tests/test_review.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return dict(module.CASES)

def audit():
    raw=json.loads((ROOT/'atlante/data/catalog.json').read_text(encoding='utf-8'));cards=raw['cards']
    baseline=json.loads((ROOT/'versioni/1.0/catalog.json').read_text(encoding='utf-8'))['cards'];before={c['id']:c for c in baseline}
    references=load_references();registry=[];errors=[];boolean_rows=0
    for c in cards:
        cid=c['id'];checks=['revisione interna di relazione, significato, condizioni ed esempio','campi obbligatori e riferimenti bibliografici per argomento']
        record={'id':cid,'title':c['title'],'origin':'v1.0' if cid in before else 'nuova v1.1','review_type':'revisione interna, non peer review',
                'content_sha256':hashlib.sha256(json.dumps({k:c.get(k) for k in FIELDS},ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
                'changed_fields':[k for k in FIELDS if cid in before and c.get(k)!=before[cid].get(k)],'checks':checks,'sources':c['sources']}
        if c.get('calculator'):
            try:
                result=calculate(c,{})
                assert math.isfinite(result['value'])
                checks.append('esecuzione numerica dei dati di esempio con dominio verificato')
                if cid in references:
                    expected=references[cid]
                    assert math.isclose(result['value'],expected,rel_tol=2e-10,abs_tol=1e-25),(result['value'],expected)
                    checks.append('confronto con valore atteso redatto separatamente nei test di riferimento')
                if cid in MANUAL_UNITS:record['units']=MANUAL_UNITS[cid]
                else:
                    q=dimensional_result(c['calculator']['expression'],c['calculator']['inputs'],quantity=True)
                    output=c['calculator']['output_unit'];target=UNIT_ALIASES.get(output,output)
                    if output not in ('%','dB'):
                        expected=float(q.to(target or '').magnitude)
                        assert math.isclose(result['value'],expected,rel_tol=2e-9,abs_tol=FLOAT_ZERO_TOLERANCE.get(cid,1e-25)),(result['value'],expected,output)
                        record['units']='dimensione e scala con quantità Pint; bit/byte logici sono conteggi nominali dichiarati dai campi' if output in UNIT_ALIASES else 'dimensione e scala delle unità verificate con quantità Pint'
                        if cid in FLOAT_ZERO_TOLERANCE:record['floating_reference_tolerance']=FLOAT_ZERO_TOLERANCE[cid]
                    else:record['units']='scala logaritmica o percentuale esplicita; risultato nominale dB o punti percentuali, non conversione lineare Pint'
                    checks.append('coerenza fra unità degli ingressi, scala numerica e unità di uscita')
            except Exception as exc:errors.append({'id':cid,'error':str(exc)});record['error']=str(exc)
        if c.get('logic'):
            logic=c['logic'];text=logic['expression']+('; '+logic['equivalent_to'] if logic.get('equivalent_to') else '')
            res=logic_lab({'operation':'equivalenza booleana' if logic.get('equivalent_to') else 'tabella di verità','expression':text})
            boolean_rows+=len(res['table']['rows']);record['boolean_assignments']=len(res['table']['rows'])
            if logic.get('equivalent_to'):assert res['equivalent'],cid;checks.append('equivalenza esaustiva dell’identità o esempio booleano associato')
            else:checks.append('tabella completa del circuito booleano associato')
        if c.get('code_example'):
            code=c['code_example']['source']
            run=subprocess.run([sys.executable,'-I','-c',code],capture_output=True,text=True,timeout=3)
            if run.returncode:errors.append({'id':cid,'error':run.stderr})
            else:checks.append('esempio Python autonomo eseguito con le asserzioni di verifica')
        registry.append(record)
    report={'version':raw['catalog_version'],'date':'2026-10-25','cards':len(cards),'original_cards_reviewed':len(before),'new_cards':len(cards)-len(before),
            'editorial_revisions_registered':len(CHANGES),'calculators':sum(bool(c['calculator']) for c in cards),
            'reference_cases_new_calculators':len(references),'boolean_assignments_checked':boolean_rows,
            'method':'Revisione interna dell’intero catalogo, controlli numerici/dimensionali e identità selezionate. Non costituisce prova formale generale o certificazione scientifica indipendente.',
            'engine_sha256':{name:hashlib.sha256((ROOT/'atlante'/name).read_bytes()).hexdigest() for name in ('engine.py','validation.py','catalog_rules.py','logic.py','sampling.py','plots.py')},
            'errors':errors,'entries':registry}
    (ROOT/'verifiche/audit-formule.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('entries','method')},ensure_ascii=True,indent=2))
    if errors:raise SystemExit(1)

if __name__=='__main__':audit()
