# Glossario del modello strutturale

Le definizioni sono concettuali: non obbligano a creare una classe, un servizio o un agente separato per ogni elemento.

| Elemento | Definizione e funzione |
|---|---|
| Obiettivo | Risultato che l'utente vuole ottenere; guida capacità e criteri di accettazione. |
| Capacità | Ciò che il sistema deve essere in grado di fare; indipendente da skill e piattaforme. |
| Skill | Metodo organizzato e riutilizzabile per svolgere un compito; pacchetto portabile Agent Skills. |
| Implementazione | Realizzazione concreta di una skill in un ambiente; può variare senza cambiare la skill canonica. |
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

### Capacità, skill e implementazione
- Capacità: che cosa deve poter fare il sistema.
- Skill: come svolgere il compito, in forma riutilizzabile.
- Implementazione: con quale realizzazione concreta viene eseguita la skill.

Esempio: capacità “analizzare un PDF”; skill “estrarre, organizzare e verificare le informazioni”; implementazione “eseguire la procedura con uno script Python in un ambiente autorizzato”. La presenza di una capacità non ne prova la disponibilità. La presenza di una skill non prova che funzioni. L'implementazione deve essere compatibile e verificata.

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
