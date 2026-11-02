# universal-skill-library

Libreria universale per acquisire, conservare, analizzare, classificare, verificare e rendere utilizzabili skill e altri materiali destinati a sistemi intelligenti. La libreria accetta pacchetti di qualsiasi formato, anche quando non sono ancora riconosciuti come skill. Gli originali restano intatti; descrizioni, classificazioni, adattamenti e verifiche sono gestiti separatamente.

Il progetto distingue capacità, materiali acquisiti, skill, implementazioni, strumenti e agenti. Il coordinatore selezionerà e comporrà le risorse adatte a un obiettivo, con tracciabilità e verifiche basate su prove.

## Principio di acquisizione
Essere ricevuto non significa essere una skill. Essere classificato come skill non significa essere verificato. Essere verificato non significa essere automaticamente compatibile o autorizzato all'esecuzione.

Agent Skills è un formato supportato, non un requisito per conservare un pacchetto.

## Documentazione
- [Architettura](ARCHITECTURE.md)
- [Modello strutturale](STRUCTURAL-MODEL.md)
- [Glossario](GLOSSARY.md)
- [Decisioni e questioni aperte](DECISIONS.md)
- [Roadmap](ROADMAP.md)
- [Struttura della libreria](docs/LIBRARY-STRUCTURE.md)
- [Dati per la selezione autonoma delle skill](docs/SKILL-SELECTION.md)

## Componente indipendente di acquisizione

Il componente `scripts/acquire_material.py` riceve file e cartelle locali, li copia sotto `intake/` senza eseguire il contenuto, calcola SHA-256, crea una scheda esterna e aggiorna `catalog/materials.json`. Riconosce gli archivi ZIP e TAR e li conserva come file opachi, senza estrarli. Può inoltre registrare un riferimento HTTP/HTTPS senza dichiarare che esista una copia locale. Usa registri di transazione per recuperare acquisizioni interrotte sullo stesso computer e rileva contenuti duplicati anche con identificativi diversi.

Esempi, dalla cartella principale della libreria:

    python scripts/acquire_material.py --id acq.nuovo-materiale --source "C:/Percorso/materiale.zip"
    python scripts/acquire_material.py --id acq.cartella --source "C:/Percorso/cartella" --kind package
    python scripts/acquire_material.py --id acq.riferimento --uri "https://example.org/repository"

Il componente rifiuta identificativi duplicati, destinazioni già esistenti e collegamenti simbolici. La copia viene preparata in una cartella temporanea e pubblicata solo dopo il controllo dell'impronta; gli errori durante la copia non producono una scheda catalogata. Il componente non estrae archivi, non esegue codice, non classifica il materiale e non ne certifica il funzionamento.

## Componente indipendente di classificazione

Il componente `scripts/classify_material.py` legge un materiale già acquisito, verifica che la sua impronta sia invariata e produce una proposta separata in `proposals/`. L'analisi iniziale è statica e limitata a file testuali ammessi: non esegue codice, non estrae archivi, non visita riferimenti remoti e non modifica i cataloghi approvati. La proposta richiede approvazione separata. Non equivale a verifica funzionale o autorizzazione all'uso.

Esempio:

    python scripts/classify_material.py --material-id acq.nome-materiale --proposal-id class.nome-proposta

Dettagli: [Componente di classificazione](docs/CLASSIFICATION-COMPONENT.md).

## Controlli disponibili
Comandi:

    python -m pip install -r requirements-dev.txt
    python -m unittest discover -s tests -v
    python scripts/validate_library.py

La suite viene eseguita tramite GitHub Actions su Linux e Windows. Il superamento dei test prova soltanto i comportamenti coperti: non equivale a certificare la sicurezza o la funzionalità dei materiali acquisiti.

## Approvazione delle classificazioni

Le proposte non diventano classificazioni approvate automaticamente. Il componente `scripts/classification_approval.py` consente a un revisore di approvare o respingere una proposta, dopo aver ricontrollato l'impronta del materiale. La decisione viene registrata nella scheda del materiale; non crea una skill operativa e non autorizza l'esecuzione.

Esempio di approvazione:

    python scripts/classification_approval.py --decision approve --proposal-id class.nome-proposta --actor "nome del revisore" --reason "Motivazione"

Esempio di rifiuto:

    python scripts/classification_approval.py --decision reject --proposal-id class.nome-proposta --actor "nome del revisore" --reason "Motivazione"

Dettagli: [Approvazione delle classificazioni](docs/CLASSIFICATION-APPROVAL.md).
