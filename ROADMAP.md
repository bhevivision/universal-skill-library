# Roadmap del progetto

Stato: il modello strutturale v1 è approvato. Il componente indipendente di acquisizione gestisce copie locali, riferimenti remoti, recupero delle transazioni interrotte e rilevamento dei duplicati. La suite GitHub Actions ha superato 48 test e il validatore su Linux e Windows nel commit `8995b94f398b43ac5a86018ca2b89a72c91d05cb` (run `41516548748`). Resta la prova sul computer Windows dell'utilizzatore. Il classificatore statico e l'approvazione/rifiuto espliciti sono implementati e verificati su Linux e Windows: 65 test superati su Linux e Windows e validatore superato nel commit `1beab4c8b033b420afc3734fced1f18341c3cb0d` (run `41520570818`). Sono stati definiti e verificati il contratto tecnico e lo schema JSON della proposta semantica. È stato implementato il controllo applicativo delle prove: verifica riferimenti, identificativi univoci, appartenenza dei percorsi al materiale acquisito, impronte SHA-256, collegamenti simbolici e intervalli di righe, con ricontrollo finale contro modifiche concorrenti. La verifica conclusiva è superata: 95 test e validatore della libreria superati sia su Linux sia su Windows nel commit `b945f948fd940c584b73c128338a23565b886a5d` (run `41525205201`). Il servizio comune di integrità dei materiali è stato aggiunto e integrato nel classificatore statico, nell'approvazione e nel verificatore semantico; la verifica successiva ha superato 109 test e il validatore su Linux e Windows (run `41530833152`). La chiusura delle lacune del contratto semantico è verificata: stati not_available/failed vincolati a risultati non classificati e privi di affermazioni sul contenuto; richiesta d'ingresso formalizzata con schema JSON e controlli applicativi su percorsi, impronte, contenuti selezionati, limiti e permessi. La suite completa ha superato 183 test e il validatore su Linux e Windows nel commit `25979aaf490efdffe3fcaa271c53c457338c68e8` (run `41545015198`). Restano il motore semantico, l'autenticazione multiutente, la prova sul PC Windows dell'utilizzatore e il coordinatore.

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
- [x] Verificare la prima implementazione tramite GitHub Actions: 40 test superati e validatore superato (run `41513402663`).
- [x] Verificare la versione rafforzata su Linux e Windows: 48 test superati su ciascun sistema e validatore superato (run `41516548748`).
- [x] Aggiungere recupero delle transazioni interrotte sullo stesso computer, con completamento o annullamento prudente.
- [x] Rilevare duplicati di contenuto per file e cartelle, oltre ai duplicati per identificativo.
- [x] Versionare l'algoritmo delle impronte e mantenere la lettura delle impronte storiche.
- [x] Definire il contratto di passaggio dal materiale acquisito al futuro classificatore.
- [ ] Valutare un indice persistente dei duplicati se il volume del catalogo lo renderà necessario.
- [x] Aggiungere l'esecuzione automatica della suite su Windows tramite GitHub Actions.
- [ ] Verificare l'esecuzione sul computer Windows dell'utilizzatore.

Criterio di uscita: un materiale locale può essere copiato e registrato senza modificare la sorgente; un riferimento remoto viene distinto da una copia locale; nessun materiale viene classificato, eseguito o certificato automaticamente durante l'acquisizione.

## Fase 2.5 — Servizio comune di integrità dei materiali
- [x] Definire il contratto tecnico di identità, stato, percorso e impronta.
- [x] Definire lo schema JSON versionato del risultato.
- [x] Implementare `scripts/material_integrity.py` senza eseguire o modificare gli originali.
- [x] Preservare gli algoritmi di impronta correnti e le impronte storiche delle cartelle.
- [x] Separare il servizio comune dal classificatore statico.
- [x] Collegare classificatore, approvazione e verificatore semantico al servizio comune.
- [x] Aggiungere test per identità, duplicati, stati, percorsi, collegamenti simbolici, impronte, riferimenti remoti e schema.
- [x] Verificare su Linux e Windows: 109 test superati su ciascun sistema e validatore superato (run `41530833152`).
- [ ] Verificare il comportamento sul computer Windows dell'utilizzatore.

