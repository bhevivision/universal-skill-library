# Analisi di riuso delle sei risorse

**Stato:** analisi documentale e di provenienza iniziale completata; verifica funzionale delle risorse esterne ancora aperta.  
**Ramo:** `research/six-resources-analysis-v1`  
**Data di rilevazione:** 2026-11-03  
**Perimetro:** esclusivamente il progetto Libreria universale delle skill e sistema intelligente di coordinamento.

## 1. Scopo e criterio di decisione

Le sei risorse non verranno importate come blocchi indistinti. Per ciascuna distinguiamo:

- risorsa originale e sua natura (standard, raccolta di skill, metodo, registro o motore);
- capacità e procedure effettivamente presenti;
- dipendenze e prerequisiti;
- provenienza e condizioni di riuso;
- contenuti universali e contenuti legati a una piattaforma o a un progetto;
- destinazione nella libreria;
- verifiche ancora necessarie.

Esiti ammessi: **riutilizzare**, **adattare**, **integrare come riferimento**, **escludere** oppure **bloccare in attesa di prove**. La presenza di un file o di una descrizione non equivale a una skill verificata.

## 2. Stato attuale della libreria di destinazione

La struttura esistente è già articolata: documentazione architetturale, modello strutturale, schemi JSON, strumenti di acquisizione e classificazione, verificatore e test automatici.

Sono presenti quattro cataloghi, ma al controllo del ramo `main` contengono zero voci:

- `catalog/materials.json`: `materials: []`;
- `catalog/skills.json`: `skills: []`;
- `catalog/capabilities.json`: `capabilities: []`;
- `catalog/implementations.json`: `implementations: []`.

Gli schemi esistenti sono già utili per il lavoro:
- la scheda materiale registra provenienza, acquisizione, classificazione, documentazione, verifica, utilizzabilità, dipendenze e riferimenti mancanti;
- la voce skill distingue ambito `universal/platform/project`, ciclo di vita, segnali di selezione, ingressi, uscite, prerequisiti, vincoli, rischio e prove;
- la voce implementazione distingue requisiti, strumenti, autorizzazioni, compatibilità con agenti e stato di verifica.

**Conseguenza:** non serve inventare un secondo catalogo. Dobbiamo valorizzare quello già definito, verificando prima che gli schemi e le procedure attuali siano coerenti con l'obiettivo.

L'inventario `docs/EXISTING-SKILLS-INVENTORY.md` è esplicitamente preliminare e registra un'ispezione statica precedente, non un'acquisizione ufficiale. Va aggiornato con le nuove prove, non trattato come certificazione.

## 3. Analisi delle sei risorse

### 3.1 UNLAZY — controllo con prove

**Natura:** metodo operativo dettagliato per pianificare, verificare e dichiarare il completamento.

**Capacità osservate**
- scomposizione progetto → attività → righe verificabili;
- definizione anticipata del criterio di verifica e della prova attesa;
- separazione fra dichiarazione, verifica, prova, risultato e stato;
- distinzione fra prova osservata, verifica documentale e semplice indizio;
- verifica indipendente, isolata, innocua e svolta sul sistema di destinazione;
- gestione di FAIL, verifica impossibile e attività fuori perimetro;
- invalidazione delle prove dopo modifiche successive;
- chiusura solo dopo controllo complessivo e rapporto.

**Dipendenze dichiarate nel documento**
- `references/tipi_di_prova.md`;
- `references/file_di_controllo.md`;
- `references/casi_reali.md`.

Questi tre file non compaiono nell'albero completo del ramo `main` del deposito attuale. Non è quindi possibile dichiarare completo il pacchetto UNLAZY.

**Riuso proposto**
- Riutilizzare il nucleo universale: criterio anticipato, prova rileggibile, verifica dell'effetto reale, stati espliciti, gestione delle anomalie e invalidazione delle verifiche.
- Adattare le regole di arresto e autorizzazione al modello dei permessi della libreria.
- Non imporre un file di controllo separato per ogni azione banale: mantenere la proporzionalità, senza perdere la prova.
- Integrare la procedura nella skill di verifica e nel ciclo di ammissione delle skill.

