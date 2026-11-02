# Architettura della libreria universale

Stato: modello strutturale v1 approvato. Sul ramo di lavoro sono implementati e verificati l'acquisizione di file, cartelle, archivi opachi e riferimenti remoti, il controllo comune d'integrità, il classificatore statico limitato, l'approvazione esplicita e i contratti della classificazione semantica. La suite ha superato 183 test e il validatore su Ubuntu e Windows nel run GitHub Actions 41545326945. La verifica sul computer Windows dell'utilizzatore resta distinta. Il motore semantico, gli analizzatori per ulteriori formati, gli adattatori interoperabili e il coordinatore non sono ancora implementati. Le skill presenti non sono per questo certificate.

## Scopo
Trasformare un obiettivo espresso in linguaggio naturale in attività eseguibili e verificabili. La libreria può ricevere e conservare materiale prima di sapere se sia una skill. Il coordinatore utilizza soltanto elementi classificati e idonei allo specifico compito. Libreria e coordinatore sono distinti e indipendenti da un singolo modello o fornitore.

## Principi
1. Indipendenza da Claude Code, Codex e altre piattaforme.
2. Accettazione di pacchetti in formati e strutture differenti, senza imporre un formato comune all'originale.
3. Conservazione dell'originale senza riscrittura, correzione o adattamento preventivo.
4. Uniformità dei dati descrittivi esterni, non della struttura interna dei pacchetti.
5. Agent Skills è un formato supportato e interoperabile, non un requisito per acquisire o conservare materiale.
6. Separazione tra capacità, skill, implementazione e strumento.
7. Acquisizione, classificazione, documentazione, verifica e autorizzazione all'uso sono stati distinti.
8. Informazioni sconosciute restano sconosciute; non si inventano contenuti o dipendenze.
9. Adattamenti e istruzioni specifiche di piattaforma restano separati dall'originale.
10. Composizione dinamica, verifica basata su prove, minimo privilegio e approvazione umana per operazioni rischiose.
11. Dichiarare limiti e impossibilità; mai simulare un successo.

## Responsabilità logiche
- Interprete dell'obiettivo: formalizza risultato, vincoli e criteri di accettazione.
- Gestore dell'acquisizione: riceve, identifica, conserva e registra la provenienza.
- Analizzatore e classificatore: esamina quanto interpretabile e propone una classificazione, mantenendo esplicita l'incertezza.
- Gestore delle skill: ricerca e seleziona skill classificate, valutandone copertura, limiti, prerequisiti e alternative.
- Catalogo centrale: conserva riferimenti ai pacchetti, metadati, versioni, relazioni e stati indipendenti.
- Pianificatore e coordinatore: crea attività, contratti operativi, dipendenze, parallelismo e ripianificazioni.
- Esecutore e adattatori: traducono richieste astratte nelle interfacce specifiche degli ambienti disponibili.
- Verificatore: confronta risultati e criteri, registra esito e prove; quando serve è indipendente dall'esecutore.
- Gestione di stato, prove e decisioni: conserva cronologia, errori, autorizzazioni, versioni e prove.
- Politiche e autorizzazioni: controllano permessi, rischio, reversibilità e necessità di approvazione. Una skill non concede autorizzazioni.

Queste responsabilità non richiedono necessariamente agenti o servizi separati.

## Ciclo di acquisizione e ammissione
1. Ricevere un elemento senza presupporre che sia una skill.
2. Registrare provenienza, data, modalità di acquisizione e identità del pacchetto.
3. Conservare una copia integra dell'originale, mantenendo struttura, nomi e contenuti; calcolare un'impronta quando tecnicamente possibile.
4. Analizzare il materiale senza eseguirlo. Identificare formato, struttura, documenti, dipendenze e riferimenti solo quando rilevabili.
5. Classificare come skill, possibile skill, strumento, agente, flusso operativo, documentazione/risorsa, pacchetto composito oppure non classificato.
6. Creare una scheda descrittiva esterna con dati noti, fonti, lacune e livello di confidenza.
7. Se è una skill, valutarne prerequisiti, ingressi, risultati, limiti, rischi e compatibilità.
8. Verificare in ambiente isolato e con autorizzazioni adeguate, quando eseguibile e sicuro.
9. Registrare separatamente esito della verifica e idoneità all'uso.
10. Rendere selezionabile dal coordinatore soltanto quando i requisiti del caso d'uso sono soddisfatti.

L'impossibilità di interpretare un pacchetto non impedisce di conservarlo. Non implica però che sia una skill, eseguibile o utilizzabile.

## Stati indipendenti
- Acquisizione: non ricevuto, ricevuto, conservato, incompleto, errore di conservazione.
- Classificazione: non esaminato, in analisi, classificato, provvisorio, non classificato.
- Documentazione: sconosciuta, parziale, completa rispetto alle informazioni disponibili.
- Verifica: non verificata, in corso, superata, fallita, non verificabile.
- Utilizzabilità: non valutata, disponibile con condizioni, richiede adattamento, incompatibile, bloccata.

Un elemento può essere conservato ma non classificato; classificato ma documentato parzialmente; verificato ma non compatibile con l'ambiente corrente. Una verifica superata vale soltanto per la versione, l'ambiente, la procedura e il perimetro registrati. L'autorizzazione all'esecuzione resta soggetta ai permessi della sessione e alle politiche di rischio.

## Ciclo di coordinamento
1. Formalizzare obiettivo e criteri.
2. Identificare capacità necessarie.
3. Cercare skill classificate e valutarne idoneità.
4. Verificare implementazioni, strumenti, compatibilità e permessi effettivi.
5. Creare attività, contratti e dipendenze.
6. Eseguire in sequenza o in parallelo secondo le dipendenze.
7. Verificare risultati intermedi e conservare prove.
8. In caso di errore, classificare il problema e ripianificare la parte coinvolta.
9. Verificare il risultato complessivo rispetto ai criteri iniziali.
10. Accettare e dichiarare completato soltanto con prove sufficienti.

## Confini e limiti attuali
Il pacchetto originale è la fonte conservata. La scheda esterna descrive ciò che è noto senza modificare la fonte. Il catalogo consente ricerca e selezione. Un adattatore rende un contenuto utilizzabile in uno specifico ambiente senza trasformare l'originale. Un'implementazione è una realizzazione eseguibile; uno strumento è una risorsa concreta.

I controlli generali di acquisizione e integrità sono separati dai controlli specifici dei profili di formato. Il validatore applica il controllo Agent Skills soltanto ai pacchetti registrati tramite SKILL.md. La conservazione di materiali eterogenei è implementata per i tipi documentati; l'interpretazione e la verifica funzionale di ogni formato non lo sono. Non si deve confondere la capacità di conservare un formato con la capacità di comprenderlo o renderlo utilizzabile.