# Verifica Windows: stato e limitazioni

## Stato attuale

**La verifica sul computer Windows personale è NON APPLICABILE e non costituisce un'attività richiesta per proseguire.**

Il precedente computer dell'utilizzatore è fuori uso e il progetto viene sviluppato direttamente nel repository GitHub. Non è presente una copia locale del repository e non si deve presumere che esista la cartella `universal-skill-library` sul computer.

Non chiedere all'utilizzatore di eseguire i comandi di questa procedura finché non comunica di avere nuovamente un computer disponibile e di voler configurare una copia locale.

## Verifiche disponibili

La verifica tecnica disponibile è eseguita da GitHub Actions sugli ambienti remoti Linux e Windows. Questi risultati dimostrano il comportamento nei rispettivi esecutori GitHub, non sul computer personale.

Per ogni modifica:
1. eseguire la suite automatica su Linux e Windows tramite GitHub Actions;
2. eseguire il validatore della libreria;
3. conservare il collegamento alla verifica e il numero di test;
4. dichiarare separatamente ogni limite che richiederebbe una prova sul computer personale.

## Procedura locale conservata per un eventuale futuro

La procedura dettagliata può essere ripristinata quando sarà disponibile un computer Windows. Non è un prerequisito per il lavoro su GitHub e non deve bloccare lo sviluppo.

Quando sarà disponibile un computer:
- scaricare o clonare il repository dal ramo concordato;
- installare Git e Python 3.11;
- eseguire `python -m unittest discover -s tests -v`;
- eseguire `python scripts/validate_library.py`;
- registrare ramo, versione Python e risultati.

## Limiti della verifica remota

GitHub Actions non dimostra:
- il funzionamento sul computer personale;
- la disponibilità di strumenti o configurazioni installati localmente;
- l'interoperabilità reale con Claude Code, Codex o altri programmi sul computer personale.

Questi aspetti restano NON VERIFICATI fino a quando non sarà possibile eseguire una prova nell'ambiente interessato.
