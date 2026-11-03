---
name: skill-authoring-adaptation
description: "Adattamento delle skill: usa quando devi trasformare una procedura, una raccolta o un flusso in una skill Agent Skills riutilizzabile e indipendente dalla piattaforma."
metadata:
  library_id: "library.skill-authoring-adaptation"
  version: "0.1.0"
  scope: "universal"
---

# Adattamento e creazione di skill

## Scopo

Trasformare una capacità o una procedura verificata in una skill riutilizzabile, senza confondere la skill con il materiale originale, il codice che la realizza o lo strumento che la esegue.

## Quando usarla

- Quando una risorsa è stata scelta per essere adattata.
- Quando una capacità utile non è ancora descritta da una skill.
- Quando una skill esistente è troppo legata a una piattaforma o a un progetto.
- Quando devi aggiornare una skill mantenendo provenienza e versioni.

## Ingressi

- Obiettivo e risultato atteso.
- Schede di tutti i materiali sorgente.
- Capacità che la skill deve coprire.
- Vincoli, dipendenze, autorizzazioni e ambiente previsto.

## Risultati

- Cartella della skill con SKILL.md conforme al formato Agent Skills.
- Contratto della skill: ingressi, risultati, prerequisiti, limiti, rischio e verifica.
- Voce nel catalogo con tutte le fonti collegate.
- Piano di prova e stato iniziale non verificato.

## Procedura

1. **Verifica le fonti.** Controlla che ogni materiale sorgente sia registrato e abbia una revisione. Se la licenza è sconosciuta, non dichiarare che il materiale è liberamente riutilizzabile.
2. **Separa i concetti.**
   - Capacità: il risultato che deve poter essere ottenuto.
   - Skill: la procedura riutilizzabile che compone una o più capacità.
   - Implementazione: il codice o servizio che realizza un'operazione.
   - Strumento: il mezzo concreto con cui l'implementazione viene usata.
   - Ruolo o agente: chi decide o svolge una responsabilità.
   - Dipendenza: ciò che deve essere disponibile prima o durante il lavoro.
   - Prova: il dato osservabile che dimostra un esito.
3. **Estrai il nucleo universale.** Mantieni le regole valide in più contesti. Sposta le istruzioni specifiche di un programma, servizio, sistema operativo o progetto in un riferimento separato o in un adattatore dichiarato.
4. **Conserva gli originali.** Non sovrascrivere la fonte. Registra le modifiche e collega tutte le schede sorgente tramite source_material_ids. Se la skill è la copia di una singola skill preesistente, usa anche il collegamento alla skill originale previsto dal catalogo.
5. **Definisci un solo scopo principale.** Evita skill monolitiche che accumulano attività non correlate. Dividi soltanto quando le procedure hanno ingressi, condizioni di attivazione o criteri di completamento realmente distinti.
6. **Scrivi il frontmatter.** Usa un nome minuscolo con parole separate da trattini, uguale al nome della cartella. La descrizione deve spiegare cosa fa e quando attivarla. Non aggiungere campi proprietari o sperimentali senza una ragione verificata.
7. **Scrivi le istruzioni principali.** Metti nel file principale i passaggi necessari in ogni esecuzione. Sposta materiale di consultazione usato solo in casi particolari in references/, con un collegamento chiaro che spieghi quando leggerlo.
8. **Definisci il contratto.** Specifica ingressi, risultati, prerequisiti, vincoli, rischio, permessi, errori possibili, condizioni di arresto e verifica. Non lasciare impliciti dati o autorizzazioni necessari.
9. **Mantieni la portabilità.** Descrivi prima il comportamento richiesto. Metti i comandi, i servizi e le dipendenze di una piattaforma in un'implementazione o in un adattatore separato. Non trasformare un comando specifico in un requisito universale.
10. **Gestisci le licenze.** Rispetta gli obblighi delle fonti derivate, conserva attribuzioni e avvisi richiesti e indica le modifiche. Non assegnare una licenza alla skill derivata se il titolare del progetto non l'ha scelta.
11. **Registra la skill.** Aggiungi la voce al catalogo, collega tutte le fonti, assegna versione e ciclo di vita. Una skill appena scritta deve restare unverified; non marcarla stable o active soltanto perché il file è valido.
12. **Controlla la struttura.** Verifica frontmatter YAML, nome, descrizione, cartella, riferimenti, ingressi, risultati, capacità collegate e fonti. Esegui il validatore della libreria.
13. **Prepara le prove.** Definisci esempi controllati con risultati attesi prima di dichiarare la skill verificata.

## Regole

- SKILL.md descrive il comportamento; non è automaticamente il codice che lo esegue.
- Non copiare intere raccolte quando bastano poche procedure.
- Non mantenere duplicati della stessa regola in più file: usa riferimenti chiari.
- Non nascondere prerequisiti, permessi o effetti collaterali.
- Non dichiarare la skill stabile senza prove funzionali indipendenti.

## Criteri di completamento

La skill è preparata quando il file è conforme, il contratto è completo, le fonti sono collegate, la licenza è registrata, il validatore passa e le prove funzionali sono definite. Fino al superamento delle prove, il ciclo di vita resta unverified.
