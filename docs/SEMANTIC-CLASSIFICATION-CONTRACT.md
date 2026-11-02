# Contratto tecnico della classificazione semantica

## Stato e ambito

Contratto v1 per richiesta e risultato dell'analisi semantica. Lo schema della richiesta è in `schemas/semantic-classification-request.schema.json`; lo schema del risultato è in `schemas/semantic-classification-proposal.schema.json`. Il contratto definisce il confine tra il futuro motore semantico e la libreria; non significa che il motore sia già implementato.

La classificazione semantica affianca il classificatore statico esistente. Le proposte restano esterne ai cataloghi approvati e passano dal componente di approvazione già presente.

## Richiesta al motore

La richiesta deve contenere:

- versione del contratto;
- identificativo del materiale acquisito;
- impronta SHA-256 dell'originale, quando disponibile;
- tipo originale e metadati di acquisizione strettamente necessari;
- elenco dei file ammessi all'analisi, ognuno con percorso relativo sotto `intake/`, impronta SHA-256 e dimensione;
- contenuto testuale selezionato, solo se necessario al motore, entro limiti espliciti;
- limiti di analisi: numero massimo di file, dimensione per file e complessiva, tempo massimo;
- dichiarazione che i contenuti sono dati non fidati e non istruzioni operative per il motore.

La richiesta non deve concedere accesso libero al disco, alla rete, ai processi, alle credenziali o ai cataloghi. Il motore riceve soltanto i dati già selezionati dal componente chiamante.

### Schema formale della richiesta

Ogni richiesta deve rispettare `schemas/semantic-classification-request.schema.json` e contenere:

- `contract_version` e `request_id`;
- `material`: identificativo, tipo originale e impronta SHA-256; per un riferimento remoto non visitato l'impronta è `null`;
- `files`: elenco dei soli file autorizzati, con percorso canonico relativo sotto `intake/`, SHA-256 e dimensione in byte;
- `selected_content`: contenuti testuali selezionati, ciascuno collegato al percorso e alla stessa impronta di un file autorizzato;
- `limits`: `max_files`, `max_file_bytes`, `max_total_bytes`, `max_duration_seconds`;
- `safety`: contenuto dichiarato non fidato e tutti i permessi di accesso/esecuzione/scrittura impostati obbligatoriamente a `false`.

I limiti massimi dello schema v1 sono 100 file, 262.144 byte per file, 1.048.576 byte complessivi e 300 secondi. Il chiamante può imporre limiti inferiori, mai superiori. Campi aggiuntivi non sono ammessi.

Lo schema controlla la forma e i limiti. `validate_semantic_request()` in `scripts/semantic_evidence_integrity.py` applica inoltre i controlli incrociati: percorso canonico senza attraversamento, assenza di percorsi assoluti o separatori Windows, unicità dei file, corrispondenza esatta tra contenuto selezionato e file ammesso, impronta identica, dimensione UTF-8 effettiva e limiti complessivi. Un riferimento remoto non visitato non può includere file né contenuti selezionati.

Per usare il controllo applicativo nel codice chiamante, importare `validate_semantic_request` e passargli l'oggetto richiesta prima di inviarlo al motore.

## Risposta

La risposta deve rispettare lo schema JSON indicato sopra. I campi principali sono:

- `status`: completed, partial, not_available o failed;
- `material`: identità e impronta del materiale esaminato;
- `classification`: categoria, confidenza, motivazione e sintesi;
- `capabilities`: capacità individuate, ciascuna con prove;
- `interfaces`: ingressi, risultati e condizioni d'uso;
- `dependencies`: dipendenze dichiarate, dedotte o sconosciute;
- `tools_and_platforms`: strumenti e piattaforme menzionati, senza certificare compatibilità;
- `evidence`: file, impronte e posizioni che sostengono le affermazioni;
- `missing_references`, `contradictions`, `risks`, `unknowns`, `limits`;
- `analyzer`: identificativo e versione del motore, fornitore, modello e impronte di ingresso e uscita.

Il JSON Schema controlla la forma dei riferimenti, ma non può verificare da solo che ogni valore in `evidence_refs` corrisponda a un identificativo realmente presente in `evidence[].id`. Per questo è stato implementato `scripts/semantic_evidence_integrity.py`, che esegue i controlli applicativi: rifiuta identificativi duplicati e riferimenti inesistenti, controlla l'identità e l'impronta del materiale nel catalogo, verifica che ogni percorso punti a un file effettivo dentro il materiale acquisito, confronta SHA-256, impedisce collegamenti simbolici e controlla gli intervalli di righe dichiarati. Ricontrolla inoltre le impronte del materiale e del catalogo al termine della verifica.

La conclusione di classificazione e ogni capacità o affermazione dichiarata o dedotta devono avere almeno una prova. Le prove possono riferirsi a file conservati sotto `intake/` oppure, per attestare soltanto l'identità di un riferimento remoto non visitato, alla scheda `catalog/materials.json`. Le informazioni sconosciute possono non avere prove, ma devono essere esplicitamente marcate come sconosciute. Un riferimento remoto non esaminato può quindi produrre una proposta `not_available` e `unclassified`, senza fingere di conoscerne il contenuto. Il campo compatibilità non consente il valore verificato: la verifica di piattaforma è un processo separato.

