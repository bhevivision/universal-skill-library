# Registro delle decisioni

Questo documento distingue decisioni confermate, proposte e questioni aperte. Le decisioni confermate sono vincolanti per il progetto; le proposte non lo sono finché non vengono approvate.

## Decisioni confermate
| ID | Decisione | Conseguenza |
|---|---|---|
| D-001 | Libreria indipendente dalle piattaforme. | Il modello non dipende da un singolo agente o fornitore. |
| D-002 | Agent Skills è un formato supportato e interoperabile, non il formato obbligatorio di acquisizione. | Le skill Agent Skills possono essere validate con il relativo profilo; gli altri materiali non vengono esclusi. |
| D-003 | Capacità, Skill e Implementazione sono distinte. | Esigenza, metodo e realizzazione concreta non si confondono. |
| D-004 | È approvata la struttura delle capacità riportata in STRUCTURAL-MODEL.md. | I campi facoltativi restano facoltativi. |
| D-005 | Documentazione strutturata più controlli automatici. | La documentazione da sola non dimostra conformità o funzionamento. |
| D-006 | Semplicità e campi obbligatori ridotti al necessario. | Ogni dato aggiuntivo deve avere una ragione concreta. |
| D-007 | Il modello strutturale v1 è approvato prima della ricollocazione delle skill esistenti. | L'approvazione non autorizza a modificare gli originali; inventario e verifica seguono fasi separate. |
| D-008 | Il lavoro strutturale non modifica direttamente main. | Le modifiche restano isolate nel ramo dedicato. |
| D-009 | Completamento richiede criteri soddisfatti e prove. | Esecuzione, prodotto, verifica, accettazione e completamento restano distinti. |
| D-010 | La libreria accetta qualsiasi pacchetto o materiale, anche non ancora riconosciuto come skill. | L'acquisizione precede e non dipende dalla classificazione. |
| D-011 | L'originale viene conservato integralmente e non viene riscritto o adattato preventivamente. | Ogni trasformazione avviene su una copia o in un'area separata; l'integrità viene registrata quando possibile. |
| D-012 | Descrizione e classificazione sono esterne al pacchetto originale. | Il materiale conserva identità e struttura. |
| D-013 | Non esiste un formato minimo obbligatorio per l'acquisizione. | Sono ammessi file, cartelle, archivi, pacchetti, documenti, riferimenti remoti e formati sconosciuti. |
| D-014 | Gli adattamenti sono separati dall'originale e tracciati rispetto alla fonte. | Nessun adattamento sovrascrive o sostituisce la fonte. |
| D-015 | Acquisizione, classificazione, documentazione, verifica e utilizzabilità sono dimensioni indipendenti. | Un elemento conservato non è automaticamente skill, verificato o utilizzabile. |
| D-016 | Anche il materiale non interpretabile può essere conservato e registrato come non classificato. | L'incertezza viene dichiarata; non si inventano struttura, funzione o dipendenze. |
| D-017 | Ogni verifica si riferisce alla precisa versione/contenuto, ambiente e procedura controllati. | Una verifica non si trasferisce automaticamente a versioni o piattaforme differenti. |

## Proposte architetturali e tecniche
| ID | Proposta | Stato |
|---|---|---|
| P-001 | Contratto operativo distinto ma memorizzabile come parte dell'attività. | Raccomandata. |
| P-002 | Stato come attributo con transizioni per tipo di oggetto. | Da dettagliare. |
| P-003 | Gestione di stato, prove e decisioni come responsabilità trasversale. | Raccomandata. |
| P-004 | Ruoli come responsabilità logiche, non agenti obbligatori. | Raccomandata. |
| P-005 | Catalogo e relazioni fuori dal frontmatter obbligatorio di SKILL.md. | Confermata da D-012; dettagli tecnici da definire. |
| P-006 | Versione gestita dalla libreria; metadata.version facoltativo. | Da validare sulle piattaforme. |
| P-007 | Nuove skill sottoposte a controlli, test isolati, sicurezza e approvazione prima dell'uso. | Principio confermato; procedura tecnica da definire. |
| P-008 | Cataloghi JSON con schemi per singole voci e contenitori completi. | Implementato per i cataloghi v1 correnti; restano aperte migrazioni e compatibilità tra versioni future. |
| P-009 | Metadati di selezione espliciti: capacità, ingressi, risultati, prerequisiti, vincoli, rischio e prove. | Criteri documentati in `docs/SKILL-SELECTION.md`; formalizzazione completa e popolamento dei cataloghi restano aperti. |
| P-010 | Una dichiarazione stabile/verificata richiede prove esistenti e riferite allo stesso oggetto. | Controlli di integrità e riferimenti alle prove implementati; soglie temporali di validità ancora da definire. |
| P-011 | Il frontmatter SKILL.md viene interpretato come YAML sicuro, con controllo delle chiavi duplicate e dei campi standard name/description. | Implementato nel validatore esclusivamente per il profilo Agent Skills; non è requisito universale. |
| P-012 | La compatibilità agente è esplicita e verificata nell'ambiente reale. | Il modello dei dati distingue compatibilità generica e specifica; prove reali su piattaforme e versioni restano aperte. |
| P-013 | Layout logico separato per acquisizione, originale, schede, cataloghi, adattamenti e verifiche. | Layout di acquisizione v1 implementato per i tipi supportati; adattamenti e aree di verifica operative restano da realizzare. |
| P-014 | Analizzatori specifici per formato, con percorso di conservazione per formati sconosciuti. | Conservazione dei formati sconosciuti e analisi statica limitata implementate; analizzatori aggiuntivi restano da realizzare. |

