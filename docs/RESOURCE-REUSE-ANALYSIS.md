# Analisi delle sei risorse per il completamento della libreria

**Data dell'analisi:** 2026-11-03  
**Stato:** analisi documentale delle sei risorse registrata; adattamenti e prove funzionali delle skill restano da eseguire.  
**Ramo:** `research/resource-reuse-analysis-v1`

## 1. Scopo e metodo

Questo documento registra l'analisi delle sei risorse già raccolte per riutilizzarne le capacità nella libreria universale, senza importare interi progetti o confondere formati, procedure, strumenti e motori di esecuzione.

Per ogni risorsa si distinguono:
- natura effettiva e funzione;
- versione o riferimento consultato;
- licenza dichiarata dalla fonte;
- capacità riutilizzabili;
- dipendenze e limiti;
- destinazione prevista nella libreria;
- verifiche ancora necessarie.

**Regola:** la presenza di un documento, una dichiarazione nella documentazione o un test di struttura non dimostrano da soli che una skill funzioni. Nessuna risorsa viene promossa a utilizzabile senza prove riferite alla versione e all'ambiente esaminati.

## 2. Sintesi delle sei risorse

| Risorsa | Natura effettiva | Riutilizzo previsto | Stato dell'analisi |
|---|---|---|---|
| Agent Skills | Specifica aperta per confezionare skill in cartelle con `SKILL.md` | Profilo di formato interoperabile della libreria | Specifica e licenze consultate; verifica del validatore interno ancora da eseguire |
| UNLAZY | Metodo di controllo e modello di governo basato su requisiti, criteri, prove, verifiche, decisioni e Gate | Procedure di verifica, completamento, gestione degli errori e ricontrollo | Fonte principale analizzata; tre riferimenti operativi separati non reperiti |
| Archivista | Sistema documentale specifico per fascicoli di libri, con regole di conservazione e storia | Principi universali di provenienza, versionamento, integrità, non invenzione e approvazione | Skill locale analizzata; documento normativo completo v3 reperito nell'archivio personale |
| Find Skills | Skill di scoperta e installazione, basata sul programma `skills` e su skills.sh | Ricerca e acquisizione controllata di skill esterne | Copia locale confrontata con la fonte corrente; procedura di installazione da correggere |
| Matt Pocock Skills | Raccolta di procedure per progettazione e sviluppo software | Metodi di chiarimento, progettazione, TDD, diagnosi, revisione e scrittura di skill | Raccolta e licenza consultate; selezione mirata necessaria |
| ORCA | Registro di capacità/skill in YAML più motore Python che esegue flussi DAG | Riferimento per contratti, dipendenze, composizione, esecuzione, stato, sicurezza e tracciabilità | Codice e documentazione consultati; discrepanze del registro e prove di funzionamento ancora aperte |

## 3. Agent Skills — formato aperto

**Fonte consultata:** `agentskills/agentskills`, ramo `main`, commit `69ef37e9424c0a7ea9dd2293b559e43ec8176379`.  
**Specifica:** `docs/specification.mdx`, blob `d9a2db099d905da8b879a5c6f996728073985279`.  
**Licenza:** codice del repository Apache-2.0; documentazione CC-BY-4.0, come dichiarato dal repository e dal file `docs/LICENSE`.

### Capacità effettive

Una skill è una cartella che contiene almeno `SKILL.md`. Il file contiene:
- frontmatter YAML obbligatorio con `name` e `description`;
- istruzioni in Markdown;
- eventuali risorse facoltative in cartelle come `scripts/`, `references/` e `assets/`.

La specifica disciplina i campi facoltativi `license`, `compatibility`, `metadata` e `allowed-tools`. Quest'ultimo è sperimentale e il supporto varia tra gli agenti.

La specifica raccomanda la divulgazione progressiva: metadati per la scoperta, istruzioni al momento dell'attivazione, risorse caricate solo quando servono.

### Limiti

Agent Skills è **un formato di confezionamento e istruzioni**, non:
- un motore universale di esecuzione;
- un sistema di pianificazione o coordinamento;
- un registro delle autorizzazioni effettive;
- una garanzia di sicurezza o correttezza;
- una prova che il contenuto sia stato eseguito.

Il campo `allowed-tools` non sostituisce un controllo dei permessi imposto dal sistema che esegue la skill.

### Decisione per la libreria

