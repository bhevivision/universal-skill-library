# Roadmap del progetto

Stato iniziale: modello strutturale v1 documentato sul ramo dedicato. Nessun coordinatore, catalogo interrogabile o controllo automatico è dichiarato funzionante in questa fase.

## Fase 0 — Conservazione e modello strutturale
- [x] Verificare repository, ramo e file correnti.
- [x] Recuperare README e contenuti delle skill presenti.
- [x] Consultare la specifica Agent Skills ufficiale.
- [x] Documentare architettura, glossario, modello, decisioni e questioni aperte.
- [ ] Revisione e approvazione della versione del modello.
- [ ] Verifica formale finale dei documenti.

Criterio di uscita: modello approvato e nessuna skill esistente spostata o modificata.

## Fase 1 — Inventario e criteri della libreria
Definire struttura del repository, catalogo capacità, indice skill, metadati esterni minimi, versioni, stati e criteri per skill generali, specifiche di piattaforma e specifiche di progetto.

Criterio di uscita: schema minimo documentato e provato con esempi rappresentativi.

## Fase 2 — Controlli automatici
Progettare controlli per frontmatter Agent Skills, nome cartella, riferimenti e risorse, metadati esterni, dipendenze, strumenti, segreti e rischi. Prevedere test isolati per skill eseguibili e registrazione degli esiti.

Criterio di uscita: controlli ripetibili in locale e integrazione continua, con casi validi e non validi.

## Fase 3 — Collocazione delle skill esistenti
Solo dopo approvazione del modello e dei criteri:
- UNLAZY: mappare riferimenti mancanti e dipendenze.
- Archivista: identificare il riferimento mancante e il suo ambito.
- Find Skills: verificare istruzioni, comandi e fonti.
- Canva KDP: preservare l'originale; il file letto è di 36 byte e appare danneggiato, non ricostruirlo come se fosse integro.

Criterio di uscita: decisione documentata per ogni file, nessuna perdita e riferimenti mancanti dichiarati.

## Fase 4 — Interoperabilità
Provare skill non sensibili su Claude Code e Codex e, se accessibile, su un'altra piattaforma. Separare contenuto canonico e adattamenti. Registrare prove, differenze e limiti.

Criterio di uscita: prove riproducibili di scoperta, caricamento ed esecuzione. Il caricamento da solo non prova il risultato funzionale.

## Fase 5 — Prototipo del coordinatore
Realizzare formalizzazione obiettivo/criteri, selezione capacità e skill, controllo disponibilità e permessi, piano con dipendenze e parallelismo, registrazione stati/prove/decisioni, recupero selettivo e ripianificazione.

Criterio di uscita: casi end-to-end, inclusi errori, parallelismo, permessi mancanti e risultati non verificabili.

## Fase 6 — Scelta e consolidamento del motore
Riprendere la ricerca già avviata su ORCA, LangGraph, Microsoft Agent Framework, Temporal, CrewAI e AutoGen. Esaminare il log Cognitive Continuous Validation, risolvere discrepanze, verificare registry/runtime/dipendenze, eseguire prove riproducibili su Windows e confrontare recupero, persistenza, parallelismo, sicurezza e osservabilità.

Criterio di uscita: scelta motivata da risultati comparabili e limiti espliciti.

## Regola generale
Una fase non è completata perché i documenti sono stati scritti o il codice prodotto. È completata quando i criteri di uscita sono verificati con prove consultabili. Se la verifica non è possibile, lo stato resta NON VERIFICABILE.