## Questioni aperte
| ID | Questione | Prossima azione |
|---|---|---|
| O-001 | Migrazioni e retrocompatibilità delle versioni future degli schemi dei record. | Definire strategia di migrazione senza invalidare i record v1 già acquisiti. |
| O-003 | Gestione delle versioni successive dello stesso materiale e delle modifiche alla fonte. | Definire come collegare versioni distinte senza sovrascrivere l'originale precedente. |
| O-004 | Analizzatori per formati aggiuntivi e relative prove specifiche. | Definire priorità e contratti per PDF, documenti d'ufficio, archivi e altri formati. |
| O-005 | Estrazione isolata, scansione e gestione avanzata dei pacchetti non fidati. | Progettare un ambiente controllato prima di introdurre estrazione o analisi attiva. |
| O-007 | Validità temporale delle prove. | Definire soglie per tipo e rischio della skill. |
| O-008 | Compatibilità esatta degli agenti e delle loro versioni. | Verificare su Claude Code e Codex. |
| O-009 | Protocollo comune degli adattatori. | Verificare differenze reali tra piattaforme. |
| O-010 | Persistenza di piani, attività, prove, decisioni e cronologia. | Definire il modello minimo runtime. |
| O-011 | Stati e transizioni. | Definire regole e casi di errore. |
| O-012 | Operazioni che richiedono approvazione umana. | Costruire matrice di rischio e reversibilità. |
| O-013 | Motore di coordinamento. | Riprendere ORCA e confrontare candidati con test end-to-end. |
| O-014 | Test funzionali per ogni skill. | Definire requisiti specifici per categoria. |
| O-015 | Inclusione di skill personali o specifiche di progetto. | Applicare le regole di separazione del progetto prima di ogni acquisizione. |
| O-016 | Versionamento del ciclo di vita dei materiali e migrazione degli schemi. | Distinguere una nuova versione della fonte da un duplicato e definire migrazioni riproducibili. |

## Questioni chiuse con prove

| ID | Questione risolta | Evidenza |
|---|---|---|
| O-002 | Layout di acquisizione v1 per file, cartelle, archivi opachi, pacchetti e riferimenti remoti. | `scripts/acquire_material.py`, `tests/test_acquisition_component.py`, `tests/test_heterogeneous_intake.py`; suite Linux/Windows nel run `41545326945`. |
| O-006 | Separazione tra controlli generali di acquisizione/integrità e controllo specifico del profilo Agent Skills. | `scripts/validate_library.py`, `tests/test_validate_library.py`; suite Linux/Windows nel run `41545326945`. |
| O-017 | Impronte SHA-256, algoritmi versionati e rilevamento dei duplicati per i tipi di materiale supportati. | `scripts/acquire_material.py`, `scripts/material_integrity.py` e test dedicati; suite Linux/Windows nel run `41545326945`. |
| O-018 | Schemi v1 dei cataloghi e dei record per materiali, capacità, skill e implementazioni. | `schemas/*-catalog.schema.json`, schemi dei record e `scripts/validate_library.py`; validatore superato nel run `41545326945`. |

## Specifica Agent Skills consultata
Fonte ufficiale: https://agentskills.io/specification

La specifica descrive un formato basato su cartella e SKILL.md, con name e description nel frontmatter. È un profilo supportato dalla libreria. Le sue regole si applicano quando un pacchetto viene dichiarato o analizzato come Agent Skills; non si applicano a ogni materiale acquisito. La verifica documentale non dimostra interoperabilità su agenti reali.

## Ricerca ORCA preesistente
La ricerca preliminare del 14 ottobre 2026 non viene ripetuta né scartata. Restano da esaminare il log del workflow Cognitive Continuous Validation, le discrepanze dei conteggi, la coerenza tra registry/runtime/dipendenze e le prove end-to-end.

## Regola di aggiornamento
Quando una proposta viene approvata o una questione risolta, registrare scelta, motivazione e prove. Non cancellare decisioni superate: marcarle come sostituite e indicare la decisione successiva.