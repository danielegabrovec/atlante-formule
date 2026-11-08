# Consegna — Atlante Formule 1.2

## Organizzazione corretta

La pagina iniziale è **Sezioni**. Le 36 materie hanno un’icona SVG distinta, un colore, una descrizione, argomenti e schede. Sono stati rimossi dall’interfaccia e dal catalogo attivo i percorsi personali e gli anni di laurea.

Algoritmi, architetture, basi di dati e sicurezza sono sezioni separate. Programmazione/OOP, sistemi operativi, Web e sistemi distribuiti hanno contenuti propri. La consultazione è per materia, con livelli Fondamenti, Università e Avanzato.

## Contenuti e prove

- 988 schede e 410 calcolatori.
- 376 visualizzazioni: figure e grafici associati.
- 24 esempi Python autonomi verificati con asserzioni.
- 36 icone di materia distinte, integrate anche come file SVG locali; icone delle azioni e delle schede operative.
- **1044 test superati**, senza fallimenti o errori.
- Audit numerico e dimensionale del catalogo con zero errori nei controlli eseguiti.
- EXE verificato al 100% e al 150%, da cartella estranea al progetto, con PATH senza Python.
- Verifica di CRC e confronto SHA256 dei byte riletti dai pacchetti Windows e sorgenti.

## File pronti

- Programma: `dist/AtlanteFormule/AtlanteFormule.exe`.
- Avvio rapido: `Avvia.cmd`.
- Distribuzione: `dist/AtlanteFormule-Windows-x64.zip`.
- Sorgenti: `dist/AtlanteFormule-Sorgenti.zip`.
- Hash: `dist/SHA256SUMS.txt` e manifest dei singoli file nel pacchetto.
- [Materie](MATERIE.md), [Guida](GUIDA.md), [Audit](AUDIT_FORMULE.md), [Verifiche](VERIFICHE.md).

Le versioni 1.0 e 1.1 sono conservate nella cartella `versioni`. Gli ID esistenti sono mantenuti; note e preferiti sono esterni alla cartella del programma.

## Arresto del sistema richiesto

Dopo il completamento e la verifica degli archivi viene richiesto l’arresto normale di Windows. Lo script `tools/arresta_dopo_verifiche.ps1` verifica nuovamente test, audit, prove EXE e hash prima di poter essere armato. La richiesta e lo stato sono registrati in `verifiche/arresto-sistema.json` al momento dell’attivazione.

Il controllo dei contenuti è interno e non una certificazione scientifica indipendente. Windows pulito, macOS, Linux e lettori di schermo non sono stati verificati.
