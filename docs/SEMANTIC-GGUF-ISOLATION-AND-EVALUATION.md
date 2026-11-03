# Esecuzione isolata del modello GGUF e valutazione semantica

## Obiettivo e stato

Questo protocollo aggiunge una prova ripetibile su un vero modello GGUF senza richiedere il computer personale. La prova viene avviata manualmente in un esecutore GitHub Actions Ubuntu. Il modello iniziale è Qwen/Qwen2.5-0.5B-Instruct-GGUF:Q4_K_M, scelto come prova tecnica leggera, non come scelta definitiva per la qualità del classificatore.

Il flusso usa l'immagine ufficiale ghcr.io/ggml-org/llama.cpp:server. Il file GGUF viene scaricato nell'esecutore prima di avviare il contenitore; il processo del modello non deve scaricare file o contattare servizi esterni durante l'inferenza.

## Isolamento e limiti applicati

Il contenitore viene avviato con:
- rete Docker interna, senza uscita verso reti esterne;
- pubblicazione della porta esclusivamente su 127.0.0.1 dell'esecutore;
- file system radice in sola lettura;
- modello montato in sola lettura;
- capacità Linux eliminate;
- no-new-privileges;
- massimo 128 processi;
- memoria massima 5 GiB, senza swap aggiuntivo;
- massimo 2 CPU;
- cartella temporanea limitata a 256 MiB, senza esecuzione, setuid o dispositivi;
- contesto massimo 4096 token e generazione massima 1024 token.

Il processo viene terminato insieme al lavoro GitHub Actions. Il rapporto registra configurazione del contenitore, digest dell'immagine, impronta SHA-256 del modello, stato, eventuale terminazione per memoria e statistiche osservate.

Limiti residui: l'esecutore GitHub è un ambiente temporaneo condiviso dal servizio GitHub; non è una macchina dedicata o una certificazione di sicurezza formale. Il runtime llama.cpp e l'immagine Docker sono componenti software da mantenere aggiornati. La rete interna e la pubblicazione loopback devono essere verificate nel lavoro reale. I limiti CPU/memoria sono limiti del contenitore, non misure di prestazione del computer personale.

## Campione di valutazione

Il file evaluation/semantic-classification-samples.json contiene dodici esempi scritti appositamente, due per ciascuna classe primaria: skill, tool, agent, workflow, resource e composite.

Le etichette attese restano nel file di valutazione e non vengono incluse nelle richieste al modello. Ogni richiesta contiene un solo materiale, il testo, il percorso e la relativa impronta SHA-256.

Il programma scripts/semantic_evaluation.py misura:
- accuratezza esatta complessiva;
- precisione, richiamo e F1 per classe;
- macro-F1;
- fedeltà delle prove (riferimenti e impronta restituiti coerenti con il testo inviato);
- numero di astensioni;
- durata per esempio ed errori.

La fedeltà delle prove non equivale alla correttezza semantica: un modello può citare correttamente il testo e classificarlo male. L'insieme è iniziale e piccolo, quindi i risultati sono indicativi, non una certificazione statistica. Prima di fissare una soglia di accettazione servono esempi indipendenti più numerosi, casi ambigui, materiali avversari e una revisione umana delle etichette.

## Avvio manuale

1. Aprire la scheda Actions del repository.
2. Selezionare Valutazione modello GGUF isolato.
3. Premere Run workflow.
4. Selezionare il ramo semantic-evaluation-isolation-v1.
5. Premere il pulsante verde Run workflow.
6. Al termine, aprire il lavoro e scaricare l'elemento semantic-gguf-evaluation.

Il rapporto e i registri sono conservati come elemento scaricabile per 30 giorni. La prova reale è completata soltanto quando il lavoro termina con esito positivo e il rapporto contiene le metriche e le impronte.

## Interpretazione

- exact_accuracy: quota di classi primarie identiche alle etichette attese.
- macro_f1: media non pesata degli F1 delle classi rappresentate.
- evidence_fidelity: quota di risposte che citano il percorso e SHA-256 del campione effettivamente inviato.
- abstention_count: numero di esempi per i quali il modello non ha prodotto una classe prevista.

Non si considera superato il classificatore soltanto perché l'inferenza restituisce JSON valido. La qualità va valutata separatamente e non produce approvazione automatica delle skill.
