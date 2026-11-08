"""Ipotesi dei modelli, oltre ai vincoli sintattici e al dominio reale."""
import sympy as s

def validate_domain(card,v):
    t=card['title'].lower();cat=card['category'];cid=card['id']
    def check(test,message):
        if not bool(test):raise ValueError(message)
    if cat=='classica':
        if {'a','b','c'}<=v.keys() and any(k in t for k in ('erone','mediana','circoscritta')):check(v['a']+v['b']>v['c'] and v['a']+v['c']>v['b'] and v['b']+v['c']>v['a'],'I tre lati non formano un triangolo non degenere.')
        if 'complementari'in t:check(0<=v['alpha']<=s.pi/2,'Angolo compreso fra 0 e π/2 richiesto.')
        if 'supplementari'in t:check(0<=v['alpha']<=s.pi,'Angolo compreso fra 0 e π richiesto.')
        if 'somma degli angoli'in t:check(v['alpha']>0 and v['beta']>0 and v['alpha']+v['beta']<s.pi,'Angoli positivi con somma minore di π richiesti.')
        if 'primo teorema'in t:check(0<v['p']<v['c'],'La proiezione deve essere positiva e minore dell’ipotenusa.')
        if 'secondo teorema'in t:check(v['p']>0 and v['q']>0,'Proiezioni strettamente positive richieste.')
        if 'angoli interni'in t:check(v['n'].is_Integer and v['n']>=3,'Numero intero di lati almeno 3 richiesto.')
        if 'similitudine'in t:check(v['k']>0,'Il rapporto di similitudine deve essere positivo.')
        if 'theta'in v:check(0<=v['theta']<=2*s.pi,'Angolo geometrico fra 0 e 2π richiesto.')
        if 'circoscritta'in t:
            a,b,c,A=v['a'],v['b'],v['c'],v['A'];p=(a+b+c)/2
            check(abs(float(A*A-p*(p-a)*(p-b)*(p-c)))<1e-7*max(float(A*A),1),'L’area non è coerente con i tre lati.')
    if cat=='analitica' and 'eccentricit' in t:check(v['a']>=v['b']>0,'Per l’ellisse occorre a≥b>0.')
    if cid=='analitica-017':check((v['a']**2+v['b']**2)/4-v['c']>0,'Non è una circonferenza reale non degenere: r² deve essere positivo.')
    if cat=='probabilita':
        if 'fav'in v:check(0<=v['fav']<=v['total'] and v['total']>0,'Esiti favorevoli fra 0 e totale; totale positivo.')
        if 'n'in v and 'k'in v and 'disposizioni'in t:check(v['k']<=v['n'],'k non può superare n.')
        if 'sigma'in v:check(v['sigma']>0,'Deviazione standard positiva richiesta.')
        if 'rate'in v:check(v['rate']>0,'Tasso strettamente positivo richiesto.')
        if 'count'in v:check(v['count']>= (2 if 'varianza'in t else 1),'Numerosità insufficiente.')
        if 'var'in v:check(v['var']>=0,'La varianza non può essere negativa.')
        if cid=='probabilita-023':check(v['sumx2']>=v['sumx']**2/v['count'],'Somme incoerenti: la varianza dei dati non può essere negativa.')
    if cat=='base':
        if 'logaritm'in t or 'cambio di base'in t:check(v.get('x',1)>0 and v.get('b0',2)>0 and v.get('b0',2)!=1,'Argomento positivo e base positiva diversa da 1 richiesti.')
        if 'progressione'in t:check(v['n']>=1,'Indice n intero positivo richiesto.')
        if 'coefficiente binomiale'in t:check(v['k']<=v['n'],'k non può superare n.')
        if 'media ponderata'in t:check(v['u']>=0 and v['w']>=0 and v['u']+v['w']>0,'Pesi non negativi con somma positiva richiesti.')
        if cid=='base-050':check(1<=abs(v['a'])<10,'In notazione scientifica normalizzata il coefficiente deve avere modulo fra 1 incluso e 10 escluso.')
    if cid=='classica-030':check(0<v['beta']<s.pi,'Angolo alla circonferenza strettamente fra 0 e π richiesto.')
    if cat=='trigonometria':
        if 'triangolo rettangolo'in t:check(0<v.get('a',v.get('b',1))<v['c'],'Cateto positivo minore dell’ipotenusa richiesto.')
        if 'teorema del coseno'in t or 'area con due lati'in t:check(v['a']>0 and v['b']>0 and 0<v['theta']<s.pi,'Lati positivi e angolo compreso fra 0 e π richiesti.')
        if 'teorema dei seni'in t:check(v['a']>0 and 0<v['alpha']<s.pi,'Lato positivo e angolo fra 0 e π richiesti.')
    if cat in ('meccanica','termo','onde','elettro','moderna'):
        for key in ('dt','sigma','eta','e0','c0','hP','hbar','kB','G'):
            if key in v and not (cid=='elettro-006' and key=='sigma'):check(v[key]>0,f'{key} deve essere strettamente positivo.')
        if 'n'in v:check(v['n'].is_Integer and (cid=='onde-029' or v['n']>=1),'Indice n intero positivo richiesto, salvo ordini di interferenza anche negativi.')
        if 't'in v:check(v['t']>=0,'Tempo non negativo richiesto in questo modello.')
        if 'c0'in v and 'v'in v:check(abs(v['v'])<v['c0'],'Velocità di modulo inferiore a c richiesta.')
        if 'c0'in v and 'u'in v:check(abs(v['u'])<v['c0'],'Velocità u di modulo inferiore a c richiesta.')
        if 'carnot'in t:check(v['T1']>v['T2']>0,'Sorgente calda più calda della fredda, entrambe in kelvin.')
        if 'celsius'in t:check(v['temp']>=s.Rational('-273.15'),'Temperatura inferiore allo zero assoluto.')
        if 'epsilon'in v and 'stefan'in t:check(0<=v['epsilon']<=1,'Emissività fra 0 e 1 richiesta.')
        if 'angolo critico'in t:check(v['a']>v['b']>0,'Indice del primo mezzo maggiore del secondo richiesto.')
        if 'doppler'in t:check(abs(v['v1'])<v['v'] and abs(v['v2'])<v['v'],'Il modello richiede sorgente e osservatore subsonici.')
        if 'fotoelettrico'in t:check(v['hP']*v['f']>=v['energy'],'Frequenza sotto soglia: nessuna emissione fotoelettrica nel modello a un fotone.')
    if cid=='termo-031':check(v['Q']<=v['heat'],'Il calore ceduto non può superare quello assorbito nel ciclo motore indicato.')
    if cid=='elettro-012':check(v['Q']/v['voltage']>=0 if v['voltage']!=0 else False,'Carica e tensione devono avere segni coerenti per una capacità passiva non negativa.')
    if cid=='elettro-030':check(v['q']!=0,'La carica deve essere non nulla per l’orbita ciclotronica.')
    if cid=='multivariabile-034':check(v['K']>0 and v['r']>0 and v['C']>-1 and 1+v['C']*s.exp(-v['r']*v['t'])>0,'Capacità e tasso positivi, C>−1 per y₀>0 e denominatore positivo richiesti.')
    if cid=='digitale-011':
        check(0<=v['u']<2**v['n'],'Il codice deve essere rappresentabile nella larghezza assegnata.')
        check(v['sign']==s.floor(v['u']/2**(v['n']-1)),'Il bit di segno non corrisponde al codice unsigned.')
    if cid=='digitale-013':check(v['u']<2**v['n'] and v['k']<v['n'],'Codice entro n bit e shift minore della larghezza richiesti.')
    if cid=='discreta-004':check(v['c']<=min(v['a'],v['b']),'Intersezione maggiore di uno degli insiemi.')
    if cid=='numerico-009':check(v['b']>v['a'],'Il bracket deve avere estremi crescenti.')
    if cid=='elettronica-016':
        check(v['vgs']>v['vth'],'Il modello quadratico richiede V_GS>V_th, altrimenti è fuori regione.')
        if 'vds'in v:check(v['vds']>=v['vgs']-v['vth'],'V_DS insufficiente: il MOSFET non è in saturazione nel modello indicato.')
    if cid=='elettronica-017':check(v['Id']+v['Is']>0,'Il punto di lavoro richiede I_D+I_S>0.')
    if cid=='reti-007':check(v['arrival']<v['service'],'Coda M/M/1 non stabile: occorre λ<μ.')
    if cid=='informatica-024':check(v['selected']<=v['total'],'Le righe selezionate non possono superare il totale.')
    if cid=='statistica-002':check(v['b']>v['a'],'Estremi della distribuzione uniforme non validi.')
    if cid=='ml-012':check(v['y'] in (-1,1),'Le etichette della hinge loss sono −1 oppure +1, mai zero.')
    if cid=='deep-017':check(v['n']+2*v['padding']>=v['dilation']*(v['kernel']-1)+1,'Kernel effettivo più grande dell’ingresso con padding.')
    if cid=='deep-018':check(v['cin']%v['groups']==0 and v['cout']%v['groups']==0,'Il numero di gruppi deve dividere entrambi i numeri di canali.')
    if cid=='visione-021':check(v['union']>0 and v['intersection']<=v['union'],'Unione positiva e intersezione non maggiore dell’unione richieste.')
    if cid=='visione-022':check(v['a']+v['b']>0 and v['intersection']<=min(v['a'],v['b']),'Conteggi di maschere e intersezione incoerenti.')
    if cid=='sistemi_operativi-004':check(v['finish']>=v['arrival'],'Il completamento non può precedere l’arrivo.')
    if cid=='sistemi_operativi-005':check(v['turn']>=v['cpu'],'Il turnaround non può essere inferiore al tempo CPU nel modello CPU-only.')
    if cid=='sistemi_operativi-006':check(v['start']>=v['arrival'],'La prima esecuzione non può precedere l’arrivo.')
