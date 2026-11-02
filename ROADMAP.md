# Roadmap del progetto

Stato: il modello strutturale v1 è approvato. Il modello di acquisizione eterogenea e il componente indipendente di acquisizione locale sono implementati sul ramo di lavoro; la verifica conclusiva del componente dipende dalla suite GitHub Actions sul commit corrente. Il coordinatore non è implementato.

## Fase 0 — Conservazione e modello strutturale
- [x] Verificare repository, ramo e file correnti.
- [x] Recuperare README e contenuti delle skill presenti.
- [x] Consultare la specifica Agent Skills ufficiale.
- [x] Documentare architettura, glossario, modello, decisioni e questioni aperte.
- [x] Approvare il modello concettuale v1, inclusa l'acquisizione di pacchetti non ancora classificati.
- [x] Aggiornare i documenti architetturali per riflettere le decisioni confermate.
- [ ] Verificare formalmente coerenza e completezza della documentazione aggiornata.

## Fase 1 — Inventario e criteri della libreria
- [x] Analizzare i materiali già presenti senza modificarli.
- [x] Definire i dati minimi per confrontare e selezionare skill.
- [x] Definire la distinzione tra materiale acquisito, classificazione e skill utilizzabile.
- [x] Definire lo schema della scheda descrittiva esterna.
- [x] Definire il trattamento di file singoli, cartelle, archivi, pacchetti compositi e riferimenti remoti.
- [ ] Definire provenienza, impronta, versionamento e gestione dei duplicati in modo completo.

## Fase 2 — Acquisizione e validazione eterogenea
- [x] Separare controlli generali di acquisizione e integrità dai controlli specifici dei profili.
- [x] Consentire la conservazione e registrazione di formati sconosciuti; gli analizzatori restano facoltativi.
- [x] Aggiungere il catalogo dei materiali e lo schema della scheda descrittiva esterna.
- [x] Aggiornare il validatore: SKILL.md è controllato soltanto per il profilo Agent Skills.
- [x] Aggiungere test per file, cartelle, archivi, pacchetti e acquisizioni incomplete/non classificate.
- [x] Verificare l'impronta degli originali e rilevare modifiche successive all'acquisizione.
- [x] Eseguire i 30 test e il validatore tramite GitHub Actions sul commit `d57f0b11690a71dafc1144b5fa8b7b560ab0bd0b`.
- [x] Definire il contratto pubblico del componente indipendente di acquisizione con test prima dell'implementazione.
- [x] Implementare copia locale, scheda descrittiva, impronta, controlli di collisione e registrazione di riferimenti remoti.
- [ ] Verificare la nuova implementazione con tutti i test tramite GitHub Actions.
- [ ] Aggiungere recupero automatico da interruzione forzata e gestione dei duplicati per contenuto, non soltanto per identificativo.
- [ ] Verificare l'esecuzione locale su Windows.

Criterio di uscita: un materiale locale può essere copiato e registrato senza modificare la sorgente; un riferimento remoto viene distinto da una copia locale; nessun materiale viene classificato, eseguito o certificato automaticamente durante l'acquisizione.

## Fase 3 — Inventario operativo delle skill esistenti
Solo dopo che la procedura di acquisizione e conservazione è verificata:
- UNLAZY: registrare riferimenti mancanti e dipendenze.
- Archivista: registrare il riferimento mancante e le sezioni assenti.
- Find Skills: verificare istruzioni, comandi e fonti.
- Canva KDP: conservare e descrivere il file disponibile; è di 36 byte e appare danneggiato, non ricostruirlo come se fosse integro.

Regola: preservare esattamente i materiali originali. Non riscrivere, correggere o adattare preventivamente. Acquisizione, documentazione, verifica e approvazione all'uso sono passaggi distinti.

## Fase 4 — Interoperabilità
Provare skill non sensibili su Claude Code e Codex e, se accessibile, su un'altra piattaforma. Separare contenuto canonico e adattamenti. Registrare prove, differenze e limiti.

## Fase 5 — Prototipo del coordinatore
Realizzare formalizzazione obiettivo/criteri, selezione capacità e skill, controllo disponibilità e permessi, piano con dipendenze e parallelismo, registrazione stati/prove/decisioni, recupero selettivo e ripianificazione.

## Fase 6 — Scelta e consolidamento del motore
Riprendere la ricerca già avviata su ORCA, LangGraph, Microsoft Agent Framework, Temporal, CrewAI e AutoGen. Esaminare il log Cognitive Continuous Validation, risolvere discrepanze, verificare registry/runtime/dipendenze, eseguire prove riproducibili su Windows e confrontare recupero, persistenza, parallelismo, sicurezza e osservabilità.

Una fase non è completata perché i documenti sono stati scritti o il codice prodotto: servono prove consultabili. Se la verifica non è possibile, lo stato resta NON VERIFICABILE.
