# Gestione operativa dei cataloghi

I cataloghi sono dati operativi: la validazione degli schemi non sostituisce le operazioni di consultazione e modifica.

Il comando `scripts/catalog_manager.py` offre operazioni di elenco, lettura, ricerca, inserimento, aggiornamento e rimozione per:
- `skills`
- `capabilities`
- `implementations`
- `materials`

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

Per `add` e `update`, `--entry` contiene l'intero oggetto JSON della voce, non una modifica parziale. L'aggiornamento sostituisce la voce esistente.

## Garanzie e limiti

- Ogni operazione legge e valida il catalogo rispetto allo schema JSON.
- Gli identificativi duplicati vengono rifiutati.
- Le scritture avvengono tramite file temporaneo e sostituzione atomica.
- I riferimenti tra skill, capacità, implementazioni e materiali vengono controllati quando si inserisce o aggiorna una voce.
- La rimozione di skill o capacità referenziate viene bloccata.
- I percorsi delle skill sono controllati prima della registrazione.
- Il comando non approva una skill, non ne certifica il funzionamento e non autorizza la sua esecuzione.

Una voce con stato `unverified` o `draft` resta tale: inserirla nel catalogo non la rende verificata.
