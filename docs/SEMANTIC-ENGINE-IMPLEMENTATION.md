# Prima implementazione del motore semantico

## Stato

Il modulo `scripts/semantic_engine.py` fornisce il confine dell'analizzatore; `scripts/semantic_pipeline.py` collega preparazione, richiesta, analisi, verifica applicativa e salvataggio esclusivo. È disponibile l'adattatore `llama.cpp` e la modalità `classification_only` è stata verificata con un vero modello GGUF su GitHub Actions. Questa prova copre la classe primaria e restituisce una proposta `partial`; l'estrazione semantica completa resta da verificare.

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

## Collegamento a un modello locale

È stato scelto `llama.cpp` come primo obiettivo d'integrazione, non come vincolo per tutta la libreria. Il progetto supporta modelli GGUF, esecuzione locale su CPU e accelerazione su più tipi di GPU, e mette a disposizione `llama-server` con interfaccia HTTP compatibile con le richieste di completamento chat. La documentazione ufficiale descrive anche l'uscita JSON vincolata da schema. Riferimenti: [repository ufficiale llama.cpp](https://github.com/ggml-org/llama.cpp) e [documentazione dell'API strutturata](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

Il modulo `scripts/llama_cpp_adapter.py` implementa il collegamento:
- usa soltanto un indirizzo IP di loopback (127.0.0.1 o ::1);
- disabilita i proxy di sistema e rifiuta i reindirizzamenti;
- imposta un limite di attesa e una dimensione massima della risposta;
- invia contenuti come dati non fidati e non abilita strumenti;
- richiede un risultato JSON strutturato;
- restituisce il risultato al motore, che ricostruisce i metadati fidati e applica i controlli di schema e delle prove.

L'adattatore è stato verificato sia con un server HTTP simulato sia con un vero modello GGUF. La prova reale ha usato `Qwen/Qwen2.5-3B-Instruct-GGUF` in quantizzazione `Q4_K_M`, eseguito con llama.cpp su GitHub Actions. Nel campione iniziale di 12 materiali la modalità di classificazione primaria ha ottenuto accuratezza esatta 1,00, copertura 1,00 e macro-F1 1,00, con tempo medio 26,711 secondi per materiale. L'integrità dei riferimenti alle fonti è 1,00, ma misura soltanto la corrispondenza tecnica dei riferimenti generati dall'adattatore con gli input: non misura la fedeltà semantica delle affermazioni del modello. Impronta GGUF: `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`. Il rapporto completo e le prove sono collegati in `docs/SEMANTIC-EVALUATION-RESULTS.md` e nell'artefatto del run `41632778918`. La prova è stata eseguita su un runner remoto, non sul computer personale fuori uso. Il campione contiene soltanto due esempi per classe e non certifica la generalizzazione. La modalità `classification_only` non estrae capacità, interfacce, dipendenze, strumenti o rischi: produce intenzionalmente una proposta `partial`. La modalità completa dell'adattatore deve ancora essere verificata con un modello reale. Non si inseriscono modelli pesanti nel repository e non si scaricano modelli durante i test automatici ordinari.

La scelta del modello GGUF specifico resta aperta fino a quando sarà noto l'hardware disponibile (memoria, processore, scheda grafica e memoria grafica). L'adattatore non dipende dal nome del modello: lo riceve come configurazione.

## Limiti e lavori aperti

1. Verificare sul computer di destinazione la compatibilità, la memoria e le prestazioni del modello: la prova corrente è su GitHub Actions e non sostituisce quella locale.
2. Verificare la modalità completa di analisi semantica con un vero GGUF: la prova attuale copre soltanto la classe primaria e restituisce una proposta `partial`.
3. Estendere le prove di isolamento e dei limiti operativi sotto carico, inclusi annullamento, consumo massimo, timeout e test avversari. La prima esecuzione Docker con rete interna, file system in sola lettura, privilegi eliminati e limiti CPU/memoria/processi è stata verificata.
4. Ampliare il campione oltre i 12 materiali iniziali, aggiungendo casi ambigui, incompleti, ostili e materiali reali indipendenti; il 100% attuale è un risultato esplorativo, non una certificazione.
5. Ampliare la copertura dei formati oltre i testi già supportati da `material_preparer.py`.

Fino al completamento di questi punti, il flusso integrato è utilizzabile per produrre proposte `not_available` o per verificare adattatori di prova; non è ancora un classificatore autonomo pronto all'uso.
