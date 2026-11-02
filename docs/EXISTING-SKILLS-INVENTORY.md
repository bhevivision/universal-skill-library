# Inventario preliminare dei materiali esistenti

## Stato e limiti della verifica

Questo documento registra una prima ispezione statica dei quattro file presenti in `personalizzazione/` nel ramo `model/structural-model-v1`.

**Non è ancora un inventario operativo della libreria e non equivale a un'acquisizione eseguita da `scripts/acquire_material.py`.** I quattro file sono presenti nel repository, ma `catalog/materials.json`, `catalog/skills.json`, `catalog/capabilities.json` e `catalog/implementations.json` sono attualmente vuoti. Non sono state create schede di acquisizione né approvate skill.

Gli originali non sono stati modificati. Le impronte indicate sotto sono identificativi Git blob, non impronte SHA-256 del contenuto.

## Materiali esaminati

| ID inventario | File | Dimensione | Identificativo Git blob | Esito preliminare |
|---|---|---:|---|---|
| INV-001 | `personalizzazione/UNLAZY-skill.md` | 15.823 byte | `c59d88d9503cf5ba3b9ba3d08f757a875087eda5` | Possibile skill / metodo di controllo, incompleto rispetto ai riferimenti dichiarati |
| INV-002 | `personalizzazione/archivista-skill.md` | 2.985 byte | `cc0074a15072111f98e3764951fae9d6b4957ca1` | Possibile skill, incompleta: manca il riferimento principale dichiarato |
| INV-003 | `personalizzazione/find-skill.md` | 4.625 byte | `1e204b37ca5fd88e7b449c4512c92c4e7990287f` | Istruzioni di ricerca e installazione; origine e aggiornamento da verificare |
| INV-004 | `personalizzazione/canva-kdp-skill.md` | 36 byte | `635c4664734d11b039f59ee1d57de0cd0791dead` | Illeggibile / apparentemente danneggiato; bloccato |

Nessuno dei quattro file contiene attualmente un frontmatter Agent Skills standard. Questo non impedisce di conservarli, ma non consente di considerarli pacchetti Agent Skills già conformi.

## Schede di analisi

### INV-001 — UNLAZY

**Contenuto osservato:** metodo dettagliato per pianificare attività, definire verifiche prima dell'esecuzione, conservare prove, gestire esiti negativi e distinguere fatto, verifica e completamento.

**Lacune e dipendenze dichiarate nel file:**
- `references/tipi_di_prova.md`;
- `references/file_di_controllo.md`;
- `references/casi_reali.md`.

Questi tre file non sono presenti nella cartella `personalizzazione/` insieme alla copia esaminata. La completezza delle risorse in altre posizioni del repository o nella fonte originale non è stata dimostrata.

**Valutazione:** materiale promettente come metodo riutilizzabile di controllo, ma non autonomo rispetto alle risorse che dichiara obbligatorie. Non va dichiarato completo né approvato come skill utilizzabile finché non vengono recuperati e verificati i riferimenti.

### INV-002 — Archivista

**Contenuto osservato:** istruzioni per controllare fascicoli documentali relativi ai libri, con regole di non scrittura autonoma, tracciabilità e approvazione esplicita dell'utente.

**Dipendenza dichiarata:**
- `reference/regole-complete.md`.

Il file richiesto non è presente nella cartella `personalizzazione/` insieme alla copia esaminata. La mappa delle 17 sezioni e i richiami alle parti del riferimento non sostituiscono il testo completo delle regole.

**Valutazione:** possibile skill specifica per un contesto documentale, ma incompleta e non verificabile nella sua interezza. Non ricostruire il riferimento mancante per supposizione.

### INV-003 — Find Skills

**Contenuto osservato:** istruzioni per cercare, valutare e installare skill nell'ecosistema esterno tramite `npx skills` e il sito skills.sh.

**Dipendenze e rischi da verificare:**
- richiede Node.js/npm e accesso alla rete;
- i risultati, le classifiche e i conteggi di installazione sono dati variabili e non sono verificati dalla copia;
- i comandi di installazione possono modificare l'ambiente dell'utente;
- l'esempio `npx skills add ... -g -y` prevede installazione globale e conferma automatica: non deve essere eseguito senza valutazione del pacchetto, dell'ambiente e dell'autorizzazione.

**Valutazione:** materiale di supporto alla ricerca e all'installazione, non prova che una skill trovata sia sicura, compatibile o funzionante. Origine, versione, data di aggiornamento e procedura di verifica vanno recuperate prima di un'eventuale approvazione.

### INV-004 — Canva KDP

**Contenuto osservato:** file di soli 36 byte, con testo troncato e caratteri non validi. Non contiene istruzioni sufficienti per comprenderne la funzione.

**Valutazione:** stato BLOCCATO / NON CLASSIFICATO. Conservare il file esattamente com'è. Recuperare la fonte originale solo se disponibile; non ricostruire il contenuto e non trattare questa copia come una skill.

## Decisioni operative

1. Conservare i quattro file senza modificarli.
2. Non aggiungere voci a `catalog/skills.json` sulla sola base di questo inventario.
3. Dopo la verifica locale Windows della base, acquisire i file leggibili con il componente ufficiale, registrando provenienza e impronte SHA-256.
4. Recuperare le risorse mancanti di UNLAZY e Archivista dalla fonte originale e verificarne la corrispondenza; se non sono recuperabili, mantenere esplicita la lacuna.
5. Per Find Skills, verificare fonte e versione delle istruzioni e rivedere i comandi che installano globalmente o saltano le conferme.
6. Per Canva KDP, cercare l'originale integro; in assenza, lasciare il materiale bloccato.
7. Solo dopo acquisizione, classificazione, controllo delle prove e approvazione esplicita si potrà valutare l'inserimento nel catalogo operativo.

## Stato complessivo

- Ispezione statica dei quattro file: **eseguita**.
- Completezza delle risorse collegate: **non verificata**.
- Acquisizione ufficiale tramite il componente: **non eseguita**.
- Classificazione approvata: **nessuna**.
- Verifica funzionale e compatibilità: **non eseguite**.
- Utilizzabilità operativa: **non valutata**.
