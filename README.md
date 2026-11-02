# universal-skill-library

Libreria universale per acquisire, conservare, analizzare, classificare, verificare e rendere utilizzabili skill e altri materiali destinati a sistemi intelligenti. La libreria accetta pacchetti di qualsiasi formato, anche quando non sono ancora riconosciuti come skill. Gli originali restano intatti; descrizioni, classificazioni, adattamenti e verifiche sono gestiti separatamente.

Il progetto distingue capacità, materiali acquisiti, skill, implementazioni, strumenti e agenti. Il coordinatore selezionerà e comporrà le risorse adatte a un obiettivo, con tracciabilità e verifiche basate su prove.

## Principio di acquisizione
Essere ricevuto non significa essere una skill. Essere classificato come skill non significa essere verificato. Essere verificato non significa essere automaticamente compatibile o autorizzato all'esecuzione.

Agent Skills è un formato supportato, non un requisito per conservare un pacchetto.

## Documentazione
- [Architettura](ARCHITECTURE.md)
- [Modello strutturale](STRUCTURAL-MODEL.md)
- [Glossario](GLOSSARY.md)
- [Decisioni e questioni aperte](DECISIONS.md)
- [Roadmap](ROADMAP.md)
- [Struttura della libreria](docs/LIBRARY-STRUCTURE.md)
- [Dati per la selezione autonoma delle skill](docs/SKILL-SELECTION.md)

## Controlli attualmente disponibili
Comandi:
    python -m pip install -r requirements-dev.txt
    python -m unittest discover -s tests -v
    python scripts/validate_library.py

Attenzione: la validazione attuale è stata costruita intorno al profilo Agent Skills e ai cataloghi precedenti. Non attesta ancora l'acquisizione universale descritta nel modello v1. L'estensione del validatore e i relativi test sono una fase di lavoro aperta.