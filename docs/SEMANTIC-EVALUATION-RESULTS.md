# Risultati della valutazione semantica — 3 novembre 2026

## Esito

La prova reale del modello **Qwen2.5-3B-Instruct GGUF, quantizzazione Q4_K_M**, eseguita con llama.cpp su GitHub Actions, è terminata con esito positivo.

| Misura | Risultato |
|---|---:|
| Materiali campione | 12 |
| Accuratezza esatta | **100% (12/12)** |
| Copertura | **100%** |
| Accuratezza sulle classificazioni prodotte | **100%** |
| Macro-F1 | **1,00** |
| Fedeltà delle prove | **100%** |
| Astensioni | **0** |
| Tempo medio per materiale | **26,711 s** |

Sono stati provati due materiali per ciascuna delle sei classi: skill, tool, agent, workflow, resource e composite. Tutte le sei classi hanno precisione, richiamo e F1 pari a 1,00 nel campione.

## Prova ripetibile

- Esecuzione GitHub Actions: [run 41632778918](https://github.com/bhevivision/universal-skill-library/actions/runs/41632778918)
- Rapporto completo e prove: [artefatto della valutazione](https://github.com/bhevivision/universal-skill-library/actions/runs/41632778918/artifacts/13228659123)
- Rapporto sintetico versionato: [reports/semantic-evaluation-qwen2.5-3b-2026-11-03.json](../reports/semantic-evaluation-qwen2.5-3b-2026-11-03.json)
- Verifica automatica del codice: [run 41632778956](https://github.com/bhevivision/universal-skill-library/actions/runs/41632778956), 205 test superati su Ubuntu e Windows.

Impronta SHA-256 del file GGUF:

`626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`

Impronta dell'immagine llama.cpp:

`ghcr.io/ggml-org/llama.cpp@sha256:10a38e6cc91760ab157f0a0a8546218d35f4a314432a70298abfa3d096829ad7`

## Isolamento e limiti applicati

Il modello è stato eseguito in un contenitore Docker con:
- memoria massima 5 GiB;
- 2 CPU;
- massimo 128 processi;
- file system principale in sola lettura;
- tutte le capacità Linux eliminate;
- divieto di acquisire nuovi privilegi;
- modello montato in sola lettura;
- rete Docker interna senza accesso esterno e senza porte pubblicate.

Il valutatore ha avuto un contenitore separato, con memoria massima 1 GiB, 1 CPU, massimo 32 processi, file system in sola lettura e codice sorgente montato in sola lettura. I due contenitori hanno condiviso soltanto il namespace di rete isolato per comunicare su loopback.

## Interpretazione e limiti

**Il risultato è positivo, ma non è una certificazione statistica.** Dodici campioni, due per classe, sono sufficienti per una prima prova funzionale e per individuare errori grossolani; non dimostrano che il modello mantenga il 100% su materiali reali vari, ambigui, incompleti o ostili.

Questa prova valuta soltanto la **classe primaria**. L'adattatore produce una proposta `partial`: non estrae ancora in questa modalità capacità, interfacce, dipendenze, strumenti e rischi. La modalità completa di analisi semantica deve essere verificata separatamente.

La prova è stata eseguita su un esecutore GitHub Actions, non sul computer personale. Questo verifica il caricamento e l'inferenza reale in un ambiente remoto controllato; non dimostra ancora prestazioni o compatibilità sull'hardware locale futuro.

## Prossimi controlli

1. Ampliare il campione con materiali reali, casi ambigui e casi negativi.
2. Separare i risultati del classificatore primario dalla qualità dell'estrazione semantica completa.
3. Misurare precisione, richiamo, F1 e tasso di astensione su un insieme più ampio e indipendente.
4. Verificare la robustezza contro istruzioni ostili contenute nei materiali e contro riferimenti/prove non validi.

Nessuna classificazione prodotta da questa prova approva o abilita automaticamente una skill.
