# Struttura della libreria universale

Stato: struttura tecnica v1 proposta e sottoposta a controlli automatici sul ramo di lavoro. Non è ancora approvata come definitiva e non certifica skill non ancora inserite.

## 1. Architettura

La libreria separa tre livelli: pacchetti skill nel formato aperto Agent Skills; cataloghi leggibili dalle macchine; implementazioni tecniche specifiche per piattaforma e agente. Nome e descrizione restano nel `SKILL.md` canonico. I cataloghi conservano identificativi, relazioni, dati di selezione e riferimenti alle prove.

## 2. Struttura

```text
/
├── README.md
├── ARCHITECTURE.md
├── STRUCTURAL-MODEL.md
├── GLOSSARY.md
├── DECISIONS.md
├── ROADMAP.md
├── skills/<skill-name>/SKILL.md
├── implementations/<platform>/<implementation-id>/manifest.json
├── catalog/{capabilities,skills,implementations}.json
├── schemas/
│   ├── capability.schema.json
│   ├── skill-entry.schema.json
│   ├── implementation.schema.json
│   ├── implementation-manifest.schema.json
│   ├── evidence.schema.json
│   └── *-catalog.schema.json
├── scripts/validate_library.py
├── tests/test_validate_library.py
├── requirements-dev.txt
├── .github/workflows/validate-library.yml
├── examples/capability-mapping.json
└── docs/{LIBRARY-STRUCTURE,SKILL-SELECTION}.md
```

Le directory e le skill preesistenti non vengono spostate o riscritte in questa fase.

## 3. Pacchetti skill

Ogni skill pubblicabile è una cartella autonoma con `SKILL.md` obbligatorio e risorse facoltative (`scripts/`, `references/`, `assets/`). Il nome della cartella coincide con il campo standard `name`. Il frontmatter obbligatorio resta quello di Agent Skills (`name` e `description`): non si introducono campi proprietari obbligatori. Le dipendenze specifiche di piattaforma vengono dichiarate nelle implementazioni.

## 4. Cataloghi

I cataloghi sono JSON versione `1.0`, validati con JSON Schema Draft 2020-12.

- **Capacità:** identificativo, nome, descrizione, categoria, risultato atteso, criteri di verifica, capacità collegate, skill associate, limitazioni e stato. Una capacità senza skill associate rappresenta una lacuna, non un errore strutturale.
- **Skill:** identificativo, percorso, capacità coperte, ambito, versione, ciclo di vita e dati di selezione: segnali del compito, ingressi, risultati, prerequisiti, vincoli, rischio e verifica.
- **Implementazioni:** identificativo, skill/versione servita, piattaforma, percorso del manifesto, requisiti, strumenti, permessi, agenti compatibili, stato e verifica.

Una skill `stable` richiede verifica superata e prove consultabili. Un'implementazione `verified` richiede verifica superata, data e prove. Il manifesto dichiara almeno identificativo, skill, versione e piattaforma e deve coincidere con il catalogo.

## 5. Prove

Le prove permanenti non riservate sono referenziate sotto `tests/evidence/`. Ogni prova descrive soggetto, esito, data, comando/procedura e sintesi. Il controllo verifica esistenza, formato e corrispondenza del soggetto. Non inserire credenziali, token, dati personali o documenti riservati. Le prove di una singola esecuzione utente appartengono al futuro coordinatore, non al catalogo pubblico.

## 6. Selezione autonoma

Il coordinatore applica prima le esclusioni obbligatorie (stato, copertura, ingressi, risultati, limiti, prerequisiti, piattaforma, agente, strumenti e autorizzazioni); poi confronta le candidate per copertura, compatibilità, prerequisiti, prove, rischio e permessi. La procedura completa è in [Dati per la selezione autonoma delle skill](SKILL-SELECTION.md). La disponibilità reale viene controllata al momento dell'esecuzione.

## 7. Controlli automatici

`python scripts/validate_library.py` controlla JSON e schemi, identificativi univoci, riferimenti e collegamenti reciproci, presenza dei pacchetti, nome nel frontmatter, compatibilità tra ambito e piattaforma, coerenza tra catalogo e manifesto, versione servita e prove. Impedisce di dichiarare stabile o verificata una voce senza prove adeguate.

I test si eseguono con `python -m unittest discover -s tests -v`. La stessa sequenza è configurata in GitHub Actions per ogni modifica e richiesta di integrazione.

La verifica strutturale non dimostra che una skill svolga correttamente il proprio compito: i test funzionali devono essere specifici, riproducibili e pertinenti alla versione.

## 8. Dati dinamici e limiti

Strumenti effettivamente disponibili, agenti attivi, autorizzazioni della sessione, credenziali, stato delle attività e prove temporanee non sono verità permanenti del catalogo. Questa versione non introduce motore semantico, database runtime, API del coordinatore, protocollo completo degli adattatori, installazione automatica o motore di coordinamento.