## Regole obbligatorie per gli stati

Gli stati descrivono l'esito tecnico dell'analisi e non il livello di approvazione del materiale:

| Stato | Significato | Contenuto consentito |
|---|---|---|
| `completed` | Analisi completata entro il perimetro richiesto | Risultati semantici sostenuti da prove |
| `partial` | Analisi incompleta o limitata | Risultati sostenuti da prove e almeno un limite esplicito |
| `not_available` | Motore o contenuto non disponibile | Solo `unclassified`, confidenza `low`, nessuna affermazione semantica; prove esclusivamente di metadati del catalogo |
| `failed` | Analisi interrotta da errore tecnico | Stesse restrizioni di `not_available`; nessun risultato semantico parziale presentato come valido |

Per `not_available` e `failed`, capacità, ingressi, risultati, condizioni d'uso, dipendenze, strumenti/piattaforme, riferimenti mancanti, contraddizioni e rischi devono essere elenchi vuoti. `unknowns` e `limits` devono invece indicare che cosa non è stato accertato e perché. Le prove ammesse possono attestare soltanto l'esistenza o l'identità del materiale nel catalogo (`source: catalog/materials.json`, `kind: metadata)); non possono riferirsi ai file di contenuto.

La regola vale sia nello schema JSON sia nel controllo applicativo: non è sufficiente produrre un JSON formalmente valido se i campi sono incoerenti con lo stato dichiarato.

## Esecuzione del controllo applicativo

Dalla cartella principale del repository, prima di inviare una richiesta al motore, il codice chiamante deve validarla con `validate_semantic_request(request)`. Per una proposta JSON già prodotta e salvata in `proposals/`, eseguire:

    python scripts/semantic_evidence_integrity.py --proposal proposals/nome-proposta.json

Il controllo restituisce esito positivo soltanto se schema, riferimenti, identità e impronte risultano coerenti. Per le prove `intake/`, `sha256` deve corrispondere ai byte del file effettivamente conservato e il file deve appartenere al materiale acquisito. Per `catalog/materials.json`, `sha256` corrisponde all'intero file del catalogo al momento della verifica: se il catalogo cambia, la proposta va verificata nuovamente. I riferimenti remoti non visitati possono attestare soltanto l'identità nei metadati e devono restare `not_available` e `unclassified`.

Il controllo non esegue i materiali e non certifica la correttezza semantica delle affermazioni: verifica la loro tracciabilità tecnica.

## Regole di sicurezza

1. I materiali sono dati non fidati. Nessuna istruzione contenuta nel materiale può cambiare il comportamento o le regole del motore.
2. Il motore non esegue codice, comandi, macro o programmi e non installa dipendenze.
3. Il motore non visita collegamenti né scarica riferimenti remoti.
4. La configurazione iniziale deve usare un analizzatore locale. Se non è disponibile, il risultato deve dichiarare `not_available`; non è ammesso simulare un'analisi.
5. Un analizzatore remoto è fuori dalla configurazione iniziale e richiede un adattatore separato e autorizzazione esplicita. Lo schema impone che la risposta remota dichiari tale autorizzazione.
6. Le proposte non devono contenere copie integrali o estratti estesi del materiale.
7. Il motore non può scrivere in `catalog/materials.json`, `catalog/skills.json` o nel registro delle decisioni.
8. Prima di salvare, il componente chiamante ricontrolla l'impronta del materiale e valida la risposta.

## Errori e comportamento

- Motore non configurato o non disponibile: `not_available`.
- Parte dei contenuti non leggibile o limiti raggiunti: `partial`, con limiti dichiarati.
- Risposta malformata o non conforme allo schema: rifiutare la risposta; non salvarla come proposta valida.
- Materiale cambiato durante l'analisi: interrompere e non salvare.
- Errore tecnico non recuperabile: `failed`, con descrizione non sensibile.
- Evidenze insufficienti: categoria `unclassified` o affermazioni esplicitamente sconosciute.

## Verifiche del contratto

`tests/test_semantic_classification_request.py` verifica lo schema e i vincoli incrociati della richiesta: limiti, percorsi, autorizzazioni, riferimenti ai file, impronte e dimensioni.

`tests/test_semantic_classification_contract.py` verifica che lo schema del risultato:
- accetti una proposta completa e correttamente documentata;
- rifiuti categorie e stati non previsti;
- rifiuti capacità o affermazioni dichiarate senza prove;
- consenta informazioni sconosciute senza prove;
- rifiuti impronte non valide, prove fuori dalle sorgenti ammesse e campi non previsti;
- accetti un riferimento remoto non visitato come non classificato, con sola prova d'identità;
- impedisca di dichiarare autorizzato un analizzatore locale o di usare un analizzatore remoto senza autorizzazione esplicita.

Questi test verificano il contratto dei dati, non la qualità di un modello né l'effettivo isolamento di un futuro motore. Tali verifiche saranno necessarie durante l'implementazione.
