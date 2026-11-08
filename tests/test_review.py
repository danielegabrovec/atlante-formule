"""Controlli scientifici aggiuntivi: casi attesi, domini, identità e unità."""
import itertools
import json
import math
import pytest
import sympy as s
from atlante.paths import ROOT
from atlante.engine import calculate,lab,units
from atlante.logic import boolean,logic_lab
from atlante.sections import SECTIONS,section_color

DATA=json.loads((ROOT/'atlante/data/catalog.json').read_text(encoding='utf-8'))
BY={c['id']:c for c in DATA['cards']}

# Risultati di riferimento fissati separatamente dalle implementazioni. I casi
# trascendenti usano funzioni math e dati noti; non si legge reference_value.
DEFAULTS={
 'sistemi_operativi':{3:1/101,4:10,5:6,6:.5,13:3,14:2288,15:111e-9,17:109.9999e-9},
 'distribuita':{2:4096,4:.001506,9:100663296,10:16000000,13:1200*math.sqrt(3),14:4096000},
 'bool':{1:0,2:0,3:1,4:0,5:1,6:0,7:0},
 'digitale':{1:0,2:1,5:17e-9,9:255,10:127,11:-1,13:144,14:-2,15:15,20:4,21:8e-9,22:.4e-9,23:2e-9,24:.9,25:108.9e-6,26:3.3e-6,27:80,28:8192,29:3.3/4096,30:74.0081},
 'discreta':{4:30,6:12,7:32,8:81,18:15,19:9},
 'numerico':{1:math.sqrt(2)-1.414,2:1-1.414/math.sqrt(2),3:2**-52,5:4.99999999999875e-7,9:9},
 'elettronica':{1:4,2:.02,8:1000/(2*math.pi),9:10000/(2*math.pi),10:20,11:10,12:math.expm1(.6/.02585)*1e-12,13:1.380649e-23*300/1.602176634e-19,14:.002,15:.002/.02585,16:.001,17:.02585/(.001+1e-12),18:-2,19:2,23:100000,24:125000/math.pi},
 'segnali':{15:100,23:-10,28:1e-6/12},
 'robotica':{6:2-2/math.exp(2),8:math.exp(-math.pi/math.sqrt(3)),9:.8,21:1},
 'reti':{1:120e-6,2:.005,4:2000000,5:.8,6:2,7:.05,8:-math.expm1(12000*math.log1p(-1e-6)),10:4000000,11:12000,12:100,13:254,14:8,15:1310720,16:1/21,17:10/9,18:1/math.e,19:.5/math.e,22:math.exp(-.1),23:3,24:7,25:.0002099,26:2000},
 'informatica':{3:10,6:.75,7:4,10:1,12:3.5e-9,13:80/17,14:.6,15:7.3,16:500000000,18:16,19:-math.expm1(-.4995),20:(-math.expm1(-.7))**7,21:10*math.log(2),23:200000,24:.1,28:3},
 'statistica':{2:4/3,9:1,16:2/math.exp(5),18:1},
 'ml':{6:.5,12:.5,19:math.log(2),26:.8,27:8/9,28:16/19,29:.97},
 'deep':{2:8256,9:1/96,10:1/64,17:16,18:1792},
 'quantum':{7:1024,18:8*math.pi},
 'bioai':{9:.00005,13:2/13,14:1881/1883,15:.925},
 'visione':{14:5,15:.125,19:20*math.log10(25.5),21:.6,22:.8},
}
CASES=[(f'{cat}-{index:03}',expected) for cat,items in DEFAULTS.items() for index,expected in items.items()]

@pytest.mark.parametrize('cid,expected',CASES)
def test_engineering_expected_values(cid,expected):
    result=calculate(BY[cid],{})
    assert result['value']==pytest.approx(expected,rel=2e-10,abs=1e-25)

def test_every_new_calculator_has_reference_case():
    categories=set(DEFAULTS)
    expected={c['id'] for c in DATA['cards'] if c['editorial_group'] in categories and c['calculator']}
    assert expected=={cid for cid,_ in CASES}

