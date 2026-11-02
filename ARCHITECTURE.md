# Architettura della libreria universale

Stato: modello strutturale v1 documentato; non ancora implementato né collaudato.

## Scopo
Trasformare un obiettivo espresso in linguaggio naturale in attività eseguibili e verificabili. Il sistema individua le capacità necessarie, seleziona skill adeguate, controlla implementazioni, strumenti e autorizzazioni, coordina l'esecuzione e accetta il risultato soltanto quando le prove soddisfano i criteri iniziali.

La libreria conserva metodi riutilizzabili. Il coordinatore li seleziona e combina in funzione dell'obiettivo e dell'ambiente reale. Libreria e coordinatore sono distinti e non dipendono da un singolo modello o fornitore.

## Principi
1. Indipendenza da Claude Code, Codex e altre piattaforme.
2. Agent Skills come formato comune; nessuna estensione proprietaria obbligatoria nel frontmatter.
3. Separazione tra capacità, skill e implementazione.
4. La presenza nel catalogo non prova la disponibilità nell'ambiente.
5. Composizione dinamica di attività e dipendenze, non flussi rigidi universali.
6. Verifica basata su prove; esecuzione, verifica, accettazione e completamento sono distinti.
7. Recupero selettivo: conservare risultati validi e ripianificare soltanto la parte coinvolta.
8. Minimo privilegio e approvazione umana per operazioni rischiose o irreversibili.
9. Dichiarare limiti e impossibilità; mai simulare un successo.

## Responsabilità logiche
Queste responsabilità non richiedono necessariamente agenti o servizi separati.
- Interprete dell'obiettivo: formalizza risultato, vincoli e criteri di accettazione.
- Gestore di capacità e skill: ricerca, seleziona e valuta copertura, limiti, prerequisiti e alternative.
- Catalogo centrale: conserva skill, versioni, metadati, relazioni e stato delle verifiche.
- Pianificatore e coordinatore: crea attività, contratti operativi, dipendenze, parallelismo e ripianificazioni.
- Esecutore e adattatori: assegnano attività agli ambienti disponibili e traducono richieste astratte nelle interfacce specifiche.
- Verificatore: confronta risultati e criteri, registra esito e prove; quando serve è indipendente dall'esecutore.
- Gestione di stato, prove e decisioni: conserva cronologia, errori, autorizzazioni, versioni e prove. È una responsabilità trasversale.
- Politiche e autorizzazioni: controllano permessi, rischio, reversibilità e necessità di approvazione. Una skill non concede autorizzazioni.

## Ciclo operativo
1. Formalizzare obiettivo e criteri.
2. Identificare capacità necessarie.
3. Cercare skill e valutarne idoneità.
4. Verificare implementazioni, strumenti, compatibilità e permessi.
5. Creare attività, contratti e dipendenze.
6. Eseguire in sequenza o in parallelo secondo le dipendenze.
7. Verificare risultati intermedi e conservare prove.
8. In caso di errore, classificare il problema e ripianificare la parte coinvolta.
9. Verificare il risultato complessivo rispetto ai criteri iniziali.
10. Accettare e dichiarare completato soltanto con prove sufficienti.

## Recupero dinamico
Il coordinatore identifica causa e portata dell'errore, determina quali risultati dipendenti sono invalidati, conserva quelli ancora validi, valuta alternative e autorizzazioni e aggiorna il piano. Non cambia silenziosamente obiettivo o criteri. La politica considera tipo e gravità, conseguenze, probabilità di successo, costo, rischio, alternative e permessi; non usa il numero di tentativi come unica regola.

## Confini
La libreria descrive metodi riutilizzabili. Il coordinatore li combina per un obiettivo concreto. L'agente è un ambiente operativo possibile. Lo strumento è una risorsa utilizzata. La verifica è un controllo fondato su prove, non una dichiarazione dell'esecutore.

Questa architettura è una definizione logica. Non dimostra che catalogo, coordinatore, adattatori o controlli automatici siano già funzionanti. Le fasi di realizzazione sono in ROADMAP.md.
