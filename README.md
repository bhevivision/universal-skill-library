# Skill operative e selezione

Per trovare skill da riusare in un progetto, inizia da [INDEX.md](INDEX.md). La libreria conserva anche materiali di riferimento non ancora classificati o verificati; consulta [l'architettura](ARCHITECTURE.md) per distinguere archivio, catalogo e skill pronte all'uso.

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
- [Progettazione della classificazione semantica](docs/SEMANTIC-CLASSIFICATION-DESIGN.md)
- [Contratto tecnico della classificazione semantica](docs/SEMANTIC-CLASSIFICATION-CONTRACT.md)
- [Schema JSON della richiesta semantica](schemas/semantic-classification-request.schema.json)
- [Schema JSON della proposta semantica](schemas/semantic-classification-proposal.schema.json)
- [Inventario preliminare dei materiali esistenti](docs/EXISTING-SKILLS-INVENTORY.md)
- [Verifica locale della libreria su Windows](docs/WINDOWS-LOCAL-VERIFICATION.md)

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

La futura analisi semantica avrà un contratto e uno schema di proposta separati. In questa fase sono stati definiti lo schema JSON e i relativi test di contratto; il motore semantico non è ancora implementato.

## Controllo dell'integrità delle prove semantiche

Il componente `scripts/semantic_evidence_integrity.py` verifica una proposta semantica senza eseguire il materiale acquisito. Controlla la conformità allo schema, l'unicità degli identificativi delle prove, l'esistenza di tutti i riferimenti, la corrispondenza tra materiale e catalogo, i percorsi ammessi, l'appartenenza dei file al materiale originale, le impronte SHA-256, i collegamenti simbolici e gli intervalli di righe dichiarati. Esegue un nuovo controllo delle impronte al termine per rilevare modifiche durante la verifica.

Esempio:

    python scripts/semantic_evidence_integrity.py --proposal proposals/nome-proposta.json

Le prove del catalogo usano l'impronta dell'intero `catalog/materials.json`: se il catalogo cambia, la proposta deve essere verificata nuovamente. Il controllo dimostra la tracciabilità tecnica delle prove, non la correttezza del significato attribuito dal classificatore.

## Servizio comune di integrità dei materiali

Il componente `scripts/material_integrity.py` centralizza la lettura del record, il controllo dello stato di acquisizione, la sicurezza del percorso e il ricalcolo dell'impronta SHA-256. Mantiene il riconoscimento delle impronte storiche delle cartelle, comprese le versioni prive del campo `digest_algorithm`. I riferimenti remoti vengono controllati solo come metadati e non sono dichiarati verificati nel contenuto.

Il risultato segue `schemas/material-integrity-result.schema.json`. Il contratto è descritto in [MATERIAL-INTEGRITY-CONTRACT.md](docs/MATERIAL-INTEGRITY-CONTRACT.md). Il servizio viene riutilizzato dal classificatore statico, dal componente di approvazione e dal verificatore delle prove semantiche. Non modifica materiali, cataloghi o proposte e non esegue contenuti.

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