@pytest.mark.parametrize('cid',[c['id'] for c in DATA['cards'] if c.get('logic') and c['logic'].get('equivalent_to')])
def test_boolean_catalog_equivalences_exhaustive(cid):
    logic=BY[cid]['logic'];result=logic_lab({'operation':'equivalenza booleana','expression':logic['expression']+';'+logic['equivalent_to']})
    assert result['equivalent'],(cid,result)

def test_boolean_truth_and_karnaugh_boundaries():
    result=logic_lab({'operation':'tabella di verità','expression':'A | ~A'})
    assert result['table']=={'headers':['A','F'],'rows':[[0,1],[1,1]]}
    result=logic_lab({'operation':'equivalenza booleana','expression':'A | B; A & B'})
    assert result['equivalent'] is False and any(row[-2]!=row[-1] for row in result['table']['rows'])
    result=logic_lab({'operation':'mappa di Karnaugh','expression':'(A & B) | (~A & C)'})
    assert result['kmap']['columns']==['00','01','11','10']
    assert result['kmap']['values']==[[0,1,1,0],[0,0,1,1]]
    with pytest.raises(ValueError):boolean("__import__('os')")
    with pytest.raises(ValueError):boolean('A & B & C & D & E & F & G')

def test_binary_exactness_and_signed_arithmetic():
    assert calculate(BY['digitale-009'],{'n':'64'})['exact']=='18446744073709551615'
    assert calculate(BY['digitale-011'],{'n':'64','u':'18446744073709551615','sign':'1'})['exact']=='-1'
    assert calculate(BY['digitale-014'],{'x':'-3','k':'1'})['exact']=='-2'
    for a,b in itertools.product((0,1),repeat=2):
        f=calculate(BY['digitale-001'],{'a':a,'b':b})['value'];c=calculate(BY['digitale-002'],{'a':a,'b':b})['value']
        assert f+2*c==a+b

def test_physical_graph_domain_mask():
    from atlante.engine import execute
    card=BY['reti-007']
    result=execute({'kind':'plot2d','expression':card['calculator']['expression'],'variable':'service','start':50,'end':150,'names':{'arrival':80},'card':card})
    assert all(y is None for x,y in zip(result['x'],result['y']) if x<80)
    assert any(y is not None for x,y in zip(result['x'],result['y']) if x>80)

@pytest.mark.parametrize('cid,values',[
 ('base-050',{'a':'32','n':'1'}),
 ('classica-030',{'beta':'-1'}),
 ('analitica-017',{'a':'0','b':'0','c':'0'}),
 ('probabilita-023',{'sumx2':'1','sumx':'10','count':'5'}),
 ('meccanica-017',{'mu':'-0.1'}),('meccanica-020',{'theta':'2'}),
 ('termo-031',{'Q':'2000','heat':'1000'}),('onde-014',{'I':'-1','I0':'-1'}),
 ('elettro-012',{'Q':'1','voltage':'-2'}),('elettro-028',{'B':'-1'}),
 ('moderna-010',{'p':'-1'}),('moderna-018',{'rate':'-1'}),
 ('bool-001',{'a':'0.5'}),('digitale-011',{'u':'255','sign':'0','n':'8'}),
 ('digitale-013',{'u':'256','n':'8','k':'1'}),('digitale-029',{'n':'1.5'}),
 ('discreta-004',{'a':'2','b':'3','c':'4'}),('elettronica-016',{'vgs':'0.5','vth':'1'}),
 ('elettronica-016',{'vgs':'2','vth':'1','vds':'0.5'}),('reti-007',{'arrival':'101','service':'100'}),
 ('reti-013',{'prefix':'31'}),('reti-017',{'prob':'1'}),('informatica-024',{'selected':'1001','total':'1000'}),
 ('statistica-002',{'a':'6','b':'2'}),('ml-012',{'y':'0'}),('ml-026',{'tp':'0','fp':'0'}),
 ('deep-017',{'n':'2','kernel':'7','padding':'0'}),('deep-018',{'cin':'3','groups':'2'}),
 ('bioai-013',{'prior':'2'}),('visione-014',{'disparity':'0'}),('visione-022',{'intersection':'90','a':'80','b':'70'}),
])
def test_revised_model_domains(cid,values):
    with pytest.raises(ValueError):calculate(BY[cid],values)