**Licenza e provenienza:** nel file non è dichiarata una licenza né una fonte esterna. Il riuso interno nel progetto può essere valutato, ma la redistribuzione pubblica del testo originale o di una sua derivazione resta **da chiarire**. Conservare attribuzione e origine effettiva quando saranno documentate.

**Esito:** ADATTARE; dipendenze mancanti da recuperare. Nessuna prova funzionale ancora eseguita.

### 3.2 Archivista — gestione documentale e storica

**Natura:** istruzione per la gestione di fascicoli documentali di libri, non una procedura universale già pronta.

**Capacità osservate**
- non scrivere o modificare senza autorizzazione esplicita;
- distinguere Documento, File, Prova, Fonte, Versione, Opera e Pubblicazione;
- non inventare dati mancanti;
- conservare la storia e registrare i cambiamenti come nuovi eventi;
- segnalare provenienza mancante, contraddizioni e questioni aperte;
- validare struttura, relazioni, documenti, storia e aspetti tecnici.

**Dipendenza dichiarata**
- `reference/regole-complete.md`.

Il riferimento non compare nell'albero completo del deposito attuale. Le 17 sezioni elencate sono specifiche del fascicolo di un libro e non devono essere trasferite nella libreria universale.

**Riuso proposto**
- Estrarre il principio di sola lettura prima dell'approvazione;
- separare oggetto documentale, file fisico, prova, fonte e versione;
- mantenere una cronologia non distruttiva;
- rendere espliciti dati mancanti e contraddizioni;
- applicare questi principi al registro dei materiali, alle prove e alle decisioni della libreria.
- Escludere cartelle, nomi, sezioni e regole specifiche KDP/Obsidian, salvo che siano richieste da un'implementazione verticale separata.

**Licenza e provenienza:** non dichiarate nel file. Riuso del testo originale e redistribuzione da chiarire.

**Esito:** ADATTARE i principi universali; BLOCCARE la validazione completa finché manca il riferimento.

### 3.3 Find Skills — ricerca e scoperta di skill esterne

**Natura:** procedura di ricerca, valutazione e installazione di skill nell'ecosistema aperto. Il testo presente nel deposito corrisponde in larga parte alla skill pubblicata da Vercel nel repository `vercel-labs/skills`, directory `skills/find-skills`.

**Capacità osservate**
- traduzione del bisogno in dominio e attività;
- ricerca nel catalogo skills.sh e tramite CLI;
- confronto delle alternative;
- valutazione di popolarità e reputazione della fonte;
- presentazione delle opzioni e installazione su richiesta.

**Verifica della fonte**
- repository originale: https://github.com/vercel-labs/skills
- file originale: https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md
- licenza del repository: MIT.

La copia presente nel deposito non contiene frontmatter Agent Skills né attribuzione esplicita. Prima di pubblicare una derivazione va aggiunta l'attribuzione e conservata la licenza MIT.

**Problemi rilevati nella procedura attuale**
- propone `-g -y`: installazione globale e conferma saltata;
- usa numero di installazioni e stelle come indicatori di fiducia, ma non sono prove di sicurezza, qualità o compatibilità;
- non impone una verifica tecnica approfondita del codice e delle dipendenze;
- non distingue ricerca, acquisizione, installazione e ammissione nella libreria;
- i dati di classifica e installazione sono variabili;
- la CLI corrente dichiara raccolta di telemetria anonima per classifica; la procedura deve informare l'utente e offrire la disattivazione prevista.

La documentazione corrente di skills.sh conferma `npx skills find` e `npx skills add`; l'installazione predefinita è nel progetto, mentre `-g` è globale. La versione corrente del pacchetto npm indica Node.js 22.20 o successivo: questo requisito va verificato al momento di ogni esecuzione, non fissato per sempre nel testo della skill.

