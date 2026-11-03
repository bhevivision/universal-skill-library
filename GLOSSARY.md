# Glossario del modello strutturale

Le definizioni sono concettuali: non obbligano a creare una classe, un servizio o un agente separato per ogni elemento.

| Elemento | Definizione e funzione |
|---|---|
| Materiale acquisito | Qualsiasi file, cartella, archivio, pacchetto, riferimento o insieme di risorse ricevuto dalla libreria, anche se non ancora classificato. |
| Pacchetto originale | Copia conservata del materiale ricevuto, mantenuta integra e non modificata preventivamente. |
| Scheda descrittiva | Record esterno che descrive il materiale e registra provenienza, classificazione, informazioni note e lacune. |
| Classificazione | Valutazione che identifica il materiale come skill, possibile skill, strumento, agente, flusso, risorsa, pacchetto composito o non classificato. |
| Capacità | Ciò che il sistema deve essere in grado di fare; indipendente da skill e piattaforme. |
| Skill | Metodo organizzato e riutilizzabile per svolgere un compito; non è vincolato a un unico formato di file. |
| Profilo di formato | Regole specifiche per riconoscere e controllare un formato, per esempio Agent Skills. Non è un requisito generale di acquisizione. |
| Implementazione | Realizzazione concreta di una skill in un ambiente; può variare senza cambiare il metodo originale. |
| Adattamento | Derivato separato dall'originale, preparato per una piattaforma o un contesto specifico e tracciato rispetto alla fonte. |
| Strumento | Risorsa usata durante il lavoro: browser, terminale, programma, API o dispositivo. |
| Agente | Sistema operativo che riceve incarichi e può usare skill e strumenti. |
| Ruolo | Responsabilità assegnata a un agente o componente; non richiede un agente dedicato. |
| Attività | Unità concreta di lavoro con risultato atteso e condizioni di verifica. |
| Piano di esecuzione | Organizzazione delle attività, assegnazioni e relazioni di dipendenza. |
| Dipendenza | Relazione per cui un'attività necessita del risultato o della condizione prodotta da un'altra. |
| Contratto operativo | Specifica di ingressi, risultati, prerequisiti, vincoli e condizioni di esecuzione. |
| Criterio di accettazione | Condizione osservabile che il risultato deve soddisfare. |
| Verifica | Controllo che confronta il risultato reale con i criteri e registra un esito. |
| Prova | Evidenza concreta e consultabile che sostiene un'affermazione sull'esecuzione o sul risultato. |
| Stato | Condizione corrente di un elemento; è un attributo, non un componente autonomo. |
| Decisione | Scelta registrata che autorizza, blocca, accetta o modifica il comportamento successivo. |

## Distinzioni fondamentali

### Acquisizione, classificazione e uso
- Acquisito: il materiale è stato ricevuto e la sua conservazione è stata registrata.
- Classificato: è stata formulata una valutazione sulla sua natura, con motivazione e confidenza.
- Documentato: le informazioni disponibili sono state registrate; possono restare lacune.
- Verificato: un controllo adeguato ha prodotto un esito documentato per una versione e un ambiente precisi.
- Utilizzabile: il materiale soddisfa le condizioni del compito, della piattaforma e delle autorizzazioni.
Questi stati sono indipendenti: un pacchetto può essere conservato senza essere riconosciuto come skill.

### Capacità, skill e implementazione
- Capacità: che cosa deve poter fare il sistema.
- Skill: quale metodo organizzato può svolgere il compito.
- Implementazione: con quale realizzazione concreta viene eseguita la skill.

Esempio: capacità “analizzare un PDF”; skill “estrarre, organizzare e verificare le informazioni”; implementazione “eseguire la procedura con uno script Python in un ambiente autorizzato”. La presenza di una capacità non ne prova la disponibilità. La presenza di una skill non prova che funzioni. L'implementazione deve essere compatibile e verificata.

### Originale e adattamento
L'originale è conservato senza riscrittura o conversione preventiva. Un adattamento è una copia derivata, separata, con modifiche, destinazione e provenienza documentate. Un adattamento non sostituisce la fonte.

### Formato comune e formati acquisibili
Agent Skills è un profilo supportato, non il formato obbligatorio di ogni skill o materiale. Un elemento privo di SKILL.md può essere acquisito, conservato e classificato; potrà essere reso utilizzabile solo dopo le verifiche necessarie.

### Esecuzione, verifica e accettazione
- Eseguito: l'azione è stata compiuta o tentata.
- Risultato prodotto: esiste un risultato osservabile.
- Verificato: un controllo adeguato ha prodotto un esito documentato.
- Accettato: i criteri applicabili risultano soddisfatti e la decisione è registrata.
- Completato: tutti i criteri richiesti per l'obiettivo sono accettati, oppure le eccezioni sono state approvate esplicitamente.

### Strumento, agente e ruolo
Lo strumento fornisce una funzione; l'agente opera; il ruolo definisce una responsabilità.

### Stato e decisione
Lo stato descrive la condizione corrente. La decisione registra una scelta e la motivazione. Una decisione può causare una transizione di stato, ma non coincide con essa.