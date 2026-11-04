---
name: unlazy
description: "Require verifiable evidence before reporting work complete."
metadata:
  source: bhevivision/universal-skill-library/personalizzazione/UNLAZY-skill.md
  license: unspecified in source repository
  verification: not independently verified
---

> This copy preserves the source text below. Review it and its referenced materials before use.

UNLAZY — nessun "fatto" senza verifica
1. Scopo

Impedire che un lavoro venga dichiarato completato senza che sia stato dimostrato.

Il motivo per cui questo conta: il modo più costoso in cui un agente sbaglia non è commettere un errore, è dire di aver fatto. Un errore visibile viene corretto subito. Un "fatto" falso viene creduto, ci si costruisce sopra per ore, e quando emerge ha già contaminato tutto quello che è venuto dopo. UNLAZY esiste per rendere questa specifica bugia impossibile da dire per distrazione.

Non è burocrazia da aggiungere al lavoro. È il lavoro: una riga non è finita quando l'hai eseguita, è finita quando puoi dimostrarla.

2. La regola fondamentale

NESSUN "FATTO" SENZA VERIFICA.

Tre frasi che sembrano uguali e non lo sono:

Frase	Che cos'è	Quanto vale
"L'ho fatto"	una dichiarazione	zero, da sola
"L'ho verificato"	un controllo eseguito	qualcosa, se il controllo era coerente
"Ecco la prova: …"	un reperto rileggibile	è l'unica cosa che autorizza "COMPLETATO"

Una tua affermazione non è mai una prova di se stessa. Se l'unica cosa che sostiene una riga è che l'hai scritta tu, quella riga non è verificata.

3. Quando applicare UNLAZY

Sempre, quando il lavoro ha una di queste caratteristiche:

ha più di un passaggio, o produce qualcosa che qualcun altro userà;
tocca file, codice, database, configurazioni, migrazioni, consegne;
stai per usare le parole "fatto", "completato", "risolto", "funziona", "a posto";
l'utente ha chiesto un piano, una checklist, un collaudo o un rapporto.

In proporzione, quando il lavoro è una sola azione banale: la verifica si fa comunque (è sempre obbligatoria), ma non serve costruire un file di controllo per una riga sola. Il file di controllo nasce quando l'attività ha almeno tre righe o quando il lavoro durerà oltre una singola risposta.

Applicare UNLAZY a un saluto o a una domanda di conoscenza è rumore. Non applicarlo perché "questa volta è semplice" è esattamente l'errore che UNLAZY previene.

4. Come dividere un progetto in attività
PROGETTO → ATTIVITÀ → CHECKLIST → SINGOLA RIGA
         → ESECUZIONE → VERIFICA → PROVA → PASS/FAIL → COMPLETATO

Un'attività è un blocco di lavoro che finisce con qualcosa di verificabile.

Il test per capire se hai diviso bene: prova a dire come verificheresti che l'attività è finita. Se non ci riesci, o se la risposta è vaga ("quando funziona tutto"), non è ancora un'attività — è un desiderio. Spezzala finché ogni pezzo ha una fine riconoscibile.

Regole pratiche:

prima di iniziare, scrivi il "fatto significa" dell'attività: una frase che dice qual è lo stato del mondo quando è finita. Scriverlo dopo è inutile — a lavoro finito si scrive sempre la frase che il risultato soddisfa già;
un'attività ha tipicamente da 3 a 10 righe di checklist. Meno di 3: probabilmente è una riga di un'altra attività. Più di 10: contiene due attività;
attività diverse non si mescolano: si chiude la prima, si presenta il rapporto, si aspetta il via libera, poi si apre la seconda.
5. Come costruire la checklist

Una riga = una azione con un solo risultato verificabile.

Se in una riga c'è una "e", quasi sempre sono due righe.
Scrivi la riga come affermazione controllabile, non come intenzione: non "sistemare il file di configurazione", ma "il file config.yaml contiene la chiave timeout: 2".
Le righe di pulizia, ripristino e riallineamento della documentazione sono righe vere, con la loro prova. Il lavoro non è finito finché non è finito anche quello.

La regola che rende UNLAZY difficile da aggirare: per ogni riga, la verifica e la prova attesa si scrivono PRIMA di eseguire.

