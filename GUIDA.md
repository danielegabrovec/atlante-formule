# Atlante Formule 1.2 — guida

## Avvio

Estrai tutto `AtlanteFormule-Windows-x64.zip` e apri `AtlanteFormule/AtlanteFormule.exe`. Mantieni la cartella `_internal` accanto all’EXE. Non serve Python installato e la consultazione funziona offline. Nella cartella di sviluppo puoi usare `Avvia.cmd`.

## Sezioni e argomenti

L’app si apre sulla pagina **Sezioni**: 36 materie, ciascuna con icona dedicata, colore, descrizione e conteggio. Il filtro in alto seleziona un’area disciplinare. Premi una materia per aprire le sue schede; nella barra laterale puoi espandere gli argomenti. **Sezioni** torna alla panoramica.

Le categorie sono le materie: matematica, fisica, elettronica, programmazione, algoritmi, architetture, sistemi operativi, basi di dati, Web, reti, sicurezza e AI. Il catalogo attuale contiene 988 schede, 410 calcolatori e 376 visualizzazioni associate. [MATERIE.md](MATERIE.md) elenca tutte le sezioni.

La ricerca dalla panoramica è globale. Nel catalogo lavora nella sezione e nei filtri scelti. Ctrl+K porta alla ricerca; il campo mostra il percorso dei risultati. I filtri distinguono Fondamenti, Università, Avanzato e strumenti disponibili.

## Schede

«Spiegazione» mostra formula o definizione, significato, condizioni, esempio, codice se presente, prerequisiti e fonti. A− e A+ cambiano la dimensione del testo. «LaTeX» copia la formula; nelle schede di programmazione il pulsante diventa «Codice» e copia l’esempio.

«Calcolatore», «Visualizzazione» e «Note» hanno icone proprie. Le schede puramente concettuali non mostrano calcolatori inventati. Preferiti e recenti aiutano a ritrovare contenuti; Alt+Sinistra torna alla scheda precedente. Il pulsante delle altre azioni permette copia personale, modifica delle proprie schede e apertura esplicita delle fonti online.

Le fonti online sono facoltative. Il testo, le formule e gli SVG funzionano localmente. Il menu Archivio contiene legenda delle icone e dei colori, guida alle materie e rapporto di controllo.

## Calcoli e unità

Inserisci numeri nelle unità dei campi: `0,25`, `1e-6`, `1/3`, `pi/6` sono esempi validi. Puoi specificare unità compatibili come `300 cm` nel campo in metri, `2 ms` nel campo in secondi o `90 deg` nel campo in radianti. Usa `*` per moltiplicare. Gli angoli senza unità esplicita sono in radianti.

La precisione riguarda le cifre significative mostrate per i risultati non interi, non l’incertezza sperimentale. Gli interi sono conservati esattamente: il massimo unsigned a 64 bit è `18446744073709551615`.

I controlli respingono valori fuori dominio e combinazioni incompatibili. Le ipotesi che richiedono contesto fisico, come piccoli angoli o regime laminare, sono nella scheda e vanno valutate sul problema reale. Le costanti possono essere arrotondate.

## Grafici e figure

Le figure geometriche hanno assi con uguale scala, punti e misure. Alcune sono costruzioni di riferimento; i parametri collegati vengono aggiornati secondo gli strumenti supportati. Nei grafici di sensibilità cambia un parametro mentre gli altri sono fissati ai dati del calcolatore.

I campioni non reali, le singolarità individuate e i valori che violano i controlli del modello vengono esclusi. Il campionamento non sostituisce uno studio analitico completo del dominio. La barra del grafico offre zoom e spostamento; l’esportazione salva PNG o SVG.

## Laboratorio

Ctrl+L apre il laboratorio. Scegli operazione e formato indicato nell’esempio. Il cambio di operazione conserva il testo dell’utente. Calcoli e campionamento onerosi sono annullabili in processi separati con timeout di 15 secondi.

