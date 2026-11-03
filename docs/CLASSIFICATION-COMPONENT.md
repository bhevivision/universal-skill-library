# Componente indipendente di classificazione

## Scopo e confini

Il classificatore riceve l'identificativo di un materiale già acquisito, controlla che la copia conservata corrisponda ancora all'impronta registrata, esamina soltanto contenuti testuali ammessi e produce una proposta esterna. Non acquisisce, non modifica l'originale, non aggiorna i cataloghi approvati, non esegue programmi e non certifica il funzionamento.

L'acquisizione e la classificazione sono componenti separati: il classificatore legge il catalogo dei materiali come ingresso, ma salva i risultati in `proposals/`, senza scrivere in `catalog/materials.json`, `catalog/skills.json` o negli altri cataloghi.

## Uso

Dalla cartella principale della libreria:

    python scripts/classify_material.py --material-id acq.nome-materiale --proposal-id class.nome-proposta

La proposta viene salvata in `proposals/class.nome-proposta.json`. Gli identificativi sono indipendenti da quelli di acquisizione.

## Analisi effettuata nella prima versione

- Controlla che il materiale esista, sia in stato `preserved` e mantenga l'impronta SHA-256 registrata.
- Rifiuta collegamenti simbolici.
- Usa `material_preparer.py` come percorso comune di preparazione e lettura, con estensioni ammesse, UTF-8, limiti per file e complessivi e controllo d'integrità finale.
- L'inventario è limitato a 10.000 elementi e 64 livelli; il superamento blocca la preparazione senza restituire contenuti parziali.
- Non estrae archivi, non visita riferimenti remoti e non esegue codice o comandi.
- Applica indicatori dichiarati e ripetibili per proporre una categoria: `skill`, `tool`, `agent`, `workflow`, `resource`, `composite` oppure `unclassified`.
- Registra percorsi e impronte dei file esaminati, senza copiare estratti del contenuto nella proposta; registra motivazione, confidenza, elementi non analizzati e limiti.

La classificazione è una proposta preliminare basata su analisi statica e regole. Non è ancora un classificatore semantico universale basato su modelli intelligenti. Se gli indizi non bastano, propone `unclassified` o una categoria a bassa confidenza invece di inventare informazioni.

## Forma della proposta

Ogni proposta contiene:
- versione del formato e identificativo univoco;
- stato `pending_approval`;
- identificativo e impronta del materiale esaminato;
- categoria proposta, confidenza e motivazione;
- prove consultabili con percorso del file;
- dipendenze e riferimenti mancanti, anche quando non sono determinabili;
- informazioni sconosciute e limiti dell'analisi;
- metodo e quantità dei file esaminati.

## Approvazione e catalogazione

La proposta non è una classificazione approvata. Il componente separato `scripts/classification_approval.py` consente di approvare o respingere una proposta. Prima della decisione verifica di nuovo l'impronta e registra esito, responsabile dichiarato, motivazione e identificativo della proposta nella scheda del materiale. I dettagli sono in `docs/CLASSIFICATION-APPROVAL.md`.

L'approvazione aggiorna soltanto la classificazione del materiale. Non crea una voce in `catalog/skills.json` e non abilita l'esecuzione. La proposta originale resta conservata come prova del suggerimento iniziale.

## Limiti e sicurezza

- I materiali sono sempre trattati come dati non fidati, mai come istruzioni da seguire.
- Il codice individuato viene letto come testo, mai eseguito.
- La presenza di una struttura simile a una skill non dimostra che la skill funzioni.
- Non vengono installate dipendenze né verificati strumenti o piattaforme.
- La confidenza è un'indicazione euristica, non una probabilità statistica calibrata.
- Archivi, riferimenti remoti, file binari e formati non supportati restano parzialmente o totalmente non esaminati.
