# Struttura definitiva proposta della libreria

Stato: proposta completa per la Fase 1; da approvare prima di migrare le skill esistenti.
Versione dello schema: 1.0.

## 1. Decisione architetturale

La libreria usa tre livelli distinti:

1. **Pacchetti skill**: cartelle Agent Skills portabili, ciascuna con il proprio `SKILL.md`.
2. **Cataloghi**: indici leggibili dalle macchine che collegano capacità, pacchetti skill e implementazioni.
3. **Implementazioni**: realizzazioni tecniche specifiche per piattaforma, separate dal metodo canonico.

I cataloghi non duplicano il contenuto di `SKILL.md`: nome e descrizione vengono letti dal pacchetto. I cataloghi conservano soltanto identificativi, relazioni e informazioni necessarie alla selezione.

## 2. Struttura del repository

```text
/
├── README.md
├── ARCHITECTURE.md
├── STRUCTURAL-MODEL.md
├── GLOSSARY.md
├── DECISIONS.md
├── ROADMAP.md
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md
│       ├── scripts/       # facoltativa
│       ├── references/    # facoltativa
│       └── assets/        # facoltativa
├── implementations/
│   └── <platform>/
│       └── <implementation-id>/
│           └── manifest.json
├── catalog/
│   ├── capabilities.json
│   ├── skills.json
│   └── implementations.json
├── schemas/
│   ├── capability.schema.json
│   ├── skill-entry.schema.json
│   └── implementation.schema.json
├── examples/
│   └── capability-mapping.json
├── tests/
│   ├── fixtures/
│   └── catalog/
└── docs/
    └── LIBRARY-STRUCTURE.md
```

Le directory di progetto già presenti nel repository non vengono rinominate o spostate in questa fase. Le skill esistenti restano intatte fino alla revisione prevista dalla Fase 3.

## 3. Regole di collocazione

### Pacchetti skill

- Ogni skill pubblicabile è una cartella autonoma in `skills/<skill-name>/`.
- `SKILL.md` è obbligatorio; scripts, references e assets sono facoltativi.
- Il nome della cartella coincide con il campo standard `name` e rispetta la specifica Agent Skills.
- Le skill canoniche descrivono il metodo, non presumono la presenza di uno specifico strumento.
- Le istruzioni specifiche di una piattaforma non contaminano la skill universale: vanno in un'implementazione/adattatore oppure in una skill dichiaratamente specifica per quella piattaforma.

### Implementazioni

- Un'implementazione si trova in `implementations/<platform>/<implementation-id>/`.
- Il suo `manifest.json` dichiara quale skill e versione realizza, piattaforma, percorso d'esecuzione, prerequisiti, permessi richiesti e stato delle verifiche.
- Il manifesto descrive requisiti e prove: non concede permessi e non dimostra da solo che l'esecuzione funzioni.
- Disponibilità effettiva di strumenti, agente e autorizzazioni viene rilevata nell'ambiente al momento dell'esecuzione; non è un dato statico affidabile del repository.

### Skill specifiche di progetto

Le skill legate a un singolo progetto o a dati riservati non entrano automaticamente nella libreria pubblica. Restano in una raccolta separata o in un livello privato che potrà riutilizzare gli stessi identificativi e schemi. La pubblicazione richiede una verifica esplicita di contenuti, licenze, segreti e dati personali.

## 4. Cataloghi e fonte dei dati

I tre cataloghi sono file JSON, uno per tipo di oggetto. JSON è scelto perché è leggibile, non ambiguo e validabile direttamente con JSON Schema senza imporre un interprete YAML.

- `capabilities.json`: definisce le capacità indipendenti dalla piattaforma.
- `skills.json`: collega ogni skill al suo pacchetto e alle capacità coperte.
- `implementations.json`: collega le implementazioni alle skill e alle piattaforme.

Gli identificativi sono stabili, univoci, in minuscolo e separati da punti. Non si riutilizza un identificativo per un concetto diverso.

### Capacità

