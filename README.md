# universal-skill-library

Libreria universale di skill per agenti AI: raccolta, analisi, verifica, test, composizione e miglioramento continuo delle skill. Il progetto separa capacità, skill e implementazioni e mira a coordinare attività con tracciabilità, verifiche basate su prove e rilevamento delle capacità mancanti.

## Documentazione
- [Architettura](ARCHITECTURE.md)
- [Modello strutturale](STRUCTURAL-MODEL.md)
- [Glossario](GLOSSARY.md)
- [Decisioni e questioni aperte](DECISIONS.md)
- [Roadmap](ROADMAP.md)
- [Struttura della libreria](docs/LIBRARY-STRUCTURE.md)
- [Dati per la selezione autonoma delle skill](docs/SKILL-SELECTION.md)

## Controlli locali
```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/validate_library.py
```

La documentazione e i controlli verificano la struttura dei dati. Non dichiarano che skill non ancora inserite, il coordinatore o le implementazioni siano già funzionanti.
