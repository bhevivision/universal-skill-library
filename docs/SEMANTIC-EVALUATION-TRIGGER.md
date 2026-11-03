# Avvio della valutazione semantica completa

Questo file attiva la valutazione GGUF isolata dell'estrazione semantica completa tramite GitHub Actions.

La prova usa il modello reale e il gruppo di campioni versionato. Non contiene etichette attese inviate al modello.

Esecuzione di verifica della correzione dell'adattatore GGUF, con mantenimento dei controlli indipendenti sulle prove. Nessuna modifica alle etichette attese o al gruppo di campioni.

Nuova esecuzione richiesta dopo la revisione delle istruzioni di estrazione completa (commit 7092e7e48aef5e21b3a06be01cffc06e64e872e9). Dataset ed etichette attese restano invariati.


Esecuzione di regressione: test RED per conservazione dei rischi documentati e stato completed quando l'estrazione è completa. Verificare inoltre il supporto testuale delle affermazioni sulle fonti originali.
