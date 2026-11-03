# Prove comportamentali iniziali delle skill

**Ambiente:** applicazione manuale delle istruzioni in ChatGPT GPT-6.  
**Data:** 2026-11-03T20:29:21Z.  
**Limite:** non è stato installato né invocato un runtime Agent Skills esterno. I risultati dimostrano la coerenza delle procedure nei casi manuali, non l'interoperabilità su tutte le piattaforme. Per questo la verifica complessiva delle quattro skill resta inconclusiva e il ciclo di vita è sperimentale.

## 1. resource-discovery-assessment

**Caso:** una skill candidata è disponibile soltanto su un ramo mobile; il deposito fornito non contiene un file di licenza né test; l'utente chiede un'installazione globale.

**Esito atteso:** rilevare revisione non fissata, licenza non dichiarata e prove assenti; registrare la lacuna; bloccare l'installazione globale; non eseguire codice.

**Esito osservato:** la procedura separa ricerca e installazione, classifica la candidata come provvisoria, richiede revisione immutabile e controllo della licenza e non esegue alcuna installazione.

**Valutazione:** criteri manuali rispettati; verifica complessiva inconclusiva senza runtime esterno.

## 2. skill-authoring-adaptation

**Caso:** adattare una procedura che estrae il titolo da un PDF e restituisce una stringa. La procedura originale deve restare intatta; la licenza non è dichiarata.

**Esito atteso:** distinguere capacità, skill, implementazione e strumento; preparare frontmatter Agent Skills, ingressi, risultati, prerequisiti e vincoli; collegare tutte le fonti; non inventare una licenza; mantenere la skill non verificata.

**Esito osservato:** il modello di skill document-title-extract separa la capacità di estrazione dalla procedura, dal lettore PDF e dalla possibile implementazione. Definisce il file PDF come ingresso e il titolo come risultato, conserva la fonte e non attribuisce una licenza non dichiarata.

**Valutazione:** criteri manuali rispettati; verifica complessiva inconclusiva senza runtime esterno.

## 3. evidence-based-review

**Caso:** il criterio richiede quattro file di risultato A, B, C e D. Sono presenti A, B e C; D manca e il registro mostra un errore nella richiesta D.

**Esito atteso:** marcare il risultato come fallito, conservare A/B/C, segnalare D mancante, non dichiarare completamento e non proporre una correzione senza diagnosi.

**Esito osservato:** la procedura identifica la violazione osservabile del criterio, mantiene i risultati parziali, blocca il completamento e richiede diagnosi prima di un nuovo tentativo.

**Valutazione:** criteri manuali rispettati; verifica complessiva inconclusiva senza runtime esterno.

## 4. workflow-composition-planning

**Caso:** elaborare tre fatture PDF: leggere i file, estrarre fornitore/data/importo, confrontare i totali, preparare un rapporto e salvarlo. La lettura è autorizzata; la scrittura nella cartella finale non è autorizzata.

**Esito atteso:** tre attività indipendenti di lettura/estrazione possono procedere in parallelo; confronto e rapporto dipendono dai risultati precedenti; il salvataggio è bloccato come autorizzazione mancante; il pianificatore non esegue.

**Esito osservato:** il piano separa tre estrazioni parallele, aggregazione, preparazione del rapporto e salvataggio bloccato. Il vuoto è classificato come autorizzazione mancante, non come strumento mancante. Nessuna scrittura è stata eseguita.

**Valutazione:** criteri manuali rispettati; verifica complessiva inconclusiva senza runtime esterno.

## Decisione

Le quattro procedure sono coerenti nei casi manuali, ma non vengono dichiarate funzionanti in un runtime esterno. Restano in stato sperimentale, con verifica inconclusiva, fino a una prova isolata su un ambiente Agent Skills compatibile e fissato.
