# Roadmap del progetto

Stato: correzioni tecniche della v1 completate sul ramo dedicato; 19 test automatici e GitHub Actions superati sul commit 0dfabf128fee1bc4f436bab598d2170686136d74. Schemi, controlli strutturali e test sono implementati; il coordinatore non è ancora implementato.

## Fase 0 — Conservazione e modello strutturale
- [x] Verificare repository, ramo e file correnti.
- [x] Recuperare README e contenuti delle skill presenti.
- [x] Consultare la specifica Agent Skills ufficiale.
- [x] Documentare architettura, glossario, modello, decisioni e questioni aperte.
- [ ] Revisione e approvazione del modello.
- [ ] Verifica formale finale dei documenti.

## Fase 1 — Inventario e criteri della libreria
- [x] Proporre struttura dei pacchetti, cataloghi e implementazioni.
- [x] Definire i dati minimi per confrontare e selezionare le skill.
- [x] Definire gli schemi delle singole voci e dei cataloghi.
- [ ] Revisione e approvazione della struttura v1.
- [ ] Collocare le skill esistenti soltanto dopo l'approvazione.

## Fase 2 — Controlli automatici
- [x] Controllo JSON e schemi.
- [x] Controllo identificativi, riferimenti e collegamenti.
- [x] Controllo pacchetti, frontmatter, piattaforme e manifesti.
- [x] Controllo delle dichiarazioni di verifica e delle prove.
- [x] Test con casi validi e non validi in locale.
- [x] GitHub Actions superata sul commit conclusivo della correzione (run 32; 19 test superati e controllo della libreria superato).

Criterio di uscita: controlli ripetibili in locale e integrazione continua, con casi validi e non validi. La verifica strutturale non certifica il comportamento funzionale delle skill.

## Fase 3 — Collocazione delle skill esistenti
Solo dopo approvazione del modello e dei criteri:
- UNLAZY: mappare riferimenti mancanti e dipendenze.
- Archivista: identificare il riferimento mancante e il suo ambito.
- Find Skills: verificare istruzioni, comandi e fonti.
- Canva KDP: preservare l'originale; il file letto è di 36 byte e appare danneggiato, non ricostruirlo come se fosse integro.

## Fase 4 — Interoperabilità
Provare skill non sensibili su Claude Code e Codex e, se accessibile, su un'altra piattaforma. Separare contenuto canonico e adattamenti. Registrare prove, differenze e limiti.

## Fase 5 — Prototipo del coordinatore
Realizzare formalizzazione obiettivo/criteri, selezione capacità e skill, controllo disponibilità e permessi, piano con dipendenze e parallelismo, registrazione stati/prove/decisioni, recupero selettivo e ripianificazione.

## Fase 6 — Scelta e consolidamento del motore
Riprendere la ricerca già avviata su ORCA, LangGraph, Microsoft Agent Framework, Temporal, CrewAI e AutoGen. Esaminare il log Cognitive Continuous Validation, risolvere discrepanze, verificare registry/runtime/dipendenze, eseguire prove riproducibili su Windows e confrontare recupero, persistenza, parallelismo, sicurezza e osservabilità.

Una fase non è completata perché i documenti sono stati scritti o il codice prodotto: servono prove consultabili. Se la verifica non è possibile, lo stato resta NON VERIFICABILE.
