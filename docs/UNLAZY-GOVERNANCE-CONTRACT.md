# UNLAZY — nessun «fatto» senza verifica

Stato: **requisito normativo del progetto; integrazione tecnica centrale da progettare e implementare**.

UNLAZY è una regola trasversale obbligatoria della Libreria universale delle skill. Non è una skill facoltativa e non deve essere duplicata manualmente nei singoli pacchetti. La futura architettura deve fornire un unico componente centrale, richiamato automaticamente da ogni skill e da ogni ruolo operativo, compresi coordinatore, esecutore e verificatore.

Questo documento è il riferimento canonico. In caso di sintesi, adattamento o traduzione per una piattaforma, i requisiti qui definiti restano prevalenti.

## 1. Scopo

Impedire che un lavoro venga dichiarato completato senza che sia stato dimostrato.

Il rischio più costoso non è soltanto commettere un errore: è dichiarare di aver fatto qualcosa quando non è stato dimostrato. Un errore visibile può essere corretto; una dichiarazione falsa può essere creduta e diventare la base di attività successive. UNLAZY impedisce dichiarazioni premature e contaminazione del lavoro.

Una riga non è finita quando è stata eseguita: è finita quando è possibile dimostrarla.

## 2. Regola fondamentale

**NESSUN «FATTO» SENZA VERIFICA.**

| Frase | Significato | Valore |
|---|---|---|
| «L'ho fatto» | Dichiarazione di esecuzione | Zero, da sola |
| «L'ho verificato» | Controllo eseguito | Vale soltanto se il controllo è coerente |
| «Ecco la prova» | Reperto rileggibile | È ciò che può autorizzare COMPLETATO |

Un'affermazione dell'agente non è prova di se stessa. Se l'unico sostegno di una riga è ciò che l'agente dichiara, la riga non è verificata.

## 3. Quando applicare UNLAZY

Applicazione obbligatoria quando il lavoro:
- ha più di un passaggio o produce qualcosa che altri useranno;
- riguarda file, codice, archivi di dati, configurazioni, migrazioni o consegne;
- richiede un piano, una lista di controllo, un collaudo o un rapporto;
- porta l'agente a usare parole come «fatto», «completato», «risolto», «funziona» o «a posto».

Per una singola azione banale la verifica resta obbligatoria, ma non serve creare un file di controllo per una sola riga. Il file di controllo è obbligatorio quando l'attività ha almeno tre righe o dura oltre una singola risposta.

UNLAZY non si applica a saluti o semplici domande di conoscenza. Non può essere omessa soltanto perché un'attività sembra semplice.

## 4. Scomposizione del progetto in attività

Catena obbligatoria:

`PROGETTO → ATTIVITÀ → LISTA DI CONTROLLO → RIGA → ESECUZIONE → VERIFICA → PROVA → PASS/FAIL → COMPLETATO`

Un'attività è un blocco di lavoro che termina con un risultato verificabile.

Prima di iniziare si definisce «fatto significa»: una frase che descrive lo stato osservabile del mondo quando l'attività è conclusa. Se non è possibile descrivere come verificarla, l'attività deve essere ulteriormente scomposta.

Regole:
- ogni attività ha normalmente da 3 a 10 righe; meno di 3 richiede di valutare se sia una riga di un'altra attività, più di 10 richiede di valutare una suddivisione;
- attività diverse non si mescolano;
- si chiude un'attività, si presenta il rapporto e si attende autorizzazione prima di iniziare la successiva.

## 5. Costruzione della lista di controllo

Una riga contiene una sola azione e un solo risultato verificabile. Va formulata come affermazione controllabile, non come intenzione.

Per ogni riga, **prima dell'esecuzione**, si scrivono:
- azione e risultato atteso;
- criterio e procedura di verifica;
- prova attesa.

Le attività di pulizia, ripristino e riallineamento della documentazione sono righe vere e richiedono prove proprie.

Se la verifica prevista si rivela errata o impossibile, l'agente non la modifica autonomamente: si ferma e chiede autorizzazione.

## 6. Campi e stati di ogni riga

Ogni riga mantiene distinti cinque campi:

1. **DICHIARAZIONE** — cosa l'agente dichiara di aver eseguito.
2. **VERIFICA** — controllo definito prima dell'esecuzione.
3. **PROVA** — reperto reale prodotto dal controllo.
4. **RISULTATO** — PASS o FAIL.
5. **STATO** — avanzamento della riga.

Stati ammessi:
- `DA FARE`
- `FATTO`
- `VERIFICATO`
- `COMPLETATO`
- `FAIL`
- `NON VERIFICABILE`
- `DA RIVERIFICARE`
- `FUORI SCOPE`

