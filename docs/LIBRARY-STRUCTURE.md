# Struttura della libreria universale

Stato: modello architetturale v1 approvato. L'acquisizione eterogenea, il catalogo dei materiali e i controlli d'integrità sono implementati sul ramo di lavoro. Il componente registra file, cartelle e riferimenti remoti; gestisce il recupero delle transazioni interrotte e il rilevamento dei duplicati. La verifica automatica è eseguita su Linux e Windows tramite GitHub Actions. La prova sul computer Windows dell'utilizzatore resta distinta.

## 1. Architettura a livelli
La libreria separa:
1. Acquisizione e conservazione: riceve materiali di qualsiasi formato e mantiene intatto l'originale.
2. Descrizione e classificazione: registra informazioni esterne e classifica soltanto dopo l'analisi.
3. Catalogo: permette ricerca e collegamento tra materiali, capacità, skill e implementazioni.
4. Adattamenti e implementazioni: contiene derivati separati dall'originale e specifici per ambiente.
5. Verifiche e prove: registra controlli riferiti a una precisa versione e a un preciso ambiente.

Agent Skills è uno dei profili di formato supportati. Non è il contenitore obbligatorio di tutti i materiali.

## 2. Tipi di materiale da accettare
L'acquisizione deve poter rappresentare almeno: file singolo testuale o binario; cartella o albero di file; archivio compresso; pacchetto con più componenti; documentazione e risorse collegate; riferimento remoto o deposito esterno; pacchetto composito o non ancora interpretabile.

La libreria non deve eseguire il materiale durante ricezione e analisi. Archivi e file potenzialmente pericolosi sono trattati come dati non fidati. L'estrazione, quando necessaria, avviene in ambiente controllato e non altera la copia originale.

## 3. Organizzazione logica proposta
Il layout fisico definitivo non viene imposto prima dei test sui diversi tipi di pacchetto. La struttura logica deve separare originale, scheda, adattamenti e verifiche. Esempio indicativo:

    /
    ├── README.md
    ├── ARCHITECTURE.md
    ├── STRUCTURAL-MODEL.md
    ├── DECISIONS.md
    ├── ROADMAP.md
    ├── intake/
    │   └── <acquisition-id>/
    │       ├── source/          # copia integra del materiale ricevuto
    │       └── acquisition.json
    ├── records/
    │   └── <record-id>.json
    ├── catalog/
    │   ├── capabilities.json
    │   ├── materials.json
    │   ├── skills.json
    │   └── implementations.json
    ├── adapters/
    ├── implementations/
    ├── verification/
    ├── schemas/
    ├── scripts/
    ├── tests/
    └── docs/

Questo schema è un'organizzazione logica, non una prescrizione di collocare ogni pacchetto sotto una cartella standard. Il contenuto di source/ può essere un file, una cartella o un archivio, mantenuto nella forma originaria. I riferimenti remoti e le acquisizioni incomplete sono registrati come tali, senza fingere che esista una copia locale.

## 4. Scheda esterna e cataloghi
La scheda esterna è indipendente dal formato del pacchetto. Registra, quando noti: identificativo e provenienza; nome originale e collocazione; tipo di elemento e formato rilevato; classificazione, motivazione e confidenza; versione dichiarata e impronta calcolata; descrizione, scopo e capacità associate; ingressi, risultati, prerequisiti e dipendenze; limitazioni, rischi, permessi e compatibilità; lacune informative e riferimenti mancanti; stati di acquisizione, classificazione, documentazione, verifica e utilizzabilità.

I dati non noti non sono inventati. Il record può essere parziale. Un pacchetto non classificato può essere conservato e ricercato senza essere inserito nel catalogo delle skill eseguibili.

I cataloghi di capacità, materiali, skill e implementazioni sono contenitori JSON versionati, con schemi per il contenitore e per le singole voci in `schemas/`. Il validatore controlla gli schemi e i collegamenti tra gli oggetti. I cataloghi presenti nel ramo sono attualmente vuoti: la presenza degli schemi non significa che l'inventario operativo sia già stato popolato. La gestione completa delle migrazioni tra versioni successive dei record resta aperta.

## 5. Profili di formato
Ogni profilo è facoltativo e specifico di un formato. Può controllare struttura e metadati previsti da quel formato, ma non può diventare un requisito generale per l'acquisizione.
- Agent Skills: riconosce cartella, SKILL.md, frontmatter standard e risorse facoltative.
- Altri formati noti: possono avere analizzatori dedicati, senza conversione automatica dell'originale.
- Formato sconosciuto o opaco: viene conservato; la descrizione indica che il contenuto non è stato interpretato.

L'assenza di un analizzatore non comporta rifiuto o perdita del materiale. Comporta una classificazione e una documentazione limitate.

## 6. Adattamenti e implementazioni
Gli adattamenti sono collocati fuori dal pacchetto originale. Ogni adattamento indica origine, versione o impronta di partenza, piattaforma di destinazione, modifiche, motivo, responsabile e prove. Le implementazioni descrivono come una skill viene effettivamente eseguita in un ambiente, con requisiti, strumenti, permessi e compatibilità.

Un adattamento non è automaticamente approvato né compatibile. La compatibilità deve essere verificata nell'ambiente dichiarato.

## 7. Verifica e prove
Ogni verifica è riferita a identificativo del materiale o della skill; versione dichiarata e/o impronta del contenuto verificato; adattamento o implementazione, se presente; ambiente e piattaforma; procedura e criteri; data, esito, limiti e riferimenti alle prove.

Una prova strutturale conferma soltanto la struttura controllata. Non certifica il comportamento funzionale. Una verifica superata non si trasferisce automaticamente a una versione modificata o a un'altra piattaforma.

