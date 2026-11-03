# Verifica locale della libreria su Windows

## Scopo

La suite GitHub Actions è già stata eseguita con successo su `windows-latest`: 183 test superati e validatore superato nel run [41545326945](https://github.com/bhevivision/universal-skill-library/actions/runs/41545326945).

Questa procedura serve a verificare la stessa base sul computer Windows dell'utilizzatore. La prova sul computer personale è distinta dalla prova su un esecutore Windows remoto.

La procedura non acquisisce materiali reali e non modifica i cataloghi. I test usano dati temporanei.

## Prima di iniziare

Occorrono:
- repository già clonato sul computer;
- Git;
- Python 3.11;
- connessione Internet per scaricare le dipendenze di sviluppo.

Non proseguire se nella cartella del repository ci sono modifiche personali non salvate.

## Passaggi

### 1. Aprire la cartella corretta

1. Aprire Esplora file.
2. Aprire la cartella in cui si trova il repository `universal-skill-library`.
3. Entrare nella cartella principale, quella che contiene `README.md`, `ROADMAP.md`, `scripts` e `tests`.
4. Fare clic con il tasto destro in uno spazio vuoto e scegliere **Apri nel Terminale**.

### 2. Controllare ramo e modifiche locali

Nel terminale PowerShell eseguire, una riga alla volta:

```powershell
git status --short
git fetch origin
git switch model/structural-model-v1
git pull --ff-only origin model/structural-model-v1
git branch --show-current
```

L'ultimo comando deve mostrare:

```
model/structural-model-v1
```

Se `git status --short` mostra file modificati, oppure Git segnala conflitti o impedisce il cambio di ramo, fermarsi: non cancellare né sovrascrivere le modifiche locali.

### 3. Controllare Python

```powershell
py -3.11 --version
```

Deve comparire Python 3.11.x. Se il comando non viene riconosciuto, fermarsi: occorre installare Python 3.11 prima di proseguire.

### 4. Creare un ambiente separato e installare le dipendenze

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Se PowerShell blocca l'attivazione dell'ambiente, eseguire soltanto per la finestra corrente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 5. Eseguire tutti i test

```powershell
python -m unittest discover -s tests -v
```

Esito atteso: tutti i test terminano con `OK` e il codice di uscita è zero. Il numero atteso nell'ultima verifica automatica era 183; se cambia dopo nuovi aggiornamenti, conta l'esito effettivo della suite sul ramo aggiornato.

### 6. Eseguire il controllo della libreria

```powershell
python scripts/validate_library.py
```

Esito atteso:

```
CONTROLLO SUPERATO: acquisizioni, cataloghi, collegamenti, implementazioni e prove coerenti.
```

### 7. Consegnare le prove

Copiare qui nella conversazione:
- l'ultima parte dell'uscita dei test, compresa la riga `Ran ... tests` e `OK`;
- l'intera riga `CONTROLLO SUPERATO`;
- l'uscita di `py -3.11 --version`;
- l'uscita di `git branch --show-current`.

Se compare un errore, copiare il messaggio completo e fermarsi. Non modificare test o file per far passare il controllo.

## Pulizia facoltativa

L'ambiente virtuale `.venv` può essere lasciato per le verifiche future. Per disattivarlo:

```powershell
deactivate
```

Non eliminare cartelle o file del repository durante questa verifica.

## Che cosa dimostra questa prova

Se entrambi i controlli terminano con esito positivo, avremo verificato che la suite e il validatore funzionano anche sul computer Windows utilizzato.

Questa prova non certifica la sicurezza o la funzionalità delle skill inventariate, non sostituisce la verifica su altre piattaforme e non dimostra ancora l'interoperabilità con Claude Code o Codex.
