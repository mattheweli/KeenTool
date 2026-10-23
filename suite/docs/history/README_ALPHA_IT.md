# r50 — Box Security & Health coerente con la Dashboard

Rimosso il pulsante Open Security & Health: il titolo è il collegamento alla pagina completa, utilizzabile anche da tastiera. Tolto il testo descrittivo ridondante. Il box mantiene tutta la larghezza, con due colonne di due righe (Firewall e privilegi web; spazio libero ed eventi recenti), oppure una colonna sugli schermi stretti. Le righe usano caratteri, separatori e allineamento degli altri box. Una sola fascia finale riporta la data dell'ultimo controllo e l'eventuale snapshot obsoleta; non ci sono ulteriori dati nascosti sotto i quattro valori.

Rimosso anche il doppio padding delle quattro card della Dashboard: la spaziatura è gestita dalle intestazioni, dalle righe e dal piè di pagina esistenti. Restano i colori semantici verde/giallo/rosso e il refresh comune. Questa modifica al CSS condiviso è limitata alla Dashboard; solo la Dashboard richiede il nuovo token della cache.

Installazione:

```sh
cd /opt/tmp
tar -xzf keentool_alpha_sources_20261020_r50.tar.gz
cd keentool-alpha-sources-r50
/opt/bin/bash ./install.sh --apply
```

Infine Ctrl+F5 sulla Dashboard. Non occorre rigenerare Ping o Traffic. Dashboard **2.0.0a22**, CSS condiviso **1.0.0a12**, installer **1.0.0a42**, **47 destinazioni**. Nessuna modifica a configurazioni, database, credenziali, cron o regole firewall. Il formato email r49 è incluso.

## Funzionalità r49 mantenute — Diagnostica delle blocklist nel riepilogo email

Le liste con warning o aggiornamento rifiutato sono descritte nel riepilogo email con esito esplicito, numero dei prefissi installati, dettagli della causa, eventuale utilizzo della cache, data/ora e fuso dell'ultimo tentativo e dell'ultima installazione riuscita registrata. La data di installazione non viene confusa con la freschezza dei dati recuperati dalla cache, che non è registrata. Se la data di successo non è disponibile, l'età della lista è dichiarata sconosciuta.

Per GeoBlock il precedente **0%** diventa una variazione del numero di prefissi chiaramente etichettata, accompagnata dalla causa del warning. Per GeoBlock6 l'email specifica **Update rejected; previous installed list retained**, riportando ad esempio l'HTTP 404 di un paese mancante. La variazione -100% di un candidato rifiutato non viene presentata come una perdita dei prefissi installati. Testo completo sia nella versione HTML con colori sia nella copia testuale; Recent events invariato.

Installazione:

```sh
cd /opt/tmp
tar -xzf keentool_alpha_sources_20261019_r49.tar.gz
cd keentool-alpha-sources-r49
/opt/bin/bash ./install.sh --apply
```

Il nuovo formato verrà usato dal prossimo riepilogo pianificato. Non occorre rigenerare le dashboard o eseguire di nuovo l'aggiornamento delle liste. Security Engine **1.0.0a11**, installer **1.0.0a41**, **47 destinazioni**. Questa release modifica il report; download, paesi selezionati, cache e regole di accettazione delle liste mantengono il comportamento esistente.

## Funzionalità r48 mantenute — Allineamento dei checkbox in Settings

Ogni checkbox mostra il titolo del campo sopra il controllo, come gli altri menu e input. Il controllo occupa una riga della stessa altezza degli altri widget e visualizza lo stato **Enabled** o **Disabled**, aggiornato quando viene selezionato. Titolo e controllo sono associati anche per la navigazione assistita. Il layout rimane su due colonne sui display ampi e su una colonna sui dispositivi più piccoli.

Installazione:

```sh
cd /opt/tmp
tar -xzf keentool_alpha_sources_20261019_r48.tar.gz
cd keentool-alpha-sources-r48
/opt/bin/bash ./install.sh --apply
```

Infine Ctrl+F5 su Settings. Non occorre rigenerare le dashboard. Settings pagina/controller **1.0.0a4**; installer **1.0.0a40**, **47 destinazioni**. Nessuna modifica a valori configurati, credenziali, database, cron o regole firewall.

## Funzionalità r47 mantenute — Numeri uniformi, Settings guidate e box Security sulla Dashboard

Tutte le pagine della suite usano il formato **1.234,56**: punto per le migliaia, virgola per i decimali. Latenze, jitter, perdita, conteggi campioni/punti, dimensioni, velocità, quote, percentuali, variazioni e valori dei grafici/tooltip seguono questa convenzione. Anche i contatori con segno nelle tabelle Firewall sono raggruppati. I dati numerici restano numeri nei file JS/JSON e nei calcoli; indirizzi IP, porte, date, versioni, log e diagnostica grezza conservano i propri formati tecnici.

La pagina **Settings** è organizzata in sezioni (protezione, timer, logging, bypass, GeoIP, sonde, storico e notifiche). I campi numerici mostrano intervallo ammesso, unità e valore predefinito. Menu a tendina per valori comuni di durata, cooldown, logging, punti dei grafici, intervalli di controllo, target DNS, fuso orario e ora del riepilogo. Dove sono ammessi altri valori rimane **Custom…**, con conservazione del valore già configurato. L'ora del riepilogo offre tutte le 24 ore. Per la retention il minimo visualizzato impedisce di scegliere un periodo inferiore all'attuale attraverso la pagina.

Gli input numerici usano lo stesso formato della visualizzazione: ad esempio **1.234,56 GB** viene salvato come numero 1234.56. Valori ambigui, fuori intervallo o frazionari per campi interi vengono respinti prima dell'invio; la validazione sul router rimane attiva. Form aperti e modifiche non salvate continuano a essere preservati dal refresh comune. Nessun preset viene applicato automaticamente.

Sulla **Dashboard**, il precedente link testuale è sostituito da un box **Security & Health a tutta larghezza**, con stato Firewall, privilegi web, spazio libero, numero di eventi recenti, data del controllo e pulsante per la pagina completa. Usa la snapshot pubblica e segue il refresh comune. Dati mancanti/inaccessibili sono indicati come non verificati.

Installazione:

```sh
cd /opt/tmp
tar -xzf keentool_alpha_sources_20261018_r47.tar.gz
cd keentool-alpha-sources-r47
/opt/bin/bash ./install.sh --apply
/opt/bin/bash /opt/bin/pingtool.sh force
/opt/bin/bash /opt/bin/traffic_manager.sh ppp0 force
```