Adottare Agent Skills come profilo standard per le skill compatibili, mantenendo:
1. originale acquisito intatto;
2. scheda esterna della libreria;
3. eventuale adattamento in `SKILL.md`;
4. implementazione eseguibile separata;
5. verifica associata alla versione esatta.

Non convertire ogni materiale ricevuto in una skill: la libreria deve poter conservare anche documenti, strumenti, pacchetti e riferimenti non classificati come skill.

## 4. UNLAZY — controllo basato su prove

**Fonti consultate:**
- `personalizzazione/UNLAZY-skill.md`, blob `c59d88d9503cf5ba3b9ba3d08f757a875087eda5`, 15.570 caratteri circa;
- documento di progettazione UNLAZY su fondazione OKF, reperito nell'archivio personale, file `pasted(1).txt`, 2.109 righe complessive.

**Licenza:** nei materiali UNLAZY consultati non è stato trovato un file di licenza autonomo. Sono materiali forniti dall'utente; non si presume che siano rilasciati con licenza aperta. La specifica OKF citata come fondazione è un'opera distinta, pubblicata da Google Cloud con licenza Apache-2.0.

### Capacità effettive

La skill UNLAZY contiene una disciplina operativa concreta:
- scomporre il lavoro in attività e righe verificabili;
- definire prima dell'esecuzione il criterio di completamento, il controllo e la prova attesa;
- distinguere dichiarazione, verifica, prova, risultato e stato;
- verificare l'effetto reale alla destinazione, non soltanto il comando o il file preparato;
- richiedere prove rileggibili, indipendenti, coerenti e innocue;
- distinguere evidenza di grado A (osservata sul sistema reale), B (dedotta leggendo codice/documenti) e C (indizio);
- conservare FAIL e tentativi precedenti;
- non riprovare senza aver identificato la causa;
- dichiarare NON VERIFICABILE quando manca uno strumento, un accesso o un dato;
- ricontrollare verifiche rese obsolete da modifiche successive.

Il modello esteso introduce entità distinte per Source, SourceVersion, Evidence, Requirement, Rule, Criterion, Procedure, Execution, Receipt, Attestation, Verification, Result, Decision, Gate, Change, Impact, Revalidation, Gap, Approval ed Event. Distingue inoltre UNKNOWN, MISSING, STALE, FAILED e BLOCKED.

### Dipendenze e lacune

La skill locale dichiara tre risorse:
- `references/tipi_di_prova.md`;
- `references/file_di_controllo.md`;
- `references/casi_reali.md`.

Questi tre file non risultano nel deposito GitHub né sono stati individuati come documenti autonomi nell'archivio personale durante le ricerche effettuate. Il modello UNLAZY esteso è disponibile, ma non sostituisce automaticamente i tre riferimenti operativi. La skill deve quindi essere adattata usando soltanto le regole effettivamente presenti nelle fonti recuperate, senza inventare il contenuto mancante.

### Decisione per la libreria

Riutilizzare il nucleo universale per:
- pianificazione delle verifiche;
- raccolta e valutazione delle prove;
- gestione degli esiti negativi;
- decisione di completamento;
- gestione delle modifiche e ricontrollo.

Non trasferire automaticamente l'intero modello UNLAZY come un'unica skill monolitica. Le entità e gli stati del modello vanno confrontati con quelli già definiti nella libreria per evitare duplicazioni. Il modello è anche una fonte per verificare che il coordinatore distingua esecuzione, risultato prodotto, risultato verificato, accettazione e completamento.

## 5. Archivista — conservazione e storia documentale

**Fonti consultate:**
- `personalizzazione/archivista-skill.md`, blob `cc0074a15072111f98e3764951fae9d6b4957ca1`;
- documento normativo completo `ARCHIVISTA DEL LIBRO — Sistema Completo`, versione `TEMPLATE_MASTER_v3`, reperito nell'archivio personale;
- versione precedente `TEMPLATE_MASTER_v1`, reperita nell'archivio personale.

**Licenza:** non è stato trovato un file di licenza autonomo nei documenti consultati. Trattare la fonte come materiale dell'utente, senza dichiararla open source.

### Capacità effettive

