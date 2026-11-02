# Contratto tecnico della classificazione semantica

## Stato e ambito

Contratto v1 per richiesta e risultato dell'analisi semantica. Lo schema del risultato è in `schemas/semantic-classification-proposal.schema.json`. Il contratto definisce il confine tra il futuro motore semantico e la libreria; non significa che il motore sia già implementato.

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

Il JSON Schema controlla la forma dei riferimenti, ma non può verificare da solo che ogni valore in `evidence_refs` corrisponda a un identificativo realmente presente in `evidence[].id`. Il componente chiamante dovrà eseguire questo controllo di coerenza, rifiutare identificativi di prova duplicati e verificare che percorso e impronta corrispondano ai file effettivamente esaminati prima di salvare la proposta. Questi controlli applicativi non sono ancora implementati.\n\nLa conclusione di classificazione e ogni capacità o affermazione dichiarata o dedotta devono avere almeno una prova. Le prove possono riferirsi a file conservati sotto `intake/` oppure, per attestare soltanto l'identità di un riferimento remoto non visitato, alla scheda `catalog/materials.json`. Le informazioni sconosciute possono non avere prove, ma devono essere esplicitamente marcate come sconosciute. Un riferimento remoto non esaminato può quindi produrre una proposta `not_available` e `unclassified`, senza fingere di conoscerne il contenuto. Il campo compatibilità non consente il valore verificato: la verifica di piattaforma è un processo separato.

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

`tests/test_semantic_classification_contract.py` verifica che lo schema:
- accetti una proposta completa e correttamente documentata;
- rifiuti categorie e stati non previsti;
- rifiuti capacità o affermazioni dichiarate senza prove;
- consenta informazioni sconosciute senza prove;
- rifiuti impronte non valide, prove fuori dalle sorgenti ammesse e campi non previsti;
- accetti un riferimento remoto non visitato come non classificato, con sola prova d'identità;
- impedisca di dichiarare autorizzato un analizzatore locale o di usare un analizzatore remoto senza autorizzazione esplicita.

Questi test verificano il contratto dei dati, non la qualità di un modello né l'effettivo isolamento di un futuro motore. Tali verifiche saranno necessarie durante l'implementazione.
