# Contratto tecnico — integrità dei materiali

Versione: 1.0  
Componente: `scripts/material_integrity.py`

## Scopo

Fornire un servizio comune per verificare l'identità del materiale nel catalogo, lo stato di acquisizione, la sicurezza del percorso e la corrispondenza dell'impronta SHA-256 con il contenuto locale conservato.

La presenza di una scheda nel catalogo non costituisce, da sola, prova dell'integrità del materiale.

## Interfaccia

### `load_material_record(root, material_id)`

Restituisce la tupla:

`(record, catalog, catalog_path)`

Controlla che il catalogo sia leggibile e strutturalmente valido, che l'identificativo esista una sola volta e che il catalogo non cambi durante la lettura. Non ricalcola l'impronta del materiale.

In caso di errore solleva `MaterialIntegrityError`, sottoclasse di `ValueError`, con il campo stabile `code`.

### `verify_material(root, material_id, expected_digest=None, allowed_states=("preserved",))`

Restituisce un risultato conforme a `schemas/material-integrity-result.schema.json`.

Il risultato contiene identità, tipo originale, stato di acquisizione, percorso relativo, impronta registrata, impronta ricalcolata, algoritmo, controlli effettuati, problemi e stato complessivo.

Stati:
- `verified`: materiale locale, percorso e impronta controllati;
- `not_applicable`: riferimento remoto controllato solo nei metadati; il contenuto non è stato visitato;
- `blocked`: condizione di sicurezza, stato o integrità non accettabile;
- `failed`: errore tecnico o strutturale che impedisce il controllo.

## Impronte supportate

- `sha256-file-v1`: SHA-256 dei byte del file.
- `sha256-tree-v2`: SHA-256 della struttura della cartella, inclusi i nomi di file e cartelle vuote.
- Campo `digest_algorithm` assente su cartelle: impronta storica precedente, mantenuta per compatibilità.
- Campo `digest_algorithm` assente su file: comportamento storico mantenuto per compatibilità.
- Algoritmi sconosciuti o incompatibili con il tipo effettivo: controllo non superato; nessun ripiego automatico.

## Sicurezza e limiti

- Rifiuta percorsi assoluti, attraversamenti con `..`, percorsi fuori da `intake/` e collegamenti simbolici.
- Non segue collegamenti simbolici e non esegue, interpreta, estrae o modifica il materiale.
- Non modifica cataloghi, proposte o originali.
- Non scarica e non visita riferimenti remoti.
- Per i riferimenti remoti, l'esito `not_applicable` non equivale a una verifica positiva del contenuto.
- Esegue un controllo iniziale e un ricontrollo finale del catalogo e del contenuto locale.
- I controlli riducono il rischio di modifiche concorrenti, ma non costituiscono una protezione assoluta contro ogni possibile attacco TOCTOU su file system condivisi o ostili.

## Integrazioni

Il classificatore statico, il componente di approvazione e il verificatore delle prove semantiche usano il servizio comune. L'approvazione non dipende più da funzioni interne del classificatore.

Il servizio non certifica correttezza semantica, sicurezza operativa, funzionamento, compatibilità o autorizzazione all'uso. Questi controlli restano responsabilità di componenti distinti.