**Riuso proposto**
- riutilizzare la ricerca e la presentazione delle alternative;
- separare scoperta, acquisizione isolata, analisi, verifica, approvazione e installazione;
- acquisire prima in area temporanea o isolata, mai direttamente nel catalogo operativo;
- richiedere verifica di contenuto, script, dipendenze, licenza, autorizzazioni e compatibilità;
- non installare globalmente e non saltare conferme per impostazione predefinita;
- non considerare popolarità o scansioni automatiche come certificazione.

**Esito:** RIUTILIZZARE DOPO ADATTAMENTO; licenza MIT verificata per la fonte Vercel, ma attribuzione e modifica della copia locale necessarie. Nessuna installazione è stata eseguita.

### 3.4 Agent Skills — standard aperto per il pacchetto skill

**Natura:** standard di formato, non motore di esecuzione e non raccolta di skill.

**Specifiche osservate**
- una cartella per skill;
- file obbligatorio `SKILL.md`;
- frontmatter YAML con `name` e `description` obbligatori;
- campi facoltativi `license`, `compatibility`, `metadata` e `allowed-tools`;
- risorse opzionali `scripts/`, `references/`, `assets/`;
- caricamento progressivo: metadati, istruzioni, risorse su richiesta;
- nome coerente con la cartella, in minuscolo, con lettere, numeri e trattini;
- descrizione che spiega cosa fa la skill e quando attivarla.

Fonti normative:
- specifica: https://agentskills.io/specification
- repository: https://github.com/agentskills/agentskills
- licenza del codice nel repository: Apache-2.0;
- documentazione: CC-BY-4.0, secondo le informazioni del repository.

**Limite fondamentale**
Agent Skills standardizza il pacchetto e il modo di descrivere istruzioni e risorse. Non definisce, da solo, un catalogo universale di capacità, un motore di esecuzione, il modello dei permessi, il coordinatore o la prova del funzionamento.

**Compatibilità con ORCA**
Il formato ORCA `skill.yaml` è un modello dichiarativo eseguibile con identificativi, ingressi, uscite, passaggi e riferimenti a capacità. Non è lo stesso formato di `SKILL.md`. Non dobbiamo sostituire lo standard scelto con `skill.yaml`. L'eventuale collegamento va realizzato separando:
1. pacchetto portabile Agent Skills;
2. contratto/capacità della libreria;
3. adattatore verso un motore esecutivo, eventualmente ORCA.

**Esito:** ADOTTARE come formato esterno delle skill. Mantenere separati formato, contratto interno, implementazione e motore.

### 3.5 Matt Pocock Skills — procedure di ingegneria

**Natura:** raccolta di skill Agent Skills per attività di progettazione e sviluppo. Repository: https://github.com/mattpocock/skills. Albero rilevato: 282 elementi; licenza MIT.

**Skill esaminate in modo mirato**
- `tdd`: test prima del codice, un'interfaccia verificabile alla volta, test indipendenti dalla realizzazione;
- `diagnosing-bugs`: costruire prima una prova riproducibile che fallisca sul difetto reale, minimizzare il caso, formulare ipotesi falsificabili, verificare la correzione e prevenire regressioni;
- `codebase-design`: interfacce semplici, moduli profondi, dipendenze iniettate, risultati espliciti e prove attraverso interfacce;
- `code-review`: revisione separata rispetto a standard e specifica; richiede un punto di confronto definito e, nella versione originale, agenti paralleli;
- `implement-spec`: traduzione di una specifica in implementazione verificabile.

**Dipendenze e limiti**
- alcune skill rimandano a file di supporto (per esempio esempi di test, regole di simulazione, approfondimenti di progettazione): non vanno copiate senza recuperare e analizzare tali riferimenti;
- la revisione parallela richiede un ambiente con agenti separati; dove non disponibile va prevista una modalità sequenziale indipendente;
- le convenzioni linguistiche di una skill non devono sovrascrivere il glossario e le decisioni architetturali della nostra libreria;
- la raccolta è orientata all'ingegneria del software: le procedure universali vanno isolate dalle istruzioni specifiche di GitHub, Codex, issue tracker o strumenti di sviluppo.