## 8. Validazione automatica

Il validatore controlla:
- schemi dei cataloghi e delle schede descrittive;
- integrità e tracciabilità dei materiali conservati sotto `intake/`;
- impronte SHA-256 di file e cartelle, incluse le cartelle vuote;
- percorsi sicuri e assenza di collegamenti simbolici;
- profilo Agent Skills soltanto quando una skill è fornita tramite `SKILL.md`;
- collegamenti tra materiali, capacità, skill, implementazioni e prove.

La presenza di `SKILL.md` non è richiesta per ogni materiale. I file sconosciuti, i pacchetti opachi e i riferimenti remoti possono essere conservati e registrati senza essere dichiarati skill.

Comandi:

    python -m unittest discover -s tests -v
    python scripts/validate_library.py

La suite viene eseguita su Linux e Windows tramite GitHub Actions. Il superamento dei test attesta soltanto i comportamenti coperti e non certifica la sicurezza o il funzionamento dei materiali acquisiti.

## 9. Stato dei cataloghi e dell'inventario

Gli schemi v1 per materiali, capacità, skill e implementazioni sono presenti e controllati dal validatore. I cataloghi sono ancora vuoti: i materiali sotto `personalizzazione/` sono stati esaminati soltanto in modo preliminare e non sono stati ancora acquisiti tramite il componente ufficiale. Il rapporto è in [EXISTING-SKILLS-INVENTORY.md](EXISTING-SKILLS-INVENTORY.md). La verifica locale su Windows è descritta in [WINDOWS-LOCAL-VERIFICATION.md](WINDOWS-LOCAL-VERIFICATION.md).

## 10. Contratto della scheda descrittiva esterna

Ogni materiale acquisito ha una voce in `catalog/materials.json`, validata da `schemas/material-record.schema.json`. La scheda non viene inserita nel pacchetto originale.

Campi principali:
- `id`: identificativo stabile della registrazione.
- `name`, `description`, `declared_version`, `format`: informazioni descrittive, facoltative se sconosciute.
- `acquisition`: stato, data, metodo, provenienza e riferimento all'originale.
- `acquisition.original.kind`: `file`, `directory`, `archive`, `package`, `remote_reference` oppure `unknown`.
- `acquisition.original.path`: percorso relativo sotto `intake/`, quando esiste una copia locale.
- `acquisition.original.uri`: riferimento remoto, quando il materiale non è conservato localmente.
- `acquisition.original.sha256`: impronta del contenuto conservato; obbligatoria per materiale locale dichiarato `preserved`.
- `classification`: stato, categoria, confidenza e motivazione.
- `documentation`, `verification`, `usability`: stati indipendenti.
- `dependencies`, `missing_references`, `notes`: dipendenze, lacune e annotazioni conosciute.

Una scheda può essere incompleta. I campi ignoti si omettono o si registrano come stato sconosciuto; non si inventano.

## 11. Regole di conservazione e integrità

- File singolo: conservato come file, senza conversione o modifica.
- Cartella: conservata come albero di file, con nomi e percorsi relativi originali.
- Archivio: conservato come archivio binario originale; la validazione non lo estrae.
- Pacchetto: può essere un singolo file o una cartella composta da più risorse.
- Riferimento remoto: si conserva l'URI e si dichiara esplicitamente che non esiste una copia locale.
- Materiale incompleto o non riconosciuto: può essere registrato senza essere dichiarato utilizzabile.

Le copie locali sono collocate sotto `intake/<identificativo-acquisizione>/source/`; il percorso esatto è registrato nella scheda. Il validatore controlla che il percorso rimanga nella libreria e sotto `intake/`, rifiuta collegamenti simbolici e confronta l'impronta SHA-256. Per una cartella, l'impronta è calcolata in modo deterministico su percorsi relativi, tipo di elemento e contenuto dei file. Gli archivi non vengono aperti né eseguiti durante il controllo.

La verifica d'integrità rileva modifiche rispetto all'impronta registrata; non certifica la sicurezza del contenuto. L'acquisizione e l'analisi non eseguono codice.

## 12. Collegamento tra materiale e skill

Una voce in `catalog/skills.json` può riferirsi:
- a `source_record_id`, che punta a una scheda materiale classificata esplicitamente come `skill`; oppure
- a `path`, per i pacchetti del profilo Agent Skills già organizzati con `SKILL.md`.

Solo il secondo caso applica il controllo del frontmatter Agent Skills. Una skill collegata tramite `source_record_id` non deve contenere `SKILL.md`. Il materiale non classificato o classificato come risorsa, strumento o possibile skill non può essere inserito come skill eseguibile nel catalogo.

Esempio di scheda minima per un file locale conservato:

    {
      "id": "acq.example",
      "name": "Procedura di esempio",
      "acquisition": {
        "status": "preserved",
        "acquired_at": "2026-11-02T10:00:00Z",
        "method": "manual-upload",
        "original": {
          "kind": "file",
          "path": "intake/acq-example/source/procedure.txt",
          "sha256": "<64 caratteri esadecimali>"
        }
      },
      "classification": {
        "status": "classified",
        "kind": "skill",
        "confidence": "medium",
        "rationale": "Scopo e procedura identificabili."
      },
      "documentation": {"status": "partial"},
      "verification": {"status": "not_verified"},
      "usability": {"status": "not_assessed"}
    }

## 13. Dati dinamici e limiti
Strumenti effettivamente disponibili, agenti attivi, autorizzazioni della sessione, credenziali, stato delle attività e prove temporanee non sono verità permanenti del catalogo. Il modello non introduce ancora un motore semantico, un database runtime, API del coordinatore, installazione automatica o un motore di coordinamento.