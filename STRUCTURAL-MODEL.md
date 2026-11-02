# Modello strutturale

Versione del modello: 1.0. Stato: APPROVATO. L'approvazione riguarda il modello concettuale e le regole di acquisizione; non equivale a implementazione completa, certificazione delle skill o approvazione di ogni dettaglio tecnico dei cataloghi.

## 1. Regola fondamentale
La libreria può ricevere qualsiasi pacchetto o materiale, anche quando non è ancora riconosciuto come skill. La sua identità e struttura originali vengono preservate. La classificazione avviene dopo l'acquisizione e può restare provvisoria o sconosciuta.

Uniformità nella descrizione esterna; libertà nella struttura interna; verificabilità nell'uso.

## 2. Elementi del modello

### Materiale acquisito
Qualsiasi elemento ricevuto: file singolo, cartella, archivio, albero di file, pacchetto binario, insieme di documenti, riferimento remoto o elemento non ancora comprensibile. La libreria registra ciò che riceve senza richiedere un formato minimo comune.

### Pacchetto originale
Copia conservata dell'elemento ricevuto, con contenuti, nomi e struttura intatti. Non viene riscritto, normalizzato o adattato preventivamente. Si registrano provenienza, data, metodo di acquisizione e impronta crittografica quando disponibile. Per riferimenti remoti si conserva il riferimento e, quando possibile, una copia identificata; l'assenza di copia locale deve essere esplicita.

La conservazione integra non garantisce che il contenuto sia sicuro o eseguibile. Il materiale non viene eseguito durante l'acquisizione o l'analisi ordinaria.

### Classificazione
Valutazione separata dall'acquisizione. Categorie possibili: skill; possibile skill; strumento; agente o ambiente operativo; flusso operativo; documentazione o risorsa; pacchetto composito; non classificato. La classificazione registra motivazione, fonte e confidenza, e può essere aggiornata senza modificare l'originale.

### Scheda descrittiva esterna
Record della libreria indipendente dal formato originale. Contiene, quando noti: identificativo stabile, provenienza, nome originale, posizione del pacchetto, tipo di contenuto, formato rilevato, classificazione, descrizione, versione o impronta, dipendenze, riferimenti, lacune, limitazioni, date e stati. I campi non conosciuti sono assenti o esplicitamente sconosciuti; non vengono dedotti senza prova.

La scheda non sostituisce né riscrive la documentazione originale. La struttura e il formato del record saranno formalizzati negli schemi tecnici.

### Capacità
Abilità richiesta al sistema, indipendente dalla piattaforma. Struttura approvata: identificativo; nome; descrizione; categoria; risultato atteso; criteri di verifica; capacità collegate facoltative; skill associate facoltative; limitazioni facoltative; stato. La registrazione non garantisce la disponibilità nell'ambiente corrente.

### Skill
Metodo organizzato e riutilizzabile per produrre un risultato. Una classificazione come skill richiede elementi sufficienti a descriverne almeno lo scopo e il comportamento atteso; se le informazioni non bastano, resta possibile skill o non classificato.

Non esiste un formato interno obbligatorio per l'acquisizione. Agent Skills, con cartella e SKILL.md, è un profilo supportato e interoperabile. Altri formati possono essere conservati e descritti senza conversione. L'assenza di SKILL.md non è motivo per rifiutare un pacchetto.

### Implementazione
Realizzazione concreta che rende eseguibile una skill in un ambiente. Registra, quando applicabile, skill e versione servita, ambiente, modalità di esecuzione, requisiti, dipendenze, stato e prove. Più implementazioni possono servire la stessa skill.

### Adattamento
Elemento derivato e separato dall'originale, creato per rendere un pacchetto utilizzabile in una piattaforma o in un contesto specifico. Registra origine, versione di partenza, modifiche, motivo, destinazione e prove. Non sostituisce né sovrascrive il pacchetto originale. Un adattamento non viene approvato automaticamente.

### Strumento, agente e ruolo
Lo strumento è una risorsa concreta richiesta o utilizzata. L'agente è un ambiente operativo con capacità, strumenti, integrazioni, limiti e permessi effettivi. Il ruolo è una responsabilità logica definita da compiti, confini e autorità; può essere svolta da agente, componente o combinazione.

### Obiettivo, attività e piano
L'obiettivo descrive risultato, ambito, vincoli e criteri di accettazione. L'attività è un'unità pianificabile e verificabile con risultato atteso, contratto operativo, dipendenze, assegnazioni, criteri, stato, prove ed esito. Il piano organizza attività, ordine, dipendenze, gruppi paralleli e condizioni di avanzamento; le revisioni non cancellano la storia.

### Contratto operativo
Specifica associata all'attività: ingressi e formato, risultato e formato, prerequisiti, vincoli, limiti, strumenti e permessi pertinenti. È concettualmente distinto ma può essere una sezione strutturata dell'attività.