`FATTO` registra soltanto una dichiarazione e non autorizza avanzamenti. `VERIFICATO` richiede una prova presente. `COMPLETATO` richiede inoltre che la prova dimostri proprio ciò che la riga dichiara.

Il controllo avviene riga per riga durante il lavoro, non soltanto alla fine.

## 7. Requisiti di una verifica valida

Una verifica è valida soltanto se soddisfa tutte e cinque le proprietà:

1. **Coerente:** controlla esattamente ciò che la riga dichiara. L'esistenza di un file non dimostra che il suo contenuto sia corretto; la presenza del codice non dimostra che funzioni; l'esecuzione di un comando non dimostra che l'effetto sia avvenuto.
2. **Alla destinazione:** controlla il sistema reale nel quale l'effetto doveva prodursi, non soltanto l'artefatto preparato alla partenza.
3. **Isolata:** può superare soltanto se la specifica riga è vera; non deve poter passare per una causa alternativa.
4. **Indipendente:** rilegge la fonte reale e non la sola dichiarazione, memoria o copia preparata dall'agente.
5. **Innocua:** non lascia residui, non altera dati reali e non espone segreti. I dati di prova devono essere eliminati e l'eliminazione verificata con una riga dedicata.

Se manca una proprietà, il controllo non è una verifica valida.

## 8. Prove e gradi di evidenza

Una prova è un reperto rileggibile che consente a un'altra persona di arrivare alla stessa conclusione senza fidarsi dell'agente. Deve indicare:
1. cosa è stato eseguito o riletto (comando, percorso, interrogazione o passaggio);
2. uscita reale o estratto sufficiente (valore, righe, byte, identificativo, esito);
3. quando è stato acquisito.

Non sono prove: il solo codice scritto, il solo file creato, la dichiarazione dell'agente, un comando senza errori, un risultato che sembra corretto, un «dovrebbe funzionare» o una risposta OK non accompagnata dal controllo dell'effetto.

Ogni prova è etichettata:

| Grado | Significato | Formula da riportare |
|---|---|---|
| **A — dimostrato** | Osservato su dati o sistemi reali | «Dimostrato con dati reali» |
| **B — verificato leggendo** | Dedotto da codice o documenti, senza osservare l'effetto | «Verificato leggendo il codice/documento; effetto non osservato» |
| **C — osservazione** | Indizio coerente, non separabile da altre cause | «Osservazione, non prova» |

Solo il grado A dimostra direttamente il comportamento reale. B e C devono mantenere la propria etichetta nel risultato e nel rapporto; non possono essere presentati come A.

## 9. Condizioni di arresto obbligatorio

L'agente si ferma immediatamente, senza modificare nulla, quando:
- una verifica dà FAIL;
- una verifica è impossibile;
- per verificare dovrebbe uscire dal perimetro autorizzato;
- sarebbe necessario modificare verifica o criterio di accettazione;
- la riga è ambigua e ammette interpretazioni con prove differenti;
- emerge una decisione non prevista.

L'agente comunica la riga interessata, cosa è accaduto, quali verifiche e prove sono già disponibili e attende istruzioni. Non sceglie autonomamente una soluzione, anche se sembra ovvia.

## 10. Condizioni per dichiarare COMPLETATO

Un'attività è COMPLETATA soltanto quando:
1. tutte le righe sono COMPLETATO oppure sono NON VERIFICABILE/FUORI SCOPE, dichiarate esplicitamente e accettate dal committente;
2. il risultato complessivo («fatto significa») è stato verificato come insieme;
3. il file di controllo, scritto dopo i fatti, corrisponde allo stato reale e non lo contraddice;
4. il rapporto è stato presentato al committente.

Dopo il rapporto l'agente si ferma. Non avvia l'attività successiva senza nuova autorizzazione esplicita.

Un progetto è COMPLETATO soltanto quando lo sono tutte le sue attività, con lo stesso criterio.

## 11. Gestione dei FAIL

In caso di FAIL:
1. fermarsi e non ritoccare il lavoro;
2. distinguere tra difetto del lavoro, difetto della verifica e difetto della formulazione della riga;
3. descrivere il motivo per cui si ritiene presente una specifica causa;
4. proporre la correzione e attendere autorizzazione.

È vietato modificare la verifica per farla passare senza autorizzazione esplicita. Il FAIL resta nel file di controllo anche dopo la correzione: non si cancella la storia. Si riprova soltanto dopo aver identificato e documentato la causa.

## 12. Gestione delle verifiche impossibili

Quando la verifica prevista non può essere eseguita, lo stato è `NON VERIFICABILE`, mai COMPLETATO.

Si registrano:
- motivo concreto dell'impossibilità;
- accesso, strumento o dato necessario per renderla possibile;
- ciò che resta dimostrabile e il relativo grado di evidenza.

La limitazione rimane visibile nel rapporto fino a quando una verifica valida non sarà possibile.

