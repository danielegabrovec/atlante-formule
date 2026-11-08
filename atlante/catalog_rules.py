"""Vincoli espliciti dei calcolatori, con semantica delle unità distinta."""
def decorate_calculator(card):
    calc=card['calculator'];cat=card['category'];cid=card['id'];inputs={f['name']:f for f in calc['inputs']}
    def bound(names,**kwargs):
        for name in names.split(','):
            if name in inputs:inputs[name].update(kwargs)
    def positive(names):bound(names,strict_min=0)
    def nonnegative(names):bound(names,min=0)
    def integers(names,minimum=0,maximum=1000000):bound(names,integer=True,min=minimum,max=maximum)
    if cat=='bool':bound(','.join(inputs),min=0,max=1,integer=True);calc['output_unit']='bit logico'
    if cat=='digitale':
        integers('n',1,256);integers('k',0,255);integers('a',0,128);integers('w',1,1024);integers('M',2,2**32)
        bound('sign',integer=True,min=0,max=1);bound('u',integer=True,min=0);bound('x',integer=True)
        for name in ('a','b'):
                if name in inputs and cid in ('digitale-001','digitale-002'):bound(name,min=0,max=1,integer=True)
        nonnegative('tc,ts,tcq,tcomb,tsetup,thold,alpha,C,voltage,current');positive('T,f,ioh,iih,iol,iil')
        if cid=='digitale-010':integers('n',2,256)
        if cid=='digitale-023':positive('T')
        if cid=='digitale-030':calc['output_unit']='dB'
        if cid in ('digitale-009','digitale-010','digitale-011','digitale-013','digitale-014','digitale-015','digitale-020','digitale-027','digitale-028'):calc['integer_output']=True
        if cid=='digitale-028':calc['output_unit']='bit'
    if cat=='discreta':
        integers('a,b,c,n,m')
        if cid=='discreta-019':integers('n',1)
        calc['integer_output']=True
    if cat=='numerico':
        integers('p',2,256);positive('tol')
        if cid=='numerico-009':calc['integer_output']=True
    if cat=='elettronica':
        positive('R1,R2,resistance,C,L,Is,n,Vt,T,qe,kn,Rf,Rin,Rg,gbw,ng,sr,amp');nonnegative('Ib,Ic');
        if cid=='elettronica-016':positive('kn')
        if cid=='elettronica-023':bound('ng',min=1)
        if cid=='elettronica-010':calc['output_unit']='dB'
        if cid=='elettronica-015':calc['output_unit']='S'
    if cat=='segnali':
        positive('fs,tau,step');nonnegative('f')
        if cid=='segnali-023':calc['output_unit']='1/s'
        if cid=='segnali-028':calc['output_unit']='V^2'
    if cat=='robotica':
        positive('tau,wn,l1,l2');nonnegative('t');bound('zeta',strict_min=0,strict_max=1)
        if cid=='robotica-009':bound('zeta',min=0.4,max=0.8)
    if cat=='reti':
        positive('rate,speed,rtt,service,band,tx,capacity,current');nonnegative('distance,arrival,bits,snr,load,wait,rate')
        bound('prob',min=0,max=1);bound('duty',min=0,max=1);nonnegative('ion,isleep')
        integers('M',2);integers('prefix',0,30);integers('k',0,32);integers('n',1);integers('faults',0)
        if cid=='reti-008':integers('bits',0)
        if cid=='reti-017':bound('prob',min=0,strict_max=1)
        if cid=='reti-022':nonnegative('rate,t')
        if cid in ('reti-010','reti-011'):calc['output_unit']='bit/s'
        if cid=='reti-004':calc['output_unit']='bit'
        if cid=='reti-015':calc['output_unit']='byte/s'
        if cid in ('reti-013','reti-014'):calc['output_unit']='host' if cid.endswith('013') else 'sottoreti'
        if cid=='reti-026':calc['output_unit']='hour'
    if cat=='informatica':
        integers('n,m,processors,align,size,total,selected',0)
        positive('m,processors,align,total,f,delay,logical');nonnegative('instructions,cpi,hit,penalty,physical')
        bound('frac,serial,miss',min=0,max=1);bound('load',min=0,strict_max=1)
        if cid=='informatica-003':integers('n',1)
        if cid in ('informatica-019','informatica-020','informatica-021'):positive('M,m,n');integers('k',1,200)
        if cid=='informatica-016':calc['output_unit']='risultati/s'
        if cid=='informatica-018':calc['output_unit']='byte'
    if cat=='statistica':
        positive('sigma,eps');integers('n',1);bound('prob',min=0,max=1)
        if cid=='statistica-018':calc['output_unit']='bit'
    if cat=='ml':
        bound('y',integer=True,min=-1,max=1);bound('error',strict_min=0,strict_max=0.5)
        integers('tp,tn,fp,fn',0)
    if cat=='deep':
        integers('inputs,outputs,fanin,fanout,n,kernel,stride,dilation,cout,cin,groups,kh,kw',1);integers('padding',0)
        if cid in ('deep-002','deep-017','deep-018'):calc['integer_output']=True
    if cat=='quantum':
        integers('n',0,256);integers('N',1,10**15)
        if cid=='quantum-007':calc['integer_output']=True
    if cat=='bioai':
        integers('m',1);bound('alpha',strict_min=0,strict_max=1);bound('sens,spec,prior',min=0,max=1)
    if cat=='visione':
        positive('focal,baseline,disparity,peak,mse');integers('intersection,union,a,b',0)
        if cid=='visione-019':calc['output_unit']='dB'
    if cat=='sistemi_operativi':
        nonnegative('overhead,turn,cpu,tlb,mem,normal,fault');positive('quantum,pagesize');integers('size',0);integers('pagesize',1);bound('hit,prob',min=0,max=1)
        if cid=='sistemi_operativi-014':calc['output_unit']='byte'
        if cid=='sistemi_operativi-013':calc['output_unit']='pagine'
    if cat=='distribuita':
        integers('workers,batch,accum,layers,heads,dim,bytesper',1);integers('tokens,parameters,capacity',0);nonnegative('latency,size,secondsperbyte,itembytes');positive('cost,mttf')
        if cid=='distribuita-004':integers('workers',2)
        if cid in ('distribuita-009','distribuita-010','distribuita-014'):calc['output_unit']='byte'
    # Corregge vincoli generici della versione 1.0 che confondevano simboli omonimi.
    if cat=='base' and cid in ('base-009','base-010','base-011','base-012'):
        for name in ('m','n'):
            if name in inputs:
                for key in ('integer','min','max'):inputs[name].pop(key,None)
        if cid!='base-012':positive('a')
    if cat in ('meccanica','termo','onde','elettro','moderna'):
        positive('g,A,R1,R2,C1,C2,nu')
        if cat in ('meccanica','onde'):positive('k')
        if cat=='termo':positive('c,k')
    if cid in ('meccanica-010','meccanica-011','meccanica-020'):bound('theta',min=0,max_expr='pi')
    if cid in ('meccanica-010','meccanica-011'):positive('v0')
    if cid=='meccanica-044':positive('a')
    if cid=='meccanica-009':nonnegative('v0')
    if cid=='meccanica-017':nonnegative('mu,N')
    if cid in ('meccanica-021','meccanica-034'):nonnegative('F,s');bound('theta',min=0,max_expr='pi')
    if cid=='meccanica-028':nonnegative('F,v');bound('theta',min=0,max_expr='pi')
    if cid=='meccanica-020':bound('theta',min=0,max_expr='pi/2')
    if cid=='termo-012':nonnegative('v')
    if cid=='termo-011':nonnegative('v');positive('D')
    if cid=='termo-027':positive('pressure')
    if cid=='termo-013':
        for name in ('R1','R2'):
            if name in inputs:inputs[name].pop('strict_min',None)
    if cid=='termo-020':
        inputs['epsilon'].pop('strict_min',None);bound('epsilon',min=0,max=1)
    if cid in ('termo-022','termo-024'):positive('p1')
    if cid=='termo-031':positive('heat');nonnegative('Q')
    if cat=='onde':nonnegative('amp')
    if cid=='onde-014':positive('I,I0')
    if cid=='onde-012':positive('F,mu')
    if cid=='onde-013':nonnegative('P')
    if cid=='onde-033':nonnegative('I0')
    if cid in ('onde-016','onde-021','onde-022','onde-034'):positive('a,b')
    if cid=='onde-021':bound('theta',min=0,max_expr='pi/2')
    if cid=='onde-017':positive('v')
    if cid in ('onde-024','onde-025','onde-027'):inputs['f'].pop('strict_min',None)
    if cid=='onde-029':integers('n',0);inputs['n']['min']=-1000000
    if cid in ('elettro-010','elettro-011'):nonnegative('p,E,d');positive('q')
    if cid in ('meccanica-034','elettro-011','elettro-028','elettro-031'):bound('theta',min=0,max_expr='pi')
    if cid in ('elettro-028','elettro-030'):nonnegative('v,B')
    if cid=='elettro-030':positive('v,B')
    if cid in ('elettro-031','elettro-036'):nonnegative('B')
    if cid in ('elettro-034','elettro-038'):integers('N',1)
    if cid=='elettro-043':nonnegative('voltage')
    if cid in ('moderna-010',):positive('p')
    if cid=='moderna-009':nonnegative('energy')
    if cid in ('moderna-017','moderna-018','moderna-019'):positive('rate');nonnegative('N,t')
    if cid=='moderna-016':positive('b')
    if cid=='moderna-019':calc['output_unit']='Bq'
    if cid in ('classica-001','classica-002','classica-004','classica-023','classica-030'):calc['output_unit']='rad'