@pytest.mark.parametrize('cid,values,expected',[
 ('base-009',{'a':'4','m':'0.5','n':'-0.5'},1),
 ('base-050',{'a':'3.2','n':'-5'},.000032),
 ('termo-020',{'epsilon':'0'},0),
 ('onde-025',{'f':'-0.1','p':'0.3'},-.075),
 ('onde-027',{'f':'-0.25'},-4),
 ('onde-029',{'n':'-1'},-.001),
 ('elettro-006',{'sigma':'-1e-8'},1e-8/(2*8.8541878128e-12)),
 ('elettro-031',{'current':'-2'},.1),
 ('statistica-018',{'prob':'0'},0),('statistica-018',{'prob':'1'},0),
 ('digitale-023',{'T':'1e-9'},-7e-9),
])
def test_valid_signed_or_boundary_cases(cid,values,expected):
    assert calculate(BY[cid],values)['value']==pytest.approx(expected)

def test_algebra_trigonometry_and_gradients():
    a,b,x=s.symbols('a b x',real=True)
    identities=[((a+b)**2,a*a+2*a*b+b*b),(a**3+b**3,(a+b)*(a*a-a*b+b*b)),
                (s.sin(a+b),s.sin(a)*s.cos(b)+s.cos(a)*s.sin(b)),
                (s.cos(a-b),s.cos(a)*s.cos(b)+s.sin(a)*s.sin(b)),
                (s.sin(2*x),2*s.sin(x)*s.cos(x)),(s.sin(x)**3,(3*s.sin(x)-s.sin(3*x))/4)]
    assert all(s.trigsimp(s.expand(lhs-rhs))==0 for lhs,rhs in identities)
    sigma=1/(1+s.exp(-x));assert s.simplify(s.diff(sigma,x)-sigma*(1-sigma))==0
    z1,z2=s.symbols('z1 z2');p1=s.exp(z1)/(s.exp(z1)+s.exp(z2));assert s.simplify(s.diff(-s.log(p1),z1)-(p1-1))==0

def test_quantum_and_robotics_reference_identities():
    H=s.Matrix([[1,1],[1,-1]])/s.sqrt(2);X=s.Matrix([[0,1],[1,0]]);Z=s.diag(1,-1)
    assert H.H*H==s.eye(2) and H*X*H==Z
    bell=s.Matrix([1,0,0,1])/s.sqrt(2);assert (bell.H*bell)[0]==1
    theta=s.symbols('theta',real=True);R=s.Matrix([[s.cos(theta),-s.sin(theta)],[s.sin(theta),s.cos(theta)]]);assert s.simplify(R.T*R)==s.eye(2)

def test_sections_and_colors(tmp_path):
    from atlante.store import Store
    store=Store(tmp_path/'sections.db')
    assert len(store.sections)==36
    for section in store.sections:
        assert len(store.search(category=section['id']))==section['count']
    assert len(store.search(category='basi_dati'))==18
    assert len(store.search(category='programmazione'))==24
    assert {c['category'] for c in store.catalog}<=SECTIONS.keys()
    assert all('courses' not in c and 'course_titles' not in c for c in store.catalog)
    store.close()
    def lum(color):
        rgb=[int(color[i:i+2],16)/255 for i in (1,3,5)];v=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in rgb];return sum(a*b for a,b in zip(v,(.2126,.7152,.0722)))
    for key in SECTIONS:
        for dark,bg in ((False,'#eff7f7'),(True,'#192d3b')):
            l1,l2=sorted((lum(section_color(key,dark)),lum(bg)))
            assert (l2+.05)/(l1+.05)>=4.5,(key,dark)
