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
| P-001 | Contratto operativo distinto ma memorizzabile come parte dell'attività. | Raccomandata. |
| P-002 | Stato come attributo con transizioni per tipo di oggetto. | Proposta. |
| P-003 | Gestione di stato, prove e decisioni come responsabilità trasversale. | Proposta. |
| P-004 | Ruoli come responsabilità logiche, non agenti obbligatori. | Proposta. |
| P-005 | Catalogo e relazioni fuori dal frontmatter obbligatorio di SKILL.md. | Necessario per preservare compatibilità. |
| P-006 | Versione gestita dalla libreria; metadata.version facoltativo. | Da validare sulle piattaforme. |
| P-007 | Nuove skill sottoposte a controlli, test isolati, sicurezza e approvazione. | Da formalizzare. |
| P-008 | Cataloghi JSON con schemi per singole voci e contenitori completi. | Implementato; 19 test automatici e CI superati (run 32). |
| P-009 | Metadati di selezione espliciti: capacità, ingressi, risultati, prerequisiti, vincoli, rischio e prove. | Proposta tecnica v1, da approvare. |
| P-010 | Una dichiarazione stabile/verificata richiede prove esistenti e riferite allo stesso oggetto. | Implementato nei controlli v1; 19 test automatici e CI superati (run 32). |\n| P-011 | Il frontmatter SKILL.md viene interpretato come YAML sicuro, con controllo delle chiavi duplicate e dei campi standard name/description. | Implementato; 19 test automatici e CI superati (run 32). |\n| P-012 | La compatibilità agente è esplicita: `any` oppure `specific` con elenco di agenti e versioni. | Modello dati v1 implementato; compatibilità effettiva ancora da collaudare con agenti reali. |

## Questioni aperte
| ID | Questione | Prossima azione |
|---|---|---|
| O-001 | Revisione e approvazione della struttura v1. | Revisione con esempi e risultati dei controlli. |
| O-002 | Validità temporale delle prove. | Definire soglie per tipo e rischio della skill. |
| O-003 | Compatibilità esatta degli agenti e delle loro versioni. | Verificare su Claude Code e Codex. |
| O-004 | Protocollo comune degli adattatori. | Verificare differenze reali tra piattaforme. |
| O-005 | Persistenza di piani, attività, prove, decisioni e cronologia. | Definire il modello minimo runtime. |
| O-006 | Stati e transizioni. | Definire regole e casi di errore. |
| O-007 | Operazioni che richiedono approvazione umana. | Costruire matrice di rischio e reversibilità. |
| O-008 | Motore di coordinamento. | Riprendere ORCA e confrontare candidati con test end-to-end. |
| O-009 | Test funzionali per ogni skill. | Definire requisiti specifici per categoria. |
| O-010 | Skill personali o specifiche di progetto. | Definire inclusione e separazione prima di ricollocare file esistenti. |

## Specifica Agent Skills consultata
Fonte ufficiale: https://agentskills.io/specification

La specifica richiede una cartella con SKILL.md; il frontmatter richiede name e description. license, compatibility, metadata e allowed-tools sono facoltativi; allowed-tools è sperimentale. Il nome deve rispettare i vincoli ufficiali e corrispondere alla cartella. Sono ammesse risorse facoltative come scripts, references e assets.

Conseguenza: nessun campo proprietario obbligatorio nel frontmatter. I metadati aggiuntivi della libreria restano esterni. Questa è una verifica documentale, non un test di interoperabilità su agenti reali.

## Ricerca ORCA preesistente
La ricerca preliminare del 14 ottobre 2026 non viene ripetuta né scartata. Restano da esaminare il log del workflow Cognitive Continuous Validation, le discrepanze dei conteggi, la coerenza tra registry/runtime/dipendenze e le prove end-to-end.

## Regola di aggiornamento
Quando una proposta viene approvata o una questione risolta, registrare scelta, motivazione e prove; non cancellare le decisioni superate, ma marcarle come sostituite.
