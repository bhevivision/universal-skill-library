# Contratto tecnico — preparazione dei materiali

Versione: 1.1  
Componente: `scripts/material_preparer.py`  
Stato: contratto tecnico definito; implementazione presente, verifiche in corso sul ramo di lavoro.

## 1. Scopo

`material_preparer.py` è il componente di sola lettura che seleziona e prepara i contenuti di un materiale già acquisito, affinché possano essere forniti a un analizzatore statico o semantico.

Il componente:
- riceve l'identificativo del materiale, non un percorso arbitrario;
- usa `material_integrity.py` per risolvere e verificare il materiale;
- individua i file testuali ammessi secondo il profilo iniziale `bounded_text_v1`;
- legge i contenuti senza eseguirli;
- restituisce in memoria contenuti, impronte, dimensioni, conteggi e file esclusi;
- ricontrolla l'integrità del materiale prima di restituire il risultato.

Non classifica il materiale, non interpreta il significato dei contenuti, non approva proposte e non decide se una skill sia utilizzabile.

## 2. Posizione nel flusso

```text
materiale acquisito
       |
       v
material_integrity.py
       |
       v
material_preparer.py
       |
       +----> classificatore statico
       |
       +----> futuro analizzatore semantico
                    |
                    v
             proposta separata
                    |
                    v
       validazione indipendente delle prove
                    |
                    v
             approvazione umana
```

La preparazione non sostituisce la verifica indipendente delle prove. Un analizzatore non può trasformare il contenuto ricevuto in una prova attendibile senza conservare riferimenti e impronte verificabili.

## 3. Interfaccia pubblica

Prima versione: una sola operazione pubblica.

```python
prepare_material(root, material_id)
```

Esempio:

```python
result = prepare_material(root=".", material_id="acq.esempio")
```

Regole:
- `root` identifica la cartella principale della libreria.
- `material_id` deve identificare un solo record in `catalog/materials.json`.
- Non sono accettati percorsi di file o cartelle forniti direttamente dal chiamante.
- Il percorso effettivo viene ricavato esclusivamente dal record acquisito e verificato.
- Non sono previsti profili configurabili, estensioni personalizzate o limiti modificabili dal chiamante nella versione 1.
- Gli errori strutturali e di integrità non devono essere trasformati in un risultato apparentemente riuscito.

## 4. Dipendenza obbligatoria da material_integrity.py

Il preparatore deve usare le funzioni pubbliche del servizio comune:
- `load_material_record(root, material_id)`, per ottenere il record univoco;
- `verify_material(...)`, per controllare stato, percorso e impronta.

Non deve duplicare le funzioni interne di risoluzione dei percorsi o calcolo dell'impronta dell'originale.

### 4.1 Materiali locali

Per file, cartelle, archivi e pacchetti locali:
- lo stato ammesso è `preserved`;
- il risultato iniziale del controllo d'integrità deve essere `verified`;
- il percorso deve essere quello restituito dal servizio d'integrità;
- il preparatore deve interrompersi se il controllo restituisce `blocked` o `failed`;
- al termine deve ripetere il controllo, usando come impronta attesa quella verificata all'inizio;
- se il controllo finale non è `verified`, non deve restituire contenuti come risultato valido.

Mappatura degli esiti:
- integrità `blocked` → preparazione `blocked`;
- integrità `failed` → preparazione `failed`.

### 4.2 Riferimenti remoti

Per `remote_reference`:
- sono ammessi gli stati `received` e `preserved`;
- il servizio d'integrità deve restituire `not_applicable`;
- il contenuto non deve essere visitato, scaricato o preparato;
- il risultato del preparatore è `not_available`, con elenco dei file vuoto e impronta del contenuto pari a `null`.

`not_applicable` del servizio d'integrità non equivale a una verifica positiva del contenuto remoto.

## 5. Profilo iniziale bounded_text_v1

Il profilo riproduce i limiti già presenti nel classificatore statico.

### 5.1 Estensioni ammesse

Confronto senza distinzione tra maiuscole e minuscole:

