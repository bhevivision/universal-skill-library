# Modello strutturale

Versione del modello: 1.0. Stato: definizione documentata; schemi e controlli automatici implementati e sottoposti a test strutturali. Il modello è ancora in revisione e non approvato definitivamente.

## 1. Regola
Il modello distingue ciò che si vuole ottenere, i metodi disponibili, l'esecuzione e la dimostrazione del risultato. Una distinzione concettuale non obbliga a creare un componente software separato.

## 2. Elementi e informazioni essenziali

### Obiettivo
Risultato richiesto, ambito, vincoli e criteri di accettazione. Non è una lista di attività: le attività vengono ricavate nella pianificazione.

### Capacità
Abilità richiesta al sistema, indipendente dalla piattaforma. Struttura approvata:
- Identificativo
- Nome
- Descrizione
- Categoria
- Risultato atteso
- Criteri di verifica
- Capacità collegate (facoltativo)
- Skill associate (facoltativo)
- Limitazioni (facoltativo)
- Stato

La registrazione non garantisce la disponibilità nell'ambiente corrente.

### Skill
Metodo organizzato e riutilizzabile. Il formato canonico è una cartella Agent Skills con SKILL.md obbligatorio e risorse facoltative quali scripts/, references/ e assets/.

Il frontmatter standard richiede soltanto name e description. La specifica ammette campi facoltativi come license, compatibility, metadata e allowed-tools (sperimentale). Il nome deve rispettare i vincoli ufficiali e corrispondere alla cartella.

La proposta minima interna (nome, descrizione, capacità associate, istruzioni, ingresso, risultato, versione) è un modello informativo, non un nuovo frontmatter. Istruzioni e risorse stanno nel pacchetto standard. Relazioni e dati di catalogo non previsti dallo standard vanno tenuti fuori dal frontmatter obbligatorio. Il formato concreto del catalogo sarà deciso nella fase successiva.

La versione può essere gestita dal sistema di libreria e, se utile, anche come metadata.version stringa. Non si presume che tutte le piattaforme interpretino allo stesso modo i metadati aggiuntivi.

