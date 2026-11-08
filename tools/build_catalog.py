"""Compila le schede editoriali in JSON: nessuna rete richiesta a runtime."""
import json
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import sympy as s
from atlante.engine import parse, calculate,dimensional_result

BASE=Path(__file__).resolve().parents[1]
GROUPS=[
('base','Aritmetica e algebra',50,'Liceo'),
('classica','Geometria classica',35,'Liceo'),
('analitica','Geometria analitica',35,'Liceo'),
('trigonometria','Trigonometria',30,'Liceo'),
('analisi','Analisi matematica',65,'Università'),
('multivariabile','Analisi multivariabile e ODE',40,'Università'),
('lineare','Algebra lineare',40,'Università'),
('probabilita','Probabilità e statistica',25,'Liceo / Università'),
('meccanica','Meccanica e gravitazione',45,'Liceo / Università'),
('termo','Fluidi e termodinamica',35,'Liceo / Università'),
('onde','Onde e ottica',35,'Liceo / Università'),
('elettro','Elettricità e magnetismo',45,'Liceo / Università'),
('moderna','Fisica moderna',20,'Università')]

DESCRIPTIONS={
'a':'Primo coefficiente o lunghezza a','b':'Secondo coefficiente o lunghezza b','c':'Terzo coefficiente o lunghezza c',
'x':'Variabile reale x','y':'Coordinata o variabile y','z':'Coordinata z','n':'Numero intero o indice n','k':'Coefficiente k',
'r':'Raggio','R':'Raggio maggiore o costante R','h':'Altezza','l':'Lunghezza','B':'Base maggiore','p':'Semiperimetro o parametro p',
'alpha':'Angolo α in radianti','beta':'Angolo β in radianti','theta':'Angolo θ in radianti','t':'Tempo','t0':'Tempo iniziale',
'x0':'Posizione iniziale','v':'Velocità','v0':'Velocità iniziale','v1':'Prima velocità','v2':'Seconda velocità',
'm':'Massa','M':'Massa del corpo attrattore','g':'Accelerazione di gravità','F':'Forza','s':'Spostamento o ascissa curvilinea',
'mu':'Coefficiente di attrito','rho':'Densità','V':'Volume','A':'Area','S':'Superficie','P':'Potenza o pressione indicata',
'T':'Temperatura assoluta o periodo indicato','Q':'Calore o carica indicata','q':'Carica elettrica','d':'Distanza',
'f':'Frequenza','omega':'Pulsazione','lambda0':'Lunghezza d’onda','I0':'Intensità iniziale','I':'Corrente o intensità indicata',
'U':'Energia o differenza di potenziale indicata','E0':'Energia iniziale','E':'Campo o energia indicata','C':'Capacità termica o elettrica indicata',
'N':'Numero di elementi o spire','L':'Lunghezza o induttanza indicata','G':'Costante gravitazionale',
'K':'Costante o energia cinetica indicata','epsilon':'Permittività','eta':'Viscosità dinamica o rendimento indicato',
'sigma':'Deviazione standard o costante σ indicata','tau':'Costante di tempo','nu':'Quantità di sostanza (mol)',
'x1':'Ascissa del primo punto','y1':'Ordinata del primo punto','z1':'Quota del primo punto','x2':'Ascissa del secondo punto','y2':'Ordinata del secondo punto','z2':'Quota del secondo punto',
'xc':'Ascissa del centro','yc':'Ordinata del centro','zc':'Quota del centro','D':'Parametro o distanza D','delta':'Variazione δ',
'u':'Prima variabile o componente u','w':'Variabile o componente w','e0':'Permittività del vuoto','mu0':'Permeabilità del vuoto',
'c0':'Velocità della luce nel vuoto','hP':'Costante di Planck','hbar':'Costante di Planck ridotta','kB':'Costante di Boltzmann',
'NA':'Costante di Avogadro','qe':'Modulo della carica elementare','Z':'Numero atomico','j':'Indice intero j',
'T1':'Temperatura iniziale o sorgente calda','T2':'Temperatura finale o sorgente fredda','V1':'Volume iniziale','V2':'Volume finale',
'p1':'Pressione iniziale','p2':'Pressione finale','q1':'Prima carica','q2':'Seconda carica','R1':'Prima resistenza o raggio','R2':'Seconda resistenza o raggio',
'C1':'Prima capacità','C2':'Seconda capacità','m1':'Prima massa','m2':'Seconda massa','s1':'Prima distanza','s2':'Seconda distanza',
'vmax':'Velocità massima','b0':'Base del logaritmo','gamma':'Esponente adiabatico o fattore γ indicato',
'amp':'Ampiezza','phase':'Fase iniziale in radianti','turns':'Numero di spire','rate':'Tasso per unità di tempo',
'success':'Numero di successi','total':'Numero totale di esiti','fav':'Esiti favorevoli','prob':'Probabilità di successo',
'mean':'Media','var':'Varianza','count':'Numero di osservazioni','sumx':'Somma dei valori','sumx2':'Somma dei quadrati',
'ax':'Componente x del primo vettore','ay':'Componente y del primo vettore','az':'Componente z del primo vettore',
'bx':'Componente x del secondo vettore','by':'Componente y del secondo vettore','bz':'Componente z del secondo vettore',
'a11':'Elemento riga 1 colonna 1','a12':'Elemento riga 1 colonna 2','a21':'Elemento riga 2 colonna 1','a22':'Elemento riga 2 colonna 2',
'mass':'Massa','speed':'Velocità','radius':'Raggio','angle':'Angolo in radianti','time':'Tempo','area':'Area','length':'Lunghezza',
'pressure':'Pressione','volume':'Volume','temp':'Temperatura assoluta','heat':'Calore','work':'Lavoro','charge':'Carica',
'current':'Corrente','voltage':'Tensione','resistance':'Resistenza','freq':'Frequenza','energy':'Energia',
'dt':'Intervallo di tempo','dx':'Variazione di posizione','dv':'Variazione di velocità','dT':'Variazione di temperatura',
}
SYMBOL_TEXT={
'base':r'a,b,c: coefficienti reali; x,y: variabili; n,k: indici interi; q: ragione di una progressione.',
'classica':r'a,b,c,l: lunghezze; b,B: basi; h: altezza; r,R: raggi; p: semiperimetro; A: area; V: volume; α,β,γ: angoli.',
'analitica':r'x,y,z: coordinate cartesiane; x₁,y₁,z₁ e x₂,y₂,z₂: coordinate dei punti; a,b,c,d: coefficienti dell’equazione; m: pendenza; r: raggio.',
'trigonometria':r'α,β,θ,x: angoli in radianti; a,b,c: lati opposti agli angoli A,B,C; n,k: numeri interi.',
'analisi':r'x,t: variabili reali; a,b: estremi o parametri; f,g: funzioni; f′: derivata; n,k: indici interi; C: costante di integrazione.',
'multivariabile':r'x,y,z,t: variabili; f: campo scalare; F: campo vettoriale; ∇: operatore nabla; D,Ω: domini; n: normale unitaria; C: costante.',
'lineare':r'A,B: matrici; v,u: vettori; λ: autovalore o scalare; I: matrice identità; T: trasposizione; det: determinante; n: dimensione.',
'probabilita':r'P: probabilità; A,B: eventi; X,Y: variabili aleatorie; μ: media; σ: deviazione standard; n: numerosità; E: valore atteso.',
'meccanica':r'm,M: masse (kg); x,s,r,h: lunghezze (m); t: tempo (s); v: velocità (m/s); a,g: accelerazioni (m/s²); F: forza (N); E,K,U,W: energie o lavoro (J); θ: angolo (rad).',
'termo':r'p: pressione (Pa); V: volume (m³); ρ: densità (kg/m³); T: temperatura (K); Q,U,W: energie (J); n o ν: moli; R: costante dei gas; η: viscosità (Pa·s) o rendimento secondo la scheda.',
'onde':r'A: ampiezza; x: posizione (m); t: tempo (s); f: frequenza (Hz); T: periodo (s); λ: lunghezza d’onda (m); k: numero d’onda (rad/m); ω: pulsazione (rad/s); n: indice di rifrazione.',
'elettro':r'q,Q: cariche (C); I: corrente (A); V,U: tensioni (V), salvo energia U esplicita; R: resistenza (Ω); C: capacità (F); L: induttanza (H); E: campo elettrico (V/m); B: induzione magnetica (T); Φ: flusso (Wb).',
'moderna':r'c: velocità della luce; h: costante di Planck; ℏ=h/(2π); m: massa; E: energia; p: quantità di moto; ν,f: frequenze; λ: lunghezza d’onda; N: nuclei residui; t: tempo.'}
SOURCES={
'base':[('OpenStax — Precalculus 2e','https://openstax.org/details/books/precalculus-2e')],
'classica':[('Euclide — Elementi, libri I–XIII (Clark University)','https://mathcs.clarku.edu/~djoyce/elements/Euclid.html')],
'analitica':[('OpenStax — Precalculus 2e, cap. 10: geometria analitica','https://openstax.org/books/precalculus-2e/pages/10-introduction-to-analytic-geometry')],
'trigonometria':[('OpenStax — Precalculus 2e, cap. 7: identità trigonometriche','https://openstax.org/books/precalculus-2e/pages/7-introduction-to-trigonometric-identities-and-equations')],
'analisi':[('OpenStax — Calculus Volume 1','https://openstax.org/details/books/calculus-volume-1'),('OpenStax — Calculus Volume 2','https://openstax.org/details/books/calculus-volume-2')],
'multivariabile':[('OpenStax — Calculus Volume 3','https://openstax.org/details/books/calculus-volume-3')],
'lineare':[('MIT OCW — 18.06 Linear Algebra, programma e materiali','https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/pages/syllabus/')],
'probabilita':[('OpenStax — Introductory Statistics 2e','https://openstax.org/details/books/introductory-statistics-2e')],
'meccanica':[('OpenStax — University Physics Volume 1','https://openstax.org/details/books/university-physics-volume-1')],
'termo':[('OpenStax — University Physics Volume 1 (fluidi)','https://openstax.org/details/books/university-physics-volume-1'),('OpenStax — University Physics Volume 2 (termodinamica)','https://openstax.org/details/books/university-physics-volume-2')],
'onde':[('OpenStax — University Physics Volume 1 (onde)','https://openstax.org/details/books/university-physics-volume-1'),('OpenStax — University Physics Volume 3 (ottica)','https://openstax.org/details/books/university-physics-volume-3')],
'elettro':[('OpenStax — University Physics Volume 2','https://openstax.org/details/books/university-physics-volume-2')],
'moderna':[('OpenStax — University Physics Volume 3','https://openstax.org/details/books/university-physics-volume-3')]}