**Riuso proposto**
- TDD e revisione come procedure di verifica delle implementazioni;
- diagnosi basata su riproduzione, prova discriminante e ipotesi falsificabili;
- progettazione di interfacce e separazione delle responsabilità;
- scomposizione della specifica e criteri di accettazione;
- adattare i passaggi dipendenti da strumenti e agenti.

**Licenza:** MIT verificata nel repository; conservare il file di licenza e l'attribuzione nei materiali derivati.

**Esito:** RIUTILIZZARE SELETTIVAMENTE E ADATTARE. Le skill non sono ancora state importate né eseguite nella libreria.

### 3.6 ORCA — registro e motore di esecuzione

**Natura:** due progetti distinti e collegati:
- `agent-skill-registry`: definizioni di capacità, skill, vocabolario, schemi e cataloghi;
- `agent-skills`: motore Python che risolve ed esegue i flussi.

**Riferimenti già raccolti e mantenuti**
- registro, ramo `main`, commit rilevato: `b70a6f99cf01ca928a94231e5d7b1a1e82098612` nelle note di ricerca precedenti; la nuova ispezione ha rilevato un albero più recente da confrontare prima di fissare una versione;
- motore, ramo `master`, commit rilevato: `d9e3644e8aac6b75f327d973f94e187d2e8f789c`;
- versione dichiarata nel `pyproject.toml`: `1.0.2`;
- Python richiesto: `>=3.11`;
- dipendenze obbligatorie dichiarate: PyYAML e requests;
- dipendenze facoltative: PDF, web, OpenTelemetry, ASGI, MCP e adattatori per framework;
- licenza runtime e registro: Apache-2.0.

**Capacità dichiarate**
- capacità con contratti tipizzati;
- skill come flussi dichiarativi;
- collegamenti a esecutori differenti;
- composizione in grafo diretto aciclico (DAG);
- esecuzione sequenziale e parallela;
- stato cognitivo, tracciabilità, controlli di sicurezza e politiche;
- interfacce SDK, HTTP, MCP e adattatori per framework.

**Skill ORCA di interesse**
- `agent.orchestrate-from-prompt`: interpreta la richiesta, cerca e ordina skill/capacità, rileva lacune, costruisce e valida un piano, compila il DAG e applica un controllo autorizzativo. La descrizione dichiara che non esegue il piano.
- `agent.execute-from-plan`: riceve il piano compilato ed esegue i passaggi, restituendo stato, risultati per passaggio e stato finale.

**Prove CI recenti consultate il 2026-11-03**
- Smoke Verification run 401: concluso con successo; include verifica del registro, canarino del motore, esecuzione completa e controlli smoke.
- Governance Continuous Validation run 156: concluso con successo.
- Cognitive Continuous Validation run 137: fallito nel passaggio `Run cognitive quality gates`; la compilazione e pubblicazione del rapporto è riuscita. La causa specifica non è stata ricavata da questa lettura dei passaggi e resta sconosciuta.

Questi risultati sono prove di alcune verifiche automatiche del progetto ORCA sul commit indicato; non dimostrano che ORCA soddisfi tutti i requisiti della nostra libreria né che funzioni nel nostro ambiente Windows.

**Disallineamento già noto da non perdere**
I conteggi dichiarati dal README del registro, dal registro corrente, dal README runtime e dai riferimenti fissati nelle azioni CI non coincidono (159/37, 184/40, 184/39 e 192/39 nelle rilevazioni precedenti). Va confrontata la coppia esatta registro/runtime e il commit effettivamente usato da ogni prova.

**Riuso proposto**
- studiare e riutilizzare i contratti di capacità, il modello DAG, il tracciamento e le procedure di esecuzione;
- valutare il motore come implementazione sostituibile, non come fondamento obbligatorio della libreria;
- non copiare il catalogo ORCA integralmente: ogni capacità va mappata ai nostri requisiti, deduplicata e verificata;
- costruire un adattatore tra i pacchetti Agent Skills e i contratti eseguibili ORCA, se le prove dimostrano che è conveniente;
- mantenere distinta la decisione di piano dall'autorizzazione e dall'esecuzione.