```python
TEXT_EXTENSIONS = {
    ".md", ".markdown", ".txt", ".rst", ".json", ".yaml", ".yml",
    ".toml", ".py", ".js", ".ts", ".sh", ".ps1", ".bat", ".xml",
    ".html", ".css"
}
```

Non si deduce il formato dal solo nome del materiale. La selezione si basa sull'estensione del singolo file.

### 5.2 Limiti

```python
MAX_FILE_BYTES = 256 * 1024
MAX_TOTAL_BYTES = 1024 * 1024
MAX_FILES = 100
```

Significato:
- massimo 256 KiB per singolo file;
- massimo 1 MiB complessivo di file selezionati;
- massimo 100 file selezionati.

I limiti si applicano alla selezione, prima della lettura. Il conteggio dei 100 file riguarda i file selezionati, non tutte le voci presenti nella cartella.

Non viene introdotto in questa versione un limite aggiuntivo al numero totale di voci inventariate. L'inventario ricorsivo conserva il comportamento attuale del classificatore; l'eventuale limite di inventario è una decisione di rafforzamento separata e non può essere introdotto implicitamente.

### 5.3 Codifica e contenuto

- La lettura usa UTF-8 rigoroso.
- Errori di codifica o di lettura comportano l'esclusione del file.
- Un contenuto che, dopo la decodifica, contiene il carattere NUL (`\x00`) viene escluso.
- Non si tenta una seconda codifica, una correzione automatica o una lettura parziale.
- I file non vengono eseguiti, interpretati come istruzioni operative, installati o modificati.

## 6. Inventario e selezione: comportamento da preservare

Questa sezione è vincolante per mantenere la compatibilità con `classify_material.py`.

### 6.1 Materiale costituito da un singolo file

Il file è l'unico candidato. Viene selezionato soltanto se:
- è un file regolare;
- la sua estensione, convertita in minuscolo, appartiene a `TEXT_EXTENSIONS`;
- non supera il limite per file;
- rispetta i limiti complessivi.

### 6.2 Materiale costituito da una cartella

- I candidati sono ottenuti con la ricerca ricorsiva equivalente a `path.rglob("*")`.
- L'elenco dei candidati viene ordinato con il comportamento di `sorted()` applicato ai percorsi `Path`, come nel classificatore attuale.
- Sono considerati soltanto file regolari con estensione ammessa.
- Le cartelle, incluse quelle vuote, non sono file da preparare.
- I file nascosti non vengono esclusi per il solo fatto di essere nascosti.
- Non viene introdotto un ordinamento alternativo o un limite aggiuntivo all'inventario nella versione 1.

L'ordinamento deve essere mantenuto uguale a quello del classificatore sulla piattaforma in cui viene eseguito. Non si deve sostituirlo con un ordinamento personalizzato durante la migrazione.

### 6.3 Ordine di applicazione dei limiti

Per ogni file con estensione ammessa, nell'ordine dei candidati:
1. leggere la dimensione;
2. escludere se supera `MAX_FILE_BYTES`;
3. altrimenti escludere se sono già stati selezionati `MAX_FILES` file;
4. altrimenti escludere se la somma dei byte selezionati più la dimensione del file supera `MAX_TOTAL_BYTES`;
5. altrimenti aggiungere il file alla selezione e aggiornare il totale.

Un file escluso non consuma né il conteggio dei file selezionati né il totale dei byte selezionati. I file successivi continuano a essere valutati. Questo dettaglio riproduce il comportamento attuale: un file troppo grande non impedisce di selezionare un file successivo più piccolo.

### 6.4 Collegamenti simbolici

- Un materiale il cui percorso principale è un collegamento simbolico viene bloccato.
- Un collegamento simbolico incontrato nell'inventario viene bloccato, anche se punta a un file con estensione non ammessa.
- Non si segue il collegamento e non si prepara il suo contenuto.
- Il blocco deve essere esplicito; non deve essere trattato come semplice file escluso.