Usare l'interfaccia configurata al posto di ppp0 se diversa. Infine Ctrl+F5 sulle pagine aperte. I force rigenerano i template attraverso i normali controlli/esportazioni degli script; in alternativa i template vengono aggiornati al prossimo ciclo pianificato.

Formatter condiviso 1.0.0a1; UI CSS 1.0.0a11 / JS 1.0.0a13; Dashboard 2.0.0a21, Firewall dashboard 2.0.0a24, Pingtool 2.0.0a22, Traffic 2.0.0a18, Security pagina 1.0.0a14 / controller 1.0.0a9, Settings pagina/controller 1.0.0a3 / schema 1.0.0a2. Installer 1.0.0a39, 47 destinazioni. Configurazioni, credenziali, database, cron e regole esistenti sono preservati.

## Funzionalità r46 mantenute — Layout uniforme per tutte le email

Il modulo email condiviso applica ora un unico layout HTML alle notifiche già esistenti: intestazione KeenTool, categoria del messaggio, stato evidenziato, contenuto in sezioni e piè di pagina. Colori coerenti con la suite: verde per ripristini/esiti positivi, giallo per warning e rosso per errori rilevati; i riepiloghi di attività usano una classificazione neutra. La copia testuale completa rimane inclusa.

- Ping: target, latenza/soglia e perdita in tabella; warning e perdita totale sono distinti, senza attribuire un evento di ping alla sessione PPP.
- MTR: tabella con hop, host, perdita/invii e tutti i valori di latenza (Last, Avg, Best, Worst, StDev). Metadati di avvio/host preservati. Output aggiuntivo o formati non riconosciuti restano in un riquadro monospazio. La versione testuale conserva il report originale completo. La perdita ai nodi intermedi non viene colorata automaticamente come guasto della WAN.
- Riepiloghi Firewall: periodo, totale blocchi, tabelle IP/hit e porte/hit, stato database e liste.
- Entware: tabella pacchetto/versione installata/versione disponibile; risultato dell'upgrade in un messaggio dedicato, senza cambiare le azioni di aggiornamento.
- PPP, Security, avvisi di aggiornamento KeenTool e messaggi generici: stessa struttura; il riepilogo Security conserva i colori dei singoli risultati e la riga neutra Recent events.

L'HTML viene escapato per i contenuti testuali e codificato quoted-printable per il trasporto. Nessuna risorsa esterna è necessaria per visualizzarlo. Se il renderer o PHP CLI non sono disponibili, l'invio conserva il formato precedente (testo semplice o HTML già fornito): un problema grafico non deve bloccare le notifiche. Frequenze, soglie, deduplicazione e ritenti restano invariati.

Installazione:

```sh
cd /opt/tmp
tar -xzf keentool_alpha_sources_20261018_r46.tar.gz
cd keentool-alpha-sources-r46
/opt/bin/bash ./install.sh --apply
```

Il nuovo layout si applica alle email inviate dopo l'installazione, comprese quelle eventualmente già in coda. Non serve rigenerare le dashboard né forzare ping/report. Non viene inviata un'email di prova automaticamente.

Modulo email 2.0.0a3, renderer 1.0.0a1 (`/opt/lib/keentool-mail/mail_layout.php`), disinstallatore 1.0.0a5, installer 1.0.0a38; 46 destinazioni. Configurazioni SMTP, credenziali, database, cron e regole sono preservati.

## Funzionalità r45 mantenute — Auto-refresh unico nella barra superiore

Tutte le pagine (Dashboard, Traffic, Connection, Firewall, Security & Health e Settings) usano il controllo fisso in alto:

- Auto-refresh: Off, 30 secondi, 1 minuto, 5 minuti; valore iniziale 1 minuto.
- Refresh now: aggiorna la vista corrente senza ricaricare l'intero documento.
- Preferenza unica nel browser, mantenuta passando tra le pagine e sincronizzata tra schede della stessa origine. Le precedenti preferenze separate non vengono usate.
- I refresh non si sovrappongono; le schede nascoste non fanno richieste periodiche. Off ferma i nuovi cicli automatici, mantenendo disponibile Refresh now.

Gli intervalli di raccolta del router e le pianificazioni cron restano invariati. La data di aggiornamento dei dati resta distinta dal momento in cui il browser li rilegge.

I log Dashboard vengono ricaricati integralmente soltanto se aperti; System log resta aperto inizialmente. Il log Firewall aperto segue la stessa cadenza; Pause updates sospende i suoi aggiornamenti automatici, mentre Refresh now richiede esplicitamente l'aggiornamento. I pannelli chiusi non vengono letti. Rimangono i controlli di salvataggio e filtro.

Connection conserva intervallo storico, picchi, zoom e scala dei grafici. Traffic conserva l'interfaccia selezionata. Settings controlla sessione/stato e ricarica i dati soltanto senza modifiche pendenti nel form; le modifiche non salvate vengono preservate anche con Refresh now. I timer di conferma/rollback della policy restano attivi indipendentemente dal refresh della vista.

Installazione:

```sh
cd /opt/tmp
tar -xzf keentool_alpha_sources_20261017_r45.tar.gz
cd keentool-alpha-sources-r45
/opt/bin/bash ./install.sh --apply
```

Per aggiornare subito anche i template generati (altrimenti avviene al successivo ciclo pianificato):

```sh
/opt/bin/bash /opt/bin/pingtool.sh force
/opt/bin/bash /opt/bin/traffic_manager.sh ppp0 force
```

Usare l'interfaccia configurata al posto di ppp0 se diversa. Infine Ctrl+F5 sulle pagine aperte. I comandi force eseguono i normali controlli/esportazioni dei rispettivi script; il refresh web non li esegue.

UI condivisa CSS 1.0.0a10 / JS 1.0.0a12; Dashboard 2.0.0a20, Firewall dashboard 2.0.0a23, Pingtool 2.0.0a21, Traffic 2.0.0a17, pagina Security 1.0.0a13 / controller 1.0.0a8, Settings pagina/controller 1.0.0a2. Installer 1.0.0a37, 45 destinazioni.

## Funzionalità precedenti mantenute — r44

I titoli dei quattro box passano da 15 a 20 px (peso 600), mentre i risultati restano a 17 px con i colori e il grassetto già previsti. Pagina Security & Health 1.0.0a12, installer 1.0.0a36. Installare e fare Ctrl+F5.