### Implementazione
Realizzazione concreta che rende eseguibile una skill. Quando applicabile, registra skill/versione servita, ambiente, modalità di esecuzione, requisiti, dipendenze, stato e prove. Più implementazioni possono servire la stessa skill. La compatibilità con gli agenti distingue `mode=any` (nessun vincolo specifico sull'agente; restano obbligatori i controlli reali di piattaforma, strumenti e permessi) da `mode=specific` (elenco non vuoto di agenti e intervalli di versione ammessi). Non si deduce mai la compatibilità dalla sola modalità `any`.

### Strumento
Risorsa concreta richiesta o utilizzata. Registra, se pertinente, nome/tipo, disponibilità, requisiti, limiti e autorizzazioni. Non è automaticamente parte della libreria delle skill.

### Agente
Ambiente operativo. Registra tipo, capacità effettive, strumenti e integrazioni accessibili, limiti, permessi e disponibilità. Non si presume che possieda tutte le capacità dichiarate dal fornitore.

### Ruolo
Responsabilità logica definita da compiti, confini e autorità decisionali. Può essere svolta da agente, componente o combinazione.

### Attività
Unità pianificabile e verificabile. Informazioni essenziali: identificativo, descrizione, risultato atteso, contratto operativo, dipendenze, assegnazioni, criteri, stato, prove ed esito.

### Piano di esecuzione
Insieme organizzato di attività, ordine, dipendenze, assegnazioni, gruppi paralleli e condizioni di avanzamento. È aggiornabile; le revisioni non cancellano la storia.

### Dipendenza
Relazione esplicita che indica quale risultato o condizione è necessario e quale attività ne è bloccata. Nella prima versione non serve un sistema generale di relazioni tra ogni tipo di oggetto.

### Contratto operativo
Specifica associata all'attività: ingressi e formato, risultato e formato, prerequisiti, vincoli, limiti, strumenti e permessi pertinenti. È concettualmente distinto ma può essere una sezione strutturata dell'attività.

### Criterio di accettazione
Condizione osservabile definita prima della verifica. Deve consentire un esito PASS, FAIL o NON VERIFICABILE. I criteri finali derivano dall'obiettivo; quelli intermedi non possono contraddirli.

### Verifica
Controllo eseguito sul risultato rispetto ai criteri. Registra criterio, metodo, esito, riferimenti alle prove e limiti. Nei casi ad alto rischio o dove l'indipendenza è importante, il verificatore deve essere distinto dall'esecutore.

### Prova
Reperto consultabile che indica che cosa è stato osservato o eseguito, quale risultato reale è stato ottenuto e quando. Può essere file, estratto di registro, risultato di comando, identificativo o osservazione documentata. Non deve esporre dati riservati.

### Stato
Attributo, non componente autonomo. Per le attività, il percorso minimo distingue: DA FARE, IN CORSO, ESEGUITA, RISULTATO PRODOTTO, VERIFICATA, ACCETTATA, BLOCCATA, NON VERIFICABILE e FALLITA. Il progetto è COMPLETATO solo dopo l'accettazione dei criteri richiesti. Gli stati delle skill (stabile, sperimentale, non verificata, deprecata, bloccata) sono una tassonomia proposta da formalizzare.

### Decisione
Scelta registrata con contenuto, motivazione, ambito, responsabile, momento e conseguenze. Le decisioni importanti non si sovrascrivono: quelle successive indicano quali sostituiscono.

## 3. Relazioni principali
1. Un obiettivo richiede capacità e definisce criteri di accettazione.
2. Una capacità può essere soddisfatta da più skill; una skill può contribuire a più capacità.
3. Una skill può avere più implementazioni.
4. Un'implementazione può richiedere strumenti, ambiente e autorizzazioni.
5. Un agente rende disponibili soltanto implementazioni e strumenti realmente accessibili.
6. Un ruolo assegna responsabilità a un agente o componente; non richiede corrispondenza uno-a-uno.
7. Il piano organizza attività; le dipendenze ne vincolano l'ordine.
8. Ogni attività ha contratto operativo, risultato atteso e criteri adeguati.
9. Un'attività può usare skill, implementazioni, strumenti e agenti differenti.
10. La verifica confronta il risultato con i criteri e fa riferimento a prove.
11. Gli stati cambiano in seguito a esecuzione, verifica e decisione.
12. Le decisioni autorizzano o bloccano azioni, approvano eccezioni o determinano ripianificazioni.

## 4. Duplicazioni evitate
- Ingresso e risultato sono parti del contratto operativo.
- Criteri, metodi di verifica e prove sono distinti.
- Stato è un attributo, non un agente.
- Ruolo è una responsabilità, non necessariamente un agente.
- Dipendenza è una relazione, non una skill.
- Decisione è un evento registrato, non lo stato.
- Implementazione è distinta dalla skill e dagli strumenti.
- Gestione di stato e prove è responsabilità trasversale, non necessariamente componente autonomo.

## 5. Ruoli logici
| Ruolo | Responsabilità | Confine |
|---|---|---|
| Direttore del progetto | Obiettivo, criteri, eccezioni e approvazione finale. | Non dirige manualmente ogni attività. |
| Manager delle skill | Scomposizione, ricerca, selezione, dipendenze, alternative e lacune. | Non dichiara verificati risultati non controllati. |
| Gestore della libreria | Catalogo, versioni, metadati e stato delle skill. | La pubblicazione non certifica il funzionamento. |
| Esecutore | Svolge attività con implementazioni e strumenti autorizzati. | Non si auto-attribuisce l'accettazione finale. |
| Verificatore | Controlla risultati e prove. | Dichiara limiti e conflitti d'interesse. |
| Gestore di stato e prove | Registra transizioni, prove, errori, permessi e decisioni. | Può essere una funzione condivisa. |

## 6. Classificazione delle lacune
Il sistema distingue capacità non rappresentata, skill mancante, implementazione incompatibile, strumento assente, autorizzazione assente, problema tecnico e attività impossibile. Prima di creare una skill cerca riuso o adattamento. Una skill nuova è pubblicabile soltanto dopo controlli strutturali, test isolati, controlli di sicurezza e approvazione.

## 7. Questioni rinviate
Formato del catalogo; schema dei metadati esterni; versionamento e compatibilità; protocollo degli adattatori; persistenza di attività, prove e decisioni; transizioni degli stati; livelli di rischio e approvazione; scelta del motore di coordinamento sulla base di test riproducibili.
