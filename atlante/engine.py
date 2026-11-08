"""Grammatica matematica esplicita: non esegue codice Python dell'utente."""
import ast
import json
import math
import re
import sys
from functools import lru_cache
import sympy as s

FUNCS = {n: getattr(s, n) for n in ('sin','cos','tan','asin','acos','atan','sinh','cosh','tanh','sqrt','exp','log','Abs','factorial','erf','floor','ceiling','Min','Max','Mod')}
FUNCS['xlogx']=lambda x:s.Piecewise((s.Integer(0),s.Eq(x,0)),(x*s.log(x),True))
CONSTS = {'pi': s.pi, 'E': s.E, 'e': s.E, 'oo': s.oo, 'I': s.I}

@lru_cache(maxsize=1)
def units():
    import pint
    return pint.UnitRegistry()

def dimensional_result(expression,fields,quantity=False):
    ureg=units()
    vals={f['name']:ureg.Quantity(float(parse(f['default'])),f.get('unit') or '') for f in fields}
    def visit(n):
        if isinstance(n,ast.Constant):return n.value
        if isinstance(n,ast.Name):return vals[n.id] if n.id in vals else float(CONSTS[n.id])
        if isinstance(n,ast.UnaryOp):return -visit(n.operand) if isinstance(n.op,ast.USub) else visit(n.operand)
        if isinstance(n,ast.BinOp):
            a,b=visit(n.left),visit(n.right)
            if isinstance(n.op,ast.Add):return a+b
            if isinstance(n.op,ast.Sub):return a-b
            if isinstance(n.op,ast.Mult):return a*b
            if isinstance(n.op,ast.Div):return a/b
            if isinstance(n.op,ast.Pow):return a**(b.to('').magnitude if hasattr(b,'to') else b)
        if isinstance(n,ast.Call):
            args=[visit(a) for a in n.args];name=n.func.id
            if name=='sqrt':return args[0]**.5
            if name=='Abs':return abs(args[0])
            return float(FUNCS[name](*[v.to('').magnitude if hasattr(v,'to') else v for v in args]))
        raise ValueError('Dimensione non ricavabile.')
    q=visit(ast.parse(expression.replace('^','**'),mode='eval').body)
    if quantity:return q if hasattr(q,'units') else ureg.Quantity(q)
    if not hasattr(q,'units') or q.dimensionless:return ''
    for unit in ('J','W','N','Pa','V','C','F','ohm','H','T','Wb','Hz','V/m','m/s^2','m/s','m^3/s','kg/m^3','W/m^2','J/m^3','J/K','kg*m/s','kg*m^2','N*s','C*m','m^3','m^2','m','s','K','A'):
        if q.check(ureg.Unit(unit).dimensionality):return unit
    return f'{q.to_base_units().units:~}'

def parse(text, names=None):
    text = str(text).strip().replace('^','**').replace('π','pi').replace('−','-').replace('·','*')
    if not text or len(text) > 1200:
        raise ValueError('Inserisci un’espressione di massimo 1200 caratteri.')
    tree = ast.parse(text, mode='eval')
    if sum(1 for _ in ast.walk(tree)) > 400:
        raise ValueError('Espressione troppo complessa.')
    names = {k:(v if isinstance(v,s.Basic) else s.Rational(str(v))) for k,v in (names or {}).items()}
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int,float):
            if not math.isfinite(float(node.value)) or abs(node.value) > 1e100:
                raise ValueError('Costante numerica fuori intervallo.')
            return s.Rational(str(node.value))
        if isinstance(node, ast.Name):
            name = node.id
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9]{0,19}',name):
                raise ValueError('Nome di variabile non consentito.')
            return names.get(name, CONSTS.get(name, s.Symbol(name, real=True)))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            v = visit(node.operand)
            return -v if isinstance(node.op,ast.USub) else v
        if isinstance(node, ast.BinOp):
            a,b = visit(node.left),visit(node.right)
            if isinstance(node.op,ast.Add): return a+b
            if isinstance(node.op,ast.Sub): return a-b
            if isinstance(node.op,ast.Mult): return a*b
            if isinstance(node.op,ast.Div):
                if b == 0: raise ValueError('Divisione per zero.')
                return a/b
            if isinstance(node.op,ast.Pow):
                if b.is_number and (not b.is_real or abs(b)>1000):
                    if b.is_Integer and 0<=b<=1000000 and (a.free_symbols or (a.is_number and abs(a)<=1)):
                        return s.Pow(a,b,evaluate=False)
                    raise ValueError('Esponente fuori intervallo; potenze numeriche crescenti limitate a 1000.')
                return a**b
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNCS and not node.keywords:
            if len(node.args) not in (1,2): raise ValueError('Numero di argomenti non valido.')
            args = [visit(x) for x in node.args]
            if node.func.id=='factorial' and (not args[0].is_Integer or not 0<=args[0]<=200):
                raise ValueError('Fattoriale ammesso per interi da 0 a 200.')
            return FUNCS[node.func.id](*args)
        raise ValueError('Sintassi non ammessa. Usa + − * / ^, parentesi e funzioni come sin(x).')
    return visit(tree.body)

