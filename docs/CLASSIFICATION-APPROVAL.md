# Approvazione delle classificazioni

## Scopo

Questo componente è separato sia dall'acquisizione sia dall'analisi. L'analisi produce una proposta; questo componente registra una decisione esplicita su quella proposta.

File del componente: `scripts/classification_approval.py`.

## Regole

- Una proposta deve esistere in `proposals/<identificativo>.json` e avere stato `pending_approval`.
- La proposta deve indicare un materiale presente in `catalog/materials.json`.
- Prima della decisione, il componente ricalcola l'impronta dell'originale locale e la confronta sia con l'acquisizione sia con la proposta. Se il materiale è cambiato, blocca la decisione.
- Il responsabile e la motivazione della decisione sono obbligatori.
- La decisione viene registrata nello storico `classification.decisions` della scheda materiale.
- Ogni decisione registra anche SHA-256 della proposta esatta esaminata; la proposta viene riletta prima della scrittura e la decisione si blocca se nel frattempo è cambiata.
- Una stessa proposta non può ricevere due decisioni.
- La proposta originale resta conservata come prova di ciò che era stato suggerito. Lo storico nella scheda materiale registra l'esito della revisione.

## Approvazione

Dalla cartella principale della libreria:

    python scripts/classification_approval.py --decision approve --proposal-id class.nome-proposta --actor "nome del revisore" --reason "Motivazione della decisione"

L'approvazione aggiorna la classificazione nella scheda del materiale: stato `classified`, categoria proposta, confidenza e motivazione. Se viene approvata la categoria `unclassified`, il materiale resta esplicitamente non classificato.

## Rifiuto

    python scripts/classification_approval.py --decision reject --proposal-id class.nome-proposta --actor "nome del revisore" --reason "Motivazione del rifiuto"

Il rifiuto registra la decisione. Se il materiale non aveva già una classificazione approvata, resta `unclassified`. Un rifiuto successivo non cancella una classificazione precedente già approvata.

## Confine importante: classificazione non significa abilitazione

L'approvazione conferma soltanto la categoria assegnata al materiale. Non:
- modifica il materiale originale;
- crea automaticamente una voce in `catalog/skills.json`;
- assegna capacità, ingressi, risultati o prerequisiti non verificati;
- verifica il funzionamento, la sicurezza o la compatibilità;
- autorizza l'esecuzione del materiale.

Una proposta approvata come `skill` è quindi riconosciuta come materiale di tipo skill, ma resta fuori dal catalogo operativo delle skill finché non vengono completati i requisiti specifici per registrarla.

## Tracciabilità e limiti

Ogni decisione conserva identificativo della proposta, esito, data, responsabile dichiarato, motivazione, impronta del materiale, impronta SHA-256 della proposta e categoria proposta.

Il campo `actor` è dichiarato da chi esegue il comando: questa prima versione non include autenticazione personale, firma digitale o controllo dei ruoli. L'approvazione è quindi un passaggio esplicito e tracciato, ma non una prova crittografica dell'identità del revisore.

La proposta viene letta da un descrittore stabile, entro 2 MiB, e convalidata rispetto a `schemas/classification-proposal.schema.json`. Le prove testuali vengono verificate singolarmente rispetto ai file reali sotto `intake/`, entro 256 KiB ciascuna.

L'approvazione usa lo stesso blocco esclusivo locale dell'acquisizione, così due operazioni cooperative non possono aggiornare contemporaneamente il catalogo. Prima della scrittura ricontrolla sia l'impronta della proposta sia quella del catalogo. Il blocco non è distribuito e non protegge da programmi esterni che ignorano il blocco; non sostituisce autenticazione o autorizzazioni multiutente.