## Fase 3 — Classificazione dei materiali
- [x] Definire il contratto di richiesta e risposta del futuro classificatore.
- [x] Implementare un classificatore statico limitato, in sola lettura, con controllo dell'impronta e proposta esterna al catalogo.
- [x] Impedire al classificatore di eseguire materiali o aggiornare direttamente i cataloghi approvati.
- [x] Definire il contratto tecnico della richiesta e della risposta semantica, indipendente dal fornitore.
- [x] Definire lo schema JSON versionato della proposta semantica.
- [x] Scrivere test automatici per campi obbligatori, categorie, stati, prove, impronte e autorizzazione all'analisi remota.
- [x] Implementare il controllo applicativo dei riferimenti alle prove, dell'identità e delle impronte dei file esaminati, senza eseguire i materiali.
- [x] Aggiungere test per riferimenti mancanti, identificativi duplicati, impronte errate, percorsi esterni, attraversamento di cartelle, collegamenti simbolici e intervalli di righe.
- [x] Eseguire e verificare i nuovi test su Linux e Windows tramite GitHub Actions: 95 test superati su ciascun sistema e validatore superato (run `41525205201`).
- [x] Vincolare nello schema gli stati `not_available` e `failed`: classificazione `unclassified`, confidenza bassa, nessuna affermazione semantica e sole prove di metadati del catalogo.
- [x] Richiedere limiti espliciti per ogni risultato `partial`.
- [x] Definire lo schema JSON della richiesta al motore, con campi obbligatori, limiti quantitativi e permessi di sicurezza non modificabili.
- [x] Aggiungere controlli applicativi per percorsi canonici sotto `intake/`, corrispondenza tra file autorizzati e contenuti selezionati, impronte, dimensioni e limiti complessivi.
- [x] Verificare la chiusura contrattuale su Linux e Windows: 183 test superati su ciascun sistema e validatore superato (run `41545015198`).
- [ ] Implementare il motore semantico locale sostituibile, con stato esplicito not_available se non configurato.
- [ ] Ampliare gli analizzatori per formati diversi e introdurre prove specifiche per ciascun formato.
- [ ] Implementare il flusso separato di revisione, approvazione e registrazione della proposta nel catalogo.
- [ ] Verificare il componente con prove automatiche e su Windows.

## Fase 4 — Inventario operativo delle skill esistenti
Solo dopo che la procedura di acquisizione e conservazione è verificata:
- UNLAZY: registrare riferimenti mancanti e dipendenze.
- Archivista: registrare il riferimento mancante e le sezioni assenti.
- Find Skills: verificare istruzioni, comandi e fonti.
- Canva KDP: conservare e descrivere il file disponibile; è di 36 byte e appare danneggiato, non ricostruirlo come se fosse integro.

Regola: preservare esattamente i materiali originali. Non riscrivere, correggere o adattare preventivamente. Acquisizione, documentazione, verifica e approvazione all'uso sono passaggi distinti.

## Fase 5 — Interoperabilità
Provare skill non sensibili su Claude Code e Codex e, se accessibile, su un'altra piattaforma. Separare contenuto canonico e adattamenti. Registrare prove, differenze e limiti.

## Fase 6 — Prototipo del coordinatore
Realizzare formalizzazione obiettivo/criteri, selezione capacità e skill, controllo disponibilità e permessi, piano con dipendenze e parallelismo, registrazione stati/prove/decisioni, recupero selettivo e ripianificazione.

## Fase 7 — Scelta e consolidamento del motore
Riprendere la ricerca già avviata su ORCA, LangGraph, Microsoft Agent Framework, Temporal, CrewAI e AutoGen. Esaminare il log Cognitive Continuous Validation, risolvere discrepanze, verificare registry/runtime/dipendenze, eseguire prove riproducibili su Windows e confrontare recupero, persistenza, parallelismo, sicurezza e osservabilità.

Una fase non è completata perché i documenti sono stati scritti o il codice prodotto: servono prove consultabili. Se la verifica non è possibile, lo stato resta NON VERIFICABILE.