def matrix(text):
    rows = [r.strip() for r in text.strip().split(';') if r.strip()]
    data = [[parse(x.strip()) for x in row.split(',')] for row in rows]
    if not data or len(data)>10 or not 1<=len(data[0])<=10 or len({len(r) for r in data})!=1:
        raise ValueError('Matrice rettangolare richiesta, massimo 10 × 10. Colonne con virgole, righe con punto e virgola.')
    return s.Matrix(data)

def numeric(text):
    v = parse(str(text).replace(',','.'))
    if v.free_symbols or not v.is_real or not v.is_finite:
        raise ValueError('Inserisci un numero reale finito.')
    return float(v)

def exact_numeric(text):
    value=parse(str(text).replace(',','.'))
    if value.free_symbols or value.is_real is not True or value.is_finite is not True:
        raise ValueError('Inserisci un numero reale finito.')
    return value

def calculate(card, inputs, precision=8):
    ureg = units()
    vals = {}
    conversions=[]
    for field in card['calculator']['inputs']:
        name = field['name']; raw = str(inputs.get(name,field['default'])).strip()
        unit = field.get('unit','')
        try:value=exact_numeric(raw)
        except (ValueError,SyntaxError,TypeError):
            if not unit:raise ValueError(f'{name}: inserisci un numero o un’espressione numerica.')
            try:
                q=ureg.Quantity(raw.replace(',','.')).to(unit);converted=float(q.magnitude)
                if not math.isfinite(converted):raise ValueError('Valore non finito.')
                value=s.Rational(str(converted))
            except Exception as exc:raise ValueError(f'{name}: quantità non compatibile con {unit}.') from exc
            conversions.append(f'{name}: {raw} = {s.N(value,10)} {unit}')
        if field.get('min') is not None and value < field['min']: raise ValueError(f'{name}: minimo {field["min"]}.')
        if field.get('strict_min') is not None and value <= field['strict_min']: raise ValueError(f'{name}: deve essere maggiore di {field["strict_min"]}.')
        if field.get('max') is not None and value > field['max']: raise ValueError(f'{name}: massimo {field["max"]}.')
        if field.get('strict_max') is not None and value >= field['strict_max']: raise ValueError(f'{name}: deve essere minore di {field["strict_max"]}.')
        if field.get('max_expr') is not None and value > parse(field['max_expr']):raise ValueError(f'{name}: massimo {field["max_expr"]}.')
        if field.get('integer') and value.is_integer is not True: raise ValueError(f'{name}: è richiesto un intero.')
        vals[name]=value
    from atlante.validation import validate_domain
    validate_domain(card,vals)
    for rule in card['calculator'].get('checks',[]):
        a,b=rule['left'],rule['right']
        lv,rv=parse(a,vals),parse(b,vals)
        valid={'gt':lambda:lv>rv,'ge':lambda:lv>=rv,'ne':lambda:lv!=rv,'lt':lambda:lv<rv}[rule['op']]()
        if not valid: raise ValueError(rule['message'])
    expr=parse(card['calculator']['expression'],vals)
    if expr.free_symbols or expr.has(s.zoo,s.oo,-s.oo,s.nan) or expr.is_real is not True:
        raise ValueError('Risultato non reale o non definito. Controlla il dominio e i dati.')
    result=expr if expr.is_Integer else s.N(expr,max(3,min(30,int(precision))))
    return {'latex':s.latex(expr),'exact':str(expr),'text':f'{result} {card["calculator"].get("output_unit","")}'.strip(),
            'steps': conversions+[f'{k} = {v}' for k,v in vals.items()]+['Sostituzione dei valori nella relazione della scheda.',f'Risultato: {result}'], 'value':float(expr),
            'conversions':conversions,'normalized':{k:float(v) for k,v in vals.items()}}

