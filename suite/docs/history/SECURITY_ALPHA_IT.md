# KeenTool Security — r24 alpha, 15 ottobre 2026

La revisione aggiunge sicurezza operativa e osservabilità. Non sostituisce il firewall nativo Keenetic e non modifica automaticamente le sue politiche.

## Installazione sul router

```bash
cd /opt/tmp
tar -xzf keentool_alpha_sources_20261015_r24.tar.gz
cd keentool-alpha-sources-r24
/opt/bin/bash ./install.sh --apply
```

L'installer controlla PHP CLI/CGI, processi/socket Unix e SQLite con output JSON; salva i file precedenti e il relativo registro checksum. Avvia i servizi WAN e Security. Inizializza lo stato privato e i set manuali con timeout, senza applicare automaticamente nuove regole. Un'eventuale modifica protetta rimasta in sospeso viene recuperata all'avvio del servizio.

Applicare e controllare l'hook:

```bash
table=filter /opt/bin/bash /opt/etc/ndm/netfilter.d/100-firewall.sh
/opt/bin/bash /opt/bin/firewall_health
/opt/bin/bash /opt/bin/firewall_security service status
/opt/bin/bash /opt/bin/firewall_stats.sh force
/opt/bin/bash /opt/bin/pingtool.sh force
/opt/bin/bash /opt/bin/traffic_manager.sh force
```

Se il preflight del kernel non accetta `limit` o `! --update-counters`, l'hook conserva le regole precedenti e segnala l'errore. Non dichiarare completata l'attivazione prima della verifica. La nuova API rifiuta nuovi ban se le regole dei nuovi set non risultano collegate.

## Isolare lighttpd e PHP

Il broker parte come root, ascolta esclusivamente su un socket Unix locale e accetta azioni fisse. Non accetta percorsi di comandi o codice da eseguire. L'API web mantiene HTTPS, password, sessioni, CSRF e token per l'automazione; delega le operazioni privilegiate al broker.

Installare il broker non cambia da solo l'utente di un lighttpd già in esecuzione. La migrazione reale è questo comando:

```bash
/opt/bin/bash /opt/bin/firewall_security harden-web --apply
```

Per vedere prima il piano: sostituire `--apply` con `--check`.

La procedura supporta il layout lighttpd corrente con include `conf.d/*.conf`, un backend PHP-CGI locale tramite socket e un init script dedicato. Richiede comandi di gestione account (`useradd/groupadd` oppure `adduser/addgroup`). Crea l'account non interattivo `ktweb`, rifiuta account/gruppi omonimi non gestiti e UID/GID 0, assegna permessi specifici a credenziali/sessioni/socket e ai percorsi runtime di lighttpd, sposta il socket PHP in una directory dedicata. Non concede al processo web la scrittura sui file di programma o sull'hash della password.

Salva configurazioni e permessi, esegue `lighttpd -tt`, riavvia solo lighttpd e controlla che i processi web non risultino root. In caso di errore ripristina la configurazione salvata; un errore anche nel ripristino viene mostrato con il percorso del backup. Un layout non supportato viene fermato prima della migrazione. L'init `S01keentool-web-user` ripristina un eventuale account volatile prima di lighttpd al reboot.

Dopo l'attivazione verificare HTTPS sulla porta 8080, pagine, login admin, diagnosi IP e log consultivo. In System Health controllare “unprivileged detected”. Il funzionamento specifico di account, TLS, socket e gestione log del router richiede questa verifica reale.

Rollback della sola migrazione web:

```bash
/opt/bin/bash /opt/bin/firewall_security harden-web --rollback
```

L'account di servizio viene conservato; una disinstallazione con purge può rimuovere il registro di gestione, quindi un omonimo residuo richiede verifica manuale prima di una nuova migrazione. Vengono ripristinati configurazioni e permessi registrati. Nessuna password viene cambiata. Le sessioni admin vengono invalidate al reboot o se l’orologio torna indietro; dopo l’aggiornamento può essere necessario rifare il login. Il broker riduce le operazioni disponibili a un processo web compromesso; non rende innocue le operazioni firewall che gli sono esplicitamente delegate.

