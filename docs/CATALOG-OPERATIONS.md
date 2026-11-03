# Gestione operativa dei cataloghi

I cataloghi sono dati operativi. La validazione degli schemi è necessaria ma non sufficiente: anche i collegamenti tra le voci e le prove devono essere coerenti.

Il comando scripts/catalog_manager.py offre operazioni di elenco, lettura, ricerca, inserimento, aggiornamento e rimozione per:
- skills
- capabilities
- implementations
- materials

## Comandi

Dalla cartella principale della libreria:

```powershell
python scripts/catalog_manager.py list skills
python scripts/catalog_manager.py show skills skill-id
python scripts/catalog_manager.py search skills "ricerca documenti"
python scripts/catalog_manager.py add capabilities --entry '{"id":"cap.example","name":"Esempio","description":"Descrizione","category":"generale","expected_result":"Risultato atteso","verification_criteria":["Criterio verificabile"],"status":"draft"}'
python scripts/catalog_manager.py update capabilities --entry '{"id":"cap.example","name":"Esempio aggiornato","description":"Descrizione","category":"generale","expected_result":"Risultato atteso","verification_criteria":["Criterio verificabile"],"status":"draft"}'
python scripts/catalog_manager.py remove capabilities cap.example
```

Per add e update, --entry contiene l'intero oggetto JSON della voce, non una modifica parziale. L'aggiornamento sostituisce la voce esistente.

## Controlli applicati

- Ogni catalogo viene validato rispetto al proprio schema JSON.
- Prima di leggere o modificare, vengono caricati tutti i cataloghi e controllati i collegamenti esistenti.
- Le capacità collegate a una skill devono esistere.
- Le skill collegate a una capacità o a un'implementazione devono esistere.
- Ogni identificativo in source_material_ids deve esistere nel catalogo materiali.
- source_record_id può puntare soltanto a un materiale classificato come skill.
- Le prove delle licenze revisionate devono esistere e riferirsi al materiale corretto.
- Le prove di verifica di una skill devono esistere, avere l'esito dichiarato e riferirsi all'identificativo della skill.
- I percorsi SKILL.md devono esistere, non essere collegamenti simbolici e restare all'interno della libreria.
- La rimozione di una skill, capacità o materiale ancora referenziato viene bloccata.
- Le scritture usano un file temporaneo e una sostituzione atomica.
- I percorsi principali vengono normalizzati per funzionare sia su Windows sia su Linux.

## Limiti da rispettare

- Il gestore controlla l'esistenza e la sicurezza del percorso SKILL.md; la verifica completa del frontmatter e della struttura resta affidata a scripts/validate_library.py.
- La ricerca è testuale, non semantica.
- Il gestore non esegue skill, non assegna autorizzazioni e non promuove automaticamente una skill a verificata.
- Le modifiche ai cataloghi devono essere serializzate: la scrittura atomica di un singolo file non impedisce la perdita di aggiornamenti concorrenti.
- Le modifiche a più cataloghi non sono una transazione unica. Per collegare una nuova capacità e una skill, inserire prima la capacità senza skill_ids, poi la skill, infine aggiornare la capacità con lo skill_id.
- Il validatore completo della libreria deve essere eseguito dopo le modifiche e prima di considerare conclusa l'operazione.

Una voce unverified, experimental, draft o blocked mantiene il proprio stato. La presenza nel catalogo non la rende automaticamente eseguibile.
