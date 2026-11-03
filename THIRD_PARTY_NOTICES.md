# Avvisi sui materiali di terzi

Questo documento registra le fonti esterne consultate e le procedure selezionate per l'adattamento. Non assegna una licenza al contenuto originale di questo deposito né alle nuove skill: la licenza del progetto deve essere decisa separatamente.

## Materiali con licenza MIT

### Matt Pocock Skills
- Fonte: https://github.com/mattpocock/skills
- Revisione: 4ae2317ddb22b046e26455e4f9c9b3aaaf62212d
- Licenza: MIT — licenses/third-party/MIT-Matt-Pocock.txt
- Procedure adattate: skill-authoring-adaptation ed evidence-based-review; sono stati inoltre riutilizzati principi di chiarimento dei requisiti e progettazione dei moduli.
- Modifiche: procedure riscritte in italiano e limitate alle parti trasferibili alla libreria; non vengono copiati i file originali delle skill.

### Vercel Skills / Find Skills
- Fonte: https://github.com/vercel-labs/skills
- Revisione: 7a5e920bead4b1039a6d6df5d7e1163b7b09423a
- Licenza: MIT — licenses/third-party/MIT-Vercel-Skills.txt
- Procedura adattata: resource-discovery-assessment; la ricerca è separata da installazione ed esecuzione.
- Modifiche: installazione separata dalla ricerca; aggiunti controlli su provenienza, revisione, licenza, dipendenze, permessi e prove; eliminate installazione globale e conferma automatica come comportamento predefinito.

## Materiali con licenza Apache-2.0

Il testo della licenza è conservato in licenses/third-party/Apache-2.0.txt.

### ORCA Runtime
- Fonte: https://github.com/gfernandf/agent-skills
- Revisione: d9e3644e8aac6b75f327d973f94e187d2e8f789c
- Licenza: Apache-2.0.
- Uso: riferimento architetturale per workflow-composition-planning, con contratti, flussi a dipendenze, collegamenti a implementazioni, stato, controlli di policy e tracciabilità.
- Modifiche: nessun codice o file YAML ORCA viene copiato nelle nuove skill.

### ORCA Registry
- Fonte: https://github.com/gfernandf/agent-skill-registry
- Revisione: b70a6f99cf01ca928a94231e5d7b1a1e82098612
- Licenza: Apache-2.0.
- Uso: riferimento per la separazione tra capacità primitive e skill composte nella skill skill-authoring-adaptation.
- Modifiche: nessun catalogo ORCA viene importato integralmente.

### Open Knowledge Format (OKF)
- Fonte: https://github.com/GoogleCloudPlatform/open-knowledge-format
- Licenza: Apache-2.0.
- Uso: riferimento concettuale citato dal materiale UNLAZY.
- Modifiche: la specifica non viene copiata nel deposito.

### Agent Skills — codice del repository
- Fonte: https://github.com/agentskills/agentskills
- Revisione: 69ef37e9424c0a7ea9dd2293b559e43ec8176379
- Licenza del codice: Apache-2.0.
- Uso: riferimento al deposito della specifica; il formato SKILL.md viene adottato senza copiare il codice del repository.

## Documentazione con licenza CC-BY-4.0

### Agent Skills — documentazione
- Fonte: https://github.com/agentskills/agentskills/tree/69ef37e9424c0a7ea9dd2293b559e43ec8176379/docs
- Licenza: CC-BY-4.0 — licenses/third-party/CC-BY-4.0-AgentSkills-Docs.txt.
- Uso: consultazione della specifica di formato applicata alle quattro nuove skill; nessun testo della specifica è riprodotto.
- Modifiche: non viene riprodotto il testo della documentazione; le nuove skill sono scritte autonomamente e rispettano la struttura del formato.

## Materiali forniti dall'utente senza licenza autonoma dichiarata

### UNLAZY e Archivista
- Fonti: materiali presenti nel deposito della libreria e documenti completi recuperati dall'archivio personale dell'utente.
- Licenza: non dichiarata nei materiali consultati.
- Uso: l'utente ha autorizzato l'uso nel progetto. Non si presume una licenza aperta e non si riproducono integralmente i testi originali.
- Modifiche: principi e procedure vengono selezionati, riscritti e adattati al modello universale della libreria.

## Avvisi e limiti

- Nei riferimenti fissati esaminati non sono stati trovati file NOTICE separati.
- Quando un derivato contiene materiale coperto da una licenza, conservare gli avvisi e applicare gli obblighi della licenza pertinente.
- Popolarità, numero di installazioni e stelle non costituiscono prove di qualità o sicurezza.
- La registrazione di una licenza non è un parere legale e non autorizza automaticamente ogni forma di redistribuzione.
- Le skill create in questo ramo restano unverified finché non superano le prove funzionali.
