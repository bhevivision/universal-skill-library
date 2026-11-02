# Contratto di integrazione con la classificazione

## Scopo

Il componente di acquisizione termina dopo aver conservato il materiale e creato la scheda. Il classificatore separato riceve un identificativo e verifica la precisa impronta prima dell'analisi.

## Dati in ingresso al classificatore

La richiesta dovrà contenere versione del contratto, identificativo, stato di acquisizione, tipo originale, percorso locale oppure URI, impronta SHA-256 quando disponibile, provenienza e metadati già noti. Dovrà dichiarare che il materiale è dato non fidato e non deve essere eseguito durante l'analisi.

## Risultato proposto

La risposta dovrà riferirsi allo stesso identificativo e alla stessa impronta e contenere categoria proposta, stato, confidenza, motivazione, evidenze, dipendenze, riferimenti mancanti, limiti e informazioni non determinabili.

## Regole

1. La richiesta è rifiutata se il materiale non esiste o la sua impronta è cambiata.
2. L'analisi non modifica l'originale e non riceve permessi di esecuzione per il solo fatto di classificare.
3. Il risultato è una proposta separata: il classificatore non aggiorna direttamente il catalogo.
4. Il componente di approvazione registra una decisione esplicita, con responsabile dichiarato e motivazione, nella scheda del materiale.
5. Una classificazione come skill non equivale a verifica funzionale né ad autorizzazione all'esecuzione.

## Stato

Il contratto è implementato nella prima versione tramite `scripts/classify_material.py`. Il componente verifica l'impronta, esegue analisi statica limitata e salva proposte in `proposals/`, senza modificare il catalogo. Non è ancora implementato un classificatore semantico universale basato su modelli intelligenti né il flusso separato di approvazione e registrazione nel catalogo.

Per il comportamento effettivo e i limiti della prima versione, vedere `docs/CLASSIFICATION-COMPONENT.md`.