## Logging e contatori

Default: `FW_LOG_RATE=2` e `FW_LOG_BURST=10` per regola NFLOG. Si modificano da KeenTool → H → L. `FW_LOG_RATE=0` disabilita il limite.

Il limite riguarda la cattura/log, mai DROP. I contatori kernel dei blocchi restano completi; i dettagli dei flussi e delle porte catturate diventano un campione durante i picchi. Le regole di logging non incrementano nuovamente i contatori dei membri ipset. Stats legge i contatori DROP ed include i nuovi ban manuali. I dati storici già salvati non vengono riscritti per correggere eventuali differenze delle versioni precedenti.

Il log consultivo resta pubblico: l'anteprima è limitata a 1000 righe, con decodifica a memoria limitata, tempo massimo per file e cache di 10 secondi. Una decodifica parziale è esplicitamente indicata. Syslog-ng e la sua rotazione non vengono modificati.

## Ban e protezione dell'accesso

La dashboard admin consente ban di IP/CIDR per 15 minuti, 1 ora, 24 ore o permanenti. Le note restano nell'audit privato. Le vecchie liste Blacklist/Blacklist6 non vengono convertite; i nuovi ban usano KTManualBan/KTManualBan6 con timeout.

Vengono protetti il client amministrativo (indirizzo diretto HTTP, senza fidarsi di X-Forwarded-For), indirizzi locali del router, reti connesse a br0, indirizzi speciali e CIDR aggiunti in KeenTool → H → 4. Vengono rifiutate anche subnet che comprendono indirizzi protetti o in whitelist. Per reti amministrative su altri bridge/VPN aggiungere esplicitamente i rispettivi CIDR.

I ban temporanei usano il tempo monotono durante lo stesso boot; dopo un reboot vengono ripristinati per il tempo residuo, senza superare la durata originale. Una variazione dell'orologio mentre il router era spento limita inevitabilmente la precisione del tempo residuo. I permanenti restano finché rimossi. Unban rimuove le voci manuali/dinamiche esatte, non una voce più ampia di una blocklist statica: la diagnosi mostra le appartenenze residue.

Le modifiche web Enable/Disable richiedono una conferma entro 120 secondi. Un guardiano separato continua anche se il processo che ha richiesto la modifica termina; se manca la conferma ripristina la configurazione precedente e verifica le regole. All'avvio del servizio recupera anche una modifica rimasta pendente al reboot. Una modifica esterna concorrente della configurazione causa un conflitto esplicito, senza sovrascriverla. Le modifiche dirette da SSH restano responsabilità dell'operatore; il normale hook mantiene preflight e recupero transazionale per famiglia.

## GeoIP e blocklist

GeoIP: gli aggiornamenti validi possono cambiare molto ogni notte e vengono installati. Default avviso: riduzione almeno 90% o aumento almeno 300%; nessun rifiuto per la sola variazione dimensionale. Un cambio della selezione paesi/fonti aggiorna la baseline senza generare l'avviso di variazione.

Liste principali: default avviso riduzione 50% / aumento 100%; rimane la protezione preesistente che rifiuta riduzioni superiori al 75%, salvo `ALLOW_LARGE_LIST_SHRINK=true` esplicito in firewall.conf. Le soglie degli avvisi sono modificabili in KeenTool → H → G/B.

Liste vuote, dati non caricabili e fallimenti di staging restano rifiutati anche per GeoIP. Si conserva il set installato precedente. I conteggi sono **prefissi**, non numero di indirizzi coperti; ottimizzazioni CIDR possono modificarli molto. Gli errori sono avvisati separatamente dalle variazioni valide.

## System Health, diagnosi e cronologia