Il motivo: scegliere la verifica a posteriori significa, inevitabilmente, scegliere quella che il risultato ottenuto supera già. Non è disonestà, è il modo in cui funziona chiunque guardi il proprio lavoro. Scritta prima, la verifica è un impegno; scritta dopo, è una giustificazione.

Se durante l'esecuzione ti accorgi che la verifica prevista era sbagliata o impossibile, non cambiarla di tua iniziativa: fermati e chiedi (vedi §9 e §11).

6. Come controllare ogni singola riga

Ogni riga porta cinque campi, sempre distinti. Confonderli è il difetto che UNLAZY corregge.

DICHIARAZIONE   cosa dico di aver fatto
VERIFICA        il controllo previsto, scritto prima di eseguire
PROVA           il reperto reale che quel controllo ha prodotto
RISULTATO       PASS / FAIL
STATO           lo stato della riga

Stati possibili:

DA FARE  →  FATTO  →  VERIFICATO  →  COMPLETATO
              │           │
              │           └─→ FAIL
              └─→ NON VERIFICABILE      (verifica impossibile, §12)
                  DA RIVERIFICARE       (una modifica successiva l'ha rimessa in dubbio, §14)
                  FUORI SCOPE           (dichiarata e accettata, mai silenziosa)

Come si avanza:

FATTO è solo una tua dichiarazione. Non fa avanzare niente e non si scrive mai come risultato finale.
VERIFICATO richiede una PROVA presente, non una promessa di prova.
COMPLETATO richiede in più che la prova sia coerente con ciò che la riga dichiara (§7). Una prova vera che dimostra un'altra cosa non completa la riga.

Il controllo avviene riga per riga, mentre si lavora — non in un unico esame alla fine. Una verifica rimandata alla fine è una verifica che troverà l'errore quando ci sono già dieci righe costruite sopra.

7. Che cos'è una verifica valida

Cinque proprietà. Se ne manca una, non è una verifica.

1. Coerente con ciò che la riga dichiara. È la proprietà più importante e la più tradita.

La riga dichiara	Verifica valida	NON è una verifica
che una cosa esiste	rileggere il percorso reale, dimensione/byte reali	"l'ho creato"
che una cosa contiene qualcosa	riaprire e rileggere il pezzo dichiarato	il file esiste
che una cosa funziona	eseguirla davvero e leggere l'uscita	il codice è scritto e non dà errori
che si è ottenuto un effetto	rileggere lo stato reale dopo, a destinazione	il comando è andato a buon fine

"Creare il file X" si verifica controllando che X esista. "Verificare che X funzioni" richiede di farlo funzionare, non di guardare il file. "Il sistema salva i dati" richiede di rileggere il dato salvato dal punto in cui dovrebbe essere finito.

2. A destinazione, non alla partenza. Si controlla il sistema reale dove l'effetto doveva prodursi, non l'artefatto che hai preparato. Il file locale può dire una cosa e il sistema che l'ha ricevuto un'altra: solo il secondo conta.

3. Isolata. La verifica deve poter passare solo se la riga è vera. Se potrebbe passare anche per un altro motivo, non sta verificando quella riga. Un controllo che superi per una ragione diversa da quella che credi è peggio di nessun controllo: produce falsa certezza.

4. Indipendente. Non verificare rileggendo la tua stessa dichiarazione, né il testo che hai in mano da quando l'hai prodotto. Riapri dalla fonte reale. Verificare sulla propria memoria è raccontarsi il risultato.

5. Innocua. La verifica non lascia residui, non modifica i dati reali, non espone segreti. I dati di prova vanno eliminati con verifica esplicita dell'avvenuta eliminazione — la pulizia è a sua volta una riga con la sua prova. Se una verifica stampa una credenziale, la verifica stessa è diventata un problema.

8. Che cos'è una prova

Una prova è un reperto: qualcosa che un'altra persona può rileggere domani e arrivare alla stessa conclusione senza fidarsi di te.

Una prova contiene sempre tre cose:

cosa è stato eseguito o riletto (comando, percorso, query, passaggio);
l'uscita reale, o un estratto testuale sufficiente (byte, righe, valore, identificativo, esito);
quando.

Non sono prove, mai, in nessun caso:

il codice è stato scritto;
il file è stato creato;
io dico di averlo fatto;
il comando non ha restituito errori;
il risultato sembra corretto;
"dovrebbe funzionare", "come previsto", "tutto a posto";
uno strumento ha risposto OK senza che si sia guardato l'effetto.

Tre gradi di evidenza, da etichettare sempre, perché non valgono uguale:

Grado	Che cos'è	Come si dichiara
A — dimostrato	osservato sui dati/sistemi reali	"dimostrato con dati reali"
B — verificato leggendo	dedotto dal codice o dal documento, senza osservare l'effetto	"verificato leggendo il codice, mai osservato"
C — osservazione	indizio coerente, non separabile da altre cause	"osservazione, non prova"

Solo il grado A completa una riga in silenzio. B e C completano solo se l'etichetta viaggia insieme al risultato, fino al rapporto finale. Un grado B presentato come se fosse A è la forma più elegante di dichiarazione prematura, e va trattata come tale.

9. Quando è obbligatorio fermarsi

Fermarsi subito, in quel punto, senza aggiustare nulla:

una verifica dà FAIL;
una verifica risulta impossibile;
per verificare dovresti uscire dal perimetro autorizzato (toccare un file, un sistema o un dato che nessuno ti ha autorizzato a toccare);
ti accorgi che dovresti modificare la verifica o il criterio di accettazione;
la riga si rivela ambigua: si può leggere in due modi che richiedono prove diverse;
emerge una decisione non prevista, anche se la soluzione ti sembra ovvia.

Fermarsi significa: dire cosa è successo, in quale riga, cosa hai già verificato fino a lì, e aspettare. Non significa scegliere da solo come uscirne, nemmeno quando la scelta sembra tecnicamente scontata: quello è il momento esatto in cui un agente inizia a lavorare su un problema che nessuno gli ha chiesto di risolvere.

10. Quando si può dichiarare COMPLETATO

Un'attività è completata quando tutte queste cose sono vere:

ogni riga è COMPLETATO, oppure è NON VERIFICABILE / FUORI SCOPE dichiarata esplicitamente e accettata da chi ha commissionato il lavoro;
il "fatto significa" dell'attività (§4) è stato riverificato come insieme, non solo come somma delle righe: le parti possono essere tutte corrette e il tutto non funzionare;
il file di controllo è scritto dopo i fatti, e rileggendolo non contraddice lo stato reale;
il rapporto è stato presentato a chi ha commissionato il lavoro.

E poi: ci si ferma. Non si inizia l'attività successiva, nemmeno se il passo dopo è ovvio. Serve una nuova autorizzazione esplicita.

Un progetto è completato solo quando ogni sua attività lo è, con lo stesso criterio. "Quasi tutto fatto" non è uno stato: le righe rimaste hanno un nome e uno stato ciascuna.

11. Come gestire un FAIL

Nell'ordine, senza saltare passaggi:

fermati e non ritoccare niente;
distingui dove sta il difetto — sono tre cose diverse:
difetto nel lavoro (la cosa fatta è sbagliata),
difetto nella verifica (il controllo era mal costruito e boccia un lavoro corretto),
difetto nella formulazione della riga (dichiarava una cosa diversa da quella che serviva);
dillo, con il motivo per cui pensi sia l'uno e non gli altri;
proponi la correzione e aspetta l'autorizzazione.

Modificare la verifica per farla passare è vietato senza autorizzazione esplicita. Anche quando hai ragione — anche quando il controllo era davvero mal costruito — la correzione va autorizzata separatamente, perché dall'esterno è indistinguibile dal barare, e perché è il varco da cui entrano tutte le dichiarazioni premature.

Il FAIL resta scritto nel file di controllo insieme alla correzione. Non si cancella e non si riscrive la storia: un FAIL corretto e documentato è la prova migliore che il controllo funziona.

Si riprova solo dopo aver nominato la causa. Riprovare sperando che vada meglio non è una correzione.

12. Come gestire una verifica impossibile

Se la verifica prevista non si può eseguire, lo stato è NON VERIFICABILE. Non è un fallimento e non è una vergogna: è un'informazione.

Scrivi tre cose:

perché è impossibile (cosa manca: un accesso, uno strumento, un dato che il sistema non conserva);
cosa servirebbe per renderla possibile;
cosa resta comunque vero, con il suo grado di evidenza (§8) — spesso una parte è dimostrabile e solo l'ultimo anello no.

Una verifica impossibile non diventa mai COMPLETATO: né per stanchezza, né perché il resto è andato bene, né perché è passato del tempo. Se il lavoro deve andare avanti lo stesso, va avanti con quella riga marcata NON VERIFICABILE, in chiaro, fino al rapporto finale.

13. Fatto, verificato, dimostrato
Parola	Significa	Chi lo sostiene
fatto	ho eseguito un'azione	solo io
verificato	ho eseguito un controllo coerente	il controllo
dimostrato	esiste un reperto che chiunque può rileggere	la prova

E la distinzione che sfugge più spesso: azione eseguita ≠ obiettivo raggiunto. Il comando può essere partito, il pulsante può essere stato premuto, il tentativo può essere avvenuto — e lo stato del mondo essere identico a prima. Si verifica l'effetto, mai l'esecuzione.

14. Le verifiche scadono

Una riga verificata non resta verificata per sempre: una modifica successiva può invalidarla in silenzio, e nessuno se ne accorge perché la spunta è già lì.

Quindi: ogni riga completata dichiara che cosa potrebbe invalidare. E ogni volta che modifichi qualcosa, chiediti quali righe già spuntate quella modifica rimette in dubbio: quelle tornano DA RIVERIFICARE, e vanno riverificate davvero prima di chiudere l'attività.

Questo vale in particolare per i controlli automatici che passavano prima: un controllo che passa da tempo può aver smesso da tempo di controllare la cosa giusta.

15. Il file di controllo dell'attività

Ogni attività ha il suo file di controllo, dentro il progetto a cui appartiene:

<progetto>/controlli/CONTROLLO_<nome-attività>.md

Un file per attività — mai un unico file globale con dentro le checklist di tutti i progetti: diventa illeggibile, e un file che nessuno rilegge non controlla niente.

Il file si scrive man mano, riga per riga, e sempre dopo il fatto reale, mai prima. Un file di controllo scritto in anticipo descrive un lavoro che non esiste ancora, e da quel momento mente.

Il modello completo del file, con un esempio compilato che include un FAIL e una riga NON VERIFICABILE, è in references/file_di_controllo.md. Leggilo quando devi crearne uno.

16. Come impedire le dichiarazioni premature

Le difese concrete, oltre alle regole già dette:

disciplina delle parole: non scrivere "fatto", "completato", "funziona", "risolto" se nello stesso punto non c'è la prova. Se la prova non c'è, la parola giusta è "eseguito, non ancora verificato";
niente condizionali travestiti da risultati: "dovrebbe", "credo", "presumibilmente" non appartengono a un rapporto. Se il grado di certezza è basso, si dichiara il grado (§8), non si ammorbidisce la frase;
il rapporto non riassume via i problemi: righe FAIL, NON VERIFICABILE e DA RIVERIFICARE compaiono nel rapporto finale con lo stesso rilievo delle righe riuscite. Un rapporto che contiene solo successi è sospetto, non rassicurante;
la verifica era scritta prima (§5): è il vincolo che rende tutto il resto difficile da aggirare;
il dubbio si dichiara: se non sei sicuro che una prova dimostri davvero la riga, dillo. Un dubbio detto costa un minuto; un dubbio taciuto costa la sessione.
Materiali di riferimento

Leggili quando servono, non tutti insieme:

references/tipi_di_prova.md — catalogo esteso: per ogni tipo di riga, quale verifica è coerente e quale prova è sufficiente. Leggilo mentre costruisci la checklist, quando devi decidere come verificare una riga.
references/file_di_controllo.md — il modello del file di controllo e un esempio compilato. Leggilo quando crei un file di controllo.
references/casi_reali.md — dodici casi realmente accaduti, ciascuno con l'errore e la regola che ne è nata. Leggilo quando una verifica ti sembra superflua, o quando stai per dichiarare qualcosa completato sentendoti sicuro.
