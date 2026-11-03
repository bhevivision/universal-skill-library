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

## Citazioni testuali e controllo delle affermazioni

Ogni affermazione semantica deve contenere `evidence_refs` e `evidence_quotes`. Ogni citazione ha la forma:

```json
{
  "evidence_ref": "ev.source-001",
  "quote": "Testo letterale copiato dal materiale sorgente."
}
```

Il controllo automatico:
- accetta risposte JSON pure, JSON in blocchi Markdown o un singolo oggetto JSON circondato da testo;
- rifiuta JSON troncato, chiavi duplicate, più oggetti ambigui e contenuti malformati;
- richiede citazioni per classificazione, capacità, ingressi, uscite, condizioni d'uso, dipendenze, strumenti, rischi e contraddizioni;
- verifica che ogni riferimento esista e che ogni citazione sia una sottostringa letterale del file UTF-8 indicato;
- verifica SHA-256 del file e che percorso e impronta corrispondano a un file selezionato nella richiesta;
- rifiuta percorsi fuori da `intake/`, attraversamenti di cartelle e collegamenti simbolici;
- rifiuta l'intera proposta se anche una sola affermazione è priva di prove o usa una citazione non valida; la proposta non viene salvata.

`completed` è accettato soltanto quando schema, identità, prove, citazioni e impronte sono coerenti e non restano riferimenti mancanti, contraddizioni, incognite o limiti. In caso contrario l'esito resta parziale o viene rifiutato.

La presenza letterale della citazione dimostra che il passaggio esiste nel file verificato; non dimostra da sola che il passaggio implichi logicamente l'affermazione. La qualità dell'interpretazione richiede ancora valutazione semantica indipendente e revisione umana.

## Stato

Il classificatore statico è implementato tramite `scripts/classify_material.py` e salva proposte separate in `proposals/`. Il flusso di revisione e approvazione esplicita è implementato tramite `scripts/classification_approval.py`; aggiorna la classificazione del materiale e registra la decisione, ma non crea automaticamente una skill operativa in `catalog/skills.json`. Il motore semantico sostituibile è implementato in `scripts/semantic_engine.py` e collegato al preparatore tramite `scripts/semantic_pipeline.py`; l'adattatore llama.cpp è in `scripts/llama_cpp_adapter.py`. La valutazione GGUF precedente alle citazioni obbligatorie del 3 novembre 2026 aveva registrato 4 campioni falliti su 4. La nuova esecuzione completa è attivata dalla CI per questa modifica e il suo rapporto sarà il riferimento per stabilire se il motore è accettabile; fino all'esito positivo non deve essere considerato pronto per uso operativo.

Per il comportamento effettivo e i limiti della prima versione, vedere `docs/CLASSIFICATION-COMPONENT.md`.
