# Roadmap del progetto

Stato: il modello strutturale v1 è approvato. Acquisizione, integrità, classificazione statica, approvazione esplicita e contratti della classificazione semantica sono implementati e verificati tramite GitHub Actions. La suite precedente ha superato 183 test e il validatore su Ubuntu e Windows nel run `41545326945`. La verifica sul computer Windows personale è **NON APPLICABILE**: il precedente computer è fuori uso, non esiste una copia locale del repository e il lavoro prosegue direttamente su GitHub. Questa limitazione è documentata in `docs/WINDOWS-LOCAL-VERIFICATION.md`; non blocca lo sviluppo. Il primo motore semantico sostituibile è in corso di realizzazione: esiste un'interfaccia per adattatori locali e, se nessun adattatore è configurato, il risultato esplicito è `not_available`. Non è ancora presente un modello locale, né l'integrazione completa di preparazione, salvataggio e verifica delle proposte. L'inventario dei quattro materiali in `personalizzazione/` resta preliminare e non equivale ad acquisizione ufficiale. Restano inoltre gli analizzatori per altri formati, l'inventario operativo, l'interoperabilità reale, il coordinatore e la scelta/consolidamento del motore di orchestrazione.

## Fase 0 — Conservazione e modello strutturale
- [x] Verificare repository, ramo e file correnti.
- [x] Recuperare README e contenuti delle skill presenti.
- [x] Consultare la specifica Agent Skills ufficiale.
- [x] Documentare architettura, glossario, modello, decisioni e questioni aperte.
- [x] Approvare il modello concettuale v1, inclusa l'acquisizione di pacchetti non ancora classificati.
- [x] Aggiornare i documenti architetturali per riflettere le decisioni confermate.
- [x] Verificare formalmente coerenza e completezza della documentazione aggiornata rispetto ai componenti implementati; correggere le descrizioni obsolete e distinguere ciò che è implementato da ciò che resta futuro (ramo `documentation-inventory-closure`).

## Fase 1 — Inventario e criteri della libreria
- [x] Analizzare i materiali già presenti senza modificarli.
- [x] Definire i dati minimi per confrontare e selezionare skill.
- [x] Definire la distinzione tra materiale acquisito, classificazione e skill utilizzabile.
- [x] Definire lo schema della scheda descrittiva esterna.
- [x] Definire il trattamento di file singoli, cartelle, archivi, pacchetti compositi e riferimenti remoti.
- [x] Implementare provenienza di acquisizione, impronte SHA-256, versionamento degli algoritmi e rilevamento dei duplicati per i tipi supportati.
- [ ] Definire il ciclo di vita delle versioni successive dello stesso materiale e le migrazioni degli schemi dei record.
- [ ] Valutare un indice persistente dei duplicati se il volume del catalogo lo renderà necessario.

## Fase 2 — Acquisizione e validazione eterogenea
- [x] Separare controlli generali di acquisizione e integrità dai controlli specifici dei profili.
- [x] Consentire la conservazione e registrazione di formati sconosciuti; gli analizzatori restano facoltativi.
- [x] Aggiungere il catalogo dei materiali e lo schema della scheda descrittiva esterna.
- [x] Aggiornare il validatore: SKILL.md è controllato soltanto per il profilo Agent Skills.
- [x] Aggiungere test per file, cartelle, archivi, pacchetti e acquisizioni incomplete/non classificate.
- [x] Verificare l'impronta degli originali e rilevare modifiche successive all'acquisizione.
- [x] Implementare copia locale, scheda descrittiva, impronta, controlli di collisione e registrazione di riferimenti remoti.
- [x] Aggiungere recupero delle transazioni interrotte sullo stesso computer, con completamento o annullamento prudente.
- [x] Rilevare duplicati di contenuto per file e cartelle, oltre ai duplicati per identificativo.
- [x] Versionare l'algoritmo delle impronte e mantenere la lettura delle impronte storiche.
- [x] Definire il contratto di passaggio dal materiale acquisito al futuro classificatore.
- [x] Aggiungere l'esecuzione automatica della suite su Windows tramite GitHub Actions.
- [ ] Progettare un percorso controllato di acquisizione dei materiali già presenti nel repository tramite GitHub Actions, senza richiedere una copia locale personale.

Criterio di uscita: un materiale può essere copiato e registrato senza modificare la sorgente; un riferimento remoto viene distinto da una copia locale; nessun materiale viene classificato, eseguito o certificato automaticamente durante l'acquisizione.

