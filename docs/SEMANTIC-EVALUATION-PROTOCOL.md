# Protocollo di valutazione semantica

## Scopo

Verificare separatamente due capacità diverse:
1. classificazione della classe primaria;
2. estrazione di informazioni semantiche strutturate.

Le due prove non sono intercambiabili. Un risultato corretto nella classificazione primaria non dimostra che il modello sappia estrarre capacità, ingressi, uscite, dipendenze, strumenti, rischi e prove.

## Modalità 1 — Classificazione primaria

Il programma `scripts/semantic_evaluation.py` usa la modalità `classification_only` dell'adattatore llama.cpp.

Il modello deve restituire:
- classe primaria: skill, tool, agent, workflow, resource oppure composite;
- livello di fiducia;
- motivazione;
- sintesi.

Il campione contiene 12 materiali, due per classe. Le etichette attese restano nel valutatore e non vengono inviate al modello. La proposta è marcata `partial`, perché non estrae le altre informazioni semantiche.

### Misure

- accuratezza esatta;
- copertura e accuratezza selettiva;
- precisione, richiamo e macro-F1 per classe;
- astensioni;
- tempo medio;
- integrità dei riferimenti alle fonti.

**Precisazione sulla metrica delle fonti:** in questa modalità l'adattatore costruisce i riferimenti a partire dai file ricevuti. La metrica `evidence_reference_integrity` verifica soltanto che percorso e SHA-256 corrispondano agli input. Non misura la fedeltà semantica delle affermazioni del modello e non dimostra che ogni affermazione sia collegata al passaggio sorgente corretto.

## Modalità 2 — Estrazione semantica completa

Il programma `scripts/semantic_extraction_evaluation.py` usa la modalità completa dell'adattatore e il flusso reale `classify_material()`.

Per ogni campione:
1. crea una piccola libreria temporanea;
2. conserva un file sorgente con impronta SHA-256;
3. invoca il flusso di preparazione e analisi;
4. valida la proposta rispetto allo schema;
5. verifica identità, percorsi e impronte delle prove;
6. confronta i campi estratti con i fatti attesi mantenuti nel valutatore.

Il campione iniziale contiene quattro descrizioni sintetiche di skill. Le etichette e i fatti attesi non vengono inseriti nel materiale inviato al modello.

### Misure

- correttezza della classe primaria;
- copertura dei fatti attesi nei campi semantici corrispondenti;
- percentuale di proposte con prove tecnicamente verificate;
- percentuale di affermazioni estratte che contengono riferimenti alle prove;
- numero di proposte complete, parziali e fallite;
- tempo medio per campione.

La copertura dei fatti usa parole-chiave dichiarate nel campione. È una misura esplorativa: non riconosce tutte le parafrasi e non sostituisce la revisione umana del significato. La verifica tecnica delle prove controlla percorsi e impronte, ma non prova da sola la correttezza semantica di ogni affermazione.

## Ambiente di esecuzione

La prova reale usa `Qwen2.5-3B-Instruct-GGUF Q4_K_M` con llama.cpp:
- contesto massimo configurato: 4096 token;
- generazione massima configurata: 1024 token per l'estrazione completa;
- limite di attesa della richiesta: 120 secondi;
- contenitore modello: rete Docker interna, file system in sola lettura, privilegi eliminati, 5 GiB di memoria, 2 CPU e 128 processi;
- contenitore valutatore: file system in sola lettura, privilegi eliminati, 1 GiB di memoria, 1 CPU e 32 processi.

Il rapporto completo è conservato come artefatto GitHub Actions; i riepiloghi versionati sono in `reports/`.

## Interpretazione e limiti

I campioni sono sintetici e pochi. I risultati servono a verificare l'integrazione e individuare errori, non a certificare la generalizzazione su materiali reali. Una proposta valida rispetto allo schema e alle impronte non è automaticamente corretta, approvata o utilizzabile.

Nessuna prova autorizza l'esecuzione del materiale. L'approvazione umana e la verifica funzionale della skill restano passaggi separati.
