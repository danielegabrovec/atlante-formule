# Revisione delle formule — Atlante Formule 1.2

Revisione interna del 25 ottobre 2026. Sono state riesaminate le **500 schede della prima versione** e aggiunte **488 schede**, per un totale di **988 schede in 36 sezioni**. Il registro riproducibile è [verifiche/audit-formule.json](verifiche/audit-formule.json): ogni scheda ha identificativo, hash del contenuto, modifiche e tipi di controllo eseguiti.

## Esito e significato del controllo

Nei controlli eseguiti non restano errori noti. Questo esito deriva da revisione delle relazioni e delle ipotesi, prove computazionali e controlli sui casi limite. **Non è una certificazione scientifica indipendente né una prova formale generale di tutti i teoremi.** Il rendering riuscito di una formula, da solo, non dimostra la sua correttezza.

| Livello | Copertura |
|---|---|
| Revisione editoriale interna | Formula, interpretazione, condizioni ed esempio per l'intero catalogo |
| Rendering locale | Tutte le 988 formule passano la conversione MathJax senza errori TeX |
| Esecuzione numerica | Tutti i 410 calcolatori passano sui dati iniziali, applicando i controlli di dominio |
| Dimensioni e scala | Verifica tramite quantità Pint; eccezioni esplicite per conversione Celsius e costante energetica di Bohr |
| Risultati attesi | 140 casi di riferimento coprono tutti i nuovi calcolatori; altri 21 casi numerici della prima edizione e ulteriori casi di bordo/sensibilità |
| Logica booleana | 148 assegnazioni complessive per circuiti e identità/esempi associati; equivalenze enumerate esaustivamente entro le variabili presenti |
| Geometria | Inizializzazione delle 70 figure e prove specifiche sulle lunghezze di mediana e sulla proporzione della bisettrice |
| Suite software | **1044 test superati**, con risultati in [test-results.xml](verifiche/test-results.xml) e [tests.log](verifiche/tests.log) |

I valori attesi sono fissati nei test e non vengono letti dal valore `reference_value` generato dal catalogo. I casi numerici non provano un'identità su un intero dominio infinito; per le identità booleane finite, invece, l'enumerazione copre tutte le assegnazioni delle variabili considerate.

## Correzioni e precisazioni principali

Sono registrate **39 revisioni editoriali** delle schede precedenti, oltre a correzioni dei vincoli dei calcolatori e delle figure. Non sono 39 equazioni numericamente errate: comprendono nomi ambigui, ipotesi incomplete, convenzioni di segno e completamenti delle relazioni.

| Area | Correzione o precisazione |
|---|---|
| Equazioni quadratiche | Il ramo con segno `+` è la radice maggiore soltanto se il coefficiente principale è positivo |
| Geometria analitica | La formula con valore assoluto restituisce l'area geometrica, non l'area orientata |
| Analisi | Precisate le ipotesi di de l'Hôpital e Taylor, il limite sulle partizioni di Riemann e gli indici della somma di Simpson |
| Equazioni differenziali | Completata la soluzione tramite fattore integrante; chiarite condizione iniziale e dominio della logistica |
| Statistica | Rifiutate somme campionarie incoerenti che darebbero varianza negativa |
| Meccanica | Distinti lavoro sul punto materiale, lavoro traslazionale del CM e cinetica totale; precisati moduli e angoli nelle formule di momento e potenza |
| Termodinamica | Emissività zero ammessa; rendimento del ciclo vincolato ai calori fisicamente coerenti; entropia con estremi di stato espliciti |
| Onde e ottica | Precisata l'esistenza del picco di risonanza; ammesse focali negative e ordini di interferenza negativi; controllate le condizioni di rifrazione |
| Elettromagnetismo | Modulo della forza sul filo con `abs(I)`; componenti orientate dei campi distinte dai moduli; carica superficiale negativa ammessa |
| Fisica moderna | Soglia fotoelettrica, impulso positivo per de Broglie e tassi di decadimento positivi; attività indicata in Bq |
| Digitale | Gli interi non passano più per un float: il massimo unsigned a 64 bit rimane esattamente `18446744073709551615` |
| Figure | Corrette la mediana opposta al lato richiesto, la mediana del baricentro, la bisettrice relativa al vertice corretto e la base dei solidi rispetto all'area assegnata |

