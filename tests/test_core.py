import json
import math
from pathlib import Path
import pytest
import sympy as s
from atlante.engine import parse,calculate,lab
from atlante.store import Store
from atlante.paths import ROOT

CARDS=json.loads((ROOT/'atlante/data/catalog.json').read_text(encoding='utf-8'))['cards']
BY={c['id']:c for c in CARDS}

def test_catalog_contract():
    assert len(CARDS)==988
    assert len(BY)==988
    assert len({c['title'] for c in CARDS})==988
    expected=[50,35,35,30,65,40,40,25,45,35,35,45,20,24,30,28,24,24,28,26,26,28,24,24,32,28,18,16,24,24,18,16,14,12]
    groups=list(dict.fromkeys(c['editorial_group'] for c in CARDS))
    assert [sum(c['editorial_group']==g for c in CARDS) for g in groups]==expected
    assert sum(bool(c['calculator']) for c in CARDS)>=120
    assert sum(bool(c['plot']) for c in CARDS)>=60
    for c in CARDS:
        for k in ('title','latex','explanation','conditions','example','symbols'):assert c[k].strip(),(c['id'],k)
        assert c['sources']
        assert all(cid in BY for cid in c['related'])

@pytest.mark.parametrize('card',[c for c in CARDS if c['calculator']],ids=lambda c:c['id'])
def test_all_calculators_default_real(card):
    # Controllo di eseguibilità per ogni scheda, distinto dagli oracoli indipendenti sotto.
    result=calculate(card,{f['name']:f['default'] for f in card['calculator']['inputs']})
    assert math.isfinite(result['value'])

@pytest.mark.parametrize('cid,inputs,expected',[
 ('base-001',{'a':'1','b':'2','c':'1','d':'3'},5/6),
 ('base-022',{'a':'3','b':'-12'},4),
 ('base-040',{'n':'6','k':'2'},15),
 ('classica-008',{'a':'3','b':'4'},5),
 ('classica-008',{'a':'300 cm','b':'4 m'},5),
 ('classica-011',{'b':'6','h':'4'},12),
 ('classica-012',{'a':'3','b':'4','c':'5'},6),
 ('classica-020',{'b':'7','h':'3'},21),
 ('classica-035',{'r':'3'},36*math.pi),
 ('analitica-001',{'x1':'1','y1':'2','x2':'4','y2':'6'},5),
 ('analitica-012',{'a':'3','b':'4','c':'-10','x0':'0','y0':'0'},2),
 ('analitica-024',{'a':'5','b':'3'},.8),
 ('trigonometria-025',{'a':'5','alpha':'pi/6'},10),
 ('meccanica-021',{'F':'10','s':'3','theta':'pi/3'},15),
 ('meccanica-022',{'m':'2','v':'3'},9),
 ('meccanica-031',{'m1':'2','v1':'3','m2':'1','v2':'0'},2),
 ('termo-021',{'nu':'1','R':'8','T':'300','V':'.024'},100000),
 ('elettro-019',{'resistance':'100','current':'.02'},2),
 ('elettro-022',{'R1':'100','R2':'200'},200/3),
 ('moderna-001',{'v':'0.6','c0':'1'},1.25),
 ('moderna-018',{'rate':'0.1'},math.log(2)/.1),
])
def test_numeric_oracles(cid,inputs,expected):
    assert calculate(BY[cid],inputs)['value']==pytest.approx(expected,rel=1e-10)

@pytest.mark.parametrize('text',["__import__('os')","x.__class__","[x for x in y]","lambda x:x","open('x')","factorial(201)","2^1001","1/0"])
def test_rejected_syntax(text):
    with pytest.raises((ValueError,SyntaxError,TypeError)):parse(text)

