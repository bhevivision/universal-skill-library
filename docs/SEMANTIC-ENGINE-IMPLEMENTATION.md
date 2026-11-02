# Prima implementazione del motore semantico

## Stato

Il modulo `scripts/semantic_engine.py` fornisce il confine dell'analizzatore; `scripts/semantic_pipeline.py` collega preparazione, richiesta, analisi, verifica applicativa e salvataggio esclusivo. Non è ancora presente un modello semantico locale reale.

## Interfaccia

Il punto d'ingresso è:

```python
run_semantic_engine(request, analyzer=None, catalog_sha256=None)
```

La funzione:
1. controlla la richiesta con `validate_semantic_request()`;
2. richiede l'impronta SHA-256 del catalogo corrente;
3. congela una copia della richiesta validata e ne calcola l'impronta;
4. se non è fornito un analizzatore, restituisce una proposta `not_available`, `unclassified`, senza affermazioni sul contenuto;
5. se è fornito un analizzatore, invoca il metodo `analyze(request)` e valida la struttura restituita rispetto allo schema della proposta;
6. se l'adattatore fallisce o restituisce una proposta non valida, produce un risultato `failed` privo di affermazioni semantiche.

Un adattatore locale deve esporre:
- `analyzer_id` e `version` (facoltativi, con valori sostitutivi espliciti);
- `analyze(request)`, che restituisce i campi della proposta semantica senza la sezione `analyzer`.

L'adattatore riceve una copia della richiesta: non può alterare l'oggetto validato dal chiamante né l'impronta registrata per l'ingresso.

## Impronte

L'impronta di ingresso è SHA-256 della rappresentazione JSON canonica della richiesta: chiavi ordinate, separatori compatti e codifica UTF-8.

L'impronta di uscita è SHA-256 della proposta canonica escluso il solo campo `analyzer.output_sha256`, per evitare un riferimento circolare. Questa regola deve restare stabile per la versione del contratto.

## Confini di sicurezza

- La richiesta è validata prima dell'invocazione.
- Il contenuto resta dato non fidato e non deve essere seguito come istruzione.
- L'adattatore è codice fidato: questa prima implementazione **non** lo esegue in un ambiente isolato e non può impedirgli tecnicamente di usare rete, disco o processi.
- Non sono implementati adattatori remoti; l'autorizzazione esterna resta falsa.
- La funzione non scrive file, proposte o cataloghi.
- La validazione dello schema non sostituisce `validate_semantic_proposal(root, proposal)`: il chiamante dovrà verificare le prove contro i file acquisiti e le impronte correnti prima di salvare.

## Flusso integrato disponibile

Il punto d'ingresso è:

```python
classify_material(root, material_id, analyzer=None, request_id=None)
```

Il flusso:
1. chiama `prepare_material()` in sola lettura;
2. interrompe l'operazione se la preparazione è `blocked` o `failed`;
3. costruisce automaticamente la richiesta dal materiale preparato, includendo soltanto file testuali ammessi e i limiti già definiti;
4. marca esplicitamente il contenuto come dato non fidato e nega accesso a file system, rete, processi, credenziali e cataloghi;
5. non invoca un analizzatore se non è stato preparato alcun contenuto;
6. esegue l'analizzatore configurato o restituisce `not_available`;
7. converte in `partial` una classificazione basata su una preparazione parziale;
8. verifica schema, identità, riferimenti, percorsi e impronte tramite `validate_semantic_proposal()`;
9. ricontrolla l'impronta del catalogo e salva la proposta senza sovrascrivere file esistenti.

Le proposte vengono salvate in `proposals/`, separate dai cataloghi approvati. Il salvataggio non approva la classificazione e non abilita l'esecuzione del materiale. Se la verifica delle prove fallisce, la proposta non viene salvata.

Il risultato del flusso espone `evidence_verified: true` soltanto dopo i controlli applicativi e `approval_required: true` sempre. La prima proprietà attesta esclusivamente la coerenza delle prove e delle impronte; **non** dimostra che la classificazione sia semanticamente corretta, che la skill funzioni o che sia approvata. Il file viene preparato in un temporaneo nella stessa cartella e pubblicato con creazione esclusiva atomica; una proposta già presente non viene sovrascritta.

## Modello locale: decisione ancora aperta

L'interfaccia è indipendente dal fornitore e consente di collegare un adattatore locale. Non è stato scelto né incluso un modello reale. La scelta del formato e del motore di esecuzione dipende dalle risorse dell'ambiente che ospiterà il modello (memoria, processore, eventuale acceleratore grafico e sistema operativo). GitHub Actions esegue i test automatici, ma non è un ambiente persistente di inferenza locale e non dimostra che un modello possa essere eseguito sul computer personale, oggi non disponibile.

Non si scaricano modelli pesanti nel repository e non si aggiungono dipendenze obbligatorie per un modello non ancora scelto. Il prossimo passo è definire un adattatore per un runtime locale con versione fissata, percorso del modello configurato, limiti effettivi, uscita JSON controllata e test d'integrazione separati dai test ordinari.

## Limiti e lavori aperti

1. Integrare un modello semantico locale realmente eseguibile, dopo aver definito l'ambiente di destinazione.
2. Isolare l'adattatore dal file system, dalla rete e dall'esecuzione di comandi; il contratto attuale esprime i permessi richiesti ma non costituisce sandbox.
3. Applicare un limite di tempo effettivo al processo d'inferenza e gestire memoria e annullamento.
4. Aggiungere un insieme di materiali campione con classificazioni attese e misure di precisione, richiamo, coerenza e qualità delle prove.
5. Ampliare la copertura dei formati oltre i testi già supportati da `material_preparer.py`.

Fino al completamento di questi punti, il flusso integrato è utilizzabile per produrre proposte `not_available` o per verificare adattatori di prova; non è ancora un classificatore autonomo pronto all'uso.
