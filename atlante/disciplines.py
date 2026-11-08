"""Organizzazione editoriale per materie, indipendente da piani personali."""
from atlante.sections import family

# Titolo, icona, descrizione, prerequisiti consigliati.
INFO={
 'base':('Aritmetica e algebra','math','Numeri, potenze, equazioni, polinomi, logaritmi e numeri complessi.','Operazioni sui numeri reali'),
 'classica':('Geometria classica','triangle','Geometria piana e solida, triangoli, poligoni, circonferenze e volumi.','Algebra e proporzioni'),
 'analitica':('Geometria analitica','coordinates','Coordinate, rette, coniche, trasformazioni e geometria nello spazio.','Algebra, geometria classica'),
 'trigonometria':('Trigonometria','sine','Funzioni, identità, equazioni trigonometriche e risoluzione dei triangoli.','Angoli, algebra'),
 'analisi':('Analisi matematica','integral','Limiti, derivate, integrali, successioni, serie e approssimazioni.','Algebra, funzioni e trigonometria'),
 'multivariabile':('Analisi multivariabile e ODE','surface','Derivate parziali, integrali multipli, campi vettoriali ed equazioni differenziali.','Analisi matematica, algebra lineare'),
 'lineare':('Algebra lineare','matrix','Vettori, matrici, sistemi, autovalori, spazi e fattorizzazioni.','Algebra e sistemi lineari elementari'),
 'discreta':('Matematica discreta e grafi','graph','Logica, insiemi, conteggio, congruenze, grafi e ricorrenze.','Algebra elementare'),
 'numerico':('Metodi numerici','numeric','Errori, condizionamento, zeri, interpolazione, quadratura e sistemi numerici.','Analisi matematica, algebra lineare'),
 'probabilita':('Probabilità','dice','Eventi, combinatoria, variabili aleatorie e distribuzioni fondamentali.','Algebra e conteggio'),
 'statistica':('Statistica e inferenza','statistics','Stima, test, intervalli, informazione e modelli stocastici.','Probabilità e analisi matematica'),
 'ottimizzazione':('Ottimizzazione','target','Convessità, gradienti, vincoli, dualità e algoritmi di discesa.','Analisi multivariabile, algebra lineare'),
 'meccanica':('Meccanica e gravitazione','pendulum','Cinematica, dinamica, energia, urti, rotazioni e orbite.','Algebra, vettori e trigonometria'),
 'termo':('Fluidi e termodinamica','thermometer','Pressione, flussi, calore, gas, lavoro, entropia e macchine termiche.','Fisica di base e analisi matematica'),
 'onde':('Onde e ottica','optics','Oscillazioni, onde, suono, rifrazione, lenti, interferenza e diffrazione.','Trigonometria e meccanica'),
 'elettro':('Elettricità e magnetismo','magnet','Campi, potenziali, capacità, circuiti, induzione ed elettromagnetismo.','Vettori, analisi e fisica di base'),
 'moderna':('Fisica moderna','atom','Relatività, fotoni, quantistica introduttiva e fisica nucleare.','Fisica classica, algebra e numeri complessi'),
 'quantum':('Informazione quantistica','qubit','Qubit, porte, misura, sistemi composti, entanglement ed entropia.','Algebra lineare complessa e probabilità'),
 'bool':('Algebra di Boole e logica','gate','Operatori, identità, mintermini, maxtermini e mappe di Karnaugh.','Logica proposizionale elementare'),
 'digitale':('Elettronica digitale','binary','Porte, sommatori, codifiche binarie, flip-flop, temporizzazioni e memorie.','Algebra di Boole, circuiti elementari'),
 'elettronica':('Elettronica analogica','circuit','Reti, filtri, diodi, transistor e amplificatori operazionali.','Elettrotecnica, numeri complessi'),
 'segnali':('Segnali e trasformate','signal','Sistemi LTI, convoluzione, Fourier, Laplace, Z e campionamento.','Analisi e numeri complessi'),
 'robotica':('Controlli e robotica','robot','Dinamica, stabilità, retroazione, cinematica e stima dello stato.','Algebra lineare, ODE e segnali'),
 'algoritmi':('Algoritmi e strutture dati','algorithm','Complessità, ricerca, ordinamento, hashing e programmazione dinamica.','Programmazione e matematica discreta'),
 'architettura':('Architettura dei calcolatori','cpu','CPU, CPI, cache, memoria, pipeline e parallelismo.','Sistemi binari ed elettronica digitale'),
 'basi_dati':('Basi di dati','database','Relazioni, SQL, chiavi, normalizzazione, indici e transazioni.','Insiemi e logica'),
 'sicurezza':('Sicurezza informatica','shield','Hash, filtri probabilistici, aritmetica modulare e crittografia di base.','Probabilità, discreta e reti'),
 'programmazione':('Programmazione e OOP','code','Funzioni, oggetti, incapsulamento, polimorfismo e progettazione del software.','Logica e strutture dati elementari'),
 'sistemi_operativi':('Sistemi operativi','os','Processi, thread, scheduling, sincronizzazione, memoria e file system.','Programmazione e architetture'),
 'reti':('Reti di calcolatori e IoT','network','Ritardi, protocolli, indirizzamento, code, affidabilità e dispositivi connessi.','Probabilità e sistemi digitali'),
 'web':('Ingegneria del Web','web','HTTP, API, browser, sessioni, sicurezza e architetture applicative.','Programmazione, reti e basi di dati'),
 'distribuita':('Sistemi distribuiti e AI scalabile','servers','Parallelismo, comunicazione, addestramento distribuito e memoria dei modelli.','Reti, architetture e machine learning'),
 'ml':('Machine learning','learning','Regressione, classificazione, kernel, alberi, clustering e valutazione.','Statistica, algebra lineare e ottimizzazione'),
 'deep':('Deep learning e rinforzo','neural','Reti neurali, backpropagation, CNN, sequenze, attenzione e apprendimento per rinforzo.','Machine learning, derivate e matrici'),
 'visione':('Visione e dati multimediali','vision','Immagini, filtri, geometria della visione, codifica e misure.','Segnali, algebra lineare e probabilità'),
 'bioai':('Bioinformatica e AI biomedica','dna','Sequenze, allineamento, genomica, metriche e validazione dei modelli.','Probabilità, statistica e machine learning'),
}