Il servizio controlla lo stato ogni 60 secondi per impostazione predefinita; il valore configurato può essere modificato in Settings → Security → Monitor interval (30–3600 secondi). La pagina rilegge la snapshot ogni 60 secondi; Refresh snapshot rilegge i risultati disponibili senza forzare un nuovo controllo del servizio. Le esecuzioni lente non si sovrappongono: il servizio attende un ciclo successivo se il controllo precedente è ancora in corso. Questa revisione non cambia gli intervalli.

## Funzionalità r43 mantenute

Security & Health e il riepilogo giornaliero scelgono automaticamente B, KB, MB, GB, TB o PB con al massimo una cifra decimale e senza zeri superflui. Le unità sono decimali (1 GB = 1.000.000.000 byte): 116938457088 byte diventano **116,9 GB**. Nella pagina anche le dimensioni dei database seguono lo stesso formato; la soglia spazio libero del 5% non cambia.

Il riepilogo email include una versione HTML con risultati in grassetto: verde OK, giallo non verificato/warning e rosso per problemi rilevati. Le liste con aggiornamento rifiutato sono rosse; le variazioni con warning restano gialle. **Recent events: N** resta una riga neutra con lo stesso conteggio. È inclusa anche una versione testuale per i client senza HTML. Le altre notifiche continuano a usare il formato testuale esistente. I dati inseriti nell'HTML sono escapati e un errore SMTP conserva il messaggio in coda per il tentativo successivo.

La modifica riguarda i prossimi riepiloghi generati; non invia una mail immediata né riscrive quelle già in coda. Pagina Security 1.0.0a11, controller 1.0.0a7, Security Engine 1.0.0a10, modulo email 2.0.0a2, installer 1.0.0a35. Installare e fare Ctrl+F5 sulla pagina; nessuna modifica a password, pianificazioni, database o regole.

## Funzionalità r42 mantenute