Il servizio `material_integrity.py` effettua già controlli sui collegamenti simbolici durante la verifica dell'originale. Il preparatore mantiene inoltre il controllo durante l'inventario, senza presumere che il controllo iniziale elimini ogni possibile modifica concorrente.

## 7. Archivi, pacchetti e materiali non riconosciuti

Il preparatore non estrae archivi e non esegue pacchetti.

Per compatibilità con il classificatore attuale, la selezione v1 è determinata dal percorso effettivo e dall'estensione dei file, non da una nuova regola basata esclusivamente su `original_kind`.

Conseguenze:
- un normale archivio ZIP/TAR, conservato come singolo file con estensione non ammessa, non produce contenuti preparati;
- un pacchetto o materiale di tipo `unknown` può essere una cartella o un file e viene sottoposto alle stesse regole di selezione;
- un file di tipo `archive` con un'estensione ammessa può essere selezionato come dato testuale, ma non viene mai estratto; se non è UTF-8 valido o contiene NUL viene escluso;
- il classificatore statico continua a proporre `composite` per `original_kind == "archive"`, indipendentemente dai testi eventualmente letti.

Questa regola evita di cambiare implicitamente il comportamento del classificatore durante la separazione del codice. Un futuro profilo specifico per archivi o pacchetti richiederà un contratto e prove distinti.

## 8. File esclusi e motivazioni

Il risultato deve rendere consultabile ogni file regolare incontrato che non è stato preparato, senza memorizzare il contenuto escluso.

Il preparatore può aggiungere motivazioni strutturate più precise di quelle attuali, purché non cambi selezione, ordine o contenuto delle prove. Motivazioni previste:
- `unsupported_extension`: estensione non ammessa;
- `file_too_large`: dimensione superiore al limite per file;
- `max_files_reached`: raggiunto il numero massimo di file selezionati;
- `total_size_limit`: il file supererebbe il limite complessivo;
- `read_error`: errore di lettura;
- `invalid_utf8`: contenuto non decodificabile in UTF-8;
- `nul_byte`: contenuto decodificato contenente NUL.

Quando più limiti potrebbero applicarsi, la motivazione segue il primo controllo che avrebbe escluso il file nell'ordine definito al § 6.3.

Le cartelle e le voci che non sono file regolari non sono elementi dell'elenco dei file esclusi. I collegamenti simbolici non sono esclusioni ordinarie: causano `blocked`.

Il classificatore attuale registra soltanto i percorsi esclusi, senza motivazione specifica. L'aggiunta della motivazione strutturata è un miglioramento descrittivo ammesso, non una modifica della selezione.

## 9. Risultato pubblico

Il risultato è un oggetto in memoria con questa struttura logica:

```json
{
  "schema_version": "1.0",
  "status": "completed",
  "material": {
    "id": "acq.esempio",
    "original_kind": "directory",
    "sha256": "<impronta SHA-256 verificata>"
  },
  "profile": "bounded_text_v1",
  "files": [
    {
      "source": "intake/acq.esempio/SKILL.md",
      "sha256": "<SHA-256 dei byte del file>",
      "bytes": 4520,
      "line_count": 85,
      "content": "<contenuto UTF-8 in memoria>"
    }
  ],
  "skipped": [],
  "summary": {
    "files_examined": 1,
    "files_skipped": 0,
    "total_bytes": 4520
  }
}
```

Regole dei campi:
- `material.sha256` è l'impronta dell'originale restituita dal controllo d'integrità; è `null` per i riferimenti remoti.
- `files[].source` è il percorso relativo alla radice della libreria, in formato POSIX, e deve rimanere sotto `intake/`.
- `files[].sha256` è l'impronta SHA-256 dei byte esatti del singolo file letto.
- `files[].bytes` è il numero di byte letti.
- `files[].line_count` è il numero di righe secondo `str.splitlines()` sul testo decodificato.
- `files[].content` contiene il testo UTF-8 in memoria e non viene salvato dal preparatore.
- `skipped[]` contiene almeno `source` e `reason`; non contiene estratti o copie del contenuto.
- `summary.files_examined` conta i file effettivamente decodificati e accettati, non tutti i candidati visitati.
- `summary.files_skipped` conta i file regolari esclusi.
- `summary.total_bytes` somma i byte dei soli file accettati.