def organize(cards):
    for c in cards:
        origin=c['category'];c['editorial_group']=origin
        if origin=='informatica':
            i=int(c['id'].rsplit('-',1)[1]);c['category']='algoritmi' if i<=9 else 'architettura' if i<=18 else 'sicurezza' if i<=22 else 'basi_dati'
            if i<=2:c['topic']='Analisi asintotica'
            elif i==3:c['topic']='Ricerca'
            elif i<=5:c['topic']='Ordinamento'
            elif i<=7:c['topic']='Hashing'
            elif i==8:c['topic']='Analisi ammortizzata'
            elif i==9:c['topic']='Programmazione dinamica'
            elif i<=11:c['topic']='CPU e istruzioni'
            elif i==12:c['topic']='Gerarchia di memoria'
            elif i<=15:c['topic']='Parallelismo e scalabilità'
            elif i==16:c['topic']='Pipeline'
            elif i==17:c['topic']='Modelli di prestazione'
            elif i==18:c['topic']='Rappresentazione e allineamento'
            elif 19<=i<=21:c['topic']='Hash e strutture probabilistiche'
            elif i==22:c['topic']='Crittografia a chiave pubblica'
            elif i in (23,24):c['topic']='Algebra relazionale'
            elif i==26:c['topic']='Progettazione relazionale'
            elif i in (25,27,28):c['topic']='Query e archiviazione'
        elif origin=='database':c['category']='basi_dati'
        info=INFO[c['category']];c['category_label']=info[0];c['section_icon']=info[1];c['prerequisites']=info[3]
        if c['level'] not in ('Liceo','Liceo / Università','Università'):c['level']='Avanzato' if c['category'] in ('ottimizzazione','deep','quantum','bioai','distribuita') else 'Università'
        c['tags']=list(dict.fromkeys([*c['tags'],c['category_label'],c['topic']]))
        c.pop('courses',None);c.pop('course_titles',None);c.pop('stage',None)
        if origin in ('programmazione','sistemi_operativi','web','database','distribuita') and not c.get('calculator'):c['kind']='concetto'

def section_index(cards):
    out=[]
    for key,(title,icon,summary,prerequisites) in INFO.items():
        entries=[c for c in cards if c['category']==key]
        if entries:out.append({'id':key,'title':title,'icon':icon,'summary':summary,'prerequisites':prerequisites,'family':family(key),'count':len(entries),'topics':list(dict.fromkeys(c['topic'] for c in entries))})
    return out
