# Roadmap del progetto

Stato: il modello strutturale v1 è approvato. I controlli e i 19 test già presenti riguardano la precedente struttura basata sul profilo Agent Skills; non dimostrano ancora la copertura dell'acquisizione eterogenea. Il coordinatore non è implementato.

## Fase 0 — Conservazione e modello strutturale
- [x] Verificare repository, ramo e file correnti.
- [x] Recuperare README e contenuti delle skill presenti.
- [x] Consultare la specifica Agent Skills ufficiale.
- [x] Documentare architettura, glossario, modello, decisioni e questioni aperte.
- [x] Approvare il modello concettuale v1, inclusa l'acquisizione di pacchetti non ancora classificati.
- [x] Aggiornare i documenti architetturali per riflettere le decisioni confermate.
- [ ] Verificare formalmente coerenza e completezza della documentazione aggiornata.

Criterio di uscita: modello e principi coerenti tra ARCHITECTURE.md, STRUCTURAL-MODEL.md, DECISIONS.md e docs/LIBRARY-STRUCTURE.md.

## Fase 1 — Inventario e criteri della libreria
- [x] Analizzare i materiali già presenti senza modificarli.
- [x] Definire i dati minimi per confrontare e selezionare skill.
- [x] Definire la distinzione tra materiale acquisito, classificazione e skill utilizzabile.
- [ ] Definire lo schema della scheda descrittiva esterna.
- [ ] Definire il trattamento di file singoli, cartelle, archivi, pacchetti compositi e riferimenti remoti.
- [ ] Stabilire provenienza, impronta, versionamento e gestione dei duplicati.

## Fase 2 — Acquisizione e validazione eterogenea
- [ ] Separare controlli generali di acquisizione e integrità dai controlli specifici dei profili.
- [ ] Rendere facoltativi gli analizzatori di formato; consentire la conservazione di formati sconosciuti.
- [ ] Aggiornare cataloghi e schemi per record parziali e classificazioni provvisorie.
- [ ] Aggiornare il validatore: nessun requisito universale di SKILL.md.
- [ ] Aggiungere test per file, cartelle, archivi, pacchetti compositi, riferimenti remoti, formati sconosciuti e acquisizioni incomplete.
- [ ] Verificare che originale e impronta non cambino dopo analisi e adattamento.
- [ ] Eseguire test locali e GitHub Actions e conservare le prove.

Criterio di uscita: un materiale non riconosciuto può essere acquisito e conservato; il sistema non lo presenta come skill utilizzabile senza classificazione e verifiche adeguate.

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