Voce “Security & Health” nel menu, con pagina autonoma `/security/index.html`. Mostra salute delle regole, set e marcatori di ripristino, spazio, dimensioni DB, servizi, ultimo backup SMB verificato tramite lettura remota dopo upload (dai nuovi backup), backup sorgenti con checksum, aggiornamenti liste, ban gestiti e bypass configurati. La verifica SMB è attestata al momento del caricamento: il monitor non ricontrolla a ogni ciclo la presenza attuale sul NAS. Un backup sorgenti verificato non equivale a un backup completo di database/configurazioni. I backup precedenti senza registro checksum vengono etichettati come sola presenza.

“Details” accanto agli IP apre la diagnosi pubblica: liste, membro corrispondente dove disponibile, timeout, contatori, metadati e regole installate. L'appartenenza a una lista non prova che un pacchetto sia stato bloccato: contano switch, whitelist, rete/interfaccia, connessioni già stabilite e ordine delle regole.

La cronologia contiene gli eventi nuovi da questa installazione: PPP, incidenti/ripristini ping, upgrade Entware, liste, salute e operazioni admin. Non reimporta tutto il vecchio syslog. La vista pubblica omette il campo actor dei client amministrativi e le note private; l'audit completo richiede admin. Rotazione interna dedicata: circa 2 MiB per file, cinque archivi più il file attivo. Non cambia logrotate esistente.

Confronti: ultime 24 ore contro le precedenti 24; ultimi 7 giorni contro i precedenti 7, usando tutti i contatori IP registrati. La geolocalizzazione usa i metadati correnti. Il confronto porte attribuisce gli hit di un IP al suo ultimo target_port noto: è dichiarato come attribuzione, non come conteggio preciso di pacchetti per porta. Uno storico incompleto influisce sul confronto.

## Email e impostazioni

KeenTool → H consente intervallo monitor (30–3600 secondi, default 60), email on/off, ora riepilogo (default 07), fuso IANA (default Europe/Rome), reti protette e soglie. La configurazione è `/opt/etc/keentool/security/settings.json`, modificabile anche con il comando CLI `settings` che legge JSON da stdin e valida chiavi e valori.

Il primo riepilogo viene inviato al successivo appuntamento giornaliero dopo l’installazione. Il monitor segnala anomalie persistenti dopo almeno due controlli e una grazia iniziale di tre minuti. Le notifiche importanti sono deduplicate; il riepilogo giornaliero include stato e variazioni. Non ripara automaticamente le regole. Le notifiche richiedono SMTP già configurato e usano il modulo esistente. I fallimenti vengono ritentati; la coda conserva fino a 50 notifiche pendenti. La consegna può ripetersi se un crash avviene dopo l'accettazione SMTP e prima della conferma locale. Le impostazioni di notifica dei precedenti tool PPP/ping/Entware vengono conservate.

## Rollback e limiti della verifica

L'installer stampa il backup sorgenti e il comando di rollback. Il rollback ferma il servizio nuovo; se rimuove il broker della prima installazione r24, ripristina prima la configurazione web precedente. Poi riapplicare l'hook ripristinato come già previsto dai pacchetti alpha. Lo stato, le password e i database non vengono cancellati dall'aggiornamento. L'uninstaller aggiornato coordina la chiusura dei servizi e la rimozione dei nuovi componenti, con keep-data predefinito.

Test locali: PHP CLI/CGI e SQLite reali; firewall/ipset e lighttpd simulati. Login/sessione/CSRF, ban protetti, persistenza/scadenza, guardiano indipendente, rollback, confronti, GeoIP e installazione vengono verificati. Il trasporto Unix non può essere aperto nell'ambiente di test: il test HTTP usa un trasporto simulato. Verificare sul router l'IPC reale, il comportamento del kernel, il riavvio lighttpd, i permessi e la resa grafica. Nessuna pubblicazione GitHub è stata eseguita.

## Correzioni r25