TOPICS={
'base':[(8,'Numeri e rapporti'),(20,'Potenze e prodotti notevoli'),(28,'Equazioni e disuguaglianze'),(33,'Logaritmi'),(40,'Progressioni e combinatoria'),(44,'Numeri complessi'),(50,'Polinomi e rappresentazione')],
'classica':[(3,'Angoli e parallele'),(17,'Triangoli e teoremi'),(24,'Quadrilateri e poligoni'),(30,'Cerchio e circonferenza'),(35,'Geometria solida')],
'analitica':[(4,'Punti e segmenti'),(15,'Rette nel piano'),(19,'Circonferenza'),(22,'Parabola'),(25,'Ellisse'),(28,'Iperbole e coniche'),(30,'Trasformazioni degli assi'),(35,'Geometria nello spazio')],
'trigonometria':[(7,'Definizioni e identità'),(19,'Addizione e angoli multipli'),(24,'Prodotti e somme'),(27,'Triangoli'),(30,'Equazioni trigonometriche')],
'analisi':[(9,'Limiti e continuità'),(24,'Derivate'),(29,'Teoremi e studio di funzione'),(34,'Sviluppi in serie'),(42,'Primitive'),(51,'Integrali definiti e impropri'),(60,'Successioni e serie'),(65,'Approssimazione e metodi numerici')],
'multivariabile':[(12,'Differenziale e ottimizzazione'),(19,'Integrali multipli'),(23,'Curve e campi conservativi'),(30,'Calcolo vettoriale'),(38,'Equazioni differenziali ordinarie'),(40,'Equazioni alle derivate parziali')],
'lineare':[(11,'Operazioni matriciali'),(17,'Sistemi e rango'),(21,'Spazi e basi'),(29,'Geometria vettoriale'),(35,'Autovalori e forme quadratiche'),(40,'Decomposizioni e applicazioni')],
'probabilita':[(7,'Eventi e condizionamento'),(10,'Combinatoria'),(15,'Momenti e dipendenza'),(21,'Distribuzioni'),(25,'Statistica campionaria')],
'meccanica':[(14,'Cinematica'),(20,'Dinamica'),(28,'Lavoro ed energia'),(33,'Urti e sistemi'),(39,'Rotazioni'),(44,'Gravitazione'),(45,'Pendolo')],
'termo':[(13,'Fluidi'),(20,'Temperatura e calore'),(25,'Gas ideali'),(29,'Trasformazioni e lavoro'),(35,'Entropia e macchine termiche')],
'onde':[(8,'Oscillazioni'),(19,'Onde meccaniche e suono'),(23,'Riflessione e rifrazione'),(28,'Ottica geometrica'),(35,'Ottica ondulatoria')],
'elettro':[(11,'Elettrostatica'),(17,'Condensatori'),(27,'Corrente e circuiti'),(35,'Magnetostatica'),(40,'Induzione'),(45,'Circuiti alternati e onde EM')],
'moderna':[(7,'Relatività ristretta'),(15,'Fisica quantistica'),(16,'Radiazione termica'),(20,'Fisica nucleare')]}