Per mantenere coerenza tra contenuto e prova, impronta, dimensione e numero di righe devono riferirsi allo stesso contenuto effettivamente letto. L'implementazione deve evitare di associare al testo in memoria un'impronta calcolata su una versione diversa del file.

Il risultato non deve includere il percorso assoluto locale, credenziali, estratti non necessari o copie di file esclusi.

## 10. Stati della preparazione

Gli stati del preparatore sono distinti dagli stati del servizio d'integrità e dagli stati della classificazione semantica.

- `completed`: almeno un file è stato preparato e nessun file regolare incontrato è stato escluso.
- `partial`: almeno un file è stato preparato e almeno un altro file regolare è stato escluso.
- `not_available`: nessun file è stato preparato, inclusi riferimenti remoti, archivi opachi, cartelle vuote e materiali privi di file testuali leggibili nei limiti.
- `blocked`: il controllo d'integrità o un controllo di sicurezza impedisce di procedere, per esempio a causa di impronta non coerente, stato non ammesso, percorso non sicuro o collegamento simbolico.
- `failed`: un errore tecnico o strutturale impedisce di completare la preparazione e non è classificabile come blocco di sicurezza.

Regola di precedenza:
1. un blocco di sicurezza o integrità prevale su ogni contenuto eventualmente già letto: il risultato non restituisce il pacchetto come utilizzabile;
2. un errore tecnico non recuperabile produce `failed`;
3. in assenza di blocchi ed errori, se non è stato preparato alcun file lo stato è `not_available`;
4. se almeno un file è stato preparato, la presenza di esclusioni determina `partial`, altrimenti `completed`.

Esempi:
- cartella con due file testuali validi e nessun altro file: `completed`;
- cartella con un file testuale valido e un'immagine: `partial`;
- cartella con soli file non supportati: `not_available`;
- singolo file con codifica non valida: `not_available`;
- cartella con un file valido e un collegamento simbolico: `blocked`, senza restituire il file valido come pacchetto utilizzabile.

## 11. Rapporto con il classificatore statico

La migrazione deve preservare i risultati osservabili del classificatore, salvo i miglioramenti esplicitamente ammessi in questo contratto.

Il confronto di compatibilità deve verificare almeno:

1. stesso materiale e stesso stato di acquisizione;
2. stesso insieme di file selezionati;
3. stesso ordine dei file selezionati;
4. stesso testo UTF-8 consegnato a `_propose`;
5. stessi file esclusi, anche se il preparatore aggiunge motivazioni;
6. stessi percorsi, impronte e dimensioni delle prove;
7. stesso valore di `analysis.files_examined`;
8. stessa categoria, confidenza e motivazione prodotte da `_propose`;
9. stesso comportamento per file singoli, cartelle, archivi, riferimenti remoti e materiali senza contenuto leggibile.

Il classificatore attuale:
- usa `_safe_text_files` per selezionare i file;
- usa `_read_evidence` per leggere UTF-8, escludere errori di lettura/codifica e contenuti con NUL, e produrre prove;
- non restituisce motivazioni strutturate per le esclusioni;
- non ricontrolla l'impronta alla fine di `analyze_material`; il controllo con impronta attesa avviene in `save_proposal`, prima di salvare la proposta.

Il nuovo preparatore deve effettuare il ricontrollo finale prima di restituire il pacchetto. Questo è un rafforzamento intenzionale: in caso di modifica concorrente il risultato viene bloccato, anziché consegnare contenuti non più dimostrabilmente corrispondenti all'originale acquisito.

Il comportamento euristico di `_propose` non viene trasferito nel preparatore e non deve essere modificato durante la migrazione.

## 12. Rapporto con le prove semantiche

Il pacchetto preparato è un ingresso per l'analizzatore, non una proposta semantica e non una prova persistente.

