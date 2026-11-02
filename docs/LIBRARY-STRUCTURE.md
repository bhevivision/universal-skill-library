# Struttura della libreria universale

Stato: modello architetturale v1 approvato. La struttura fisica e i controlli per acquisizione eterogenea sono ancora da implementare; il validatore attuale è stato progettato intorno al profilo Agent Skills e non dimostra la conformità del nuovo modello.

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

I cataloghi di capacità, materiali, skill e implementazioni sono viste strutturate collegate tramite identificativi. Il formato dei record e i relativi schemi saranno aggiornati prima di dichiarare operativa questa architettura.

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

## 8. Validazione automatica: transizione necessaria
I controlli già presenti verificano cataloghi JSON e pacchetti nel profilo Agent Skills, inclusi frontmatter e SKILL.md. Non sono ancora sufficienti per il modello eterogeneo approvato.

Il validatore dovrà distinguere: integrità e tracciabilità dell'acquisizione; validità della scheda esterna; controlli specifici del profilo soltanto quando applicabile; collegamenti tra record, adattamenti, implementazioni e verifiche; condizioni necessarie per rendere una skill utilizzabile.

Il validatore non deve richiedere SKILL.md a ogni materiale. Deve rifiutare dati incoerenti senza rifiutare per questo la conservazione di un originale non interpretabile. I test devono includere file singoli, cartelle, archivi, pacchetti compositi, riferimenti remoti, formati sconosciuti, acquisizioni incomplete e tentativi di modifica dell'originale.

Comandi della suite esistente:
    python -m unittest discover -s tests -v
    python scripts/validate_library.py

Il loro superamento attesta soltanto i controlli implementati nella versione corrente, non la copertura del nuovo modello eterogeneo.

## 9. Dati dinamici e limiti
Strumenti effettivamente disponibili, agenti attivi, autorizzazioni della sessione, credenziali, stato delle attività e prove temporanee non sono verità permanenti del catalogo. Il modello non introduce ancora un motore semantico, un database runtime, API del coordinatore, installazione automatica o un motore di coordinamento.