---
name: resource-discovery-assessment
description: "Ricerca e valutazione delle risorse: usa quando devi trovare, confrontare o registrare skill, strumenti, standard o raccolte esterne prima di riutilizzarli."
metadata:
  library_id: "library.resource-discovery-assessment"
  version: "0.1.0"
  scope: "universal"
---

# Ricerca e valutazione delle risorse

## Scopo

Individuare una risorsa utile e stabilire, con prove, se conviene riutilizzarla, adattarla, conservarla come riferimento o escluderla. La ricerca non autorizza l'installazione o l'esecuzione.

## Quando usarla

- Quando manca una capacità e occorre cercare una skill o uno strumento.
- Quando devi confrontare una risorsa esterna con una già presente nella libreria.
- Quando devi acquisire una raccolta, uno standard, un motore o una procedura.
- Prima di installare, copiare o collegare una risorsa esterna.

## Ingressi

- Obiettivo che la risorsa dovrebbe aiutare a raggiungere.
- Eventuali fonti o candidati già conosciuti.
- Vincoli di piattaforma, licenza, sicurezza, costo e autorizzazioni.

## Risultati

- Identificazione precisa della fonte e della revisione.
- Scheda materiale con tipo, ambito, licenza, dipendenze, limiti e prove.
- Decisione motivata: riutilizzare, adattare, solo riferimento, escludere o bloccare.
- Elenco delle informazioni mancanti e delle verifiche successive.

## Procedura

1. **Chiarisci il bisogno.** Descrivi il risultato atteso e la capacità mancante. Se l'obiettivo è ambiguo, chiedi il chiarimento che cambia la scelta della risorsa.
2. **Cerca la fonte primaria.** Preferisci il deposito ufficiale, la documentazione dell'autore e le revisioni identificabili. I cataloghi e i motori di ricerca servono a scoprire candidati, non a certificarli.
3. **Fissa la revisione.** Registra un tag, una versione o un identificativo immutabile del commit. Non usare soltanto un collegamento al ramo mobile quando è possibile fissare una revisione.
4. **Classifica la natura della risorsa.** Distingui almeno: standard, singola skill, raccolta di skill, registro, motore di esecuzione, strumento, agente, flusso o documento. Distingui inoltre ambito universale, dipendente da piattaforma o specifico di progetto.
5. **Esamina il contenuto reale.** Leggi istruzioni, codice, prove, dipendenze e documentazione. Non considerare una descrizione, un numero di installazioni, le stelle o una dichiarazione nel README come prova di funzionamento.
6. **Verifica la licenza.** Cerca il file e la dichiarazione effettiva alla revisione fissata. Registra identificativo, percorso, fonte, revisione, obblighi e prova. Se non trovi una licenza, registra «non dichiarata»; non dedurre che sia libera. Se le fonti sono discordanti, usa «ambigua» o «in conflitto» e richiedi revisione umana.
7. **Esamina dipendenze e rischi.** Registra requisiti di sistema, pacchetti, servizi esterni, rete, credenziali, dati trattati, permessi richiesti, scritture, installazioni e possibili effetti irreversibili.
8. **Controlla la compatibilità.** Se la risorsa segue Agent Skills, verifica cartella, SKILL.md, frontmatter e risorse collegate. Se usa un altro formato, conserva l'originale e descrivi l'adattatore necessario. Non rinominare un file YAML in SKILL.md fingendo che i due formati siano equivalenti.
9. **Valuta le prove.** Distingui documentazione, codice e test automatici da una prova eseguita nell'ambiente reale. Registra le lacune: una prova mancante non è una prova positiva.
10. **Registra il materiale.** Usa il componente di acquisizione della libreria. Se registri soltanto un riferimento remoto, dichiaralo: non affermare che esista una copia locale.
11. **Decidi.** Riutilizza soltanto se scopo, licenza, dipendenze, permessi e prove sono adeguati. Adatta se il nucleo è utile ma il formato, il linguaggio o le procedure sono specifici. Conserva come riferimento se l'architettura è interessante ma non verificata. Escludi se è fuori obiettivo o non accettabile.
12. **Separa l'attivazione.** Installazione, esecuzione di codice, collegamento di servizi e modifiche al sistema sono passaggi distinti. Procedi solo con autorizzazione esplicita e con il livello minimo di permessi. Non usare installazioni globali o opzioni che saltano le conferme come impostazione predefinita.

## Regole di sicurezza

- Non eseguire codice, script di installazione o pacchetti durante la sola fase di scoperta.
- Non inviare credenziali o dati riservati a servizi esterni.
- Non concedere permessi più ampi di quelli necessari.
- Non sostituire una fonte originale con una versione modificata.
- Non dichiarare «nessuna dipendenza» quando la dipendenza non è stata controllata.
- Non dichiarare «compatibile» senza aver verificato il formato e il comportamento nell'ambiente previsto.

## Criteri di completamento

La valutazione è completa soltanto quando sono registrati: obiettivo, fonte primaria, revisione, tipo e ambito, licenza o assenza dichiarata, dipendenze, permessi, rischi, compatibilità, prove disponibili, lacune e decisione. Se manca un elemento essenziale, lo stato resta incompleto o non verificabile.