@pytest.mark.parametrize('cid,inputs',[
 ('classica-012',{'a':'1','b':'2','c':'3'}),('classica-008',{'a':'-1','b':'2'}),
 ('classica-004',{'alpha':'pi','beta':'pi/3'}),('classica-009',{'c':'5','p':'9'}),
 ('analitica-024',{'a':'3','b':'5'}),('probabilita-001',{'fav':'8','total':'6'}),
 ('moderna-001',{'v':'2','c0':'1'}),('onde-022',{'a':'1','b':'1.5'}),
 ('termo-032',{'T1':'300','T2':'400'}),('base-029',{'x':'8','b0':'1'}),
 ('moderna-009',{'f':'1','hP':'1','energy':'2'})])
def test_model_domains(cid,inputs):
    with pytest.raises(ValueError):calculate(BY[cid],inputs)

@pytest.mark.parametrize('req,expected',[
 ({'operation':'derivata','expression':'x^3'},'3*x**2'),
 ({'operation':'integrale definito','expression':'x^2','a':'0','b':'3'},'9'),
 ({'operation':'limite','expression':'sin(x)/x','a':'0','direction':'+-'},'1'),
 ({'operation':'determinante','expression':'1,2;3,4'},'-2'),
 ({'operation':'rango','expression':'1,2;2,4'},'1'),
 ({'operation':'distanza punto-retta','expression':'0;0;3;4;-10'},'2'),
 ])
def test_lab(req,expected):assert lab(req)['text']==expected

def test_geometry_and_gauss():
    r=lab({'operation':'intersezione retta-conica','expression':'y-1;x^2+y^2-1'})
    assert len(r['steps'])==3 and '1.' in r['steps'][-1]
    assert lab({'operation':'intersezione retta-conica','expression':'y-2;x^2+y^2-1'})['text']=='[]'
    with pytest.raises(ValueError):lab({'operation':'intersezione retta-conica','expression':'y-x;x^2-y^2'})
    with pytest.raises(ValueError):lab({'operation':'retta per due punti','expression':'1;1;1;1'})
    assert lab({'operation':'retta per due punti','expression':'2;1;2;5'})['text']=='Eq(4*x - 8, 0)'
    with pytest.raises(ValueError):lab({'operation':'inversa','expression':'1,2;2,4'})
    result=lab({'operation':'riduzione','expression':'1,1,3;2,1,4'})
    assert result['text']=='Matrix([[1, 0, 1], [0, 1, 2]])'
    assert len(result['steps'])>=3

def test_store_roundtrip(tmp_path):
    store=Store(tmp_path/'a.db');c=store.save_card({'title':'Area di prova','latex':'A=bh','explanation':'Base per altezza.','conditions':'b,h>0','example':'3*4=12','tags':['test']})
    store.favorite(c['id']);store.save_note(c['id'],'Annotazione italiana: π.');store.visit(c['id']);store.set_setting('theme','dark')
    assert store.search('pitagroa')[0]['id']=='classica-008'
    assert store.search('Euclide',category='classica')
    data=store.export();store.close()
    store=Store(tmp_path/'a.db');assert store.note(c['id'])=='Annotazione italiana: π.';assert store.setting('theme')=='dark';store.close()
    other=Store(tmp_path/'b.db');assert other.import_data(data)==1;assert other.note(c['id'])=='Annotazione italiana: π.'
    assert c['id'] in other.favorites;other.delete_card(c['id']);assert c['id'] not in other.by_id;other.close()

def test_invalid_import_atomic(tmp_path):
    store=Store(tmp_path/'a.db');before=len(store.cards)
    with pytest.raises(ValueError):store.import_data({'schema_version':1,'cards':[{'title':'Incompleta'}]})
    assert len(store.cards)==before;store.close()

def test_invalid_settings_import(tmp_path):
    store=Store(tmp_path/'a.db')
    for settings in ({'font_size':'abc'},{'font_size':'999'},{'theme':'invalid'}):
        with pytest.raises(ValueError):store.import_data({'schema_version':1,'cards':[],'settings':settings})
    assert store.setting('font_size','16')=='16';store.close()

def test_curve_discontinuity():
    import numpy as np
    from atlante.plots import sample_curve
    x,y=sample_curve('1/x','x',-1,1)
    assert np.isnan(y[np.argmin(abs(x))])
    _,y=sample_curve('sqrt(x)','x',-2,2)
    assert np.isnan(y[:500]).all()
