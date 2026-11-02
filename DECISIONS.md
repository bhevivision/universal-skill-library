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
| P-008 | Cataloghi JSON con schemi per singole voci e contenitori completi. | Implementato per il modello precedente; da adeguare al nuovo modello. |
| P-009 | Metadati di selezione espliciti: capacità, ingressi, risultati, prerequisiti, vincoli, rischio e prove. | Da formalizzare negli schemi aggiornati. |
| P-010 | Una dichiarazione stabile/verificata richiede prove esistenti e riferite allo stesso oggetto. | Controlli presenti nel profilo precedente; estensione necessaria. |
| P-011 | Il frontmatter SKILL.md viene interpretato come YAML sicuro, con controllo delle chiavi duplicate e dei campi standard name/description. | Controllo specifico del profilo Agent Skills; non è requisito universale. |
| P-012 | La compatibilità agente è esplicita e verificata nell'ambiente reale. | Modello precedente contempla any/specific; regole definitive da collaudare. |
| P-013 | Layout logico separato per acquisizione, originale, schede, cataloghi, adattamenti e verifiche. | Esempio documentato; layout fisico definitivo subordinato ai test sui diversi pacchetti. |
| P-014 | Analizzatori specifici per formato, con percorso di conservazione per formati sconosciuti. | Da implementare e testare. |

## Questioni aperte
| ID | Questione | Prossima azione |
|---|---|---|
| O-001 | Schema e versionamento dei record esterni. | Definire campi, valori sconosciuti, provenienza e retrocompatibilità. |
| O-002 | Layout fisico per file singoli, cartelle, archivi, pacchetti compositi e riferimenti remoti. | Progettare casi di prova prima di fissare il layout. |
| O-003 | Integrità, impronte, duplicati e aggiornamento delle versioni. | Definire procedura e prove riproducibili. |
| O-004 | Profili e analizzatori per formati conosciuti e sconosciuti. | Stabilire interfaccia minima e comportamento quando manca un analizzatore. |
| O-005 | Analisi di sicurezza e gestione di pacchetti non fidati. | Definire estrazione isolata, scansione e regole di non esecuzione. |
| O-006 | Validatore: separazione tra controlli generali e controlli specifici di formato. | Aggiornare codice e test; l'attuale requisito SKILL.md non è universale. |
| O-007 | Validità temporale delle prove. | Definire soglie per tipo e rischio della skill. |
| O-008 | Compatibilità esatta degli agenti e delle loro versioni. | Verificare su Claude Code e Codex. |
| O-009 | Protocollo comune degli adattatori. | Verificare differenze reali tra piattaforme. |
| O-010 | Persistenza di piani, attività, prove, decisioni e cronologia. | Definire il modello minimo runtime. |
| O-011 | Stati e transizioni. | Definire regole e casi di errore. |
| O-012 | Operazioni che richiedono approvazione umana. | Costruire matrice di rischio e reversibilità. |
| O-013 | Motore di coordinamento. | Riprendere ORCA e confrontare candidati con test end-to-end. |
| O-014 | Test funzionali per ogni skill. | Definire requisiti specifici per categoria. |
| O-015 | Inclusione di skill personali o specifiche di progetto. | Applicare le regole di separazione del progetto prima di ogni acquisizione. |

## Specifica Agent Skills consultata
Fonte ufficiale: https://agentskills.io/specification

La specifica descrive un formato basato su cartella e SKILL.md, con name e description nel frontmatter. È un profilo supportato dalla libreria. Le sue regole si applicano quando un pacchetto viene dichiarato o analizzato come Agent Skills; non si applicano a ogni materiale acquisito. La verifica documentale non dimostra interoperabilità su agenti reali.

## Ricerca ORCA preesistente
La ricerca preliminare del 14 ottobre 2026 non viene ripetuta né scartata. Restano da esaminare il log del workflow Cognitive Continuous Validation, le discrepanze dei conteggi, la coerenza tra registry/runtime/dipendenze e le prove end-to-end.

## Regola di aggiornamento
Quando una proposta viene approvata o una questione risolta, registrare scelta, motivazione e prove. Non cancellare decisioni superate: marcarle come sostituite e indicare la decisione successiva.