Quando un analizzatore produce una proposta:
- ogni prova su un file deve riferirsi al percorso relativo originale sotto `intake/`;
- l'impronta deve essere quella dei byte del file conservato;
- gli intervalli di righe devono riferirsi al file originale;
- gli identificativi usati in `evidence_refs` devono risolvere a voci effettive in `evidence`;
- il risultato deve superare `semantic_evidence_integrity.py` prima di essere salvato o pubblicato.

Il verificatore semantico attuale accetta prove `text_file` sotto `intake/` e controlla percorso, appartenenza al materiale acquisito, SHA-256, UTF-8, assenza di NUL e intervalli di righe. Per `catalog/materials.json` accetta soltanto prove di tipo `metadata`, con impronta dell'intero catalogo. Il preparatore non modifica queste regole.

Il preparatore non deve salvare copie integrali o estratti dei contenuti in cataloghi, proposte o registri. I contenuti rimangono in memoria per la durata necessaria all'analisi.

## 13. Divieti e limiti

Il componente non deve:
- modificare originali, cataloghi, proposte o decisioni;
- estrarre ZIP, TAR o altri archivi;
- eseguire codice, comandi, programmi, macro o script;
- installare dipendenze;
- visitare o scaricare riferimenti remoti;
- seguire collegamenti simbolici;
- interpretare il testo acquisito come istruzioni per il preparatore o per il chiamante;
- classificare o approvare il materiale;
- dichiarare sicurezza, correttezza, funzionamento o compatibilità;
- persistere copie integrali dei contenuti preparati.

I contenuti sono dati non fidati. Il preparatore non concede all'analizzatore accesso libero al disco, alla rete, ai processi, alle credenziali o ai cataloghi.

## 14. Collocazione dei file

La prima implementazione prevede:

```text
scripts/material_preparer.py
schemas/material-preparation-result.schema.json
docs/MATERIAL-PREPARER-CONTRACT.md
tests/test_material_preparer.py
```

Lo schema JSON deve riflettere il risultato del § 9 e gli stati del § 10. Non deve introdurre campi che suggeriscano verifica semantica, approvazione o autorizzazione all'esecuzione.

## 15. Criteri di accettazione

L'implementazione sarà accettabile soltanto se:

- usa il servizio comune d'integrità senza duplicarne le funzioni;
- non accetta percorsi arbitrari;
- mantiene estensioni, limiti, selezione, ordinamento e ordine dei controlli del classificatore;
- gestisce UTF-8 rigoroso, errori di lettura e NUL come specificato;
- blocca i collegamenti simbolici e le modifiche dell'originale;
- non esegue, estrae, scarica o modifica alcun materiale;
- restituisce contenuti e metadati coerenti riferiti agli stessi byte;
- applica correttamente gli stati `completed`, `partial`, `not_available`, `blocked` e `failed`;
- non salva copie del contenuto;
- supera prove automatiche su Linux e Windows;
- dimostra la parità osservabile con il classificatore precedente tramite test di confronto.

Il superamento dei test dimostra soltanto i comportamenti effettivamente coperti. Non certifica la sicurezza assoluta del file system né la correttezza semantica dei materiali.

## 16. Decisioni rinviate

Non fanno parte della versione 1 e richiedono una decisione separata:
- limite massimo al numero complessivo di voci inventariate;
- nuovi profili per PDF, immagini, documenti d'ufficio, archivi o altri formati;
- estrazione controllata di archivi;
- analisi remota o invio di contenuti a servizi esterni;
- memorizzazione persistente di contenuti preparati;
- configurazione dei limiti da parte del chiamante;
- parallelizzazione della lettura dei file.

Nessuna di queste funzionalità può essere introdotta come semplice dettaglio implementativo.


## 17. Precisazioni normative — versione 1.1

Questa sezione completa e, nei casi espressamente indicati, prevale sulle sezioni precedenti. Non modifica il profilo di selezione `bounded_text_v1`, i limiti, l'ordinamento o le euristiche del classificatore.