**Esito:** RIFERIMENTO ARCHITETTURALE E CANDIDATO MOTORE; non ancora adottato. Apache-2.0 consente il riuso nei limiti della licenza e degli avvisi richiesti. Prima di un'integrazione reale servono confronto dei commit, analisi delle dipendenze, test mirati, prova isolata e prova su Windows.

## 4. Matrice decisionale consolidata

| Risorsa | Elementi da riutilizzare | Elementi da adattare/escludere | Licenza/provenienza | Stato |
|---|---|---|---|---|
| UNLAZY | prove, criteri, stati, arresto, invalidazione | riferimenti mancanti; dettagli da proporzionare | non dichiarata | Adattare, bloccata su completezza |
| Archivista | provenienza, storia, non sovrascrittura, approvazione | 17 sezioni e procedure specifiche libri | non dichiarata | Adattare, bloccata su riferimento |
| Find Skills | ricerca, confronto, scoperta | installazione globale automatica; popolarità come prova | fonte Vercel MIT, attribuzione da aggiungere | Adattare |
| Agent Skills | formato `SKILL.md`, pacchetto e caricamento progressivo | non è catalogo né motore | Apache-2.0 codice; CC-BY-4.0 documentazione | Adottare come formato |
| Matt Pocock Skills | TDD, diagnosi, progettazione, revisione | passaggi specifici degli strumenti e dipendenze dei riferimenti | MIT | Riuso selettivo |
| ORCA | contratti, DAG, esecuzione, stato, tracciabilità | formato `skill.yaml` distinto; adozione integrale non dimostrata | Apache-2.0 | Riferimento/candidato |

## 5. Regole di integrazione che emergono dall'analisi

1. Ogni materiale deve avere provenienza, versione o commit, licenza, impronta e riferimenti mancanti.
2. Ogni skill derivata deve indicare la fonte e la trasformazione effettuata.
3. La skill Agent Skills deve dichiarare in modo leggibile cosa fa, quando si attiva, prerequisiti, limiti e risorse richieste.
4. La scheda interna della libreria deve continuare a descrivere ambito, capacità, ingressi, uscite, dipendenze, rischi, permessi e prove: il frontmatter Agent Skills da solo non basta.
5. Una skill importata o adattata parte come `experimental` o `unverified`, mai come `stable` per il solo fatto di provenire da una fonte nota.
6. Nessuna installazione o esecuzione di codice esterno prima dell'ispezione isolata e dell'autorizzazione appropriata.
7. La prova di funzionamento deve essere separata dalla verifica del formato e dalla verifica della licenza.
8. Un motore esterno come ORCA deve restare sostituibile tramite un'interfaccia, senza rendere proprietario il formato della skill.

## 6. Lavoro ancora necessario prima dell'integrazione operativa

- recuperare e confrontare i tre riferimenti mancanti di UNLAZY;
- recuperare il riferimento completo di Archivista e chiarire la provenienza/licenza di entrambi i materiali;
- fissare la versione esatta della skill Vercel Find Skills e preparare la derivazione con attribuzione MIT;
- completare la selezione delle skill Matt Pocock e acquisire i relativi file di supporto necessari;
- confrontare gli ultimi commit del registro e del motore ORCA, identificare i commit usati dalle azioni CI e analizzare il rapporto del controllo cognitivo fallito;
- verificare il profilo di compatibilità Agent Skills rispetto agli schemi interni già presenti;
- definire test isolati e prove di ammissione prima di promuovere qualsiasi voce nei cataloghi.

## 7. Stato delle prove

| Attività | Stato |
|---|---|
| Ispezione dei file locali UNLAZY, Archivista e Find Skills | Eseguita a livello documentale |
| Controllo delle dipendenze dichiarate mancanti | Eseguito sull'albero completo del deposito |
| Verifica della fonte e licenza Vercel Find Skills | Eseguita a livello di repository e file |
| Verifica della specifica Agent Skills e licenze dichiarate | Eseguita a livello documentale |
| Ispezione di skill selezionate Matt Pocock e licenza | Eseguita a livello documentale |
| Ispezione di documentazione, versione, dipendenze e prove CI ORCA | Parziale; esiti CI e metadati raccolti |
| Esecuzione funzionale isolata delle sei risorse | Non eseguita |
| Integrazione nei cataloghi | Non eseguita |
| Verifica su Windows | Non eseguita |

