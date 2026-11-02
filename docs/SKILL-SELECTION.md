# Dati per la selezione autonoma delle skill

Stato: contratto tecnico proposto per il catalogo v1.

## Principio

Il coordinatore non sceglie una skill perché il nome sembra pertinente. Prima elimina le alternative non utilizzabili, poi confronta quelle rimaste per copertura, compatibilità, prerequisiti, prove e rischio. Il catalogo descrive requisiti relativamente stabili; strumenti, agenti, versioni e autorizzazioni realmente disponibili vengono rilevati nell'ambiente.

## Dati necessari per ogni skill

| Campo | Informazione | Utilità |
|---|---|---|
| `capability_ids` | Capacità coperte | Collega la skill al risultato richiesto. |
| `scope`, `platforms` | Ambito e piattaforme ammesse | Evita ambienti incompatibili. |
| `version`, `lifecycle` | Versione e stato | Esclude versioni ritirate o bloccate. |
| `selection.task_signals` | Segnali del compito | Aiuta a trovare candidate pertinenti; non prova l'idoneità. |
| `selection.inputs` | Ingressi, formato, obbligatorietà | Controlla che i dati richiesti siano disponibili. |
| `selection.outputs` | Risultati e formato | Confronta il risultato con quello richiesto. |
| `selection.prerequisites` | Prerequisiti | Verifica le condizioni necessarie prima dell'esecuzione. |
| `selection.constraints`, `limitations` | Vincoli e limiti | Esclude i casi fuori ambito. |
| `selection.risk_level` | Rischio | Determina cautele e approvazioni necessarie. |
| `selection.verification` | Stato, data e prove | Distingue metodi verificati da semplici descrizioni. |

Nome e descrizione restano nel file canonico `SKILL.md`, senza duplicarli nel catalogo.

## Dati necessari per ogni implementazione

- `skill_id` e `skill_version`: skill e versione esatta servita.
- `platform`: ambiente tecnico.
- `requirements`: requisiti e dipendenze.
- `tool_requirements`: strumenti necessari.
- `permissions_required`: autorizzazioni richieste.
- `agent_compatibility`: oggetto con `mode` e `agents`. `mode=any` richiede `agents=[]` e dichiara che l'implementazione non impone un agente specifico; `mode=specific` richiede almeno un agente e le versioni ammesse. In entrambi i casi il coordinatore verifica nell'ambiente reale piattaforma, requisiti, strumenti e autorizzazioni.
- `path`: manifesto dell'implementazione.
- `status` e `verification`: stato e prove.

## Procedura di selezione

1. Tradurre la richiesta in capacità e criteri di risultato.
2. Cercare skill collegate alle capacità; usare segnali, descrizioni e tag per ampliare la ricerca.
3. Escludere skill bloccate o ritirate, prive di copertura, con ingressi o risultati incompatibili, fuori dai propri limiti o senza prerequisiti.
4. Verificare che esista un'implementazione della versione corretta.
5. Escludere implementazioni incompatibili con piattaforma, agente, strumenti o autorizzazioni effettive.
6. Sospendere o richiedere approvazione se rischio e permessi superano la politica applicabile.
7. Confrontare le candidate rimaste in questo ordine: copertura completa; compatibilità di ingressi e risultati; prerequisiti già soddisfatti; compatibilità dimostrata; qualità e attualità delle prove; rischio e numero di permessi; limiti e possibilità di recupero.
8. Registrare perché la candidata è stata scelta e quali alternative sono state escluse.

La prima versione usa un confronto leggibile e tracciabile, non un punteggio numerico opaco. Una skill sperimentale o non verificata può essere proposta solo se la politica lo consente e il suo stato viene dichiarato.

## Controllo nell'ambiente reale

Prima dell'esecuzione il coordinatore rileva agente e versione, piattaforma, strumenti e versioni disponibili, prerequisiti, autorizzazioni e limiti della sessione. I cataloghi dichiarano requisiti: non concedono permessi e non attestano la disponibilità corrente.

## Prove

- Una verifica superata richiede data e almeno un riferimento sotto `tests/evidence/`.
- La prova deve esistere, essere leggibile, rispettare lo schema e riferirsi allo stesso identificativo della skill o implementazione.
- `stable` richiede verifica superata della skill; `verified` richiede verifica superata dell'implementazione.
- Il riferimento non sostituisce il test funzionale: le prove devono essere riproducibili e pertinenti alla versione. Per `not_run` non esistono data né prove: il catalogo registra `evidence_refs: []`.
- La soglia temporale di validità delle prove sarà definita quando saranno noti tipo e rischio delle skill.

## Limiti della v1

Non vengono ancora definiti ricerca semantica, punteggio matematico universale, memoria runtime o installazione automatica. Si definiscono i dati e le regole; il coordinatore potrà adottare tecniche di ricerca diverse senza cambiare il significato dei campi.