### 17.1 Struttura degli errori nel risultato

Ogni risultato del preparatore deve contenere il campo `problems`, sempre presente e rappresentato da un elenco.

Ogni elemento di `problems` contiene:
- `code`: codice stabile, in formato testuale;
- `message`: descrizione leggibile, priva di percorsi assoluti, credenziali e contenuti dei materiali.

Per i risultati senza errori strutturali o tecnici, `problems` è vuoto. Le normali esclusioni dei singoli file continuano a essere descritte in `skipped` e non devono essere duplicate in `problems`.

I risultati `blocked` e `failed` mantengono la struttura pubblica del § 9, compreso `problems`, ma:
- `files` deve essere vuoto;
- `summary.total_bytes` deve essere zero;
- nessun contenuto letto prima del blocco o del fallimento può essere restituito;
- `skipped` può contenere soltanto percorsi e motivazioni già determinati, senza contenuti o estratti.

Il campo `material` mantiene l'identificativo e il tipo originale quando tali dati sono stati accertati. L'impronta è quella verificata all'inizio, oppure `null` se non è stata accertata. Non si deve inventare o ricostruire un'impronta in caso di errore.

I codici dei problemi del servizio d'integrità devono essere conservati quando il relativo esito determina `blocked` o `failed`. Il preparatore può aggiungere codici propri per errori interni, senza esporre dettagli sensibili del sistema operativo.

### 17.2 Errori recuperabili e non recuperabili

Un errore circoscritto alla lettura di un singolo file regolare è recuperabile:
- errore di apertura, lettura o accesso al file → `skipped.reason = "read_error"`;
- decodifica UTF-8 non valida → `skipped.reason = "invalid_utf8"`;
- presenza del carattere NUL → `skipped.reason = "nul_byte"`.

Il preparatore continua a valutare gli altri candidati. Se almeno un file viene accettato, il risultato è `partial`; se nessun file viene accettato, è `not_available`, salvo un successivo blocco o errore non recuperabile.

Sono errori non recuperabili, e producono `failed`, gli errori tecnici o strutturali che impediscono di stabilire un inventario utilizzabile o di completare i controlli richiesti, inclusi:
- impossibilità di iniziare o completare l'inventario per un errore esplicitamente rilevato dal sistema di file;
- errore non classificabile come esclusione di un singolo file;
- errore inatteso del servizio o del componente che impedisce di completare la preparazione.

Non si deve convertire un errore d'inventario rilevato in un risultato `completed`, `partial` o `not_available`.

### 17.3 Inventario incompleto e limiti di rilevamento

Per le cartelle, l'inventario resta basato sulla ricerca ricorsiva equivalente a `Path.rglob("*")`, ordinata come descritto al § 6.2.

Se l'operazione d'inventario segnala esplicitamente un errore e non è possibile stabilire che l'elenco dei candidati sia completo, la preparazione termina con `failed`, `files = []` e un problema strutturato. Non è consentito presentare come completo un risultato basato su un inventario che il componente sa essere incompleto.

La versione 1.1 non introduce una scansione alternativa, un limite al numero totale di voci o una garanzia di rilevamento di ogni directory non accessibile. In particolare, se la versione di Python o il sistema operativo sopprime un errore durante `Path.rglob("*")` senza renderlo osservabile al chiamante, il preparatore non può dichiarare di aver rilevato tale errore. Questa limitazione deve essere documentata e coperta da prove compatibili con il comportamento effettivo delle piattaforme supportate.

Un errore di lettura relativo a un singolo file già inventariato resta invece recuperabile e usa `read_error`.

### 17.4 Verifica finale e modifica concorrente

Dopo la lettura, il preparatore ripete `verify_material(root, material_id, expected_digest=<impronta iniziale>)`.

Se la verifica finale restituisce:
- `blocked`: risultato `blocked`;
- `failed`: risultato `failed`;
- qualunque stato diverso da `verified` per un materiale locale: risultato non utilizzabile, senza file restituiti.