Il sistema è specifico per fascicoli documentali di libri e prevede 17 sezioni fisse. I principi trasferibili sono:
- non inventare informazioni mancanti;
- distinguere dato dichiarato, documento e prova;
- mantenere separati originale, versione ufficiale e pubblicazione;
- conservare la cronologia senza sovrascrivere il passato;
- assegnare identificativi non riutilizzabili;
- mantenere provenienza e collegamenti alle prove;
- usare stati espliciti per dato non disponibile, non applicabile e caso non previsto;
- richiedere una decisione umana quando una situazione esce dalle regole;
- non attribuire all'archivista competenze valutative che spettano a un professionista.

La fonte v3 consolida in un unico documento il Template Master, il vocabolario, il glossario, la struttura dell'archivio aziendale e il registro delle versioni.

### Limiti

Le 17 sezioni, le regole del fascicolo del libro, i riferimenti ad Obsidian e le valutazioni giuridiche sono specifici del dominio. Non devono diventare requisiti della libreria universale.

La regola locale secondo cui l'Archivista non scrive mai autonomamente è troppo rigida se applicata senza distinzione a ogni operazione della libreria. Il principio riutilizzabile è invece: conservare gli originali, non modificare dati senza autorizzazione, e richiedere approvazione per azioni rischiose o irreversibili.

### Decisione per la libreria

Usare Archivista come fonte di principi per provenienza, conservazione, versionamento, storia e approvazione. Non importare le 17 sezioni né creare una skill universale che replichi il fascicolo del libro. Le funzioni di acquisizione e integrità già presenti nella libreria devono essere confrontate con questi principi prima di creare nuove skill.

**Nota sulla dipendenza mancante:** `reference/regole-complete.md` non è nel deposito GitHub, ma il documento normativo completo v3 è stato recuperato nell'archivio personale. La dipendenza è quindi recuperabile; resta da registrare correttamente la fonte e la sua versione.

## 6. Find Skills — ricerca di skill esterne

**Fonte locale:** `personalizzazione/find-skill.md`, blob `1e204b37ca5fd88e7b449c4512c92c4e7990287f`.  
**Fonte upstream confrontata:** `vercel-labs/skills/skills/find-skills/SKILL.md`, commit del repository `7a5e920bead4b1039a6d6df5d7e1163b7b09423a`; blob del file `a41bdd074bb587afd861332cf2f473f3154de4d7`.  
**CLI consultata:** pacchetto npm `skills` versione `1.7.6`, repository `vercel-labs/skills`.  
**Licenza:** MIT per il repository e il pacchetto CLI.

### Capacità effettive

- interpretare la richiesta per ricavare dominio e attività;
- cercare skill tramite `skills find` e skills.sh;
- elencare skill disponibili in un deposito senza installarle;
- individuare una skill specifica e la sua fonte;
- installare o aggiornare skill attraverso la CLI.

La versione CLI consultata richiede Node.js 22.20 o successivo. Prevede installazione nel progetto per impostazione predefinita; `-g` seleziona l'ambito globale, `-y` salta le conferme, `--list` elenca senza installare. La CLI raccoglie telemetria anonima per impostazione predefinita; la documentazione indica `DISABLE_TELEMETRY=1` o `DO_NOT_TRACK=1` per disabilitarla.

### Limiti e rischi

La skill upstream suggerisce soglie di popolarità, reputazione della fonte e stelle GitHub. Questi sono segnali di scoperta, non prove di sicurezza, qualità, licenza o funzionamento. La procedura suggerisce inoltre un comando globale con conferma automatica (`-g -y`): non è accettabile come comportamento predefinito della libreria.

La copia locale non ha frontmatter Agent Skills e non riporta la versione della fonte. È una copia di istruzioni, non un pacchetto già conforme.

### Decisione per la libreria

Riutilizzare la parte di scoperta, ma separare nettamente:
1. ricerca;
2. acquisizione o registrazione della fonte;
3. controllo della provenienza e della versione;
4. controllo della licenza;
5. analisi di contenuto, dipendenze, permessi e rischi;
6. prova isolata;
7. approvazione;
8. installazione o attivazione.

La ricerca non deve installare automaticamente né proporre come sicura una skill soltanto perché è popolare. La CLI è uno strumento opzionale, non un requisito del formato o della libreria.

## 7. Matt Pocock Skills — procedure di ingegneria

**Fonte consultata:** `mattpocock/skills`, ramo `main`, commit `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`.  
**Versione dichiarata in `package.json`:** `1.3.2`.  
**Licenza:** MIT.

La raccolta contiene 27 file `SKILL.md` nelle aree engineering e productivity. Non tutte le skill sono pertinenti alla libreria.

### Procedure con maggiore valore di riuso

