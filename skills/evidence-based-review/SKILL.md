---
name: evidence-based-review
description: Verifica basata su prove: usa quando devi dimostrare che una skill, un'implementazione o un risultato rispetta criteri di accettazione, oppure diagnosticare un esito fallito.
metadata:
  library_id: "verification.evidence-based-review"
  version: "0.1.0"
  scope: "universal"
---

# Verifica basata su prove

## Scopo

Stabilire se un risultato soddisfa criteri dichiarati, usando prove osservabili e riferite alla versione e all'ambiente effettivamente controllati.

## Quando usarla

- Prima di dichiarare una skill o un'implementazione funzionante.
- Quando devi verificare un risultato consegnato.
- Quando una prova fallisce, è incompleta o è diventata obsoleta.
- Prima di cambiare lo stato di una skill in verificata o stabile.

## Ingressi

- Oggetto da verificare e sua versione.
- Criteri di accettazione.
- Ambiente, dati e autorizzazioni disponibili.
- Prove già raccolte e verifiche precedenti.

## Risultati

- Esito: passed, failed, inconclusive o not_run.
- Prove collegate, con origine, data, versione, ambiente e procedura.
- Lacune, causa identificata o motivazione per cui non è possibile verificare.
- Decisione: accettare, bloccare, correggere o chiedere intervento umano.

## Procedura

1. **Definisci prima il criterio.** Per ogni requisito scrivi quale risultato osservabile lo soddisfa e quale prova lo dimostra. Non cambiare il criterio dopo aver visto il risultato per far apparire il test superato.
2. **Fissa l'oggetto.** Registra versione o commit, configurazione, ambiente, dati di prova e dipendenze. Una prova non si trasferisce automaticamente a una versione diversa.
3. **Scegli il punto di verifica.** Usa l'interfaccia pubblica attraverso cui il comportamento viene realmente usato. Evita controlli interni che non dimostrano l'effetto visibile al chiamante.
4. **Prepara una prova capace di fallire.** Per il software usa test prima della modifica e un ciclo rosso-verde-rifinitura. Per altri compiti usa casi campione, fonti indipendenti o controlli ripetibili.
5. **Esegui e conserva.** Registra comando o procedura, risultato integrale utile, data, ambiente e riferimenti. Conserva anche gli esiti parziali e negativi; non sovrascrivere la storia.
6. **Valuta la qualità della prova.**
   - A: osservata direttamente nell'ambiente reale.
   - B: ricavata da codice, configurazione o documentazione esaminati.
   - C: indizio indiretto o dichiarazione non riprodotta.
   Una prova B o C non dimostra da sola il funzionamento operativo.
7. **Assegna l'esito.** passed solo se tutti i criteri applicabili sono soddisfatti; failed se una prova riproducibile dimostra una violazione; inconclusive se i dati sono discordanti o insufficienti; not_run se la verifica non è stata eseguita.
8. **Se fallisce, diagnostica prima di correggere.** Riproduci il sintomo, riduci il caso al minimo, formula ipotesi verificabili e identifica la causa. Non applicare correzioni speculative e non ripetere la stessa prova senza cambiare una condizione motivata.
9. **Dopo la correzione, ripeti.** Riesegui la prova che aveva fallito e aggiungi un controllo che impedisca la ricomparsa del problema. Registra separatamente i risultati prima e dopo la correzione.
10. **Controlla l'obsolescenza.** Se cambia il codice, la fonte, la configurazione, il modello, il servizio o il dato da cui dipende una prova, valuta se la prova è stale e deve essere ripetuta.
11. **Decidi il completamento.** Accetta soltanto se tutti i criteri iniziali sono soddisfatti. Se manca accesso, autorizzazione o prova, dichiara il blocco o l'impossibilità di verificare; non simulare il successo.

## Regole

- Un comando avviato non equivale a un'attività completata.
- Un file prodotto non equivale a un risultato verificato.
- Un test superato non equivale automaticamente all'accettazione del progetto.
- L'assenza di errori visibili non dimostra che il risultato sia corretto.
- Il produttore del risultato non deve essere l'unica fonte della sua verifica quando il rischio lo richiede.
- Non eliminare prove negative, log o tentativi precedenti.
- Non attribuire una causa se le prove non la sostengono.

## Criteri di completamento

La verifica è conclusa quando ogni criterio ha un esito, ogni esito ha una prova tracciabile o una motivazione esplicita di mancanza, le prove sono riferite alla versione corretta e la decisione finale è coerente con gli esiti. In caso contrario, lo stato resta incompleto, fallito o non verificabile.