**Conclusione:** l'analisi ha individuato materiale riutilizzabile e una strada concreta per accelerare la libreria. Non è ancora stata dichiarata alcuna delle sei risorse come skill funzionante o ammessa. Il passo successivo è completare la verifica delle dipendenze e delle fonti, quindi trasformare le procedure approvate in pacchetti Agent Skills e schede interne coerenti con gli schemi già esistenti.


## 8. Integrazione delle fonti recuperate dalla Library dell'utente

Dopo la prima stesura di questa analisi è stata eseguita una ricerca separata nella Library delle conversazioni precedenti. Sono emersi materiali che non erano presenti nell'albero GitHub del progetto e che correggono due valutazioni preliminari.

### UNLAZY: modello esteso già disponibile

È stato individuato il documento **“Studio e progettazione completa del sistema UNLAZY su fondazione OKF”**, di 2.109 righe, che descrive:
- analisi del modello OKF v0.2;
- distinzione tra conoscenza, fonte, versione, documento, prova, verifica, risultato e attestazione;
- requisiti, criteri, regole versionate, esecuzioni, ricevute, decisioni e Gate;
- modello dell'agente e limiti che gli impediscono di inventare prove, ignorare un blocco o sovrascrivere la storia.

È stato inoltre individuato il documento di struttura **UNLAZY-SYSTEM**, che specifica un sistema permanente separato dallo stato dei singoli progetti, con 14 documenti CORE, modelli di piano e registro verifiche, cartelle separate per pianificazione, esecuzione, verifica, prove e cronologia, oltre a 10 test avversari.

Questi documenti costituiscono fonti di approfondimento importanti e non devono essere confusi con i tre file esatti citati dalla skill (`tipi_di_prova.md`, `file_di_controllo.md`, `casi_reali.md`). La ricerca non ha ancora dimostrato che quei tre file esistano con quei nomi o che siano contenuti integralmente nei documenti più ampi. Il loro stato resta quindi **non recuperato**, mentre il modello UNLAZY più ampio è **recuperato e consultabile**.

Nuova decisione: non attendere quei tre file per estrarre il nucleo universale già documentato; mantenere però aperta la verifica delle differenze e degli esempi che potrebbero contenere.

### Archivista: fonte completa individuata

È stato individuato nella Library il documento **“ARCHIVISTA DEL LIBRO — Sistema Completo — File Unico”**, versione `TEMPLATE_MASTER_v3`, datato 09/08/2026. La descrizione del documento indica che unifica il Template Master, il vocabolario, il glossario, l'Archivio Aziendale e il registro delle versioni. È presente anche una versione precedente `TEMPLATE_MASTER_v1`.

Questa fonte permette di superare il blocco concettuale causato dal riferimento `reference/regole-complete.md` mancante nel deposito GitHub: il riferimento è stato recuperato come documento completo nella Library, ma non è ancora stato acquisito nel deposito del progetto né sottoposto a confronto riga per riga con la skill breve.

Nuova decisione: analizzare il documento v3 come fonte principale dell'Archivista, estrarre solo le regole trasferibili (identità distinte, provenienza, cronologia, versioni, non sovrascrittura, gestione dei mancanti e approvazione umana) e lasciare fuori la struttura delle 17 sezioni del libro e le regole specifiche KDP.

### Effetto sulla matrice decisionale

| Risorsa | Stato aggiornato |
|---|---|
| UNLAZY | Modello esteso recuperato dalla Library; tre riferimenti specifici ancora non individuati |
| Archivista | Documento completo TEMPLATE_MASTER_v3 recuperato dalla Library; acquisizione e confronto con la skill breve ancora da eseguire |

**Nota di provenienza:** i documenti recuperati dalla Library non sono ancora file versionati nel repository GitHub del progetto. Non vanno presentati come già acquisiti nel catalogo materiali. La loro presenza nella Library è una fonte recuperabile, non una prova di integrazione o funzionamento.
