# Progettazione del classificatore semantico

## Stato
Proposta tecnica v1. Il classificatore semantico affianca quello statico già verificato; non lo sostituisce. Questa progettazione non autorizza l'esecuzione dei materiali né l'invio dei loro contenuti a servizi esterni.

## Obiettivo
Comprendere il significato e la funzione dei materiali acquisiti, non soltanto riconoscere parole o strutture. Il componente deve proporre:
- che cosa contiene il materiale e quale problema dichiara di risolvere;
- quali capacità sembra offrire;
- categoria: skill, strumento, agente, flusso di lavoro, risorsa, composito o non classificato;
- ingressi, risultati e condizioni d'uso dichiarati;
- dipendenze esplicite e dipendenze soltanto ipotizzate;
- strumenti e piattaforme menzionati, senza presumere compatibilità;
- lacune, contraddizioni, ambiguità e informazioni non determinabili;
- prove puntuali che consentano una revisione umana.

Il risultato resta una proposta: non è classificazione approvata, verifica funzionale, certificazione di sicurezza o autorizzazione all'esecuzione.

## Separazione dei componenti
1. Acquisizione: riceve e conserva qualsiasi materiale.
2. Analisi statica: individua file e contenuti leggibili entro limiti dichiarati.
3. Analisi semantica: interpreta i contenuti selezionati e restituisce affermazioni strutturate, prove e incertezze.
4. Controllo: verifica schema, riferimenti alle prove, identità e impronta del materiale.
5. Approvazione: resta nel componente separato già esistente.
6. Verifica funzionale: fase futura, distinta, in ambiente isolato e con autorizzazioni specifiche.

Il classificatore semantico non può modificare l'originale, il catalogo approvato o le decisioni di approvazione.

## Sicurezza e riservatezza
- Il materiale è sempre dato non fidato. Le istruzioni contenute nei file sono oggetto di analisi, mai istruzioni da seguire.
- Nessun programma, comando, script, macro o contenuto incorporato viene eseguito.
- Nessuna dipendenza viene installata e nessun collegamento remoto viene visitato automaticamente.
- Impostazione iniziale: analisi locale e nessun invio di contenuti a servizi esterni. Un eventuale analizzatore remoto sarà separato, disattivato per impostazione predefinita e richiederà autorizzazione esplicita dopo aver indicato quali dati verrebbero trasmessi.
- L'analizzatore riceve soltanto contenuti selezionati e necessari, entro limiti di dimensione e quantità.
- La proposta conserva percorsi, impronte, posizioni e identificativi delle prove; non copia documenti integrali né estratti estesi.
- I tentativi del materiale di impartire istruzioni, cambiare ruolo, richiedere segreti o alterare il risultato devono essere segnalati, non seguiti.
- In caso di contenuto illeggibile, dubbio, conflitto o prove insufficienti, il sistema dichiara il limite e può proporre la categoria non classificato.

## Architettura dell'analizzatore
Il motore semantico deve essere sostituibile e indipendente da un singolo fornitore, modello o piattaforma.

Contratto concettuale:
- ingresso: richiesta versionata con identificativo e impronta del materiale, tipo, metadati, inventario dei file selezionati, contenuti ammessi e limiti;
- uscita: risultato strutturato secondo uno schema versionato;
- errori espliciti: configurazione assente, modello non disponibile, contenuto non supportato, limite superato, risposta non valida, impronta cambiata;
- tracciabilità: identificativo e versione dell'analizzatore, modello e versione quando disponibili, data, parametri non segreti e impronte di ingresso e uscita.

Il classificatore deve poter funzionare senza un modello configurato: in tal caso restituisce lo stato not_available e non simula un'analisi semantica.

## Struttura minima della proposta
- versione dello schema e identificativo della proposta;
- identificativo e impronta esatta del materiale;
- stato: completed, partial, not_available o failed;
- categoria proposta e motivazione;
- descrizione sintetica;
- capacità individuate, ognuna collegata a prove;
- ingressi, risultati e condizioni d'uso, distinguendo dichiarato, dedotto e sconosciuto;
- dipendenze, distinguendo esplicite, inferite e non determinate;
- strumenti e piattaforme menzionati, senza attribuire compatibilità non verificata;
- riferimenti mancanti, contraddizioni, rischi e limiti;
- prove: percorso, impronta, posizione o intervallo e tipo;
- incertezza e motivazione della confidenza;
- informazioni sull'analizzatore.