Details usa inet_pton senza dipendere dall’estensione PHP filter. Security & Health è una pagina separata; il login usa la stessa sessione della pagina firewall. Se “root detected” è presente e la separazione non è ancora attiva, eseguire il check/apply descritti sopra. Se è già configurata ma rileva root, conservare l’output della procedura per la diagnosi.

## Compatibilità BusyBox e backup precedenti — r27

Il nuovo helper legge mode/UID/GID tramite PHP CLI e controlla il risultato prima di cambiare permessi. Non richiede `stat -c`. Il file della configurazione FastCGI conserva i permessi con `cp -p`.

Se una vecchia migrazione ha stampato errori `stat: invalid option -- c`, il relativo `permissions.tsv` può essere incompleto. Il nuovo `--check` lo segnala; `--rollback` rifiuta quel registro prima di modificare le configurazioni. I permessi precedenti non possono essere dedotti affidabilmente da quelli correnti. Il backup delle configurazioni resta disponibile per un recupero manuale con revisione dei permessi. Non eliminare il backup né rilanciare la migrazione per tentare di ricostruirlo. Il setup di avvio conserva l’operatività usando i percorsi gestiti senza attribuire valori ai permessi originali mancanti.

## r34 — log consultivi e cron

La dashboard usa l’azione pubblica `systemlog` del broker, limitata a un elenco fisso di ID log e a 128 KiB / 1000 righe. Nessun percorso libero è accettato. Non richiede permessi ktweb sui file originali e non riscrive le impostazioni di rotazione. Il download del pannello esporta l’anteprima mostrata.

L’init Security controlla il demone cron al suo avvio/riavvio; l’installer esegue lo stesso controllo una volta. Se manca viene richiamato l’unico script cron Entware eseguibile esistente e verificata la comparsa del processo. Non viene eseguito un watchdog continuo né modificato alcuno schedule; un fallimento viene segnalato esplicitamente.

## r35 — paginazione dei log

Il limite di 1000 righe / 128 KiB è per richiesta. **Load older entries** permette di consultare progressivamente tutto il file corrente, senza un limite totale di righe. I cursori identificano il log, la posizione e la versione del file; rotazioni e troncamenti richiedono un nuovo caricamento, evitando di mescolare file differenti. Gli archivi ruotati/compressi non fanno parte di questa navigazione. Nessuna modifica ai file originali o alla loro rotazione.

## r36 — ripristino della vista completa

La dashboard carica automaticamente tutto il file corrente nei riquadri aperti, con messages esteso di default. I blocchi interni non sono una limitazione di visualizzazione e non richiedono pulsanti aggiuntivi. I log chiusi non vengono caricati; una vista incompleta non sostituisce l’ultima vista completa. I limiti di sicurezza del broker e la protezione dei file originali restano attivi.

## r37 — limiti del trasferimento e dimensioni

Le risposte interne per i log vengono limitate dopo la codifica JSON a 48.000 byte, così anche i caratteri con escape rientrano nella soglia. La pagina ricostruisce automaticamente il file completo. L’operazione consultiva log_sizes restituisce solo le dimensioni dei log già ammessi, anche per i riquadri chiusi; non accetta percorsi liberi e non legge il contenuto dei log chiusi.

## r38 — Settings protette

Le azioni settings_get e settings_save richiedono entrambe autenticazione admin; settings_save richiede anche POST e CSRF. Il broker accetta solo gruppi, chiavi e valori tipizzati e scrive esclusivamente file di configurazione prestabiliti, conservando backup privati. I valori non gestiti e i file delle credenziali SMTP/Telegram/AbuseIPDB non vengono restituiti alla pagina. Le fonti URL configurate sono visibili solo all’admin. La revisione impedisce sovrascritture di configurazioni modificate nel frattempo. Ogni modifica Firewall usa il guardian indipendente già esistente: conferma entro il termine o rollback dell’intero file. L’audit registra le chiavi cambiate, non i valori. La sessione admin è la stessa del Firewall; le forme private vengono rimosse al logout. Le limitazioni della prima pagina sono descritte nel README r38.