| Skill originale | Procedura utile | Destinazione possibile |
|---|---|---|
| `grill-me` / `grill-with-docs` | Chiarire obiettivo, vincoli e ambiguità prima di agire | Interpretazione della richiesta e raccolta requisiti |
| `domain-modeling` | Definire termini, glossario e decisioni senza confondere dominio e implementazione | Manutenzione del modello strutturale |
| `codebase-design` | Moduli profondi, interfacce piccole, punti di sostituzione e testabilità | Progettazione di componenti e adattatori |
| `to-spec` / `implement-spec` | Trasformare requisiti in specifiche verificabili e poi in lavoro | Preparazione di skill e componenti |
| `tdd` | Test prima della modifica, una porzione verificabile per volta | Verifica delle skill e delle modifiche al codice |
| `diagnosing-bugs` | Riprodurre, ridurre, formulare ipotesi falsificabili, isolare la causa e poi correggere | Gestione errori e recupero |
| `code-review` | Revisione separata rispetto a standard e specifica | Verifica indipendente delle modifiche |
| `writing-for-agents` | Istruzioni concise, progressive disclosure, puntatori e criteri di completamento | Scrittura delle nuove skill Agent Skills |

### Limiti

Alcune procedure presuppongono un sistema di issue tracker, sottagenti paralleli o specifici comandi dell'agente. Queste dipendenze non vanno trasformate in requisiti universali. La revisione parallela, per esempio, deve diventare una procedura adattabile: se non esistono sottagenti indipendenti, la limitazione va dichiarata.

### Decisione per la libreria

Riutilizzare i principi e le procedure selezionate, non importare in blocco l'intera raccolta. Ogni adattamento deve conservare attribuzione e licenza MIT, includendo il testo della licenza e le indicazioni di modifica quando si ridistribuiscono porzioni derivate.

## 8. ORCA — registro e motore di esecuzione

**Registro:** `gfernandf/agent-skill-registry`, commit `b70a6f99cf01ca928a94231e5d7b1a1e82098612`.  
**Motore:** `gfernandf/agent-skills`, commit `d9e3644e8aac6b75f327d973f94e187d2e8f789c`.  
**Versione Python dichiarata:** `1.0.2`; Python `>=3.11`.  
**Dipendenze principali:** PyYAML `>=6.0`, requests `>=2.28`; le funzioni PDF, web, OpenTelemetry, ASGI, MCP e integrazioni con framework hanno dipendenze opzionali.  
**Licenza:** Apache-2.0 per registro e motore.

### Capacità effettive dichiarate e presenti nella struttura

Il registro definisce capacità primitive e skill composte in YAML. Il motore dichiara di:
- risolvere le capacità tramite collegamenti a implementazioni;
- eseguire skill come grafi DAG;
- gestire dipendenze sequenziali e parallele;
- mantenere stato, eventi e tracciabilità;
- applicare controlli di policy e sicurezza;
- collegarsi a backend differenti tramite binding;
- esporre integrazioni SDK, HTTP, MCP e adattatori per framework.

Le skill `agent.orchestrate-from-prompt` e `agent.execute-from-plan` sono particolarmente pertinenti come riferimento per separare pianificazione ed esecuzione.

### Incompatibilità con Agent Skills

ORCA usa `skill.yaml` e un proprio linguaggio dichiarativo per i flussi. Non è il formato `SKILL.md` di Agent Skills. Non bisogna rinominare o convertire meccanicamente i file YAML in Markdown: il contenuto dichiarativo richiede un adattatore o una rappresentazione distinta.

### Discrepanze misurate nel registro

I conteggi sono stati ricontrollati sui cataloghi JSON alle revisioni indicate:

| Revisione del registro | Capacità | Skill |
|---|---:|---:|
| `main` / commit `b70a6f9` | 184 | 40 |
| Pin usato da `smoke.yml` — `63e127c` | 184 | 39 |
| Pin usato da `ci.yml` — `ca58b34` | 192 | 39 |

Il README del registro dichiara ancora 159 capacità e 37 skill. Il README del motore dichiara 184 capacità e 39 skill, mentre `catalog/stats.json` del registro corrente riporta 184 e 40.

La workflow `cognitive_continuous_validation.yml` clona il registro `main` senza fissare una revisione. Le workflow CI e smoke usano invece due pin differenti. Questo rende non uniforme la base di confronto.

### Prova di funzionamento già recuperata

