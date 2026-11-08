"""Espressioni booleane senza eval; tabelle e mappe a ordine Gray."""
import ast
import itertools
import re
import sympy as s

def boolean(text,with_symbols=False):
    text=text.strip().replace('∧','&').replace('∨','|').replace('¬','~').replace('⊕','^')
    if not text or len(text)>700:raise ValueError('Espressione booleana richiesta, massimo 700 caratteri.')
    try:root=ast.parse(text,mode='eval')
    except SyntaxError as exc:raise ValueError('Sintassi booleana non valida: usa A & B, A | B, ~A, A ^ B e parentesi.') from exc
    if sum(1 for _ in ast.walk(root))>250:raise ValueError('Espressione booleana troppo complessa.')
    names=set()
    def visit(n):
        if isinstance(n,ast.Constant) and type(n.value) in (int,bool) and n.value in (0,1):return s.true if n.value else s.false
        if isinstance(n,ast.Name) and re.fullmatch('[A-Za-z]',n.id):
            symbol=s.Symbol(n.id);names.add(symbol);return symbol
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.Invert,ast.Not)):return s.Not(visit(n.operand))
        if isinstance(n,ast.BoolOp):return (s.And if isinstance(n.op,ast.And) else s.Or)(*[visit(v) for v in n.values])
        if isinstance(n,ast.BinOp):
            a,b=visit(n.left),visit(n.right)
            if isinstance(n.op,(ast.BitAnd,ast.Mult)):return s.And(a,b)
            if isinstance(n.op,(ast.BitOr,ast.Add)):return s.Or(a,b)
            if isinstance(n.op,ast.BitXor):return s.Xor(a,b)
        raise ValueError('Sono ammessi solo bit, variabili a una lettera, NOT, AND, OR e XOR.')
    expr=visit(root.body)
    if len(names)>6:raise ValueError('Massimo 6 variabili (64 righe).')
    return (expr,names) if with_symbols else expr

def evaluate(expr,assignment):return int(bool(expr.subs(assignment)))

def logic_lab(request):
    op=request['operation'];parts=request.get('expression','A & B').split(';')
    expr,names=boolean(parts[0],with_symbols=True)
    other,other_names=boolean(parts[1],with_symbols=True) if len(parts)==2 else (None,set())
    if len(parts)>2 or (op=='equivalenza booleana' and other is None):raise ValueError('Per confrontare due espressioni usa F;G.')
    variables=sorted(names|other_names,key=str)
    if len(variables)>6:raise ValueError('Massimo 6 variabili complessive.')
    headers=[str(v) for v in variables]+['F']+(['G'] if other is not None else [])
    rows=[];counterexample=None
    for bits in itertools.product((0,1),repeat=len(variables)):
        assignment=dict(zip(variables,bits));f=evaluate(expr,assignment);g=evaluate(other,assignment) if other is not None else None
        rows.append(list(bits)+[f]+([g] if other is not None else []))
        if g is not None and f!=g and counterexample is None:counterexample={str(k):v for k,v in assignment.items()}
    simplified=s.simplify_logic(expr,form='cnf' if op=='forma CNF' else 'dnf',force=True)
    result={'latex':s.latex(simplified),'text':str(simplified),'table':{'headers':headers,'rows':rows},
            'steps':['Ordine delle variabili: '+(', '.join(map(str,variables)) or 'nessuna, funzione costante')+'.',
                     'Si valutano tutte le 2^n assegnazioni: la verifica è esaustiva per queste variabili.',
                     ('Forma congiuntiva CNF.' if op=='forma CNF' else 'Forma disgiuntiva DNF; minima secondo il criterio del motore, non un costo tecnologico di una libreria.')],
            'conditions':'Logica classica a due valori. ^ significa XOR in questo strumento; nel laboratorio aritmetico ^ indica una potenza.', 'unresolved':False}
    if other is not None:
        result['equivalent']=counterexample is None
        result['steps'].append('Le espressioni sono equivalenti.' if counterexample is None else 'Non equivalenti. Controesempio: '+str(counterexample))
    if op=='mappa di Karnaugh':
        n=len(variables)
        if not 1<=n<=4:raise ValueError('La mappa di Karnaugh supporta da 1 a 4 variabili; usa la tabella per funzioni costanti o con 5–6 variabili.')
        nr=n//2;nc=n-nr
        gray=lambda width:[format(i^(i>>1),f'0{width}b') if width else '' for i in range(2**width)]
        rowlabels,collabels=gray(nr),gray(nc)
        values=[]
        for row in rowlabels:
            values.append([evaluate(expr,dict(zip(variables,map(int,row+col)))) for col in collabels])
        result['kmap']={'row_variables':','.join(map(str,variables[:nr])) or '—','column_variables':','.join(map(str,variables[nr:])),
                        'rows':rowlabels,'columns':collabels,'values':values}
        result['steps'].append('Righe e colonne seguono l’ordine Gray: celle a bordo opposto sono adiacenti. Non sono presenti don’t care impliciti.')
    return result
