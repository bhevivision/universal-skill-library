# Componente indipendente di acquisizione

## Scopo e confini

Il componente di acquisizione riceve materiali e li conserva nella libreria. Non decide se siano skill, non analizza semanticamente le istruzioni, non installa dipendenze, non esegue codice, non verifica il comportamento e non autorizza l'uso. Queste responsabilità restano a componenti separati.

## Interfaccia operativa

Modulo: `scripts/acquire_material.py`

Interfacce pubbliche:
- `acquire_material(root, source, material_id, ...)`: acquisisce un file o una cartella locale.
- `acquire_remote_material(root, material_id, uri, ...)`: registra un riferimento HTTP/HTTPS senza scaricare il contenuto.
- `main()`: interfaccia da riga di comando.

Esempi:

    python scripts/acquire_material.py --id acq.nuovo-materiale --source "C:/Percorso/materiale.zip"
    python scripts/acquire_material.py --id acq.cartella --source "C:/Percorso/cartella" --kind package
    python scripts/acquire_material.py --id acq.riferimento --uri "https://example.org/repository"

## Sequenza di acquisizione locale

1. Controlla identificativo, sorgente e tipo di elemento.
2. Ispeziona la sorgente senza seguire collegamenti simbolici e applica i limiti massimi prima della copia.
3. Acquisisce un blocco esclusivo per evitare due aggiornamenti simultanei del catalogo.
4. Rifiuta identificativi già registrati e cartelle di destinazione già esistenti.
5. Copia il materiale in una cartella temporanea sotto `intake/`.
6. Calcola SHA-256, algoritmo usato e dimensione; confronta l'impronta della copia con quella della sorgente.
7. Valida la scheda con lo schema del catalogo.
8. Pubblica la cartella conservata e aggiorna il catalogo tramite sostituzione atomica del file JSON.
9. Se un errore ordinario avviene prima della registrazione, elimina la copia temporanea; se l'aggiornamento del catalogo fallisce dopo la pubblicazione, rimuove la cartella appena pubblicata.

Il file o la cartella sorgente non vengono modificati. I permessi e i metadati di base dei file sono copiati con `shutil.copy2`; l'obiettivo di integrità riguarda nomi, percorsi e contenuto dei file, non una replica forense di ogni metadato del file system.

## Tipi supportati

- File: conservato come file nella sottocartella `source/`.
- Cartella: conservata come albero nella sottocartella `source/`.
- Archivio ZIP/TAR riconosciuto: conservato come file binario originale; non viene estratto.
- Pacchetto: tipo dichiarabile esplicitamente per un file o una cartella.
- Sconosciuto: tipo dichiarabile esplicitamente; la conservazione non richiede interpretazione.
- Riferimento remoto: registra URI HTTP/HTTPS e stato `received`; non dichiara una copia locale e non scarica il contenuto.

## Stati iniziali e responsabilità

Ogni acquisizione locale riuscita crea una scheda con:
- acquisizione: `preserved`;
- classificazione: `not_examined / unclassified`;
- documentazione: `unknown`;
- verifica: `not_verified`;
- utilizzabilità: `not_assessed`.

Un riferimento remoto viene registrato con acquisizione `received`, perché il contenuto non è stato copiato. La classificazione e la verifica non vengono anticipate.

## Recupero da interruzioni

Ogni acquisizione locale scrive un registro di transazione prima di pubblicare la copia conservata. All'avvio di una nuova acquisizione, il componente controlla il blocco precedente: se appartiene allo stesso computer e il processo non esiste più, recupera le transazioni. Una copia già pubblicata con impronta valida viene registrata nel catalogo; una copia non ancora pubblicata viene annullata eliminando soltanto la cartella temporanea. Le cartelle temporanee orfane vengono eliminate dopo aver acquisito il blocco. Registri incoerenti, originali mancanti o impronte diverse bloccano il recupero e richiedono controllo: il componente non indovina e non sovrascrive.

Un blocco creato da un altro computer o illeggibile non viene rimosso automaticamente, perché non è possibile dimostrare che sia inattivo.

## Riconoscimento dei duplicati

Prima della pubblicazione viene confrontata l'impronta SHA-256 con i materiali locali già conservati dello stesso tipo fisico (file con file, cartella con cartella). Se il contenuto coincide, l'acquisizione viene rifiutata e vengono indicati gli identificativi già presenti. Per i riferimenti remoti viene rilevato lo stesso URI. Non viene creato un secondo originale e non viene sovrascritto il primo.

## Protezioni e limiti noti

- Identificativi duplicati e destinazioni esistenti vengono rifiutati; non si sovrascrivono acquisizioni precedenti.
- Un blocco esclusivo impedisce scritture concorrenti tramite questo componente.
- Le copie vengono verificate rispetto alla sorgente prima della pubblicazione.
- Collegamenti simbolici vengono rifiutati.
- Prima della copia vengono applicati limiti: 10.000 file, 1 GiB complessivo e 64 livelli di profondità. Il superamento interrompe l'acquisizione prima della pubblicazione.
- I limiti di pre-ispezione non eliminano ogni rischio di modifica concorrente della sorgente durante la copia; l'impronta della copia viene confrontata con quella della sorgente prima della pubblicazione.
- Gli archivi non vengono estratti né eseguiti.
- Il componente non scarica riferimenti remoti.
- Il recupero automatico riguarda transazioni locali interrotte sullo stesso computer; blocchi di altri computer o registri corrotti richiedono controllo.
- SHA-256 dimostra la corrispondenza dei contenuti rispetto all'impronta registrata, non la sicurezza del materiale. Ogni scheda registra anche la versione dell'algoritmo: `sha256-file-v1` per file e archivi, `sha256-tree-v2` per cartelle e pacchetti a cartella.
- I record precedenti privi del campo `digest_algorithm` continuano a essere verificati con il calcolo storico, senza invalidare le acquisizioni già registrate.
- L'impronta delle cartelle include anche le cartelle vuote e distingue cartelle e file.
- Il calcolo delle cartelle considera percorsi relativi e contenuti dei file; le cartelle vuote e i metadati del file system non fanno parte dell'impronta corrente.

## Verifiche automatiche

I test dedicati controllano copia fedele, immutabilità della sorgente, cartelle annidate, archivi opachi, riferimenti remoti, duplicati, collegamenti simbolici, collisioni di destinazione e pulizia dopo un errore di copia. La suite completa e il validatore vengono eseguiti tramite GitHub Actions su Ubuntu e Windows. La verifica su un esecutore Windows remoto non sostituisce una prova sul computer Windows dell'utilizzatore.