## 13. Distinzione tra fatto, verificato e dimostrato

| Termine | Significato | Sostegno |
|---|---|---|
| **Fatto** | È stata eseguita un'azione | Dichiarazione dell'agente |
| **Verificato** | È stato eseguito un controllo coerente | Controllo e relativo esito |
| **Dimostrato** | Esiste un reperto rileggibile | Prova consultabile |

Azione eseguita e obiettivo raggiunto non sono equivalenti. Si verifica l'effetto nello stato reale, non il solo tentativo o comando.

## 14. Scadenza e invalidazione delle verifiche

Ogni riga COMPLETATA dichiara quali modifiche potrebbero invalidarne la prova. Ogni modifica successiva deve essere valutata rispetto alle righe già completate: quelle coinvolte passano a `DA RIVERIFICARE` e vengono controllate di nuovo prima della chiusura dell'attività.

La verifica vale per la versione, l'ambiente, la procedura e il perimetro effettivamente controllati. Anche i controlli automatici devono essere riesaminati quando cambia ciò che dovrebbero controllare.

## 15. File di controllo dell'attività

Ogni attività con almeno tre righe o che dura oltre una singola risposta ha un proprio file:

`<progetto>/controlli/CONTROLLO_<nome-attività>.md`

Non si usa un unico file globale per attività appartenenti a progetti diversi. Il file viene aggiornato durante il lavoro, riga per riga, dopo il fatto reale; non deve descrivere anticipatamente attività non ancora eseguite.

Quando disponibili, usare i riferimenti:
- `references/file_di_controllo.md` — modello del file e esempio compilato, inclusi FAIL e NON VERIFICABILE;
- `references/tipi_di_prova.md` — scelta della verifica e della prova coerenti con ogni tipo di riga;
- `references/casi_reali.md` — casi di errore e regole conseguenti.

Se questi riferimenti non sono presenti nel progetto, la loro assenza va dichiarata: non si presume di averli letti.

## 16. Difese contro le dichiarazioni premature

- Non usare «fatto», «completato», «funziona» o «risolto» senza mostrare nello stesso contesto la prova che li sostiene. In assenza di prova: «eseguito, non ancora verificato».
- Non usare «dovrebbe», «credo» o «presumibilmente» come risultati. Dichiarare il grado di evidenza e il limite.
- Il rapporto include FAIL, NON VERIFICABILE e DA RIVERIFICARE con la stessa visibilità dei successi.
- La verifica e la prova attesa si definiscono prima dell'esecuzione.
- Ogni dubbio sulla pertinenza di una prova viene dichiarato, non nascosto.

## 17. Obbligo architetturale per tutte le skill e tutti i ruoli

La Libreria deve implementare UNLAZY come **componente centrale unico e obbligatorio**:
- ogni skill deve dichiarare la dipendenza dal contratto UNLAZY centrale;
- il coordinatore deve richiamare UNLAZY prima di avviare un'attività, durante i passaggi di esecuzione e prima di accettarne il risultato;
- esecutori e verificatori devono rispettare lo stesso contratto e non possono disattivarlo o sostituirlo con regole locali più deboli;
- le skill nuove, importate, adattate o aggiornate non sono ammissibili all'esecuzione finché la loro conformità al requisito centrale non è stata verificata;
- le istruzioni specifiche di una skill possono aggiungere controlli, ma non ridurre o aggirare i requisiti UNLAZY;
- il richiamo deve essere automatico e verificabile a livello di architettura/runtime, non affidato alla memoria dell'agente o alla copia manuale del testo in ogni skill.

Il componente centrale deve gestire almeno: definizione preventiva di attività e criteri; registrazione delle cinque parti di ogni riga; validità e grado delle prove; stati e transizioni; arresti e richieste di autorizzazione; conservazione dei FAIL; invalidazione delle prove; file di controllo e rapporto conclusivo.

## 18. Stato di implementazione e criterio di ammissione

L'approvazione di questo contratto documentale **non dimostra che il richiamo automatico sia già implementato**.

La funzionalità sarà dichiarata implementata soltanto dopo:
- interfaccia e contratto del componente centrale definiti;
- richiamo automatico dimostrato per ogni percorso di esecuzione delle skill e per tutti i ruoli;
- impossibilità tecnica di aggirare o disattivare il controllo senza autorizzazione esplicita;
- prove automatiche e prove operative su skill differenti e su più percorsi di esecuzione;
- test dei casi FAIL, NON VERIFICABILE, DA RIVERIFICARE, FUORI SCOPE, autorizzazioni e modifiche successive;
- verifica indipendente, rapporto con reperti consultabili e approvazione del committente.

Fino a quel momento lo stato è: **REQUISITO REGISTRATO — IMPLEMENTAZIONE NON ANCORA VERIFICATA**.