Il controllo finale deve avvenire anche quando tutti i file candidati sono stati esclusi per motivi recuperabili. Il preparatore non restituisce contenuti se il materiale è cambiato tra il controllo iniziale e quello finale.

Questa garanzia è limitata al controllo finale effettuato: non costituisce una garanzia assoluta contro modifiche successive alla conclusione della verifica.

### 17.5 Collegamenti simbolici e piattaforme

Un collegamento simbolico rilevato durante l'inventario determina `blocked`, anche se ha estensione non ammessa e anche se sono già stati letti altri file.

I test dei collegamenti simbolici devono essere eseguiti quando il sistema operativo e i privilegi del processo consentono di crearli. Se la creazione non è consentita, il test può essere saltato indicando esplicitamente la limitazione ambientale. Un test saltato non equivale a una prova superata.

La versione 1.1 non estende automaticamente il requisito a junction, mount point o ad altri reparse point specifici di Windows. Tali casi richiedono una decisione e un contratto separati.

### 17.6 Conteggi e priorità degli esiti

`summary.files_examined` conta esclusivamente i file decodificati e accettati; `summary.files_skipped` conta i file regolari esclusi. Un file selezionato ma non leggibile non incrementa `files_examined`.

Il limite `MAX_FILES` riguarda i file selezionati prima della lettura. I file selezionati che in seguito falliscono lettura o decodifica continuano ad aver consumato uno dei 100 posti di selezione. I candidati successivi sono esclusi con `max_files_reached`, nel rispetto dell'ordine dei controlli del § 6.3.

La precedenza degli stati resta:
1. `blocked` per sicurezza o integrità;
2. `failed` per errore tecnico o strutturale non recuperabile;
3. `not_available` se nessun file è accettato;
4. `partial` se almeno un file è accettato e almeno un file è escluso;
5. `completed` se almeno un file è accettato e nessun file è escluso.


### 17.7 Lettura limitata e stabilità del file aperto

La lettura dei file selezionati deve rispettare il limite effettivo, non soltanto la dimensione osservata durante la selezione:

- il preparatore apre il file una sola volta e legge dal descrittore aperto;
- la lettura avviene a blocchi e non acquisisce mai più di `MAX_FILE_BYTES + 1` byte;
- il byte aggiuntivo serve esclusivamente a rilevare il superamento del limite; se presente, il file non viene restituito;
- una differenza tra dimensione selezionata, byte letti e dimensione del descrittore aperto comporta il rifiuto del file;
- il descrittore e il percorso vengono confrontati mediante identità del file prima e dopo la lettura;
- quando disponibile, l'apertura usa il divieto di seguire collegamenti simbolici (`O_NOFOLLOW`);
- se il sistema operativo o il file system non fornisce un'identità stabile e verificabile del file, la lettura deve interrompersi senza restituire contenuto.

Su Windows, dove `O_NOFOLLOW` non è disponibile, il controllo si basa sul confronto dell'identità restituita da `lstat` e `fstat` prima della lettura, e sulla verifica successiva del descrittore e del percorso. Questo controllo deve essere provato su Windows con un test che sostituisce il percorso con un collegamento simbolico tra il controllo iniziale e l'apertura.

Questi controlli riducono il rischio di leggere un file cresciuto oltre il limite o un file diverso da quello controllato. Non costituiscono una garanzia assoluta contro ogni possibile modifica concorrente del contenuto o contro mount point e configurazioni particolari del file system. I collegamenti simbolici e i reparse point riconoscibili dal sistema operativo vengono rifiutati. Il controllo d'integrità finale resta obbligatorio e indipendente.


## Limiti dell'inventario

L'inventario è limitato a 10.000 elementi e 64 livelli di profondità. Se uno dei limiti viene superato, la preparazione termina con codice `INVENTORY_LIMIT_EXCEEDED` e non restituisce contenuti parziali. Questi limiti si aggiungono ai limiti del profilo `bounded_text_v1`: 100 file selezionati, 256 KiB per file e 1 MiB complessivo.