from tools.engineering_catalog import GROUPS as EXTRA_GROUPS,TOPICS as EXTRA_TOPICS,SOURCES as EXTRA_SOURCES,SYMBOLS as EXTRA_SYMBOLS
GROUPS.extend(EXTRA_GROUPS);TOPICS.update(EXTRA_TOPICS);SOURCES.update(EXTRA_SOURCES);SYMBOL_TEXT.update(EXTRA_SYMBOLS)

def build():
    cards=[]
    for key,label,count,level in GROUPS:
        lines=[v for v in (BASE/'contenuti'/f'{key}.txt').read_text(encoding='utf-8').splitlines() if v.strip() and not v.startswith('#')]
        if len(lines)!=count:raise ValueError(f'{key}: {len(lines)} invece di {count}')
        for i,line in enumerate(lines,1):
            fields=line.split('|')
            if len(fields)!=7:raise ValueError(f'{key}:{i}: attesi 7 campi, trovati {len(fields)}')
            title,tex,expr,defaults,explanation,conditions,example=map(str.strip,fields)
            card={'id':f'{key}-{i:03}','category':key,'category_label':label,'title':title,'latex':tex,
                  'level':level,'explanation':explanation,'conditions':conditions,'example':example,
                  'symbols':SYMBOL_TEXT[key],'sources':[{'title':a,'url':b} for a,b in SOURCES[key]],
                  'tags':[key,label.lower(),title.lower()],'related':[],'calculator':None,'plot':None}
            card['topic']=next(text for end,text in TOPICS[key] if i<=end)
            card['tags'].append(card['topic'])
            if expr:
                inputs=[]
                for spec in defaults.split(';'):
                    name,val=spec.split('=',1)
                    vals=val.split('@');default=vals[0];unit=vals[1] if len(vals)>1 else ''
                    desc=DESCRIPTIONS.get(name,f'Parametro {name}, come definito nella relazione')
                    if key=='classica':
                        desc={'a':'Lunghezza a','b':'Lunghezza b','c':'Lunghezza c','P':'Perimetro','A':'Area','p':'Semiperimetro','q':'Seconda proiezione sull’ipotenusa','k':'Rapporto di similitudine'}.get(name,desc)
                        if 'Pitagora' in title and name in ('a','b'):desc='Cateto '+name
                        if 'Euclide' in title and name=='p':desc='Prima proiezione sull’ipotenusa'
                        if 'rombo' in title and name in ('a','b'):desc='Diagonale '+name
                        if 'mediana' in title and name=='a':desc='Lato opposto alla mediana'
                    if key=='analitica' and name in ('a','b','c'):desc='Coefficiente '+name+' dell’equazione indicata'
                    if unit=='m/s^2':desc='Accelerazione '+name
                    if name=='I0' and unit=='kg*m^2':desc='Momento d’inerzia rispetto all’asse indicato'
                    if name=='mass' and unit=='kg/mol':desc='Massa molare'
                    if name=='gamma' and unit=='N/m':desc='Tensione superficiale'
                    if name=='rho' and unit=='ohm*m':desc='Resistività elettrica'
                    if name=='sigma' and unit=='C/m^2':desc='Densità superficiale di carica'
                    if name=='p' and unit=='kg*m/s':desc='Modulo della quantità di moto'
                    if name=='B' and unit=='T':desc='Modulo del campo magnetico'
                    if name=='N' and unit=='N':desc='Forza normale di contatto'
                    if name=='k' and unit=='N/m':desc='Costante elastica della molla'
                    if name=='k' and unit=='W/m/K':desc='Conducibilità termica'
                    if name=='L' and unit=='J/kg':desc='Calore latente specifico'
                    if name=='c' and unit=='J/kg/K':desc='Calore specifico'
                    if name=='R' and unit=='J/mol/K':desc='Costante universale dei gas'
                    if len(vals)>2:desc=vals[2]
                    field={'name':name,'label':desc,'default':default,'unit':unit}
                    if key=='classica' and name in ('r','R','h','l','a','b','B','A','p','P','c'):field['strict_min']=0
                    if key in ('meccanica','termo','onde','moderna','elettro') and name in ('m','M','r','R','T','T1','T2','V','V1','V2','rho','f','freq','c0','kB','hP','hbar','d','length','radius','mass','resistance','C','L','epsilon','e0','mu0','lambda0'):field['strict_min']=0
                    if name in ('n','N','turns','total','fav','count','success','k') and key in ('probabilita','base'):
                        field.update(min=0,integer=True)
                    if key=='base' and 'Notazione scientifica' in title and name=='n':field.pop('min',None)
                    inputs.append(field)
                card['calculator']={'expression':expr,'inputs':inputs,'output_unit':'','checks':[]}
                card['calculator']['output_unit']=dimensional_result(expr,inputs)
                if key=='moderna' and 'Bohr' in title:card['calculator']['output_unit']='eV'
                if 'decibel' in title:card['calculator']['output_unit']='dB'
                if key=='base' and 'Variazione percentuale' in title:card['calculator']['output_unit']='%'
                if key=='meccanica' and title=='Velocità angolare':card['calculator']['output_unit']='rad/s'
                if key=='meccanica' and title=='Momento di una forza':card['calculator']['output_unit']='N*m'
                if key=='onde' and title=='Numero d’onda':card['calculator']['output_unit']='rad/m'
                if key=='onde' and title=='Numero d\'onda':card['calculator']['output_unit']='rad/m'
                if key=='termo' and title=='Temperatura Celsius-Kelvin':card['calculator']['output_unit']='K'
                if key=='trigonometria' and title=='Gradi e radianti':card['calculator']['output_unit']='rad'
                if key=='onde' and title in ('Legge di Snell','Angolo critico','Angolo di Brewster','Criterio di Rayleigh'):card['calculator']['output_unit']='rad'
                if key=='elettro' and title=='Dipolo in campo uniforme: momento torcente':card['calculator']['output_unit']='N*m'
                from atlante.catalog_rules import decorate_calculator
                decorate_calculator(card)
                if 'Erone' in title:
                    card['calculator']['checks']=[{'left':'a+b','right':'c','op':'gt','message':'Triangolo impossibile o degenere: a+b deve superare c.'},{'left':'a+c','right':'b','op':'gt','message':'Triangolo impossibile o degenere: a+c deve superare b.'},{'left':'b+c','right':'a','op':'gt','message':'Triangolo impossibile o degenere: b+c deve superare a.'}]
                if key=='probabilita':
                    for field in inputs:
                        if field['name']=='prob':field.update(min=0,max=1)
                    if 'success' in defaults and 'n=' in defaults:card['calculator']['checks'].append({'left':'n','right':'success','op':'ge','message':'I successi non possono superare n.'})
                try:
                    res=calculate(card,{p['name']:p['default'] for p in inputs})
                except Exception as e:raise ValueError(f'{key} {title}: {e}') from e
                card['calculator']['reference_value']=res['value']
                subst=', '.join(f'{p["name"]}={p["default"]} {p["unit"]}'.strip() for p in inputs)
                if not example:card['example']=f'Dati: {subst}. Si sostituiscono i valori nella formula: risultato {res["text"]}. Le unità di uscita si ricavano dalla relazione indicata; usare dati coerenti con le unità dichiarate.'
                # Una vera curva di sensibilità numerica della formula rispetto al parametro scelto.
                first=next((p for name in ('x','t','r','h','v','T','theta','alpha','omega','a','b') for p in inputs if p['name']==name),None)
                if not first:first=next((p for p in inputs if p['name'] not in ('n','N','k','turns','total','success','fav','count','G','e0','c0','hP','hbar','kB','NA')),None)
                if first:card['plot']={'kind':'sensitivity','variable':first['name']}
            if key in ('classica','analitica'):
                card['plot']={'kind':'geometry','preset':geometry_preset(key,title)}
            if card.get('plot',{} ) and card['plot']['kind']=='sensitivity':
                variable=card['plot']['variable'];selected=next(p for p in card['calculator']['inputs'] if p['name']==variable)
                if selected.get('integer'):card['plot']=None
            from tools.logic_catalog import attach_logic
            attach_logic(card)
            if not card['example']:raise ValueError(f'Esempio mancante: {title}')
            cards.append(card)
        batch=cards[-count:]
        for j,card in enumerate(batch):card['related']=[batch[(j-1)%len(batch)]['id'],batch[(j+1)%len(batch)]['id']]
    overrides=json.loads((BASE/'contenuti'/'arricchimenti.json').read_text(encoding='utf-8')) if (BASE/'contenuti'/'arricchimenti.json').exists() else {}
    for c in cards:c.update(overrides.get(c['id'],{}))
    (BASE/'atlante'/'data').mkdir(exist_ok=True)
    from atlante.disciplines import organize,section_index
    organize(cards)
    from tools.software_examples import attach_code
    attach_code(cards)
    (BASE/'atlante'/'data'/'catalog.json').write_text(json.dumps({'schema_version':1,'catalog_version':'1.2.0','sections':section_index(cards),'cards':cards},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{len(cards)} schede; {sum(bool(c["calculator"]) for c in cards)} calcolatori; {sum(bool(c["plot"]) for c in cards)} visualizzazioni')

def geometry_preset(key,title):
    t=title.lower()
    if key=='classica':
        if 'inscritta' in t or 'circoscritta' in t:return 'triangle'
        if any(v in t for v in ('sfera','cilindro','cono','prisma','piramide','cubo','parallelepipedo','tronco')):return 'solid'
        if any(v in t for v in ('cerchio','circonferenza','arco','settore','corda','corona','angolo al centro')):return 'circle'
        if any(v in t for v in ('rettangolo','quadrato','rombo','parallelogramma','trapezio','poligono')):return 'polygon'
        if any(v in t for v in ('angoli','parallele','talete')):return 'angles'
        return 'triangle'
    if any(v in t for v in ('sfera','piano','spazio','quadric','3d')):return 'space'
    if 'ellisse' in t:return 'ellipse'
    if 'iperbole' in t:return 'hyperbola'
    if 'parabola' in t:return 'parabola'
    if any(v in t for v in ('circonferenza','cerchio')):return 'circle'
    return 'line'

if __name__=='__main__':build()
