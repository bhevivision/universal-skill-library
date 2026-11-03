# Stato della prova GGUF

Il ramo aggiunge un'esecuzione ripetibile del modello Qwen 0.5B GGUF attraverso llama.cpp in un contenitore Docker.

## Controlli configurati

- Rete Docker interna senza accesso esterno.
- Porta pubblicata solo sull'indirizzo locale dell'esecutore.
- File system del contenitore in sola lettura.
- Modello montato in sola lettura.
- Capacità Linux eliminate e blocco dell'acquisizione di nuovi privilegi.
- Limite di 128 processi.
- Limite di memoria di 5 GiB e massimo 2 CPU.
- Cartella temporanea limitata a 256 MiB.
- Contesto di 4096 token e generazione di 1024 token.

## Campione e misure

Sono presenti 12 esempi, due per ciascuna classe primaria. Le etichette attese non vengono inviate al modello. Il rapporto misura accuratezza, precisione, richiamo, macro-F1, coerenza delle prove, astensioni e durata.

## Stato di verifica

L'implementazione del protocollo e del campione è presente nel ramo. L'esecuzione reale è considerata completata soltanto dopo che GitHub Actions ha prodotto il rapporto con le metriche, l'impronta del file GGUF, il digest dell'immagine e i dati del contenitore. Non si presume il successo in anticipo.

Il campione è esplorativo e non costituisce una certificazione statistica o di sicurezza. Il modello è un riferimento tecnico iniziale, non una scelta definitiva per la produzione.