Le affermazioni dedotte devono essere marcate come tali. Nessuna dipendenza, capacità o compatibilità diventa un fatto certo senza prove adeguate.

## Contratto tecnico

Il contratto di ingresso e uscita, i vincoli di riservatezza e i comportamenti in caso di errore sono definiti in [SEMANTIC-CLASSIFICATION-CONTRACT.md](SEMANTIC-CLASSIFICATION-CONTRACT.md). Lo schema versionato della proposta è `schemas/semantic-classification-proposal.schema.json`; i test del contratto sono in `tests/test_semantic_classification_contract.py`. Questi elementi specificano il confine tecnico, ma non implementano ancora il motore semantico.

## Categorie
Si mantengono le categorie già introdotte: skill, tool, agent, workflow, resource, composite e unclassified. La categoria skill non viene assegnata soltanto perché un documento si chiama SKILL o contiene metadati simili: occorre evidenza di istruzioni operative riutilizzabili e di una capacità identificabile. Un pacchetto con più elementi autonomi può essere proposto come composite, senza dividerlo o modificarlo.

## Formati nella prima versione
La prima versione semantica lavora soltanto sui testi che gli analizzatori statici esistenti sanno già leggere, mantenendo i limiti attuali. Non estrae archivi e non interpreta binari. L'estensione a PDF, documenti d'ufficio, pagine web, archivi e altri formati richiede analizzatori separati, prove specifiche e limiti documentati.

## Controlli prima di salvare
1. Verificare che identificativo e impronta corrispondano al materiale acquisito.
2. Validare la risposta rispetto allo schema e rifiutare campi o tipi non previsti.
3. Verificare che ogni prova punti a un file esaminato e alla sua impronta tramite `scripts/semantic_evidence_integrity.py`, inclusi unicità degli identificativi, riferimenti esistenti, appartenenza al materiale acquisito, assenza di collegamenti simbolici e validità degli intervalli di righe.
4. Segnalare come non supportate le affermazioni prive di prove.
5. Registrare metodo e versione dell'analizzatore.
6. Ricontrollare l'impronta prima del salvataggio.
7. Salvare una proposta separata, senza aggiornare il catalogo approvato.
8. Lasciare la decisione al componente di approvazione esistente.

## Stato del controllo delle prove

Il controllo applicativo descritto nel contratto è implementato come componente indipendente e dispone di una suite dedicata. Verifica lo schema JSON e la coerenza dei riferimenti con i file conservati, senza eseguire il materiale. L'integrazione automatica nel futuro flusso di salvataggio delle proposte sarà effettuata insieme al motore semantico; fino ad allora il comando di verifica è eseguibile separatamente.

## Piano di realizzazione
A. Contratto e schema: definire richiesta e proposta semantica; aggiungere test di validazione e compatibilità con le proposte statiche.
B. Motore sostituibile: introdurre un'interfaccia indipendente dal fornitore e un analizzatore locale configurabile. Senza modello, restituire not_available. Nessuna chiamata remota predefinita.
C. Sicurezza: testare istruzioni ostili, mancata esecuzione di codice, immutabilità di originali e catalogo, impronte, risposte malformate, timeout, limiti e file non supportati.
D. Qualità: preparare materiali con classificazione attesa; valutare errori di categoria, capacità inventate, dipendenze mancate e affermazioni senza prove. I casi ambigui devono poter restare unclassified.

## Criteri di completamento
La prima versione è completata soltanto quando:
- contratto e schema sono documentati e validati;
- un analizzatore semantico locale effettivamente disponibile produce proposte strutturate;
- l'assenza del modello non viene mascherata;
- ogni affermazione sostanziale è collegata a prove o marcata come deduzione;
- prove di sicurezza e integrità superate;
- suite completa superata su Linux e Windows;
- qualità valutata su un insieme noto di materiali;
- nessuna proposta viene approvata o inserita automaticamente nel catalogo.

Finché manca uno di questi punti, lo stato resta parziale o non verificato.