| Operazione | Esempio |
|---|---|
| Derivata | `x^3*sin(x)` |
| Equazione | `x^2-5*x+6=0` |
| Sistema lineare | `x+y=3; x-y=1` |
| Matrici | `1,2;3,4` — virgole fra colonne, punto e virgola fra righe |
| Limite | `sin(x)/x`, punto 0, direzione bilatera |
| Retta per due punti | `0;0;2;3` |
| Distanza punto-retta | `0;0;3;4;-10` per punto e coefficienti ax+by+c=0 |
| Circonferenza | `1;-2;3` per centro e raggio |
| Intersezione retta-conica | `y-x; x^2+y^2-2`, espressioni uguali a zero |
| Grafico | `sin(x)/x`, estremi −5 e 5 |
| Superficie | `x^2+y^2`, estremi −3 e 3 |

Gli integrali indefiniti richiedono una costante C. Sono disponibili passaggi guidati per le famiglie dichiarate; negli altri casi il motore restituisce risultato e condizioni, segnalando espressioni non risolte. La semplificazione non estende automaticamente il dominio iniziale.

Funzioni aritmetiche: `sin`, `cos`, `tan`, inverse e iperboliche supportate, `sqrt`, `exp`, `log`, `Abs`, `factorial`, `erf`, `floor`, `ceiling`, `Min`, `Max`, `Mod`, `xlogx`. `log` è naturale, `oo` indica infinito. Il fattoriale numerico è limitato a 200 e le matrici a 10×10.

## Logica booleana

Tabella di verità, semplificazione Boole, equivalenza, CNF e Karnaugh usano bit 0/1 e variabili a una lettera. `~` è NOT, `&` AND, `|` OR e `^` XOR; usa parentesi per rendere esplicito il raggruppamento. In questa modalità sono nascosti i parametri aritmetici non pertinenti.

Per equivalenza inserisci due espressioni separate da `;`: `~(A & B); ~A | ~B`. La verifica enumera le assegnazioni e mostra un controesempio quando le funzioni differiscono. Le tabelle supportano fino a 6 variabili, Karnaugh da 1 a 4 in ordine Gray, senza don't care impliciti.

**`^` indica potenza in aritmetica e XOR in logica.** Le schede booleane aprono direttamente il proprio strumento. Il laboratorio logico non simula ritardi analogici o metastabilità.

## Archivio personale

Crea una scheda o duplica un contenuto dal catalogo. Puoi conservare spiegazioni, condizioni, esempi e codice. Le annotazioni vengono salvate automaticamente, anche prima del cambio di scheda o della chiusura.

I dati sono in `%LOCALAPPDATA%\AtlanteFormule\atlante.sqlite3`, separati dalla cartella del programma. L’aggiornamento del pacchetto mantiene gli ID esistenti. Esporta il backup JSON dal menu Archivio; l’importazione valida i dati e salva un backup precedente. Il codice delle schede è visualizzato e copiato, non eseguito dall’app.

## Sviluppo e verifica

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe tools\build_catalog.py
.\.venv\Scripts\python.exe main.py
```

L’archivio sorgenti include MathJax e font. Se mancanti: `npm.cmd ci --prefix vendor`.

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=verifiche\test-results.xml -p no:faulthandler
.\.venv\Scripts\python.exe tools\audit_scientific.py
powershell -ExecutionPolicy Bypass -File .\Build.ps1
.\.venv\Scripts\python.exe tools\test_executable.py
.\.venv\Scripts\python.exe tools\test_executable.py 1.5
.\.venv\Scripts\python.exe tools\package_release.py
```

Le schede sono in `contenuti/*.txt`; il compilatore produce il JSON del catalogo e l’indice delle sezioni. Nei file editoriali il separatore è `|`: per moduli in LaTeX usa `\lvert` e `\rvert`. Esempi Python e tassonomia sono nei rispettivi moduli sorgente. Le revisioni precedenti sono conservate in `versioni`.