Le nuove schede esplicitano convenzioni spesso fonte di errori: OR booleano e somma aritmetica; XOR e potenza; complemento a due e overflow; shift aritmetico e troncamento; parametrizzazione Gamma; fattore `1/2` delle loss; riduzione sul batch; GRU reset-before; normalizzazione delle trasformate; conteggi in bit/byte e unità fisiche.

## Modelli, unità e limiti

- I vincoli verificabili dai dati vengono controllati: probabilità, conteggi, temperatura, passi, range binari, regioni MOSFET quando è fornita V_DS, stabilità M/M/1 e compatibilità dei canali convoluzionali.
- Ipotesi sperimentali come piccole oscillazioni, flusso laminare, assenza di saturazione dell'op-amp o indipendenza dei campioni restano esplicite nella scheda e richiedono il contesto del problema.
- Nei grafici di sensibilità vengono esclusi anche punti che violano i controlli di dominio del modello. Il campionamento numerico non riconosce necessariamente ogni possibile discontinuità di un'espressione arbitraria.
- Bit, byte, host, parametri e risultati sono conteggi con un significato dichiarato. Percentuali e dB sono scale nominali; non si applica una conversione lineare indiscriminata alle loro etichette.
- L'offset Celsius e il coefficiente di Bohr in eV hanno un controllo esplicito, perché la sola espressione numerica non codifica tutte le unità implicite. Il secondo valutatore in floating point ha tolleranze dichiarate nei due esempi trigonometrici il cui risultato esatto è zero.
- La potenza dinamica CMOS, il timing ideale, i modelli di transistor e le metriche AI sono strumenti didattici; i parametri e le ipotesi vanno confrontati con il caso concreto.

## Riferimenti e tracciabilità

Le schede rimandano a fonti primarie o materiali degli autori per argomento: [MIT Computation Structures](https://computationstructures.org/notes/combinational_logic/notes.html), [MIT Signals and Systems](https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/), [Boyd e Vandenberghe](https://web.stanford.edu/~boyd/cvxbook/), [Deep Learning degli autori](https://www.deeplearningbook.org/), [IBM Quantum Learning](https://quantum.cloud.ibm.com/learning/courses/basics-of-quantum-information) e [Szeliski](https://szeliski.org/Book/), oltre alle fonti matematiche e fisiche già presenti.

I testi e gli esempi sono redatti per l'applicazione; il collegamento a un libro o corso indica una fonte di approfondimento, non un'approvazione dell'autore sulle nostre schede. L'accessibilità degli URL è registrata in [fonti-online.json](verifiche/fonti-online.json). Un HTTP 200 non certifica una formula; timeout, blocchi del publisher e problemi TLS del client di verifica sono distinti da un URL inesistente. Un collegamento errato al sommario di Computation Structures è stato sostituito con la pagina effettiva sulle prestazioni.

## Ripetere i controlli

```powershell
.\.venv\Scripts\python.exe tools\build_catalog.py
.\.venv\Scripts\python.exe -m pytest -q --junitxml=verifiche\test-results.xml -p no:faulthandler
.\.venv\Scripts\python.exe tools\audit_scientific.py
.\.venv\Scripts\python.exe tools\check_references.py
```

`Build.ps1` esegue nuovamente il controllo scientifico computazionale prima di creare l'EXE. Gli hash del registro permettono di riconoscere se una scheda o il motore sono cambiati dopo la revisione.


## Organizzazione disciplinare della versione 1.2

Le materie sono sezioni disciplinari con icone distinte. Algoritmi, architetture, basi di dati e sicurezza sono separati; programmazione/OOP, sistemi operativi, Web e AI distribuita hanno contenuti propri. I 24 esempi Python sono eseguiti con asserzioni nella suite e nel controllo del catalogo.


La pagina Sezioni raccoglie 36 materie con icone SVG dedicate. Le verifiche controllano i 36 simboli distinti, la rasterizzazione visibile nei due temi e la navigazione verso le materie, senza percorsi personali.