## Fase 2.5 — Servizio comune di integrità dei materiali
- [x] Definire il contratto tecnico di identità, stato, percorso e impronta.
- [x] Definire lo schema JSON versionato del risultato.
- [x] Implementare `scripts/material_integrity.py` senza eseguire o modificare gli originali.
- [x] Preservare gli algoritmi di impronta correnti e le impronte storiche delle cartelle.
- [x] Separare il servizio comune dal classificatore statico.
- [x] Collegare classificatore, approvazione e verificatore semantico al servizio comune.
- [x] Aggiungere test per identità, duplicati, stati, percorsi, collegamenti simbolici, impronte, riferimenti remoti e schema.
- [x] Verificare su Linux e Windows tramite GitHub Actions.
- [ ] Verifica sul computer Windows personale: **NON APPLICABILE** finché il computer precedente resta fuori uso; non blocca il progetto.

## Fase 3 — Classificazione dei materiali
- [x] Definire il contratto tecnico della richiesta e della risposta semantica, indipendente dal fornitore.
- [x] Definire gli schemi JSON versionati e i relativi test.
- [x] Implementare il controllo applicativo delle prove, dell'identità e delle impronte.
- [x] Vincolare gli stati `not_available` e `failed` a risultati non classificati e privi di affermazioni sul contenuto.
- [x] Formalizzare la richiesta al motore con limiti e permessi di sicurezza non modificabili.
- [ ] Implementare il motore semantico locale sostituibile.
  - [x] Creare il confine eseguibile e l'interfaccia per adattatori locali.
  - [x] Restituire `not_available` se nessun adattatore è configurato.
  - [ ] Integrare preparazione del materiale, costruzione della richiesta e controllo delle impronte nel flusso unico.
  - [ ] Integrare un analizzatore semantico locale effettivamente disponibile.
  - [ ] Validare le prove con `validate_semantic_proposal` prima del salvataggio.
  - [ ] Salvare le proposte separatamente, senza aggiornare i cataloghi approvati.
  - [ ] Aggiungere test di sicurezza, timeout, errori, risposte malformate e qualità semantica.
- [ ] Ampliare gli analizzatori per formati diversi e introdurre prove specifiche per ciascun formato.
- [ ] Collegare la classificazione approvata al processo controllato di ammissione nel catalogo operativo delle skill.
- [ ] Verificare il componente tramite GitHub Actions su Linux e Windows. La prova sul computer personale resta separata e non applicabile al momento.

## Fase 4 — Inventario operativo delle skill esistenti
È già stata eseguita un'ispezione statica preliminare, documentata in `docs/EXISTING-SKILLS-INVENTORY.md`. L'acquisizione ufficiale non è ancora avvenuta. Il precedente vincolo della verifica sul PC personale è stato rimosso: occorre progettare un percorso di acquisizione eseguibile su GitHub per i materiali già presenti nel repository.
- UNLAZY: recuperare e verificare i tre riferimenti mancanti.
- Archivista: recuperare e verificare `reference/regole-complete.md`.
- Find Skills: verificare fonte, versione, dipendenze e comandi con effetti sull'ambiente.
- Canva KDP: file di 36 byte apparentemente danneggiato; conservarlo senza modificarlo e recuperare l'originale soltanto se disponibile.

Regola: preservare esattamente i materiali originali. Non riscrivere, correggere o adattare preventivamente. Acquisizione, documentazione, verifica e approvazione all'uso sono passaggi distinti.

## Fase 5 — Interoperabilità
Provare skill non sensibili su Claude Code e Codex e, se accessibile, su un'altra piattaforma. Separare contenuto canonico e adattamenti. Registrare prove, differenze e limiti. Le verifiche che richiedono applicazioni installate su un computer personale restano non verificabili finché tale ambiente non sarà disponibile.

## Fase 6 — Prototipo del coordinatore
Realizzare formalizzazione obiettivo/criteri, selezione capacità e skill, controllo disponibilità e permessi, piano con dipendenze e parallelismo, registrazione stati/prove/decisioni, recupero selettivo e ripianificazione.

## Fase 7 — Scelta e consolidamento del motore di orchestrazione
Riprendere la ricerca già avviata su ORCA, LangGraph, Microsoft Agent Framework, Temporal, CrewAI e AutoGen. Esaminare il log Cognitive Continuous Validation, risolvere discrepanze, verificare registry/runtime/dipendenze e confrontare recupero, persistenza, parallelismo, sicurezza e osservabilità. Le prove su Windows remoto tramite GitHub Actions non sostituiscono quelle su un'installazione Windows personale.

Una fase non è completata perché i documenti sono stati scritti o il codice prodotto: servono prove consultabili. Se la verifica non è possibile, lo stato resta NON VERIFICABILE.
