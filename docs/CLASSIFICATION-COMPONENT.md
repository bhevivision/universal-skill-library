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
- Legge soltanto file testuali con estensioni ammesse, codifica UTF-8 e limiti massimi di dimensione e numero di file.
- Non estrae archivi, non visita riferimenti remoti e non esegue codice o comandi.
- Applica indicatori dichiarati e ripetibili per proporre una categoria: `skill`, `tool`, `agent`, `workflow`, `resource`, `composite` oppure `unclassified`.
- Registra fonti, estratti limitati, motivazione, confidenza, elementi non analizzati e limiti.

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

La proposta non è una classificazione approvata. Una persona o un futuro componente autorizzato dovrà:
1. verificare che identificativo e impronta corrispondano ancora al materiale;
2. esaminare prove, motivazione, incertezze e limiti;
3. approvare, respingere o chiedere un'analisi diversa;
4. solo dopo l'approvazione, registrare separatamente la classificazione nel catalogo.

La procedura di approvazione automatica e l'inserimento nel catalogo non fanno parte di questo componente.

## Limiti e sicurezza

- I materiali sono sempre trattati come dati non fidati, mai come istruzioni da seguire.
- Il codice individuato viene letto come testo, mai eseguito.
- La presenza di una struttura simile a una skill non dimostra che la skill funzioni.
- Non vengono installate dipendenze né verificati strumenti o piattaforme.
- La confidenza è un'indicazione euristica, non una probabilità statistica calibrata.
- Archivi, riferimenti remoti, file binari e formati non supportati restano parzialmente o totalmente non esaminati.
