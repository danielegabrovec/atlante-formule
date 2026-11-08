"""Campionamento numerico eseguito nei processi di lavoro."""
import math
import numpy as np
import sympy as s
from atlante.engine import parse

def sample_curve(expression,var,start,end,points=1400,names=None):
    if not math.isfinite(start+end) or end<=start:raise ValueError('L’estremo finale deve essere maggiore di quello iniziale.')
    symbol=s.Symbol(var,real=True)
    values=dict(names or {});values[var]=symbol
    expr=parse(expression,values)
    if expr.free_symbols-{symbol}:raise ValueError('Assegna un valore agli altri parametri prima del grafico.')
    # Algebra costruita dal parser chiuso: lambdify riceve solo oggetti SymPy ammessi.
    fn=s.lambdify(symbol,expr,modules='numpy',cse=True)
    xx=np.linspace(start,end,points)
    with np.errstate(all='ignore'):
        yy=np.asarray(fn(xx),dtype=complex)
        if yy.ndim==0:yy=np.full_like(xx,yy,dtype=complex)
        real=np.abs(yy.imag)<1e-9
        yy=np.where(real,yy.real,np.nan)
    yy[~np.isfinite(yy)]=np.nan
    finite=yy[np.isfinite(yy)]
    if not len(finite):raise ValueError('Nessun valore reale finito nell’intervallo selezionato.')
    scale=max(float(np.nanpercentile(np.abs(finite),85)),1e-6)
    yy[np.abs(yy)>scale*15]=np.nan
    jumps=np.where(np.abs(np.diff(yy))>scale*3)[0]
    yy[jumps]=np.nan;yy[np.minimum(jumps+1,len(yy)-1)]=np.nan
    # Interrompe anche in corrispondenza di singolarità algebriche note.
    denominator=s.denom(s.together(expr))
    if denominator!=1 and s.count_ops(denominator)<80:
        try:
            roots=s.solveset(denominator,symbol,domain=s.Interval(start,end))
            if isinstance(roots,s.FiniteSet):
                for root in roots:
                    if root.is_real:
                        idx=np.searchsorted(xx,float(root));yy[max(0,idx-2):min(len(yy),idx+2)]=np.nan
        except (NotImplementedError,ValueError,TypeError):pass
    return xx,yy

