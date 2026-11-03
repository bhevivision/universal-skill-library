# Protocollo di valutazione della classificazione primaria

## Scopo

Misurare la capacità del modello GGUF di assegnare una sola classe primaria ai materiali campione. Il risultato non certifica l'estrazione completa di capacità, interfacce, dipendenze o rischi.

## Modalità di prova

Il programma di valutazione usa la modalità `classification_only` dell'adattatore llama.cpp. In questa modalità il modello deve restituire soltanto:
- `kind`: skill, tool, agent, workflow, resource oppure composite;
- `confidence`: low, medium oppure high;
- `rationale`: motivazione basata sul testo;
- `summary`: sintesi del materiale.

Il programma non invia al modello l'etichetta attesa. Le prove di origine (percorso e SHA-256) sono costruite dall'adattatore a partire dai dati della richiesta, non dal modello. La proposta risultante è marcata `partial`, perché questa prova non estrae le altre informazioni semantiche.

## Misure

Il rapporto registra:
- accuratezza esatta sull'intero campione;
- copertura, cioè quota di materiali classificati;
- accuratezza sulle sole classificazioni non astenute;
- precisione, richiamo e F1 per classe;
- fedeltà delle prove;
- numero di astensioni;
- tempo medio per campione;
- esito e motivazione sintetica restituita dal modello per ogni campione.

## Interpretazione

Il campione iniziale contiene due esempi per classe. È utile per individuare errori grossolani e problemi d'integrazione, ma è troppo piccolo per una certificazione statistica. Nessuna soglia di accuratezza è considerata superata automaticamente e nessun risultato approva o abilita una skill.