La workflow run `38500893498` del 14 ottobre 2026, sul commit motore `d9e3644e8aac6b75f327d973f94e187d2e8f789c`, è fallita nel controllo end-to-end delle capacità cognitive: 4 capacità non hanno superato i controlli di contratto/risultato.

Gli estratti del registro di esecuzione identificano due cause concrete:
- `reasoning.plan.decompose`: il binding invoca `split_problem` senza gli argomenti obbligatori `problem` e `strategy`;
- `reasoning.plan.generate`: il binding passa `objective`, argomento non accettato da `generate_skill_from_prompt`.

Le altre due capacità segnalate sono `memory.context.store` e `perception.input.structure`; il rapporto di dettaglio dei quattro casi non era incluso nell'artefatto pubblicato, quindi le loro cause restano da identificare. Il rapporto aggregato segnala inoltre come mancanti lo scorecard e il report di dismissione: il controllo iniziale fallisce prima che tali file vengano prodotti.

### Decisione per la libreria

ORCA è un candidato di riferimento per il coordinatore e per l'esecuzione dei flussi, non una base da adottare senza prove. Prima di riutilizzare il motore bisogna:
1. fissare una coppia coerente di revisioni registro/motore;
2. risolvere i conteggi e i pin divergenti;
3. analizzare le quattro capacità fallite;
4. eseguire test riproducibili su una versione fissata;
5. verificare policy, permessi, gestione errori, tracciabilità e recupero;
6. confrontare il modello ORCA con l'architettura già presente nella libreria.

## 9. Cosa dobbiamo estrarre e costruire

La sintesi non è importare sei raccolte. È riutilizzare procedure e principi che coprono parti diverse del sistema:

| Funzione della libreria | Fonti principali | Risultato atteso |
|---|---|---|
| Scoperta e valutazione di skill esterne | Find Skills + Agent Skills + UNLAZY | Procedura di ricerca, registrazione, verifica di fonte/licenza e approvazione |
| Chiarimento e definizione dell'obiettivo | Matt Pocock + UNLAZY | Procedura per trasformare richieste in requisiti e criteri verificabili |
| Conservazione e provenienza | Archivista + UNLAZY | Regole di integrità, versionamento, storia e non sovrascrittura |
| Creazione e adattamento di skill | Agent Skills + Matt Pocock + ORCA | Skill `SKILL.md` con contratti e risorse esterne, senza confondere il formato con il motore |
| Verifica e completamento | UNLAZY + Matt Pocock | Criteri preventivi, prove, test, gestione FAIL e ricontrollo |
| Composizione ed esecuzione | ORCA + modello strutturale esistente | Coordinatore con dipendenze, stato, policy, esecutori e tracciabilità |

## 10. Lacune rilevate nel repository della libreria

1. Il catalogo materiali contiene ora 7 schede di riferimento remoto: le sei risorse concettuali, con ORCA separato in registro e motore. I cataloghi capacità, skill e implementazioni sono ancora vuoti. Le schede dichiarano esplicitamente che non è stata acquisita una copia locale e che il funzionamento non è verificato. La base dispone già del componente `scripts/acquire_material.py`; non va ricostruito. La base dispone già del componente `scripts/acquire_material.py`, che conserva file/cartelle/archivi e registra riferimenti remoti senza eseguirli; non va ricostruito.
2. Il modello e le schede già distinguono materiale, skill e implementazione; non bisogna duplicare tali oggetti importando i modelli delle fonti.
3. Il campo strutturato `license` è stato aggiunto a `schemas/material-record.schema.json` in questo ramo. Registra dichiarazione, fonte, revisione, obblighi sintetizzati e prove; non determina automaticamente i diritti di redistribuzione.
4. `schemas/skill-entry.schema.json` richiede capacità collegate, ambito, versione, ciclo di vita, ingressi, risultati, prerequisiti, vincoli, rischio e verifica. È stato aggiunto `source_material_ids` per collegare più fonti a una skill adattata; il validatore controlla che ogni scheda esista.
5. La skill locale Find Skills e la skill locale Archivista non hanno frontmatter Agent Skills; non sono pacchetti conformi già pronti.
6. Il validatore Agent Skills già presente controlla frontmatter YAML, chiavi duplicate, `name`, `description` e corrispondenza tra nome e cartella. La conformità completa a tutti i campi facoltativi della specifica e l'interoperabilità su agenti reali restano da provare.

