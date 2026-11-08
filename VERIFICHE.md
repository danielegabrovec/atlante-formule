# Verifiche — Atlante Formule 1.2

Controlli del 25 ottobre 2026 su Windows x64 build 26200, Python 3.13.13, PyQt6 6.11.0 e Qt 6.11.2.

## Contenuti e motore

| Controllo | Esito |
|---|---|
| Catalogo | 988 schede, 36 sezioni, 500 ID originali mantenuti e 488 schede aggiunte rispetto alla prima edizione |
| Calcolatori | 410 eseguiti sui dati iniziali; 140 nuovi casi di riferimento, 21 ulteriori casi numerici originali e regressioni sui domini |
| Visualizzazioni | 376 schede: 70 figure geometriche e 306 grafici di sensibilità |
| Formule | Tutte le 988 renderizzate da MathJax locale senza errori TeX |
| Revisione | 39 revisioni editoriali registrate; controllo dimensionale e della scala, con eccezioni esplicite |
| Boole | Tabelle, equivalenza con controesempio, CNF/DNF, Karnaugh Gray e preservazione delle variabili nelle tautologie |
| Programmazione | 24 esempi Python compilati ed eseguiti con asserzioni; copia ed editor conservano il codice |
| Digitale | Interi a 64 bit esatti, complemento a due, shift negativo, ADC, temporizzazioni e potenza |
| Grafici | Maschera dei domini del modello, singolarità e valori non reali; regressioni sulle mediane e bisettrici |
| Sezioni | 36 materie con indice, argomenti, descrizioni e icone distinte |
| Colori | Contrasto del testo di sezione almeno 4.5:1 sui pannelli dei due temi; nomi e icone sempre presenti |
| Persistenza | Note e preferiti, editor, backup e importazione atomica; impostazioni non valide respinte |
| Processi | Calcoli e campionamento separati, annullamento, scarto dei risultati obsoleti e timeout di produzione a 15 secondi |
| Suite completa | **1044 test superati**, zero fallimenti ed errori; `verifiche/test-results.xml` e `verifiche/tests.log` |

Il dettaglio scientifico è in [AUDIT_FORMULE.md](AUDIT_FORMULE.md), con registro per ciascuna scheda e hash del contenuto e del motore in `verifiche/audit-formule.json`. Esecuzione numerica, rendering e revisione interna sono tipi di evidenza diversi: non equivalgono a una certificazione scientifica esterna.

## Distribuzione Windows

La verifica dell'EXE 1.2 controlla rendering locale, calcolatore, simbolica, massimo unsigned a 64 bit, equivalenza booleana, Karnaugh, sezioni e icone, avviando il pacchetto da una cartella temporanea estranea al progetto con `PATH` limitato a Windows e senza `PYTHONPATH`. Gli esiti del pacchetto finale sono in `verifiche/package-smoke.json` e `package-smoke-dpi150.json`.

Stato della verifica EXE 1.2: **superata al 100% e al 150%**, con `frozen=true`, catalogo da 988 schede e tutti i controlli `ok=true`. Sezioni, icone, navigazione, rendering, calcolo, interi a 64 bit, simbolica, Boole e Karnaugh funzionano dal pacchetto senza Python nel PATH. I log degli avvii finali sono conservati.

Il confezionamento confronta gli hash dei byte riletti dallo ZIP con il manifest dei file ed esegue il controllo CRC. `dist/SHA256SUMS.txt` contiene gli hash dei due archivi, mentre `dist/AtlanteFormule/SHA256.json` elenca quelli dei singoli file.

## Limiti espliciti

- Windows pulito, macOS e Linux non verificati; nessuna firma digitale del pacchetto.
- I teoremi generali sono stati riesaminati internamente; le prove automatiche simboliche e numeriche coprono le famiglie e i casi documentati.
- Le figure includono costruzioni di riferimento; il programma non è un CAD o un simulatore completo di circuiti.
- I passaggi guidati sono disponibili per le operazioni dichiarate; le altre restituiscono il risultato con le condizioni e l'eventuale indicazione di mancata soluzione esplicita.
- Il riconoscimento delle discontinuità nei grafici numerici di funzioni arbitrarie non è completo.
- Lettori di schermo non verificati. Navigazione, temi, ridimensionamento e scala 150% sono oggetto di prove dell'interfaccia e del pacchetto.

## Riproduzione

```powershell
.\.venv\Scripts\python.exe tools\build_catalog.py
.\.venv\Scripts\python.exe -m pytest -q --junitxml=verifiche\test-results.xml -p no:faulthandler
.\.venv\Scripts\python.exe tools\audit_scientific.py
powershell -ExecutionPolicy Bypass -File .\Build.ps1
.\.venv\Scripts\python.exe tools\test_executable.py
.\.venv\Scripts\python.exe tools\test_executable.py 1.5
.\.venv\Scripts\python.exe tools\package_release.py
```

L'opzione pytest evita segnalazioni spurie di faulthandler per eccezioni COM gestite da Qt; asserzioni ed eccezioni Python restano controllate. La build usa un PATH isolato per evitare DLL omonime di altri strumenti, come ICU di Poppler, problema rilevato e risolto nella prima edizione. La versione 1.0 e i relativi ZIP sono conservati in `versioni/1.0`.