def lab(req):
    op=req['operation']; text=req.get('expression','x^2'); var=req.get('variable','x')
    if op in ('tabella di verità','semplifica Boole','equivalenza booleana','forma CNF','mappa di Karnaugh'):
        from atlante.logic import logic_lab
        return logic_lab(req)
    x=parse(var)
    if not isinstance(x,s.Symbol): raise ValueError('La variabile deve essere un simbolo, per esempio x.')
    steps=[]; conditions='Calcolo simbolico sui reali; eventuali parametri richiedono le condizioni della formula.'
    if op in ('determinante','rango','inversa','riduzione','autovalori','trasposta'):
        m=matrix(text)
        if op in ('determinante','inversa','autovalori') and m.rows!=m.cols: raise ValueError('Serve una matrice quadrata.')
        if op=='inversa' and m.det()==0: raise ValueError('Matrice singolare: inversa non esistente.')
        if op=='riduzione':
            a=m.copy(); pivot=0
            for col in range(a.cols):
                k=next((r for r in range(pivot,a.rows) if a[r,col]!=0),None)
                if k is None: continue
                if k!=pivot:
                    a.row_swap(k,pivot);steps.append(f'Scambia R{k+1} con R{pivot+1}.')
                q=a[pivot,col]
                if q!=1:
                    a.row_op(pivot,lambda v,j:v/q);steps.append(f'R{pivot+1} ← R{pivot+1} / ({q}).')
                for r in range(a.rows):
                    if r!=pivot and a[r,col]!=0:
                        q=a[r,col]; a.row_op(r,lambda v,j:v-q*a[pivot,j]);steps.append(f'R{r+1} ← R{r+1} − ({q}) R{pivot+1}.')
                pivot+=1
                if pivot==a.rows:break
            result=a
        else:
            result={'determinante':lambda:m.det(),'rango':lambda:s.Integer(m.rank()),'inversa':lambda:m.inv(),'autovalori':lambda:m.eigenvals(),'trasposta':lambda:m.T}[op]()
    elif op in ('retta per due punti','distanza punto-retta','circonferenza','intersezione retta-conica'):
        # Parametri separati da punto e virgola: nessuna esecuzione di codice.
        parts=[p.strip() for p in text.split(';')]
        y=s.Symbol('y',real=True)
        if op=='retta per due punti':
            if len(parts)!=4: raise ValueError('Inserisci x1; y1; x2; y2.')
            a,b,c,d=map(parse,parts)
            if a==c and b==d: raise ValueError('Due punti coincidenti non determinano una retta.')
            result=s.Eq(s.expand((d-b)*(x-a)-(c-a)*(y-b)),0)
            steps=[f'Vettore direzione: ({c-a}, {d-b}).','Imponi il determinante tra direzione e vettore punto-punto uguale a zero.','La forma implicita gestisce anche le rette verticali.']
        elif op=='distanza punto-retta':
            if len(parts)!=5: raise ValueError('Inserisci x0; y0; a; b; c per ax+by+c=0.')
            px,py,a,b,c=map(parse,parts)
            if a*a+b*b==0: raise ValueError('a e b non possono essere entrambi zero.')
            result=s.Abs(a*px+b*py+c)/s.sqrt(a*a+b*b)
            steps=[f'Numeratore |a x0 + b y0 + c| = {s.Abs(a*px+b*py+c)}.',f'Norma del vettore normale = {s.sqrt(a*a+b*b)}.','Dividi numeratore per norma.']
        elif op=='circonferenza':
            if len(parts)!=3: raise ValueError('Inserisci xc; yc; r.')
            a,b,r=map(parse,parts)
            if not r.is_positive: raise ValueError('Il raggio deve essere positivo.')
            result=s.Eq((x-a)**2+(y-b)**2,r*r)
            steps=[f'Centro C=({a}, {b}); raggio r={r}.','Imponi che la distanza dal centro sia uguale al raggio.','Eleva al quadrato entrambi i membri.']
        else:
            if len(parts)!=2: raise ValueError('Inserisci due espressioni uguali a zero separate da ;, per esempio y-x; x^2+y^2-2.')
            f,g=map(parse,parts)
            if (f.free_symbols|g.free_symbols)-{x,y}:raise ValueError('Sono ammesse soltanto le coordinate x e y.')
            poly=s.Poly(f,x,y)
            if poly.total_degree()!=1: raise ValueError('La prima espressione deve descrivere una retta.')
            con=s.Poly(g,x,y)
            if con.total_degree()!=2:raise ValueError('La seconda espressione deve descrivere una conica di grado 2.')
            coeff=s.Matrix([[con.coeff_monomial(x*x),con.coeff_monomial(x*y)/2,con.coeff_monomial(x)/2],[con.coeff_monomial(x*y)/2,con.coeff_monomial(y*y),con.coeff_monomial(y)/2],[con.coeff_monomial(x)/2,con.coeff_monomial(y)/2,con.coeff_monomial(1)]])
            if coeff.det()==0: raise ValueError('La conica è degenere; usa equazioni e sistemi per analizzarla.')
            sols=s.solve([f,g],[x,y],dict=True)
            result=[p for p in sols if all(v.is_real is not False for v in p.values())]
            steps=['Ricava una coordinata dalla retta e sostituisci nella conica.','Risolvi l’equazione risultante, poi ricostruisci le coordinate.',f'Intersezioni reali trovate: {len(result)}. Una sola indica tangenza.']
    elif op=='sistema':
        eqs=[]
        for part in text.split(';'):
            ab=part.split('=');eqs.append(parse(ab[0])-(parse(ab[1]) if len(ab)==2 else 0))
        symbols=sorted(set().union(*(v.free_symbols for v in eqs)),key=str)
        if not symbols: raise ValueError('Il sistema non contiene incognite.')
        if len(symbols)>8: raise ValueError('Massimo 8 incognite.')
        result=s.linsolve(eqs,symbols)
        conditions=f'Ordine delle incognite: {", ".join(map(str,symbols))}. Parametri liberi indicano infinite soluzioni.'
    elif op=='equazione':
        ab=text.split('=')
        if len(ab)>2: raise ValueError('Usa una sola uguaglianza.')
        f=parse(ab[0])-(parse(ab[1]) if len(ab)==2 else 0)
        result=s.solveset(f,x,domain=s.S.Reals)
        if f.is_polynomial(x):
            p=s.Poly(f,x)
            if p.degree()==1:
                a,b=p.all_coeffs();steps=[f'Raccogli: ({a}) {x} + ({b}) = 0.',f'Porta il termine noto a destra: ({a}) {x} = {-b}.',f'Dividi per {a}: {x} = {-b/a}.']
            elif p.degree()==2:
                a,b,c=p.all_coeffs();delta=b*b-4*a*c
                steps=[f'a={a}, b={b}, c={c}.',f'Calcola Δ = b² − 4ac = {delta}.', 'Se Δ<0 non ci sono radici reali; se Δ=0 la radice è doppia; se Δ>0 ci sono due radici.',f'Applica x = (−b ± √Δ)/(2a), con a={a}.']
    else:
        f=parse(text)
        if op=='semplifica':result=s.simplify(f)
        elif op=='sviluppa':result=s.expand(f)
        elif op=='fattorizza':result=s.factor(f)
        elif op=='derivata':
            result=s.diff(f,x)
            def explain(g,depth=0):
                if depth>4:return
                if g==x:steps.append(f'Derivata della variabile {x}: 1.')
                elif x not in g.free_symbols:steps.append(f'{g} è costante rispetto a {x}: derivata 0.')
                elif g.is_Add:
                    steps.append('Linearità: deriva separatamente gli addendi.')
                    for a in g.args:explain(a,depth+1)
                elif g.is_Mul:
                    steps.append('Prodotto: somma i termini ottenuti derivando un fattore alla volta.')
                    for a in g.args:explain(a,depth+1)
                elif g.is_Pow and x not in g.exp.free_symbols:
                    steps.append(f'Potenza e catena: d({g})/d{x} = ({g.exp}) ({g.base})^({g.exp-1}) · d({g.base})/d{x}.')
                    explain(g.base,depth+1)
                elif g.func in (s.sin,s.cos,s.exp,s.log):
                    steps.append(f'Regola di {g.func.__name__} e catena: {s.diff(g,x)}.')
                else:steps.append(f'Derivazione simbolica del termine {g}: {s.diff(g,x)}.')
            explain(f)
        elif op=='integrale':result=s.integrate(f,x);conditions='Primitiva rispetto a '+str(x)+': aggiungere una costante arbitraria C su ogni intervallo del dominio.'
        elif op=='integrale definito':
            a=parse(req.get('a','0'));b=parse(req.get('b','1'));result=s.integrate(f,(x,a,b))
            conditions='Integrale definito: verificare convergenza e dominio dell’integranda sull’intervallo.'
        elif op=='limite':
            side=req.get('direction','+')
            result=s.limit(f,x,parse(req.get('a','0')),dir=side)
            conditions=f'Limite {"bilatero" if side=="+-" else "da destra" if side=="+" else "da sinistra"}; non implica esistenza di limiti negli altri versi.'
        elif op=='taylor':
            order=int(req.get('order',6))
            if not 1<=order<=20:raise ValueError('Ordine ammesso da 1 a 20.')
            result=s.series(f,x,parse(req.get('a','0')),order)
        else:raise ValueError('Operazione sconosciuta.')
    unresolved=bool(isinstance(result,s.Basic) and result.has(s.Integral,s.Limit,s.ConditionSet,s.Derivative))
    if not steps:steps=['Operazione eseguita dal motore simbolico; non è disponibile una derivazione didattica dettagliata per questo caso.']
    return {'latex':s.latex(result),'text':str(result),'steps':steps,'conditions':conditions,'unresolved':unresolved}

