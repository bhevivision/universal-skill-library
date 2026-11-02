# Registro delle decisioni

Questo documento distingue decisioni confermate, proposte e questioni aperte. Una proposta documentata non diventa vincolante finché non viene approvata o validata.

## Decisioni confermate
| ID | Decisione | Conseguenza |
|---|---|---|
| D-001 | Libreria indipendente dalle piattaforme. | La skill canonica è riutilizzabile da agenti compatibili differenti. |
| D-002 | Agent Skills è il formato comune di base. | Non si introduce un formato proprietario incompatibile. |
| D-003 | Capacità, Skill e Implementazione sono distinte. | Esigenza, metodo e realizzazione concreta non si confondono. |
| D-004 | È approvata la struttura delle capacità riportata in STRUCTURAL-MODEL.md. | I campi facoltativi restano facoltativi. |
| D-005 | Documentazione strutturata più controlli automatici. | La documentazione da sola non dimostra conformità o funzionamento. |
| D-006 | Semplicità e campi obbligatori ridotti al necessario. | Ogni dato aggiuntivo deve avere una ragione concreta. |
| D-007 | Il modello viene completato prima di ricollocare o convertire le skill esistenti. | Nessuna skill esistente viene spostata in questa fase. |
| D-008 | Il lavoro strutturale non modifica direttamente main. | Le modifiche sono isolate nel ramo dedicato. |
| D-009 | Completamento richiede criteri soddisfatti e prove. | Esecuzione, prodotto, verifica, accettazione e completamento restano distinti. |

## Proposte architetturali
| ID | Proposta | Stato |
|---|---|---|
| P-001 | Contratto operativo concettualmente distinto ma memorizzabile come parte dell'attività nella prima versione. | Raccomandata, da confermare nella progettazione dati. |
| P-002 | Stato come attributo con transizioni per tipo di oggetto. | Proposta. |
| P-003 | Gestione di stato, prove e decisioni come responsabilità trasversale, senza obbligo di servizio separato. | Proposta. |
| P-004 | Ruoli come responsabilità logiche, non come agenti obbligatori. | Proposta. |
| P-005 | Catalogo capacità e relazioni skill-capacità fuori dal frontmatter obbligatorio di SKILL.md. | Necessario per preservare compatibilità; formato concreto da scegliere. |
| P-006 | Versione gestita dal sistema della libreria; metadata.version facoltativo. | Da validare con le piattaforme di destinazione. |
| P-007 | Nuove skill sottoposte a controlli strutturali, test isolati, sicurezza e approvazione prima della pubblicazione. | Da formalizzare nei controlli. |

## Questioni aperte
| ID | Questione | Prossima azione |
|---|---|---|
| O-001 | Formato del catalogo capacità e relazioni. | Confrontare soluzioni leggere. |
| O-002 | Metadati esterni alla skill standard. | Progettare un indice esterno minimo e provarlo. |
| O-003 | Versioni di skill, implementazioni e adattatori. | Definire compatibilità, deprecazione e ripristino. |
| O-004 | Interfaccia comune degli adattatori. | Verificare differenze reali tra piattaforme. |
| O-005 | Persistenza di piano, stato, prove, decisioni e cronologia. | Definire il minimo modello runtime. |
| O-006 | Stati e transizioni. | Definire regole e casi di errore. |
| O-007 | Operazioni che richiedono approvazione umana. | Costruire matrice di rischio e reversibilità. |
| O-008 | Motore di coordinamento. | Riprendere ORCA e confrontare candidati con test end-to-end. |
| O-009 | Soglia minima di qualità delle skill. | Definire controlli strutturali, riferimenti, sicurezza e test funzionali. |
| O-010 | Criteri per skill personali o specifiche di progetto. | Definire inclusione e separazione prima di ricollocare file esistenti. |

## Specifica Agent Skills consultata
Fonte ufficiale: https://agentskills.io/specification

La specifica consultata richiede una cartella con SKILL.md; il frontmatter richiede name e description. license, compatibility, metadata e allowed-tools sono facoltativi; allowed-tools è sperimentale. Il nome deve rispettare i vincoli ufficiali e corrispondere alla cartella. Sono ammesse risorse facoltative come scripts, references e assets.

Conseguenza: nessun campo proprietario obbligatorio nel frontmatter. I metadati aggiuntivi della libreria vanno conservati esternamente o, con cautela, nel campo standard metadata. Non si presume che tutte le piattaforme li interpretino allo stesso modo.

Questa è una verifica documentale della specifica, non un test di interoperabilità su Claude Code, Codex o altri agenti.

## Ricerca ORCA preesistente
La ricerca preliminare del 14 ottobre 2026 non viene ripetuta né scartata. Restano da esaminare il log del workflow Cognitive Continuous Validation, le discrepanze dei conteggi, la coerenza tra registry/runtime/dipendenze e le prove end-to-end. I dati già raccolti sono preliminari, non una certificazione tecnica.

## Regola di aggiornamento
Quando una proposta viene approvata o una questione risolta, registrare scelta, motivazione e prove; aggiornare modello e roadmap; non cancellare le decisioni superate, ma marcarle come sostituite.