I risultati OK nei quattro box Security & Health sono in grassetto (700), con un verde più acceso e saturo nel tema chiaro (#00843d) e una variante luminosa nel tema scuro (#5cda91). Giallo e rosso mantengono il significato della r41. Pagina 1.0.0a10, installer 1.0.0a34. Installare e fare Ctrl+F5. Nessuna modifica a logica, configurazioni o database.

## Funzionalità r41 mantenute

Box Security & Health: verde per OK verificati, giallo per dati non verificati/indisponibili e backup con sola presenza senza verifica, rosso per problemi rilevati (regole non conformi, root rilevato, spazio libero sotto il 5%).

L'indicatore condiviso in alto riceve ora il risultato del caricamento Security: mostra Data available con la data del controllo dopo il caricamento, avverte dopo 3 minuti di anzianità (come il controllo già mostrato nella pagina), e segnala Security data unavailable se il caricamento fallisce. Non rimane più su Waiting for data con una snapshot disponibile. La disponibilità dei dati è distinta dallo stato di salute dei componenti nei box.

Pagina 1.0.0a9, controller Security 1.0.0a6, UI condivisa JS 1.0.0a11; installer 1.0.0a33. Installare e fare Ctrl+F5 su Security & Health. Nessun cambio a database, configurazioni, cron o regole.

## Revisione precedente r40

I quattro box usano il verde Keenetic per gli esiti verificati e il rosso per gli altri, mantenendo le descrizioni testuali. Firewall: verde se healthy, inclusa la disattivazione intenzionale verificata. Spazio Entware: verde con almeno il 5% libero, coerente con il controllo del servizio; rosso se inferiore o non verificabile. Privilegi web: verde solo quando viene rilevato un processo senza privilegi root. Backup: verde solo per un backup verificato; la sola presenza di un archivio non verificato resta rossa. Un errore di caricamento rende indisponibili e rossi i risultati, evitando di mantenere vecchi esiti verdi.

Pagina Security & Health 1.0.0a8, controller 1.0.0a5, installer 1.0.0a32. Dopo l'installazione fare Ctrl+F5 sulla pagina Security & Health. Nessuna modifica a configurazioni, database, regole o pianificazioni.

## Funzionalità r39 mantenute — Notifiche ping: warning e raggiungibilità separati

Pingtool **2.0.0a20**: un warning per perdita parziale o latenza alta continua a inviare l’alert con MTR, ma il suo rientro viene registrato solo nel log e nella timeline Security, senza email di ripristino.

L’email **Ping target reachable again** viene inviata solo dopo un controllo con perdita del 100%, al primo controllo che riceve almeno una risposta. Il tempo parte dal primo controllo con perdita totale e rappresenta un intervallo campionato, non una durata certa di disconnessione WAN. Un warning può restare attivo anche dopo il ritorno della raggiungibilità; l’email riporta perdita e stato della soglia correnti. IPv4 e IPv6 hanno stati indipendenti. Il cambio target elimina lo stato di indisponibilità del target precedente.

Le vecchie date degli eventi misti warning/outage non generano email di ripristino: non consentono di stabilire se vi fosse stata perdita totale. Il nuovo stato si costruisce dai controlli successivi. Le notifiche PPP da syslog restano indipendenti e invariate. Nessuna modifica a cron, impostazioni o database; basta installare e attendere i controlli pianificati. Installer **1.0.0a31**, 45 destinazioni.

## Funzionalità r38 mantenute — GeoIP e Settings da web

La pagina **Settings** è disponibile dal menu laterale oppure su `https://IP-ROUTER:8080/settings/`. Usa la stessa password admin del Firewall, senza username. Configurazioni e modifiche sono riservate all’admin; i salvataggi richiedono POST e CSRF. Sono disponibili quattro gruppi:

- Firewall: attivazione, IPv6, protezione forwarded, AutoBan/manuale/brute-force/connlimit, porte, bypass, timer, logging NFLOG, fonti e paesi GeoIP.
- Connection Monitor: target, IPv6, durata e soglia, alert email, limite punti, conservazione, nome WAN e lettura PPP syslog. La conservazione può essere aumentata; la riduzione resta una scelta esplicita da CLI per evitare cancellazioni involontarie.
- Traffic: quota mensile e alias delle interfacce già configurate.
- Security: intervalli, notifiche/digest, fuso orario, soglie di variazione liste e reti di gestione protette.

Ogni salvataggio verifica che il file non sia cambiato, preserva campi/commenti non gestiti e crea un backup privato in `/opt/var/backups/keentool-settings/`. Le modifiche Firewall applicano l’hook con il rollback temporizzato esistente: verificare l’accesso e premere **Confirm working configuration** entro il termine. Le variazioni dei paesi/fonti vengono usate dal successivo aggiornamento liste; non viene avviato un download dal form. Gli altri monitor acquisiscono le impostazioni al successivo ciclo pianificato. La quota Traffic entra nella firma del template e quindi si aggiorna senza force manuale.

Installazione:

```sh
cd /opt/tmp
tar -xzf keentool_alpha_sources_20261017_r45.tar.gz
cd keentool-alpha-sources-r45
/opt/bin/bash ./install.sh --apply
```

Poi Ctrl+F5. Per aggiornare subito anche le pagine generate con il link Settings:

```sh
/opt/bin/bash /opt/bin/pingtool.sh force
/opt/bin/bash /opt/bin/traffic_manager.sh ppp0 force
```

## GeoIP e fonti non raggiungibili

I download IPdeny preferiscono il trasporto IPv4 e, per errori di connessione/DNS/timeout/TLS-handshake, riprovano con la selezione automatica degli indirizzi. Questo non cambia la famiglia dei prefissi scaricati: le liste IPv6 continuano a essere validate e caricate come IPv6. Vengono ritentate anche le connessioni rifiutate. TLS resta verificato e UPDATE_INTERFACE viene rispettata anche nel fallback. Le cache vengono ricontrollate prima del riutilizzo; in mancanza di dati validi il set installato resta attivo.

`kp` non compare nell’indice ufficiale IPv6 IPdeny verificato durante questa revisione. Non significa che possiamo dedurre automaticamente zero allocazioni: la release non elimina paesi dalla politica. Se si sceglie di ometterne la fonte GeoIP IPv6, in Settings → Firewall inserire `kp` in **Explicit IPv6-only country exclusions**, lasciandolo in **GeoIP blocked country codes**. Salvare e confermare. L’esclusione viene descritta nei dettagli degli aggiornamenti senza generare da sola un allarme; IPv4 resta selezionato. Deve rimanere almeno un paese IPv6.

Per ritentare dopo la scelta:

```sh
/opt/bin/bash /opt/bin/update_blocklist.sh
```

Se IPdeny resta irraggiungibile, retry e trasporto IPv4 non costituiscono una prova di risoluzione: le cache/liste precedenti vengono conservate e serve una verifica della connessione dal router. Nessuna whitelist o regola di rete viene aggiunta automaticamente.

Questa prima pagina non sostituisce tutti i menu CLI: schedule, credenziali email/Telegram, backup SMB, installazioni/upgrade, password e migrazione del webserver restano gestiti da KeenTool/CLI. Non espone un editor libero dei file di configurazione. Syslog-ng, logrotate, database e schedule non vengono riscritti dall’installer.

# r37 — trasporto JSON dei log e dimensioni nelle intestazioni

L’errore “Unterminated string … position 65528” è compatibile con una risposta interrotta attorno a 64 KiB. Questa revisione limita ogni risposta interna del log a 48.000 byte di JSON effettivamente codificato, includendo l’espansione di Unicode, virgolette, slash e caratteri di controllo. Il log completo continua a essere ricomposto automaticamente: nessun limite totale alla visualizzazione e nessun pulsante per caricare altre righe. Il punto esatto del taglio sul router non è stato identificato in questa sede; le prove locali verificano risposte inferiori alla soglia osservata.

La dimensione compare accanto al nome di ogni log anche quando il riquadro è chiuso, tramite una lettura separata dei soli metadati. Viene aggiornata anche al primo blocco ricevuto e non viene cancellata se il caricamento del contenuto fallisce. System log (`messages`) resta esteso di default; gli altri file vengono caricati integralmente solo quando aperti.

```sh
cd /opt/tmp
tar -xzf keentool_alpha_sources_20261016_r37.tar.gz
cd keentool-alpha-sources-r37
/opt/bin/bash ./install.sh --apply
```

Poi Ctrl+F5. Non occorre applicare l’hook, cambiare permessi o riavviare syslog-ng. Nessuna modifica a logrotate, file originali, cron o database.

# r36 — ripristino dei log completi nei riquadri aperti

**System log (`messages`) è esteso di default e carica tutto il file corrente.** Gli altri log vengono caricati integralmente quando si espande il rispettivo riquadro. Non sono presenti pulsanti o limiti di paginazione nella visualizzazione. I riquadri chiusi non vengono caricati e la chiusura interrompe il trasferimento in corso.

Refresh aggiorna l’intero contenuto; l’aggiornamento automatico riguarda solo i riquadri aperti. Save to file salva il contenuto completo visualizzato. Il caricamento mantiene i dati precedenti fino al completamento; in caso di errore o rotazione durante il trasferimento viene mostrato un avviso, senza sostituirli con una vista parziale. I dati degli altri monitor vengono aggiornati senza attendere il caricamento dei log.

Il trasferimento interno usa blocchi limitati, caricati automaticamente fino al completamento. Non esiste un limite totale alle righe visualizzate e non richiede interventi dell’utente. Nessuna modifica a syslog-ng, logrotate, permessi dei file originali o database; restano incluse le correzioni precedenti per cron e per i dati pubblici dei monitor.

```sh
cd /opt/tmp
tar -xzf keentool_alpha_sources_20261016_r36.tar.gz
cd keentool-alpha-sources-r36
/opt/bin/bash ./install.sh --apply
```

Poi Ctrl+F5. Non occorrono chmod manuali o applicazione dell’hook.

# r35 — consultazione progressiva dei log

Il limite è ora per singola richiesta, non per la consultazione complessiva. La dashboard carica inizialmente le ultime 1000 righe / 128 KiB; il pulsante **Load older entries** aggiunge i blocchi precedenti fino all’inizio del file corrente. Non viene imposto un limite complessivo alle righe caricate manualmente. I blocchi vengono aggiunti in testa preservando la posizione di lettura, senza righe duplicate o saltate.

Durante la consultazione delle righe precedenti viene sospeso solo l’aggiornamento automatico di quel riquadro: **Refresh latest** torna ai dati recenti e lo riattiva. Gli altri monitor continuano ad aggiornarsi. **Save loaded entries** salva tutto il contenuto caricato nella vista. La dimensione indicata è quella del file al primo caricamento: nuove righe vengono acquisite con Refresh latest.

Una rotazione o un troncamento rilevati tra due richieste producono un avviso e richiedono di aggiornare la vista recente; non vengono mescolati file differenti. La navigazione riguarda il file corrente, non gli archivi ruotati/compressi. File originali, permessi, syslog-ng, logrotate e database non vengono modificati.

```sh
cd /opt/tmp
tar -xzf keentool_alpha_sources_20261016_r35.tar.gz
cd keentool-alpha-sources-r35
/opt/bin/bash ./install.sh --apply
```

Poi Ctrl+F5. Questa revisione include tutte le correzioni r33/r34; non serve ripetere chmod, manutenzione DB o applicazione dell’hook.

# r34 — syslog consultivo e ripristino cron

La dashboard legge i log tramite il broker locale esistente, con un elenco fisso di log ammessi e un’anteprima limitata alle ultime 1000 righe / 128 KiB. Non dipende dai permessi ktweb sul file originale: syslog-ng può continuare a creare `messages` con permessi 600. Nessuna modifica a syslog-ng.conf, logrotate, ai link esistenti o ai permessi dei log. L’anteprima segue il file corrente anche dopo rotazione; il download dalla dashboard contiene l’anteprima visualizzata, non l’intero archivio.

Installazione e riavvio Entware verificano cron: se già attivo viene lasciato in esecuzione; se assente viene avviato tramite l’unico script S*cron/S*crond eseguibile già presente. Script mancante, ambiguo, avvio fallito o processo ancora assente producono un avviso; non vengono creati script/configurazioni sostitutivi o riscritti gli schedule. Un arresto successivo di cron non viene corretto automaticamente in ciclo: il nuovo controllo opera all’installazione e all’avvio del servizio Security. Security & Health riporta anche cron, syslog-ng e vnstatd.

```sh
cd /opt/tmp
tar -xzf keentool_alpha_sources_20261016_r34.tar.gz
cd keentool-alpha-sources-r34
/opt/bin/bash ./install.sh --apply
pidof crond cron
```

Poi Ctrl+F5. Per rigenerare subito le viste, senza attendere gli schedule esistenti:

```sh
/opt/bin/bash /opt/bin/pingtool.sh force
/opt/bin/bash /opt/bin/traffic_manager.sh ppp0 force
```

Non occorre applicare nuovamente l’hook, riavviare syslog-ng o cambiare permessi manualmente. Un eventuale precedente chmod 640/chgrp ktweb non viene annullato alla cieca: l’accesso della dashboard non ne dipende più. Nessuna pulizia o aggregazione dei database.

# r33 — dati pubblici leggibili dopo isolamento web

Corregge un difetto dei generatori Ping e Traffic: i file pubblicati tramite mktemp conservavano permessi 600 e potevano risultare illeggibili a lighttpd/PHP eseguiti come ktweb. I nuovi file dati e HTML sono pubblicati con permessi 644; vengono resi leggibili anche gli asset JavaScript noti delle due pagine. Database, credenziali e log originali non cambiano permessi.

Installare `keentool_alpha_sources_20261016_r33.tar.gz` dalla cartella `keentool-alpha-sources-r33` con `/opt/bin/bash ./install.sh --apply`, poi rigenerare:

```sh
/opt/bin/bash /opt/bin/pingtool.sh force
/opt/bin/bash /opt/bin/traffic_manager.sh ppp0 force
```

Eseguire Ctrl+F5 sulla dashboard. La sola installazione aggiorna i generatori: la rigenerazione rende leggibili gli export esistenti. In futuro ogni nuova pubblicazione imposta esplicitamente i permessi. “DATA UNAVAILABLE” non prova che uno schedule sia disabilitato; il precedente “DISABLED” veniva mostrato anche per file illeggibili. Gli errori dei log mostrano il codice HTTP quando disponibile.

Questa revisione non accerta né modifica lo stato syslog-ng sul router: verificare processo, cron e accesso ai log separatamente. Non modifica syslog-ng.conf, logrotate, cron, isolamento web o banche dati.

# r32 — tipografia e layout Security & Health

Rende più chiara la gerarchia della pagina: titolo pagina 26 px, sezioni 18 px, sottosezioni 16 px, titoli box 15 px, intestazioni tabella 13 px con peso maggiore e dati 14 px. Allinea i valori dei box, le colonne numeriche e le spaziature tra titoli, controlli e tabelle. Le tabelle ampie scorrono nel loro contenitore; i box passano da quattro a due o una colonna secondo lo spazio disponibile. Le regole sono limitate alla pagina Security & Health.

Installare `keentool_alpha_sources_20261016_r32.tar.gz` dalla cartella `keentool-alpha-sources-r32` con `/opt/bin/bash ./install.sh --apply`, quindi Ctrl+F5. Non occorre eseguire aggiornamenti blocklist, manutenzione DB o applicare l’hook per questa modifica grafica.

# r31 — dettagli degli aggiornamenti blocklist

Le tabelle “Blocklist updates” ed “Event timeline” mostrano una colonna Details con il motivo dei nuovi fallimenti: HTTP/DNS/timeout/TLS, fonte vuota, cache mancante, creazione/caricamento/swap ipset, memoria/capacità e salvataggio. L’uso di cache precedente è una warning distinta dal rifiuto. I dettagli pubblici non contengono chiavi API o URL completi.

Installare `keentool_alpha_sources_20261016_r31.tar.gz` dalla cartella `keentool-alpha-sources-r31` con `/opt/bin/bash ./install.sh --apply`, quindi Ctrl+F5. Per un nuovo tentativo immediato: `/opt/bin/bash /opt/bin/update_blocklist.sh`. Altrimenti attendere lo schedule esistente. La procedura aggiorna le liste usando i controlli e la riapplicazione dell’hook già previsti dall’updater.

Per il fallimento GeoBlock6 del 16/10 alle 04:01, il precedente updater non ha registrato un motivo preciso nell’evento: non è possibile ricostruirlo con certezza dallo screenshot. La nuova versione non inventa motivi per gli eventi passati. Nessuna GeoIP valida viene rifiutata per la sola variazione dimensionale. Non serve ripetere l’ottimizzazione DB.

# r30 — confronto periodi Security & Health

Corregge la doppia riga XX unificando i paesi sconosciuti prima del raggruppamento, completa il riempimento delle intestazioni e mostra esplicitamente i periodi confrontati. “Last 24h” indica le ultime 24 ore fino allo snapshot; “Preceding 24h” le 24 ore immediatamente precedenti. Analogo confronto per due finestre consecutive di 7 giorni. Non sono giorni/settimane di calendario. Le date sono visualizzate nel fuso del browser.

Installare il pacchetto r30 ed eseguire Ctrl+F5. Il monitor rigenera lo snapshot entro circa un minuto. Non serve applicare l’hook o ripetere l’ottimizzazione DB.

# r29 — Security & Health

Aggiunge la favicon condivisa e rimuove “· KeenTool” dal titolo della scheda. Installare il pacchetto r29 ed eseguire Ctrl+F5. Non occorre ripetere la manutenzione del DB né applicare l’hook.

# Ottimizzazione senza perdita r28

Installare `keentool_alpha_sources_20261015_r28.tar.gz` dalla cartella `keentool-alpha-sources-r28` con `/opt/bin/bash ./install.sh --apply`. Eseguire poi:

```bash
/opt/bin/bash /opt/bin/firewall_stats.sh --optimize-db
```

Il comando lavora sul database corrente del router: backup online verificato in `/opt/var/backups/keentool-db/`, indice più piccolo, VACUUM e controllo integrità. Conserva tutte le righe, timestamp, hit, metadati, porte e registri di segnalazione. Non legge contatori kernel o PCAP, non rigenera la dashboard e non cambia regole. Il nuovo codice non ricrea l’indice vecchio nei run successivi.

Sulla copia dell’allegato: 31.211.520 → 26.206.208 byte (29,8 → 25,0 MiB). Il risultato sul router dipende dai dati aggiunti nel frattempo. Il backup resta separato e occupa ancora spazio: dopo la verifica può essere spostato sul NAS. Non cancellarlo automaticamente. Non sostituire il DB live con la copia dell’allegato, che è precedente ai dati correnti.

Se il comando segnala database occupato o compattazione fallita, non ripristinare automaticamente il backup sopra dati nuovi: la transazione SQLite conserva i dati; ripetere la manutenzione quando gli altri accessi sono terminati. Con lettori WAL attivi il recupero fisico dello spazio può essere rinviato. Se appare “Already running”, attendere il termine dell’aggiornamento statistiche programmato e ripetere.

Non serve riapplicare l’hook. Le precedenti limitazioni del backup dei permessi web restano quelle descritte sotto.

# Correzione r27 — BusyBox stat

La migrazione web usa ora le funzioni filesystem di PHP, senza `stat -c`. Installare il pacchetto r27 con `install.sh --apply`; se l’isolamento risulta già attivo, non rilanciare la migrazione. Il check segnala l’eventuale registro permessi incompleto lasciato dalle versioni precedenti.

Nel caso segnalato del backup `20261015_161942-30062`, i permessi originali non sono stati registrati correttamente. La correzione non può ricostruirli: conserva i backup delle configurazioni e impedisce il rollback automatico che altrimenti ripristinerebbe solo una parte dello stato. Non cancellare il backup o il marker di isolamento. Verificare HTTPS, login, Details, log e lo stato dei processi web. Non serve riapplicare l’hook.

# Correzione r26 — migrazione web

Il precontrollo ora ignora gli esempi FastCGI commentati. Installare `keentool_alpha_sources_20261015_r26.tar.gz` dalla cartella `keentool-alpha-sources-r26`, poi ripetere `firewall_security harden-web --check` e, se riuscito, `firewall_security harden-web --apply`. Non cancellare gli esempi o modificare a mano la configurazione. Per questa correzione non serve riapplicare l’hook.

# Aggiornamento r25 — 15 ottobre 2026

Corregge Details su PHP senza estensione filter, allarga le colonne IP/porte e sposta Security & Health in `/security/index.html`. Installazione: estrarre `keentool_alpha_sources_20261015_r25.tar.gz`, entrare in `keentool-alpha-sources-r25` ed eseguire `/opt/bin/bash ./install.sh --apply`. Aggiornare il browser con Ctrl+F5. Per rigenerare le altre pagine: `pingtool.sh force` e `traffic_manager.sh ppp0 force`. Non serve riapplicare l’hook per queste modifiche.

“root detected” indica un processo web eseguito come root. Per attivare la separazione: `/opt/bin/bash /opt/bin/firewall_security harden-web --check`, poi `--apply`. Verificare HTTPS, login, Details e log. La procedura conserva backup e rollback.

# Sorgenti alpha consolidati — 15 ottobre 2026

## Revisione corrente: sicurezza e nuove funzionalità r24
Firewall Dashboard **2.0.0a18**, Hook **3.0.0a6**, Stats **4.0.0a9**, API **2.0.0a6**, KeenTool **2.0.0a8**. Per aggiornare una precedente alpha già funzionante:
```bash
cd /opt/tmp/keentool-alpha-sources-r24
/opt/bin/bash ./install.sh --apply
table=filter /opt/bin/bash /opt/etc/ndm/netfilter.d/100-firewall.sh
/opt/bin/bash /opt/bin/firewall_health
/opt/bin/bash /opt/bin/firewall_stats.sh force
/opt/bin/bash /opt/bin/pingtool.sh force
/opt/bin/bash /opt/bin/traffic_manager.sh force
```
Aggiornare il browser con Ctrl+F5. Questa revisione richiede l'applicazione separata dell'hook. Il nuovo monitor si avvia con l'installer. La separazione dell'utente lighttpd/PHP si attiva con `/opt/bin/bash /opt/bin/firewall_security harden-web --apply`. Leggere `SECURITY_README_IT.md` per precontrolli, conferma temporizzata, soglie GeoIP e rollback.

## Verifiche hook e monitor PPP
Hook **3.0.0a5**, Pingtool **2.0.0a12**, KeenTool **2.0.0a7**. Questa sezione sostituisce le precedenti istruzioni del monitor PPP a10 collegato allo schedule ping.

Dopo aver estratto il pacchetto:
```bash
cd /opt/tmp/keentool-alpha-sources-r24
/opt/bin/bash ./install.sh --apply
table=filter /opt/bin/bash /opt/etc/ndm/netfilter.d/100-firewall.sh
/opt/bin/bash /opt/bin/firewall_health
/opt/bin/bash /opt/bin/wan_syslog_service status
```
L'installer copia i file e avvia soltanto il nuovo servizio PPP. Il comando separato applica l'hook. Controllare il risultato del comando prima di procedere: un errore di preflight conserva le regole esistenti; un errore dopo un commit tenta il recupero e ne verifica l'esito. Il controllo restituisce JSON con `enabled`, `applied`, `healthy`, `ipv4_ok`, `ipv6_ok`; in stato abilitato `applied=true` richiede entrambe le famiglie previste e la configurazione applicata. Per una verifica con exit status usare `firewall_health --quiet`.
Il rollback stampato dall'installer ripristina i file e gestisce il servizio PPP. Non sostituisce automaticamente le regole kernel: dopo un rollback dei sorgenti, riapplicare l'hook precedente con lo stesso comando `table=filter ...`. Non vengono modificati syslog-ng, logrotate, cron, password, configurazioni o database durante la copia.

I sei interventi sull'hook:
1. Generazione di batch limitati alle catene del tool, validazione di entrambe le famiglie e commit per famiglia con `iptables-restore --noflush`. Le altre catene/policy del router non vengono sostituite. IPv4/IPv6 non sono un'unica transazione: dopo un errore si recuperano le nostre regole e si verifica il risultato. Un riferimento esterno inatteso alle nostre catene provoca un rifiuto prima della modifica. Il recupero lascia intatte le regole esterne; può fallire se il kernel/regole cambiano contemporaneamente, e in quel caso compare una diagnostica CRITICAL. La manutenzione Entware non impedisce più all'hook kernel di eseguire.
2. AutoBan OFF impedisce anche gli inserimenti SET dalle regole brute-force; i DROP brute-force restano indipendenti se abilitati.
3. Il LED verifica la firma di tutte le nostre regole, il loro ordine, le catene, i collegamenti INPUT/FORWARD e la revisione di configurazione. Il controllo riguarda le regole, non la qualità delle liste scaricate o la raggiungibilità Internet.
4. Ripristino completo dei record salvati nei set parziali senza svuotarli; importazione add-only per set esistenti, marker solo dopo successo. La nuova revisione del marker forza una ricontrollata importazione alla prima applicazione anche nello stesso boot dopo l'aggiornamento. I timeout salvati mantengono il comportamento precedente.
5. Disabilitare IPv6 rimuove anche BLACKLIST6 e le altre nostre sottocatene.
6. Nessun killall tcpdump. Bypass configurabili dal Firewall Manager → impostazioni → **15**, con gli stessi valori iniziali dell'upstream e possibilità di valori vuoti. Il loopback IPv4 INPUT e i controlli anti-spoofing restano salvaguardie del codice.

Campi persistenti opzionali in `/opt/etc/firewall.conf`:
```bash
BYPASS_INTERFACES="tun+"
TRAP_BYPASS_INTERFACES="br0 tun+"
BYPASS_NETWORKS_V4="10.0.0.0/8 172.16.0.0/12 192.168.0.0/16 169.254.0.0/16"
BYPASS_NETWORKS_V6="::1/128 fe80::/10"
DNS_BYPASS_PORTS="53 853"
```
Le reti IPv4 valgono INPUT/FORWARD; le reti IPv6 configurate mantengono il bypass INPUT originale. Queste sono eccezioni fidate: rimuoverle cambia la politica del firewall. Il manager ora le conserva nei salvataggi e segnala gli errori dell'hook invece di mostrare un successo non verificato.

Il servizio **S95keentool-wan** legge il syslog ogni 5 secondi ed è indipendente dai ping. L'invio SMTP usa un worker separato: la lettura continua durante un invio lento. La prima lettura è silenziosa, lo stato/coda è persistente e i lock riconoscono il cambio di boot. Durante un reboot la durata di un evento già aperto è dichiarata non disponibile se non ricostruibile in modo affidabile. Syslog e logrotate conservano le impostazioni esistenti.
KeenTool → configurazione Ping Monitor: voce **9** nome WAN, voce **10** intervallo PPP (1–60 secondi). I valori sono ricaricati dal servizio senza cambiare il cron ping. Controlli manuali:
```bash
/opt/bin/bash /opt/bin/wan_syslog_service status
/opt/bin/bash /opt/bin/wan_syslog_service restart
```
`WAN_SYSLOG_ENABLED="false"` in pingtool.conf arresta il ciclo; per riabilitarlo impostare true e avviare il servizio. La coda SMTP è almeno-una-volta: un arresto dopo l'accettazione SMTP ma prima del salvataggio può causare una riconsegna. Le email di caduta possono arrivare al ritorno della connessione. Il servizio non usa nohup.

Verifiche della suite: validazione export JSON vnStat con PHP CLI e conservazione dell'ultimo export valido; Entware senza dipendenza nohup e exit status corretto dopo upgrade fallito; scanner VPN consuma soltanto righe complete; backup SMB verificato prima di rinomina/purge, cutoff retention portabile a secondi. Il checker PHP dell'installer deve passare sul router. Non è stata eseguita una prova su kernel Keenetic/BusyBox o SMTP/SMB/opkg reali; vedere VALIDATION.md per la copertura locale.


Questo archivio contiene i listati correnti aggiornati: suite originaria più Entware, menu cambio password, accesso admin firewall, ripristino/log e storico Pingtool. Versioni e changelog sono allineati alla convenzione richiesta. Nessuna pubblicazione GitHub.

Aggiornamento locale: `/opt/bin/bash ./install.sh --apply`. Senza argomenti mostra il piano. Richiede la suite e gli addon Entware, admin e reboot/log già installati; verifica i percorsi e la sintassi PHP/Bash prima di cambiare file. Salva i file sostituiti sotto /opt/var/backups/keentool-alpha e stampa il comando di rollback. Non cambia configurazioni, credenziali, database, cron, HTTPS o ulogd; non applica regole e non riavvia servizi.

Dopo: riaprire KeenTool; `/opt/bin/bash /opt/bin/pingtool.sh force` e `/opt/bin/bash /opt/bin/firewall_stats.sh force` per rigenerare le relative dashboard (sono esecuzioni normali degli script, con misurazioni e normale retention). Traffic Manager rigenera al prossimo cron, oppure eseguire `/opt/bin/bash /opt/bin/traffic_manager.sh ppp0 force` per l'interfaccia indicata da Matteo. Ctrl+F5 nel browser.

admin_auth.php viene installato in /opt/lib/keentool-admin, come richiesto dall'API. projects e support contengono i sorgenti; INSTALL.tsv è la mappa dei file effettivamente installati. Gli altri file di supporto sono conservati come riferimento e non vengono reinstallati.

Dettagli: VERSIONS.md e CHANGELOG_ALPHA.md. Nessuna pubblicazione su GitHub.

Tema grafico: vedere UI_THEME.md. Dopo l'installazione rigenerare Ping, Traffic e Firewall, poi Ctrl+F5. Per Traffic, usando la tua interfaccia: `/opt/bin/bash /opt/bin/traffic_manager.sh ppp0 force`. Gli asset condivisi vengono installati in /opt/var/www/assets. Nessuna impostazione lighttpd/HTTPS viene cambiata.

Storico Ping: KeenTool → 2 Ping Monitor → 3 Configure Settings → 6 DB Retention Days oppure 8 Maximum Chart Points. Retention: 1–3650 giorni; punti: 100–10000, default 2000. Il limite dei punti non elimina campioni dal database e non garantisce di disegnare esattamente quel numero di punti.

## Notifiche WAN — Pingtool 2.0.0a9 / KeenTool 2.0.0a6
Le email di anomalia e ripristino riportano WAN e famiglia, ad esempio `ppp0 · IPv4`. KeenTool → Ping Monitor Configuration → 9 permette di impostare il nome; vuoto usa l'interfaccia restituita dalla route verso il target. Il nome è un'etichetta e non modifica l'instradamento delle sonde.
Il tempo di ripristino è la differenza tra l'inizio del primo test anomalo e l'inizio del primo test sano, non la durata esatta di una disconnessione continua. Perdita parziale o latenza sopra soglia mantengono aperto l'evento, anche dopo il ritorno della connessione. Intervalli tra test, reboot e periodi senza campionamento possono aumentare la finestra riportata. Il messaggio ora spiega questa distinzione e mostra minuti/secondi; con timestamp non valido o orologio arretrato la durata è dichiarata non disponibile. Stato incidenti e condizioni di allarme esistenti conservati.

## Monitor sessione PPP — Pingtool 2.0.0a10
Il nuovo `/opt/bin/wan_syslog_monitor` legge `/opt/var/log/messages` ad ogni esecuzione di Pingtool, separatamente dagli incidenti ping. Non modifica syslog-ng, cron o routing. La prima esecuzione costruisce una base iniziale silenziosa: nessuna email per eventi storici. I controlli successivi leggono i nuovi record, associano host/PID all'interfaccia `pppN`, registrano la prima caduta (Serial link disconnected/Modem hangup/Connection terminated) e il ripristino IPv4 (local IP address), usando i timestamp del syslog. Using interface, CHAP e local LL address da soli non confermano il ripristino IPv4 o Internet IPv6.
Le notifiche seguono lo schedule Pingtool e possono arrivare dopo l'evento. Le email fallite restano nella coda persistente per un nuovo tentativo; dopo un arresto durante l'invio SMTP è possibile una riconsegna. La durata PPP non dipende dall'intervallo dei ping, ma include il ritardo con cui pppd rileva il guasto. È la finestra della sessione PPP, non una misura della raggiungibilità Internet.
Configurazione opzionale in `/opt/etc/pingtool.conf`:
```bash
WAN_LABEL="ppp0"
WAN_SYSLOG_ENABLED="true"
WAN_SYSLOG_FILE="/opt/var/log/messages"
```
Una WAN_LABEL pppN limita le notifiche PPP a quell'interfaccia; vuota legge le interfacce PPP presenti nel log. Nomi personalizzati restano etichette delle notifiche ping. Per il syslog si conserva il nome reale dell'interfaccia. Stato, cursore, mapping e coda sono privati in `/opt/etc/pingtool/wan-events`; il riepilogo è aggiunto al log incidenti del Connection Monitor. Le anomalie ping conservano soglie e campioni originali.
Il lettore riconosce rotazioni rename con coda non compressa `.1`/`.0` e troncamenti (anche tramite impronta iniziale). Se la vecchia coda non è più disponibile, eventuali durate aperte diventano non affidabili e vengono dichiarate non disponibili. Correzioni dell'orologio e timestamp arretrati invalidano le durate aperte. RFC3164 non contiene l'anno: viene scelta la data più vicina all'orologio corrente, entro 183 giorni; non è un importatore di archivi. I record PPP privi del precedente mapping PID/interfaccia vengono ignorati per evitare attribuzioni inventate. Il log deve contenere i messaggi pppd senza filtrarli.
Dopo l'installazione eseguire Pingtool una volta per inizializzare il cursore (oppure attendere lo schedule). Il helper può essere eseguito manualmente con `/opt/bin/bash /opt/bin/wan_syslog_monitor`; se eseguito fuori da Pingtool non legge automaticamente pingtool.conf e usa le impostazioni di default.

## Copertura IPv6 — Pingtool 2.0.0a12
Il footer mostra separatamente le date effettive IPv4 e IPv6 del periodo selezionato. IPv6 compare solo se abilitato; se il periodo non contiene campioni IPv6 compare una nota esplicita. I dati non vengono modificati. Per aggiornare subito la pagina generata dopo l’installazione eseguire `/opt/bin/bash /opt/bin/pingtool.sh force`, oppure attendere il normale schedule.

## Dettaglio porte — Stats 4.0.0a6 / Dashboard 2.0.0a12
Il badge `(+N)` dopo le prime tre porte apre l’elenco completo delle porte/protocolli associati all’IP. Il tooltip originale GitHub resta come anteprima; il clic permette di consultare, copiare o scaricare tutte le porte, anche oltre il limite di anteprima di 100 porte aggiuntive. È consultivo e non richiede accesso admin. Le liste sono esportate una volta per IP e scaricate solo al clic, mantenendo compatta la tabella. Il modal degli IP attaccanti per porta conserva il suo comportamento.
Dopo l’installazione eseguire `/opt/bin/bash /opt/bin/firewall_stats.sh force` per rigenerare badge e liste oppure attendere il normale schedule, poi Ctrl+F5. Non serve riapplicare l’hook.

## Correzione AWK — Stats 4.0.0a7
La concatenazione del tooltip usa sprintf esplicito, evitando che BusyBox interpreti tip(...) come una funzione inesistente. Gli errori di rendering ora interrompono l’export prima della pubblicazione, conservando il dashboard precedente; la raccolta DB già eseguita non viene annullata. Le cache incomplete e la directory di staging del run vengono rimosse.

## Mappa geografica — r20
Dopo l'installazione eseguire `/opt/bin/bash /opt/bin/firewall_stats.sh force`, poi Ctrl+F5 sul browser.
La mappa usa tutti i contatori IP del periodo, indipendentemente dalle tabelle Top 10, includendo IPv4/IPv6. I totali possono differire dai contatori pacchetti globali del firewall.
Colori blu su scala logaritmica, legenda, classifica dei paesi (percentuali sul totale inclusi sconosciuti), zoom, reset e schermo intero. Il clic su un paese o sulla classifica apre i dettagli pubblici.
Dettagli limitati ai primi 100 IP/subnet per paese; porte: anteprima delle prime 12 osservate nello storico, non filtrata sul periodo. I metadati geografici sono quelli locali attuali, anche per periodi storici. Le posizioni sconosciute restano conteggiate e consultabili separatamente.

## Table readability r23
Monitor pages with tables include Table density: Comfortable or Compact, saved in this browser and reused across monitor pages. Compact changes table spacing, not source data or sampling.
Long tables scroll within a bounded panel; column headings remain visible inside that panel. Scrollable table regions are keyboard-focusable. Geographic source panels keep their matched outer heights.
Hover/focus row highlighting, stronger secondary text contrast, restrained numeric colors and consistent 36px controls apply across dashboards. Traffic Rx/Tx colors and risk indicators retain their meaning.