## 11. Sequenza operativa successiva

1. Chiudere l'inventario delle fonti, comprese le dipendenze mancanti e i limiti delle prove.
2. Completare la revisione dei termini di licenza dei derivati, senza trasformare il controllo della dichiarazione in un parere legale.
3. Separare procedure universali, procedure dipendenti da una piattaforma e materiali di sola consultazione.
4. Preparare un primo gruppo ridotto di skill Agent Skills, senza duplicare componenti già presenti.
5. Aggiungere i contratti delle capacità e le skill ai cataloghi, mantenendoli non verificati finché non esistono prove funzionali.
6. Eseguire prove isolate e poi prove di composizione.
7. Solo dopo queste prove scegliere e integrare il motore del coordinatore.

## 12. Stato delle attività

- Analisi statica delle sei fonti: **completata a livello documentale**; restano esplicite le lacune dei tre riferimenti UNLAZY e delle due verifiche ORCA non dettagliate.
- Licenze delle fonti pubbliche: **identificate a livello di repository/pacchetto; obblighi di distribuzione da applicare ai singoli derivati**.
- Campo strutturato per licenza del materiale: **implementato nel ramo di analisi**; la revisione richiede prove e non produce un giudizio legale automatico.
- Verifica della licenza con prova collegata: **7 prove registrate**; il validatore controlla esistenza, soggetto ed esito. I run `41711115849` e `41711127483` hanno superato 199 test e validazione cataloghi su Ubuntu e Windows.
- Provenienza multipla delle skill: **campo `source_material_ids` e controllo dei riferimenti implementati**; i run `41711560135` e `41711570317` hanno superato 201 test e validazione su Ubuntu e Windows.
- Recupero del riferimento completo Archivista: **eseguito dall'archivio personale**.
- Recupero dei tre riferimenti operativi UNLAZY: **non riuscito; lacuna dichiarata**.
- Registrazione dei materiali: **completata come riferimenti remoti**, non equivale a verifica funzionale o approvazione all'uso.
- Verifica del funzionamento delle skill adattate: **non eseguita**.
- Registrazione delle fonti nel catalogo materiali: **7 riferimenti remoti creati e validati** (ORCA separato in runtime e registro); nessuna copia locale è stata dichiarata o acquisita. Il componente di acquisizione esistente è stato riutilizzato come modello dati, senza eseguire i contenuti.
- Coordinatore universale: **non ancora scelto né integrato**.


## Gestore dei cataloghi: integrazione

La versione del gestore sviluppata nella linea di lavoro PR #16 è stata portata in un ramo dedicato e riallineata ai nuovi schemi materiali/skill. Il gestore ora:
- verifica tutte le schede materiali sorgente di una skill;
- accetta source_record_id soltanto se la fonte è una skill classificata;
- verifica prove di licenza e prove di verifica della skill;
- blocca la rimozione di materiali ancora referenziati da source_record_id o source_material_ids;
- controlla i collegamenti esistenti prima di leggere o modificare i cataloghi;
- normalizza i percorsi radice per Windows e Linux.

Limiti espliciti: nessun blocco per scritture concorrenti, nessuna transazione multi-catalogo, ricerca testuale e non semantica; collegamenti reciproci, manifesti e prove delle implementazioni e frontmatter completo restano nel validatore generale. Le scritture devono essere serializzate dal coordinatore e il validatore completo va eseguito prima di usare i cataloghi per pianificare.

Questa integrazione è separata dalla linea PR #16 per evitare di modificare la verifica del motore semantico mentre si riallinea il gestore. La duplicazione temporanea del file catalog_manager.py tra le due linee dovrà essere consolidata prima della fusione finale.

## Stato del coordinatore universale

Il coordinatore non è ancora implementato. Le quattro skill di pianificazione, adattamento, ricerca e verifica forniscono procedure iniziali, ma non sostituiscono il motore. Prima dell'implementazione vanno riconciliate:
- la correzione dell'adattatore semantico PR #14 e la prova reale PR #15;
- il ramo cataloghi PR #16, che deriva da PR #8 e non include PR #14;
- la nuova provenienza multipla e le prove di licenza introdotte nelle PR #19/#20;
- il gestore cataloghi aggiornato in questa linea.

Il primo componente del coordinatore dovrà essere un pianificatore indipendente dalla piattaforma e un validatore deterministico del piano; l'esecuzione degli strumenti resterà separata.