### Criterio di accettazione, verifica e prova
Il criterio è una condizione osservabile definita prima della verifica e consente PASS, FAIL o NON VERIFICABILE. La verifica confronta un risultato con i criteri e registra metodo, esito, limiti e riferimenti alle prove. La prova è un reperto consultabile che documenta ciò che è stato osservato o eseguito, quale risultato reale è stato ottenuto e quando. Ogni verifica è riferita a una precisa versione, ambiente e procedura.

### Stato e decisione
Lo stato è un attributo, non un componente autonomo. Per le attività si distinguono almeno: DA FARE, IN CORSO, ESEGUITA, RISULTATO PRODOTTO, VERIFICATA, ACCETTATA, BLOCCATA, NON VERIFICABILE e FALLITA. Il progetto è COMPLETATO solo dopo l'accettazione dei criteri richiesti. La decisione è una scelta registrata con contenuto, motivazione, ambito, responsabile, momento e conseguenze; le decisioni successive indicano quali sostituiscono.

## 3. Dimensioni di stato indipendenti per il materiale
- Acquisizione: non ricevuto, ricevuto, conservato, incompleto, errore di conservazione.
- Classificazione: non esaminato, in analisi, classificato, provvisorio, non classificato.
- Documentazione: sconosciuta, parziale, completa rispetto alle informazioni disponibili.
- Verifica: non verificata, in corso, superata, fallita, non verificabile.
- Utilizzabilità: non valutata, disponibile con condizioni, richiede adattamento, incompatibile, bloccata.

Queste dimensioni non si sostituiscono a vicenda. Un elemento può essere conservato ma non classificato; classificato ma documentato parzialmente; verificato ma non compatibile con l'ambiente corrente.

## 4. Relazioni principali
1. Un elemento acquisito ha un pacchetto originale o un riferimento esplicitamente dichiarato.
2. Una scheda descrittiva esterna descrive il materiale senza alterarlo.
3. Un pacchetto può contenere più elementi e ricevere più classificazioni collegate.
4. Una skill soddisfa una o più capacità; una capacità può essere coperta da più skill.
5. Una skill può avere più implementazioni e adattamenti.
6. Un adattamento rimanda sempre all'originale e alla versione di partenza.
7. Un'implementazione può richiedere strumenti, ambiente e autorizzazioni.
8. Un agente rende disponibili soltanto implementazioni e strumenti realmente accessibili.
9. Il piano organizza attività; le dipendenze ne vincolano l'ordine.
10. Ogni attività ha contratto operativo, risultato atteso e criteri adeguati.
11. La verifica confronta il risultato con i criteri e fa riferimento a prove.
12. Stati e decisioni sono registrati senza cancellare la cronologia.

## 5. Ruoli logici
| Ruolo | Responsabilità | Confine |
|---|---|---|
| Direttore del progetto | Obiettivo, criteri, eccezioni e approvazione finale. | Non dirige manualmente ogni attività. |
| Gestore dell'acquisizione | Riceve e conserva materiale e provenienza. | Non decide da solo che sia una skill. |
| Analizzatore/classificatore | Esamina e classifica con motivazioni e incertezza esplicita. | Non modifica l'originale e non certifica il funzionamento. |
| Manager delle skill | Scomposizione, ricerca, selezione, dipendenze, alternative e lacune. | Non dichiara verificati risultati non controllati. |
| Gestore della libreria | Catalogo, versioni, metadati e stati. | La pubblicazione non certifica il funzionamento. |
| Esecutore | Svolge attività con implementazioni e strumenti autorizzati. | Non si auto-attribuisce l'accettazione finale. |
| Verificatore | Controlla risultati e prove. | Dichiara limiti e conflitti d'interesse. |
| Gestore di stato e prove | Registra transizioni, prove, errori, permessi e decisioni. | Può essere una funzione condivisa. |

## 6. Classificazione delle lacune
Il sistema distingue capacità non rappresentata, skill mancante, implementazione incompatibile, strumento assente, autorizzazione assente, documentazione mancante, dipendenza non disponibile, problema tecnico e attività impossibile. Prima di creare una skill cerca riuso o adattamento. Una skill nuova è ammessa all'uso soltanto dopo controlli pertinenti, test isolati, controlli di sicurezza e approvazione.

## 7. Questioni tecniche rinviate
Formato e versionamento dei record esterni; layout fisico per file singoli, cartelle, archivi e riferimenti remoti; impronte e integrità; analizzatori e profili di formato; scansione di sicurezza; protocollo degli adattatori; persistenza runtime; transizioni dettagliate degli stati; livelli di rischio; scelta del motore di coordinamento sulla base di test riproducibili.

Queste questioni non annullano l'approvazione del modello concettuale. Nessun layout tecnico deve essere dichiarato universale prima di averne verificato la copertura sui diversi tipi di pacchetto.