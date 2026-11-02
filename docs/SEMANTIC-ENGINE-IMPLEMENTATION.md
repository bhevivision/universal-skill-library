# Prima implementazione del motore semantico

## Stato

Il modulo `scripts/semantic_engine.py` introduce il primo confine eseguibile del motore semantico. Non è ancora un classificatore semantico completo e non include un modello locale.

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

## Cosa manca

1. Costruzione automatica della richiesta a partire da `prepare_material()`.
2. Controllo dell'impronta del catalogo e del materiale nel flusso integrato.
3. Adattatore per un modello semantico locale effettivamente disponibile.
4. Isolamento dell'adattatore, limiti di tempo reali e gestione delle risorse.
5. Verifica applicativa delle prove e salvataggio atomico in `proposals/`.
6. Prove di qualità semantica su materiali con risultati attesi.

Fino al completamento di questi punti, il motore è un primo nucleo sostituibile, non una funzione di classificazione pronta all'uso.