def execute(req):
    kind=req.get('kind','lab')
    if kind=='calculator': return calculate(req['card'],req['inputs'],req.get('precision',8))
    if kind=='plot2d':
        import numpy as np
        from atlante.sampling import sample_curve
        x,y=sample_curve(req['expression'],req.get('variable','x'),req['start'],req['end'],names=req.get('names'))
        if req.get('card'):
            from atlante.validation import validate_domain
            card=req['card'];key=req['variable'];fixed={name:s.Rational(str(value)) for name,value in req.get('names',{}).items()}
            field=next(f for f in card['calculator']['inputs'] if f['name']==key)
            for i,value in enumerate(x):
                if not np.isfinite(y[i]):continue
                current=s.Float(value)
                try:
                    for name,operator in (('min',lambda a,b:a>=b),('strict_min',lambda a,b:a>b),('max',lambda a,b:a<=b),('strict_max',lambda a,b:a<b)):
                        if name in field and not bool(operator(current,field[name])):raise ValueError('Fuori dominio.')
                    if 'max_expr' in field and current>parse(field['max_expr']):raise ValueError('Fuori dominio.')
                    validate_domain(card,{**fixed,key:current})
                except (ValueError,TypeError):y[i]=np.nan
        return {'x':x.tolist(),'y':[float(v) if np.isfinite(v) else None for v in y]}
    if kind=='plot3d':
        import numpy as np
        a,b=req['start'],req['end']
        if not math.isfinite(a+b) or b<=a:raise ValueError('Intervallo finito crescente richiesto.')
        expr=parse(req['expression']);x,y=s.symbols('x y',real=True)
        if expr.free_symbols-{x,y}:raise ValueError('La superficie può usare soltanto x e y.')
        fn=s.lambdify((x,y),expr,'numpy');xx,yy=np.meshgrid(np.linspace(a,b,90),np.linspace(a,b,90))
        with np.errstate(all='ignore'):zz=np.asarray(fn(xx,yy),dtype=complex)
        if zz.ndim==0:zz=np.full_like(xx,zz,dtype=complex)
        zz=np.where(np.abs(zz.imag)<1e-9,zz.real,np.nan);zz[~np.isfinite(zz)]=np.nan
        if not np.isfinite(zz).any():raise ValueError('Nessun punto reale finito nella superficie selezionata.')
        return {'x':xx.tolist(),'y':yy.tolist(),'z':[[float(v) if np.isfinite(v) else None for v in row] for row in zz]}
    return lab(req)

def worker_main():
    from pathlib import Path
    job=Path(sys.argv[sys.argv.index('--job')+1]) if '--job' in sys.argv else None
    try:
        req=json.loads((job/'request.json').read_text(encoding='utf-8') if job else sys.stdin.read())
        result={'ok':True,'result':execute(req)}
    except Exception as exc:
        result={'ok':False,'error':str(exc) or type(exc).__name__}
    output=json.dumps(result,ensure_ascii=True)
    if job:
        tmp=job/'response.tmp';tmp.write_text(output,encoding='utf-8');tmp.replace(job/'response.json')
    else:sys.stdout.write(output);sys.stdout.flush()
