---
name: workflow-composition-planning
description: "Pianificazione e composizione dei flussi: usa quando un obiettivo richiede più attività, dipendenze, parallelismo, strumenti, autorizzazioni, verifiche intermedie o recupero dagli errori."
metadata:
  library_id: "workflow.composition-planning"
  version: "0.1.0"
  scope: "universal"
---

# Pianificazione e composizione dei flussi

## Scopo

Trasformare un obiettivo in un piano verificabile di attività collegate, scegliendo capacità e skill adeguate senza eseguire il piano.

## Quando usarla

- Quando l'obiettivo richiede più attività o risultati intermedi.
- Quando un'attività dipende dall'uscita di un'altra.
- Quando occorre distribuire il lavoro tra ruoli, agenti o strumenti.
- Quando servono autorizzazioni, controlli intermedi, recupero o intervento umano.

## Ingressi

- Obiettivo dell'utente e contesto.
- Criteri di accettazione e risultato finale richiesto.
- Cataloghi di capacità, skill, implementazioni e strumenti disponibili.
- Permessi effettivamente concessi e vincoli operativi.

## Risultati

- Piano con attività, ingressi, risultati, dipendenze e gruppi eseguibili in parallelo.
- Mappatura tra capacità, skill, implementazioni, strumenti e ruoli.
- Verifiche, permessi, gestione degli errori e condizioni di intervento umano.
- Elenco dei vuoti e delle condizioni che impediscono l'esecuzione.

## Procedura

1. **Interpreta l'obiettivo.** Riscrivilo come risultato osservabile. Se mancano informazioni che cambiano il piano, chiedi un chiarimento prima di scegliere.
2. **Definisci l'accettazione.** Elenca criteri misurabili, risultato finale, vincoli e condizioni che impediscono di dichiarare il lavoro concluso.
3. **Individua le capacità necessarie.** Cerca prima nel catalogo. Distingui la capacità richiesta dalla skill che la descrive, dall'implementazione che la realizza e dallo strumento che la rende disponibile.
4. **Valuta le candidate.** Preferisci skill verificate e compatibili. Una skill unverified, blocked o deprecated non va trattata come esecutore pronto: può essere indicata come candidata da verificare, non selezionata per un'esecuzione ordinaria.
5. **Rileva i vuoti.** Classifica ogni impedimento come capacità mancante, skill mancante, strumento mancante, autorizzazione mancante, problema tecnico o attività impossibile. Non confondere le categorie e non fingere che una skill risolva l'assenza di un permesso.
6. **Scomponi il lavoro.** Crea attività piccole, ciascuna con ingresso, risultato atteso, criterio di completamento e responsabile. Ogni attività deve produrre ciò che serve alla successiva.
7. **Definisci le dipendenze.** Collega le attività che dipendono da risultati precedenti. Raggruppa in parallelo soltanto quelle che non condividono dati da modificare e non dipendono l'una dall'altra. Verifica che il grafo non contenga cicli.
8. **Assegna ruoli e strumenti.** Separa direzione del progetto, coordinamento delle skill, libreria, esecutori, verificatore e gestione dello stato/prove. Collega gli strumenti solo dove sono necessari e registra la loro disponibilità.
9. **Controlla i permessi.** Applica il principio del minimo privilegio. Distingui lettura, scrittura, installazione, accesso a dati, invio esterno e azioni irreversibili. Richiedi approvazione umana prima delle azioni rischiose o non reversibili.
10. **Pianifica la verifica.** Per ogni attività indica come verificare il risultato, quali prove conservare e chi deve controllarle. La verifica deve essere distinta dalla produzione quando il rischio lo richiede.
11. **Pianifica il recupero.** Per ogni errore prevedibile indica come conservare lo stato parziale, come riprendere, quando annullare e quando fermarsi per chiedere intervento umano.
12. **Produci il piano, non l'esecuzione.** Restituisci il piano e i suoi vuoti. Non avviare attività, installazioni o modifiche: la fase di esecuzione richiede un esecutore separato e le autorizzazioni necessarie.

## Struttura minima del piano

Il piano deve contenere almeno:

- objective: obiettivo interpretato;
- acceptance_criteria: criteri di accettazione;
- steps: elenco delle attività con identificativo, capacità, skill, ingressi, risultati, dipendenze, permessi, verifica e recupero;
- parallel_groups: attività indipendenti eseguibili in parallelo;
- gaps: impedimenti classificati;
- human_approval: azioni che richiedono approvazione;
- completion_rule: condizione per dichiarare il progetto concluso.

Il formato concreto può essere JSON, YAML o una tabella strutturata. Non imporre il linguaggio proprietario di un singolo motore. Il modello di flusso dichiarativo ORCA è un riferimento architetturale, non un requisito di formato.

## Regole

- Il pianificatore non è l'esecutore e non dichiara il risultato finale.
- Non scegliere una skill soltanto perché è popolare o presente nel catalogo.
- Non inventare strumenti, permessi, capacità o prove.
- Non eseguire in parallelo attività con dipendenze o scritture concorrenti non controllate.
- Se il piano non può essere validato, fermati e indica gli errori.
- La conclusione del progetto dipende dall'accettazione dei risultati verificati, non dal completamento della lista di attività.

## Criteri di completamento

Il piano è pronto quando ogni criterio di accettazione è collegato ad almeno un'attività e a una verifica, tutte le dipendenze sono esplicite, non esistono cicli, i permessi sono dichiarati, i vuoti sono classificati e le condizioni di recupero e approvazione umana sono definite. Il piano non equivale all'esecuzione.