Campi: `id`, `name`, `description`, `category`, `expected_result`, `verification_criteria`, `related_capabilities` (facoltativo), `skill_ids` (facoltativo), `limitations` (facoltativo), `status`.

Stati iniziali: `draft`, `active`, `deprecated`, `blocked`. Una capacità attiva descrive un bisogno riconosciuto, non garantisce che esista una skill o un'implementazione disponibile.

### Voce del catalogo skill

Campi: `id`, `path`, `capability_ids`, `scope`, `version`, `lifecycle`; `tags` è facoltativo.

- `id` identifica la skill nel catalogo.
- `path` punta alla cartella contenente `SKILL.md).
- `capability_ids` collega la skill alle capacità che contribuisce a soddisfare.
- `scope`: `universal`, `platform` oppure `project`.
- `version` è la versione pubblicata del pacchetto.
- `lifecycle`: `stable`, `experimental`, `unverified`, `deprecated`, `blocked`.

Nome e descrizione non vengono copiati nel catalogo: la fonte canonica è `SKILL.md). La versione nel catalogo è la versione pubblicata; `metadata.version` nel frontmatter può essere aggiunto come dato facoltativo, ma non è obbligatorio né usato come seconda fonte indipendente.

### Voce del catalogo implementazioni

Campi: `id`, `skill_id`, `skill_version`, `platform`, `path`, `requirements`, `permissions_required`, `status`, `verification`.

Lo stato dell'implementazione è distinto dal ciclo di vita della skill. Un'implementazione verificata non rende automaticamente verificata ogni altra implementazione della stessa skill.

## 5. Dati che NON vengono catalogati staticamente

Non si registrano come verità permanenti nel repository:
- strumenti effettivamente disponibili sul computer dell'utente;
- agenti attivi e loro capacità effettive;
- autorizzazioni concesse nella sessione;
- credenziali, token o segreti;
- stato corrente di un'attività o di un progetto;
- prove temporanee di una singola esecuzione.

Questi dati appartengono all'inventario dell'ambiente e alla futura memoria operativa del coordinatore. Il repository può contenere soltanto requisiti, regole e riferimenti a prove non riservate.

## 6. Esempi di copertura

Il file `examples/capability-mapping.json` mostra tre richieste indipendenti dal settore:
- analizzare un PDF;
- ricercare informazioni sul web;
- operare su applicazioni Windows.

Gli esempi dimostrano la distinzione tra capacità richiesta, skill candidata, implementazione e verifica. Non dichiarano che tali skill o implementazioni siano già presenti o collaudate.

## 7. Regole di validazione

Prima di accettare una modifica ai cataloghi, i controlli automatici dovranno verificare almeno:

1. JSON valido e conforme allo schema.
2. Identificativi univoci e riferimenti esistenti.
3. Ogni percorso skill esistente e contenente `SKILL.md`.
4. Corrispondenza tra nome cartella e campo `name` del frontmatter.
5. Relazioni capacità-skill e skill-implementazione coerenti.
6. Versioni e stati ammessi.
7. Nessun segreto o dato riservato nei file pubblici.
8. Ogni dichiarazione di verifica collegata a una prova consultabile.

La validazione strutturale non equivale a un test funzionale. I test funzionali devono essere isolati e specifici per la skill e l'implementazione.

## 8. Limiti deliberati della prima versione

Non vengono ancora definiti:
- database o motore di ricerca;
- API del coordinatore;
- formato di memorizzazione di piani, attività e cronologia;
- protocollo completo degli adattatori;
- sistema automatico di installazione;
- politica completa di approvazione per ogni categoria di rischio.

Questi aspetti dipendono dal prototipo e dalle prove successive. Non devono complicare prematuramente la libreria dei metodi.

## 9. Criterio di approvazione della struttura

La struttura è pronta per l'approvazione quando:
- gli schemi descrivono senza ambiguità i tre cataloghi;
- gli esempi coprono casi diversi senza dipendere da una piattaforma;
- i collegamenti tra capacità, skill e implementazioni sono verificabili;
- la struttura Agent Skills rimane integra;
- le skill esistenti non sono state spostate o riscritte.
