# Changelog alpha consolidato

## KeenTool 2.0.0a3
- a1: diagnostica, disinstallazione selettiva, conservazione configurazioni, aggiornamenti validati, correzioni moduli notifiche.
- a2: controllo aggiornamenti Entware, email deduplicata, schedule, upgrade esplicito con download preliminare, backup, arresto/riavvio servizi, log e recupero dopo interruzione.
- a3: voce A per cambiare la password admin del firewall tramite il comando interattivo esistente.

## Pingtool 2.0.0a2
- a1: sonde parallele, lock condiviso, NULL su perdita completa, configurazione esterna, notifiche ripristino, esportazione storico.
- a2: periodi 1 ora/1 giorno/7 giorni/30 giorni/MAX, preferenza browser, medie originali del periodo e conteggi dei campioni, grafici limitati tramite aggregazione.

## Traffic Manager 2.0.0a2 e dashboard KeenTool 2.0.0a2
- a1: dati indicizzati per interfaccia, parsing argomenti, download Chart.js autonomo, pubblicazione atomica, freshness e quota.
- a2: sha256sum invece di cksum; dashboard principale legge TRAFFIC_DATA per interfaccia.

## Firewall
- API e dashboard 2.0.0a1: prima revisione suite, token per modifiche e operazioni controllate.
- API/dashboard a2: sessioni admin, CSRF, rate limit, reset password via SSH.
- API/dashboard a3: accesso con sola password e maschere IP nascoste agli ospiti.
- API/dashboard a4: log consultabile senza admin, data completa leggibile, lettura catture persistenti e archiviate.
- Stats 4.0.0a1: ottimizzazioni, lock, cache, dati compatibili e preservazione dettaglio statistico.
- Stats a2: firme sha256sum, correzione etichetta dimensione DB.
- Stats a3: PCAP/cursore persistenti, rotazione nello stesso percorso, checkpoint set dinamici.
- Hook 3.0.0a1: regole e kill switch sicuri, helper runtime.
- Hook a2: ripristino set vuoti tramite helper persistente.
- Hook a3: ripristino dei timeout come salvati, rispettando il comportamento originale.
- State 1.0.0a1: checkpoint atomico, ripristino per boot, archiviazione PCAP.
- State a2: mapping di tutte le liste e timeout conservati senza sottrarre il tempo trascorso.
- State a3: importa solo add nei set esistenti; create solo per set assenti, risolvendo il conflitto maxelem/hashsize.
- Loader 2.0.0a2: ripristino iniziale e persistenza/archiviazione alla fermata e all'avvio.

Gli altri componenti sono a1 del rispettivo major; i dettagli sono conservati nelle intestazioni. Le intestazioni upstream restano storiche, con le versioni originali.

## Etichette di sviluppo
Banner HTML e indicazioni runtime riportano componente e versione alpha. Il vecchio watermark datato è rimosso. Quando si pubblica una release definitiva, rimuovere il suffisso alpha e il banner Alpha; successivamente incrementare le minor per migliorie/correzioni.

## English source and top history control
Pingtool 2.0.0a3 moves history selection beside auto-refresh, uses English labels and explains samples versus chart points. The other affected components increment their alpha revision for English comments, prompts and error messages; no runtime logic changes.

## Keenetic-inspired UI theme
- Main dashboard 2.0.0a4: shared shell, navigation, card/table/control styling and data state.
- Pingtool 2.0.0a4: shared shell, top controls, optional peak curves, exact coverage and chart reset.
- Traffic Manager 2.0.0a3: shared shell, remembered interface picker and version-aware page regeneration.
- Firewall dashboard 2.0.0a6: shared shell, readable protection status, list/drop distinction, log search/protocol/pause/follow controls, English auth/log messages.
- Shared UI 1.0.0a1: local CSS/JS, light/dark palettes, desktop sidebar and mobile navigation.
- Entware helper 1.0.0a2 and SMB 2.0.0a3: remaining messages/comments translated to English.
- Installer 1.0.0a2: deploy and roll back shared assets, including first-time asset creation.

## Width and traffic doughnut alignment
- Shared UI 1.0.0a2: override inherited body width caps, use full available width, remembered Hide/Show menu and chart resize after toggling; traffic timestamp fallback accepts displayed dates with commas.
- Traffic Manager 2.0.0a4: responsive summary grid, data and doughnut stay in the same tile; actual-only 72% cutout doughnuts use blue Rx / green Tx consistently, volume tooltips and an All Time doughnut. Estimates remain separate text values.
- Main dashboard 2.0.0a5, Pingtool 2.0.0a5, firewall dashboard 2.0.0a7: current shared asset version references and alpha indicators.

## Visual polish
- Shared UI 1.0.0a3: consistent heading/secondary text hierarchy and shared log terminal palette/font/spacing.
- Dashboard 2.0.0a6: remove decorative log emoji, readable labels, remove neon terminal override and use shared favicon.
- Firewall dashboard 2.0.0a8: remove decorative card/log emoji, consistent blue entry counts, shared log terminal and favicon; preserve semantic risk/status colors.
- Pingtool 2.0.0a6: neutral jitter/loss values, highlight nonzero packet loss; shared typography/favicon.
- Traffic Manager 2.0.0a5: updated typography theme and shared favicon.
- Installer 1.0.0a3: manifest includes the shared SVG favicon; backup/rollback handle its creation.

## Firewall dashboard 2.0.0a9
CNT/HITS columns use intrinsic non-wrapping width instead of fixed 60px. Numeric cells override break-all; long counters expand their column and remain right-aligned. All 24h/30d/year/all-time and GeoIP views are covered; source/description wrapping and data values are unchanged.

## Firewall admin actions, indicator and number grouping
- Dashboard firewall 2.0.0a10: quick-unban IP/subnet links visible only after admin login, including freshly rendered and legacy cached rows; hide immediately on logout or session rejection.
- Dedicated status LED turns green only when enabled and linked flags are true, stays off for disabled/unlinked/unavailable status. FW Enable replaces Protection; loading feedback remains separate. Status uses the existing API linkage check, not a full audit of all firewall rules.
- Stats 4.0.0a5: exported quick-unban links default to hidden/admin-only.
- Shared UI 1.0.0a4: dot-grouped integer counters, including dashboard firewall summary; large integers retain precision. CNT/HITS and map hit tooltips follow the same format.
- Main dashboard 2.0.0a7, Pingtool 2.0.0a7, Traffic Manager 2.0.0a6 reference current shared assets. No database or API authorization changes.

## Traffic Manager 2.0.0a7
Align all 20 numeric headings (Rx, Tx, Total, Avg Rate in five tables) to the right, matching their cells and overriding shared left alignment. Date/hour/month/year and Volume remain left-aligned. Data values and chart calculations unchanged.

## Traffic Manager 2.0.0a8
Top 10 Days shows full DD/MM/YYYY dates, distinguishing entries from different years. Sorting and traffic values are unchanged; other tables retain their existing date formats.

## Ping history settings and header peak control
- KeenTool 2.0.0a5: Ping Monitor settings option 8 configures MAX_DISPLAY_POINTS from 100 to 10000, preserves other external settings and replaces duplicate point settings. Option 6 validates retention from 1 to 3650 days; lower retention removes older records on the next normal run.
- Pingtool 2.0.0a8: validate retention before cleanup; move remembered Show latency and packet-loss peaks checkbox into the header with tooltip. Peak curves represent MAX(ping) and MAX(loss) over samples in each aggregated time bucket; mean curves and jitter remain unchanged.
- No hard sample-count cap: original rows depend on retained days and cron cadence. MAX_DISPLAY_POINTS limits displayed aggregates, not stored rows; actual points may be fewer because long ranges use minimum time buckets.

## Notifiche WAN — Pingtool 2.0.0a9 / KeenTool 2.0.0a6
Le email di anomalia e ripristino riportano WAN e famiglia, ad esempio `ppp0 · IPv4`. KeenTool → Ping Monitor Configuration → 9 permette di impostare il nome; vuoto usa l'interfaccia restituita dalla route verso il target. Il nome è un'etichetta e non modifica l'instradamento delle sonde.
Il tempo di ripristino è la differenza tra l'inizio del primo test anomalo e l'inizio del primo test sano, non la durata esatta di una disconnessione continua. Perdita parziale o latenza sopra soglia mantengono aperto l'evento, anche dopo il ritorno della connessione. Intervalli tra test, reboot e periodi senza campionamento possono aumentare la finestra riportata. Il messaggio ora spiega questa distinzione e mostra minuti/secondi; con timestamp non valido o orologio arretrato la durata è dichiarata non disponibile. Stato incidenti e condizioni di allarme esistenti conservati.

## Pingtool 2.0.0a10 / WAN Syslog Monitor 1.0.0a1
- Caduta/ripristino sessione PPP separati da anomalie ping; durata dai timestamp syslog e nome reale pppN.
- Lettura incrementale di /opt/var/log/messages ad ogni run, primo avvio silenzioso, mapping PID/interfaccia e deduplicazione dei messaggi di caduta.
- Ripristino IPv4 solo dopo negoziazione dell'indirizzo; IPv6 link-local non considerato prova di accesso Internet.
- Stato atomico privato, lock, email fallite in coda persistente; nessun cambiamento syslog-ng o schedule.
- Rotazione/troncamento, righe incomplete e orologio discontinuo gestiti senza durate inventate. Installatore a4 permette l'aggiunta del nuovo helper con rollback.

## Revisione affidabilità — 14 ottobre 2026
- Hook 3.0.0a5 / Apply 1.0.0a1: staging/preflight dual-stack, commit delle sole catene possedute, rollback verificato, controllo errori/config/set e nessuna terminazione globale tcpdump.
- Hook: SET brute-force condizionato ad AutoBan, pulizia IPv6 completa, bypass configurabili conservando i default.
- Health 1.0.0a1 / API 2.0.0a5 / Dashboard 2.0.0a11: verifica dell'intero ruleset posseduto, ordine, link e configurazione; LED rules verified/incomplete.
- State 1.0.0a4 / Loader 2.0.0a3: completa set parziali, marker solo dopo successo, niente ripristini ripetuti per ogni evento hook.
- Firewall Manager 3.0.0a2: editor bypass, conservazione dei campi e risultato hook verificato.
- Pingtool 2.0.0a11 / WAN Monitor 1.0.0a2 / Service e init 1.0.0a1: PPP indipendente dal cron ping, polling 5s configurabile, scan separato da SMTP, lock/cursori persistenti e riconoscimento reboot.
- KeenTool 2.0.0a7: voce 10 per intervallo PPP; Entware 1.0.0a3: HUP-safe worker senza nohup, exit status upgrade propagato, testi inglesi.
- Common 1.0.0a3 / Traffic 2.0.0a9: verifica JSON vnStat prima di pubblicare; hook consentito durante manutenzione Entware.
- VPN scanner 2.0.0a2: righe incomplete ritentate; SMB 2.0.0a4: cutoff retention portabile e commenti inglesi.
- Installer 1.0.0a5: nuovi helper e init, prerequisiti restore, avvio/rollback del solo servizio PPP; nessun cambiamento syslog-ng/logrotate/cron/config/database.

## Pacchetto 20261014-r14 / Installer 1.0.0a6
Archivio e directory di estrazione distinti per evitare confusione con download precedenti dal nome identico. L'installer stampa la revisione del pacchetto e verifica i 31 target attesi prima di qualsiasi modifica. Versioni dei componenti funzionali invariate rispetto alla revisione precedente.

## Pacchetto 20261014-r15 / Firewall Health 1.0.0a2
Correzione del controllo di stato su Keenetic senza /dev/stdin: awk legge dallo standard input tramite `-`. Nessuna modifica alle regole o al monitor PPP. Installer 1.0.0a7 identifica il pacchetto r15.

## Pacchetto 20261014-r16 / Pingtool 2.0.0a12
Copertura IPv6 nel footer quando abilitato, usando i propri timestamp per il periodo selezionato; messaggio esplicito senza campioni. Installer 1.0.0a8 identifica r16; nessuna modifica alla raccolta, alle notifiche o al database.

## Pacchetto 20261014-r17 / Firewall Stats 4.0.0a6 / Dashboard 2.0.0a12
- Confronto con main GitHub: badge originali basati su tooltip e modal IP attaccanti basato su liste statiche.
- Badge +N ora button nativo cliccabile da mouse/tastiera, anteprima hover originale conservata, elenco porte completo per IP caricato al clic.
- Copia/download consultivi pubblici; protocolli TCP/UDP conservati, lista completa oltre 100 porte, validazione dei token e file per-IP riutilizzati nelle tabelle.
- Modal IP attaccanti conservato; errori di caricamento leggibili e risposta precedente ignorata dopo una nuova selezione.
- Installer 1.0.0a9 identifica il pacchetto r17; hook e monitor PPP invariati.

## Pacchetto 20261014-r18 / Firewall Stats 4.0.0a7
Correzione BusyBox AWK della concatenazione tooltip: sprintf esplicito. Propagazione degli errori di rendering nelle 28 tabelle IP/porte, cache fallite rimosse, staging ripulito e export precedente conservato. Installer 1.0.0a10 identifica r18; hook e dashboard invariati.

## Typography revision — package 20261014-r19
- KeenTool Dashboard 2.0.0a8: Firewall Details, Traffic Monitor and Connection Monitor card titles use 18px text, overriding the shared 12px compact heading rule.
- Firewall Dashboard 2.0.0a13: targeted-port badges and clickable +N buttons share 10px text, 500 weight and 1.5 line height; the shared button font no longer enlarges +N.
- Installer 1.0.0a11: package banner updated to r19; the same 31 targets and installation behavior are preserved.

## Geographic overview — package 20261015-r20
- Firewall Dashboard 2.0.0a14: Keenetic blue logarithmic choropleth and numeric legend; top-10 country ranking with total-share percentages; public source details, keyboard navigation, zoom/reset/fullscreen, responsive layout and theme colors.
- Counts use numeric geographic exports rather than parsing formatted top-10 HTML rows. Preserve the selected period across automatic refresh. Unknown/non-country metadata is excluded from country totals and remains separately inspectable.
- Firewall Stats 4.0.0a8: aggregate all recorded IP counters for each period in one consistent SQLite read snapshot; include IPv6, subnets and unknown metadata. Bound source details to 100 per country and historical port previews to 12; reuse target_port for legacy records without port_history. Fail geographic export without publishing incomplete dashboard data.
- Installer 1.0.0a12: r20 identification, unchanged 31 targets and installation behavior.

## Layout and copyright — package 20261015-r21
- Firewall Dashboard 2.0.0a15: geographic column headers share a 42px minimum height; stretch subnet and map panels to matching top/bottom edges; label country ranking columns.
- KeenTool Dashboard 2.0.0a9, Pingtool 2.0.0a13, Traffic Manager 2.0.0a10: consistent bottom copyright footer, © current year mattheweli. Firewall uptime remains separately visible below copyright.
- Shared UI 1.0.0a5: consistent footer styling and automatic current-year updates, including pages left open across New Year. Asset URLs refreshed in all four pages; generated-page signatures advanced.
- Installer 1.0.0a13: r21 identification, same 31 targets.

## Traffic History alignment — package 20261015-r22
- Firewall Dashboard 2.0.0a16: numeric headers and values use equally specific right-alignment rules, overriding shared left-aligned header defaults; dates and history counters stay on one line with horizontal overflow available. Covers hourly, daily, monthly, yearly and Top Days tables.
- Installer 1.0.0a14: r22 package identification, same 31 targets.

## Readability and interaction — package 20261015-r23
- Shared UI 1.0.0a6: Comfortable/Compact table density with browser persistence and validated fallback; smaller padding without smaller type, including removal of fixed source row heights in Compact. Only pages with tables show the density control; home and chart-only pages do not show an irrelevant setting.
- Scrollable table panels use bounded heights, sticky headings, keyboard focus and labelled regions. Geographic source panels retain matched heights. Hover/focus highlights rows without replacing semantic text colors.
- Improve metadata contrast in light/dark themes and section headings. Neutralize ordinary count badges/history totals; blue category badges/actions, green ready status, theme-aware warning text. Preserve traffic Rx/Tx, risk colors, admin controls and terminal colors.
- Uniform 36px header/tab/map controls and responsive gaps; retain numeric alignment. Geographic header height raised to 48px to accommodate the uniform controls.
- KeenTool Dashboard 2.0.0a10, Firewall Dashboard 2.0.0a17, Pingtool 2.0.0a14, Traffic Manager 2.0.0a11: refreshed shared assets and generated-page signatures.
- Installer 1.0.0a15: r23 identification, same 31 targets.

## Security and observability — package 20261015-r24
- Hook 3.0.0a6: default per-NFLOG-rule limit 2 packets/second, burst 10; FW_LOG_RATE=0 opts out. DROP is never rate-limited. Logging set matches do not update member counters; DROP owns the complete counter update. Both-family preflight/rollback remains unchanged. New managed timeout sets retain legacy lists without conversion.
- Stats 4.0.0a9: consume DROP counters rather than sampled NFLOG counters; record early AutoBan re-drops and legacy manual/connlimit/bruteforce subchain drops; include managed manual bans and combine same-IP/list counters before delta calculations. Existing database/history is not rewritten.
- Engine/CLI/service/guardian/web isolation/init/UI 1.0.0a1: fixed local Unix-socket command protocol, root-only state and append-only bounded audit, public sanitized snapshot and private authenticated audit. Typed IP/CIDR/TTL validation, overlap protection for active admin/local interfaces/management bridges/custom CIDRs/whitelists; 15m/1h/24h/permanent bans with notes and persistence. Monotonic timers protect live temporary bans and policy confirmation against clock rollback.
- Guarded web enable/disable: independent HUP-safe guardian, 120s default confirmation, verified prior-policy restore on expiry/reboot, fail visibly on external-config conflict. No automatic healthy-policy repair.
- Dedicated web-user migration: account checks, credential read-only group access, private session/socket permissions, socket relocation, lighttpd configuration validation/restart/process-user check, rollback and early-boot account preparation. The migration is separately executed by the owner on the router.
- System Health: actual rule status, sets/restore markers, services, storage/DB sizes, source backup checksum verification, policy bypass review and managed bans. Per-IP diagnosis reports list membership, timeout/counters, matching installed rules, current metadata and historical exact-key counters without claiming membership proves an effective DROP.
- Timeline: new PPP, ping instability/recovery, explicit Entware upgrade, feed/health/admin transitions; no historical syslog re-import or rotation changes. Equal rolling day/week comparisons include all recorded IP hits; country/port attribution uses current metadata and is labelled accordingly.
- Blocklist updater 3.0.0a2: GeoIP size changes are warning-only (default shrink 90% / growth 300%) with configuration-aware baselines; valid nightly changes still install. Main-list defaults warn at shrink 50% / growth 100%; existing >75% shrink rejection remains unless explicitly overridden. Empty/invalid/staging-failed lists remain rejected; previous installed counts are retained in failed-update snapshots.
- Health monitor defaults to 60s, email daily at 07:00 Europe/Rome and deduplicated important failures after startup grace. Only configured SMTP is used; pending notification queue is bounded/retried. Existing ping/PPP/Entware notification configuration is preserved.
- API 2.0.0a6: retain HTTPS, password-only sessions, CSRF and token automation; no direct command execution in the web handler. Add guarded confirmation/rollback, private audit, typed timed bans, broker failure handling and bounded/cached public capture decoding.
- Manager 2.0.0a8: menu H exposes health, management networks, email/hour/timezone/interval, logging rate, list thresholds and isolation/rollback. Firewall Manager 3.0.0a3 retains logging/safety extension settings during atomic config saves and handles new manual sets in explicit flushes.
- Dashboards: KeenTool 2.0.0a11, Firewall 2.0.0a18, Pingtool 2.0.0a15, Traffic 2.0.0a12; shared UI 1.0.0a7. PPP monitor 1.0.0a3 and Entware Manager 1.0.0a4 contribute transition events. Password setter 1.0.0a2 preserves isolated credential group access.
- Installer 1.0.0a16: 40 targets, CLI Unix/process and SQLite JSON checks, checksum ledger for source backups, coordinated WAN/security service lifecycle. Uninstaller 1.0.0a2 stops daemons/reverts web isolation before deleting new helpers; keep-data behavior retained. No GitHub publication.
- SMB Backup 2.0.0a5 records its verified remote read-back manifest after successful completion. System Health prefers this attestation when present and explicitly distinguishes upload-time verification from a current remote-presence check.
- Admin Auth 1.0.0a3 binds sessions to the kernel boot identity and invalidates sessions on backward clock jumps; an existing pre-upgrade admin session requires login again.

## Package 20261015-r25
- Security Engine 1.0.0a2: use core inet_pton for strict IPv4/IPv6 validation in diagnostics, actor validation and anti-lockout checks; remove dependency on optional PHP filter extension.
- Firewall Dashboard 2.0.0a19: source/port cells have a 270px minimum, metadata retains 145px, tables scroll inside cards; source panels use two columns at intermediate desktop widths and three only on wide displays.
- Security & Health 1.0.0a2 moves to /security/index.html. The firewall tab is removed; old #security links redirect. Dedicated page retains public diagnostics and an administrator-only audit/unban through the same server session and CSRF checks. Absolute same-origin API/snapshot URLs work from either page.
- Web privileges card explains whether isolation has been activated. A detected root process is not automatically hidden or relabelled; web isolation remains an explicit owner action.
- Shared UI 1.0.0a8 updates navigation across five pages; home 2.0.0a12, Pingtool 2.0.0a16 and Traffic Manager 2.0.0a13 refresh asset URLs. Installer 1.0.0a17 includes 42 targets and rollback for the new page/controller. Uninstaller 1.0.0a3 removes the separate security page.

## Package 20261015-r26
- Web isolation 1.0.0a2: ignore fully commented FastCGI examples when selecting the PHP backend and counting socket assignments. Count assignments rather than lines so two real sockets on one line remain rejected. Preserve commented examples during relocation.
- Reject non-literal active socket expressions before any migration; existing configuration validation, backups and rollback remain in place.
- Installer 1.0.0a18, package 20261015-r26, still 42 targets. No firewall/kernel or database changes.

## Package 20261015-r27
- Web isolation 1.0.0a3: replace GNU-style stat -c with checked PHP core filesystem metadata, preserving octal permission bits and numeric owner/group IDs. Permission recording failures stop before the corresponding chmod/chgrp. Socket configuration uses cp -p before rewriting instead of stat-based chmod.
- Validate permission ledgers before restoring any configuration. Legacy incomplete/empty ledgers are reported explicitly and cannot be used for automatic rollback. Original permissions lost by a previous migration are not invented or silently replaced with current permissions. Configuration backups remain available.
- Early-boot account setup can still reassign managed groups from legacy path fields, warning about the invalid original-permission backup; it does not claim to reconstruct original modes. Reuse an already existing managed group without running addgroup again.
- Installer 1.0.0a19, package 20261015-r27, 42 targets. No hook or database changes.

## Package 20261015-r28 — lossless database optimization
- Firewall Stats 4.0.0a10 adds explicit --optimize-db maintenance before all kernel/capture/export operations. It uses the regular shared stats lock, creates and verifies a private SQLite online backup, validates known index definitions, transactionally replaces idx_list_ts_ip(list_type,timestamp,ip) with idx_list_ts(list_type,timestamp), runs VACUUM, attempts WAL truncation and checks integrity. Active readers can defer physical WAL reclamation without deleting data.
- No pruning, row aggregation, port cap, metadata deletion or report-state changes. No table schema changes. Failed backup/unknown index stops before index changes; interrupted/busy compaction retains the backup and SQLite transactional data protection.
- Normal scheduled updates accept the compact index and do not recreate the oversized index. Existing DBs are optimized only by the explicit maintenance command; fresh DBs receive the compact index.
- Installer 1.0.0a20, package 20261015-r28, 42 targets. The installer does not compact/replace the router database.

## Package 20261015-r29
- Security & Health page 1.0.0a3 adds the existing shared SVG favicon and shortens its browser-tab title to Security & Health.
- Installer 1.0.0a21, 42 targets. No backend, firewall, settings or database changes.

## Package 20261015-r30 — comparison clarity
- Security Engine 1.0.0a3 normalizes missing/empty/placeholder country codes and case/whitespace variants before GROUP BY and top-10 ranking. SQLite previously grouped source i.country rather than the identically named display alias, producing two XX rows. Countries now use an unambiguous normalized derived column. No database values are rewritten.
- Day/week comparisons include exact start/end timestamps for adjacent rolling equal-length periods and exclude future-dated records beyond snapshot time consistently across summaries, countries and ports.
- Security UI 1.0.0a3 and page 1.0.0a4 replace Current/Previous with Last 24h/Preceding 24h or Last 7 days/Preceding 7 days, show both exact date ranges in browser local time and label Unknown (XX). Empty tables use their actual header column count.
- Shared UI 1.0.0a9 removes the unused Security scrollbar gutter and fills the heading background to the table edge. Home 2.0.0a13, Pingtool 2.0.0a17, Traffic Manager 2.0.0a14 and Firewall Dashboard 2.0.0a20 refresh shared cache tokens.
- Installer 1.0.0a22, 42 targets. No hook, credentials or database changes.

## Package 20261016-r31 — blocklist update diagnostics
- Blocklist Updater 3.0.0a3 records sanitized failure codes and descriptions for HTTP/DNS/connectivity/timeout/TLS/empty sources, missing cache, merge/sort/optimization, kernel set creation/staging/count/swap and persistence. ipset staging errors distinguish capacity/memory and report a safe input line number when available. No credentials, full URLs, query strings or raw upstream error text enter public diagnostics.
- A failed source with a usable prior cache installs through the existing validation/staging path and produces a warning explaining cache fallback. A failed source without cache retains the installed list. GeoIP size variation remains warning-only.
- A save failure restores the prior kernel set when possible. If rollback itself fails, the recovery staging set is retained, the installed count is marked unknown and Details explicitly warns about uncertain kernel/persisted state.
- Security Engine 1.0.0a4 persists reason/source-warning/last-success fields, exposes only explicit sanitized blocklist details in public events, keeps private actor/note fields private and includes the reason in newly queued failure notifications. Events say update rejected when rejected; legacy records are not rewritten.
- Security UI 1.0.0a4 and page 1.0.0a5 add Details to both list status and timeline; rejected deltas say Not applied, and baseline status cannot hide rejection. Older events with no reason are labelled accordingly. Firewall Dashboard 2.0.0a21 refreshes its shared diagnostic asset token.
- Installer 1.0.0a23, 42 targets; no database normalization, pruning, credential change or new firewall policy.

## r32 — Security typography and layout (2026-10-16)
- Security page 1.0.0a6: explicit semantic section/subsection headings, larger summary card headings, distinct section/table heading weights and consistent line heights.
- Align summary status values, right-align prefix/change/database size columns, improve heading/control spacing and retain readable table text with contained horizontal scrolling.
- Scope all new CSS to Security & Health; responsive summary cards use four, two or one column. Shared styles and Security data/session controllers remain unchanged.
- Installer 1.0.0a24, package 20261016-r32; unchanged 42 targets. No rule, credential or database changes introduced.

## r33 — Public monitor output permissions (2026-10-16)
- Pingtool 2.0.0a18: set the generated data temporary file to 0644 before atomic publication; explicitly allow read-only access to the three known chart JavaScript dependencies.
- Traffic Manager 2.0.0a15: publish data/HTML as 0644, including exports generated under umask 077; repair modes of retained valid exports and public chart/index files when generated.
- Main Dashboard 2.0.0a14: missing/unreadable monitor data is DATA UNAVAILABLE, not DISABLED. Log fetch failures include HTTP status and do not claim the syslog daemon stopped.
- Installer 1.0.0a25, package 20261016-r33, 42 unchanged targets. Regeneration is required after install to repair existing exports. No credential/DB/raw-log permission changes or cron/syslog/logrotate edits. Syslog service state on the router remains unconfirmed.

## r34 — System log preview and scheduler startup (2026-10-16)
- Security Engine 1.0.0a5: fixed-ID log allowlist, regular-file/symlink checks, bounded tail read (128 KiB / 1000 lines), per-log request throttling and rotation-safe reopening. Source logs remain private and unchanged. Health snapshot includes syslog-ng, vnstatd and cron process status.
- Firewall API 2.0.0a7: expose public read-only systemlog through existing HTTPS/origin and bounded broker transport; administrative authorization/CSRF stays unchanged.
- Main Dashboard 2.0.0a15: consume broker log previews, report preview limits and retain text-only rendering/download of displayed content.
- Security init 1.0.0a2: ensure an existing scheduler is running at install/start/restart, without changing schedules or stopping an active daemon. Refuse ambiguous/missing init scripts and verify an actual scheduler process after start. Warn if recovery fails; Security can still start.
- Installer 1.0.0a26, package 20261016-r34; unchanged 42 targets. No syslog-ng/logrotate/configuration/DB rewrite, raw-log chmod, firewall rule application or additional cron entries.

## r35 — Progressive system-log browsing (2026-10-16)
- Security Engine 1.0.0a6: bounded cursor-based backward pagination over the current log. Stable snapshot offsets exclude later appends; device/inode, original-size and tail-anchor checks detect rotation/truncation before pages are mixed.
- Preserve line and UTF-8 boundaries, including very long lines, blank lines and a final line without newline. Page limits are 1000 lines / 128 KiB; no total browsing limit. Invalid/cross-log cursors and arbitrary paths are refused; sources remain read-only.
- Firewall API 2.0.0a8 forwards only the pagination cursor in addition to existing typed read fields; HTTPS/origin/admin/CSRF boundaries remain unchanged.
- Main Dashboard 2.0.0a16 adds Load older entries, prepends pages while preserving the reading position, pauses only that pane’s automatic refresh while browsing older entries, resumes on Refresh latest, reports loaded/source sizes and labels downloads Save loaded entries.
- Installer 1.0.0a27, package 20261016-r35; unchanged 42 targets. Prior scheduler and public-file permission fixes retained. No archive browsing or logrotate changes.

## r36 — Complete expanded log panes (2026-10-16)
- Main Dashboard 2.0.0a17 restores complete current-file logs on expansion, with System log open by default. Closed panes are not fetched; closing a pane stops further transfers. Remove manual pagination controls and restore Refresh / Save to file labels.
- Continue bounded backend pages automatically, publish only a completed snapshot and retain the previous full view on errors/rotation. Retry short rate-limit responses; active-log auto-refresh resumes normal whole-view behavior. Monitor cards render without waiting for full log transfers.
- Security Engine 1.0.0a7 separately paces internal continuation requests while retaining the normal full-refresh limit. Existing read allowlist, source privacy and file-version checks remain unchanged.
- Installer 1.0.0a28, package 20261016-r36; unchanged 42 targets. No syslog-ng/logrotate/DB/raw-log permission changes.

## r37 — Encoded log transport bound and title sizes (2026-10-16)
- Security Engine 1.0.0a8 bounds actual encoded system-log responses to 48,000 bytes, including escaping/Unicode expansion, with a 32 KiB raw read window. Whole-log automatic reconstruction and cursor continuity are retained. Continuation pacing is adjusted for the smaller responses.
- Add public read-only log_sizes using the existing fixed log allowlist, regular-file checks and per-actor throttling; return only metadata, not closed log contents.
- Firewall API 2.0.0a9 allows log_sizes through the existing HTTPS/origin and broker boundaries. Admin writes/private audit remain protected.
- Main Dashboard 2.0.0a18 shows sizes beside titles for closed/open panes, updates the label on the first valid data block and retains it after content failures. The log remains complete; System log remains expanded by default.
- Installer 1.0.0a29, package 20261016-r37; unchanged 42 targets. Router truncation layer remains unconfirmed; no lighttpd/syslog-ng/logrotate/cron/DB configuration or source-log mode changes.

## r38 — GeoIP recovery and typed web Settings (2026-10-17)
- Blocklist Updater 3.0.0a4 retries refused connections, prefers IPv4 HTTP transport for IPdeny and retries connection/DNS/timeout/handshake errors with automatic address selection. Preserve explicit update interface/TLS checks, revalidate cached prefixes and retain installed sets when a source remains unavailable.
- Add explicit IPv6-only country exclusions; no country is omitted automatically. IPv4 selection is unchanged, exclusion policy participates in the baseline signature and successful updates record the exclusion as an informational detail, without a repeated source-failure warning. Missing/empty source data are not guessed from country availability.
- New Settings page/controller/engine 1.0.0a1 expose typed Firewall, Connection Monitor, Traffic and Security groups behind the existing administrator session. No raw-file/shell editor or credential export. Save changed fields only, validate types/ranges/ports/CIDRs/URLs, reject unknown keys, use revision checks, preserve unrelated lines, private backups and audit key names only.
- Security Engine 1.0.0a9 reuses the existing independent timed firewall guardian for complete configuration replacement, confirmation and rollback. Firewall API 2.0.0a10 requires admin for Settings reads and POST/CSRF for writes; bounded payloads remain brokered.
- Shared UI JS 1.0.0a10 adds Settings navigation; session controller 1.0.0a2 supports the Settings lifecycle and clears private forms on logout. Navigation references refresh on the main/firewall/Security/Ping/Traffic pages; CSS tokens remain unchanged.
- Traffic Manager 2.0.0a16 includes quota changes in its template signature. Installer 1.0.0a30, package 20261017-r38, 45 targets; uninstaller 1.0.0a4 removes Settings artifacts with the security stack. No automatic firewall/list update or schedule/database rewrite by installation.


## r39 — 2026-10-17
- Pingtool 2.0.0a20: warning clearance no longer sends recovery email; partial packet loss and high latency retain warning/MTR alerts and local timeline events.
- Explicit per-family target-unreachable state opens only at 100% sampled loss. Receiving any reply closes it, even if another warning remains. The email includes target, sampled interval and current warning status; it never claims a measured WAN/PPP outage.
- Earlier warning timestamps cannot start an outage interval. Ambiguous legacy incidents clear without recovery mail; changing the configured target retires its previous reachability state.
- Installer 1.0.0a31, package 20261017-r39, unchanged 45-target manifest. PPP syslog notifications, cron, configuration and databases are unchanged.


## r40 — 2026-10-17
- Security & Health page 1.0.0a8 and Security UI 1.0.0a5: use shared Keenetic green/red tokens for summary results, including dark theme; retain text descriptions.
- Verified firewall health, at least 5% free storage, detected unprivileged web processes and verified backups are green. Failed/unverified results are red. Snapshot loading failures clear previous results rather than retaining stale green statuses.
- Installer 1.0.0a32, package 20261017-r40, unchanged 45 targets. No configuration, database, firewall policy or schedule changes.


## r41 — 2026-10-17
- Security & Health page 1.0.0a9 and Security UI 1.0.0a6 distinguish verified OK (green), unverified/unavailable (Keenetic warning yellow), and detected failures (red). Unverified backup presence does not imply a failed backup.
- Shared UI JS 1.0.0a11 consumes the asynchronously published Security snapshot timestamp and load status. Its banner updates immediately after loading instead of remaining at Waiting for data; freshness uses the existing Security three-minute threshold. Load errors clear prior card results to unknown and display an explicit data-loading error.
- Installer 1.0.0a33, package 20261017-r41, unchanged 45 targets. Existing settings, policy, scheduling and databases preserved.


## r42 — 2026-10-17
- Security & Health page 1.0.0a10: verified OK results use bold weight 700 and a brighter, more saturated green (#00843d in light mode, #5cda91 in dark mode). The override is scoped to Security summary results; warning/error colors and state logic are unchanged.
- Installer 1.0.0a34, package 20261017-r42; unchanged 45 install targets.


## r43 — 2026-10-17
- Security & Health page 1.0.0a11 / UI 1.0.0a7 and Security Engine 1.0.0a10: automatic decimal storage units with up to one decimal digit, including database sizes; 116938457088 bytes displays as 116,9 GB. Raw snapshot byte values and low-space thresholds remain unchanged.
- Daily summary renders escaped HTML with bold green OK, yellow unverified/warning and red failure results; rejected list updates are shown explicitly. Recent events remains a neutral count line.
- Email module 2.0.0a2 accepts an optional third HTML alternative and builds multipart/alternative with plain-text fallback. Existing two-argument notifications retain plain content and escaped-newline handling. Notification queue preserves HTML and retry behavior; queued legacy messages remain supported.
- Installer 1.0.0a35, package 20261017-r43, unchanged 45 targets. No credentials, schedule, policy or database migration.


## r44 — 2026-10-17
- Security & Health page 1.0.0a12: summary-card titles increase from 15px to 20px with weight 600 and line-height 1.35. Result text remains 17px with existing status colors and weights.
- Installer 1.0.0a36, package 20261017-r44; unchanged 45 targets. Monitoring and browser refresh intervals are unchanged.


## r45 — 2026-10-17
- Shared UI JS 1.0.0a12 / CSS 1.0.0a10: fixed topbar Auto-refresh (Off, 30 seconds, 1 minute, 5 minutes) and Refresh now across all six pages. New shared browser preference defaults to one minute, persists through navigation and synchronizes with other tabs; legacy per-page preferences are retired.
- A single network refresh scheduler waits for each refresh to settle, prevents overlapping requests and skips hidden-tab auto-refresh. Manual refresh remains available when Off. Clock, presentation/freshness indicators and policy safety timers remain independent.
- Dashboard 2.0.0a20: remove its selector and individual log refresh buttons; shared refresh loads monitor exports and complete logs only in expanded panels. Existing full-log continuation, sizes, closed-panel cancellation and System log default-open behavior remain.
- Firewall Dashboard 2.0.0a23: replace stats and 10-second ULOGD timers with the shared cadence. Open ULOGD refresh respects Pause updates automatically; explicit Refresh now overrides pause. Closed panels do not fetch, and repeated log/stat loads are guarded.
- Pingtool 2.0.0a21: fetch generated data in place, retain history/peak selection and reuse existing charts so zoom and logarithmic scale survive refresh. Traffic Manager 2.0.0a17 refreshes interface exports in place, retaining selected interface and last rendering on download failure.
- Security page 1.0.0a13 / Security UI 1.0.0a8: immediate initial snapshot, then shared refresh instead of its separate minute timer. Settings page/controller 1.0.0a2 uses the common refresh without overwriting unsaved fields; redundant page refresh buttons removed.
- Installer 1.0.0a37, package 20261017-r45, unchanged 45 targets. Generated Ping/Traffic templates gain the new UI on their next normal run or explicit force. Router collection intervals, cron, data, credentials and firewall policy unchanged.


## r46 — 2026-10-18
- Email module 2.0.0a3 / new Mail Layout 1.0.0a1: shared HTML shell for every existing two-argument or custom-HTML caller, including ping/MTR, firewall summaries, PPP, Entware, Security, updates and test messages. Plain text remains complete and available as a MIME alternative.
- Escaped metric tables and report sections; firewall attacker/port tables support IPv6 sources and grouped hit counts, and Entware package listings show installed/available versions.
- MTR renders every standard latency metric with hop/host/probes in a readable table; Start/HOST metadata remain visible. Unrecognized/extra diagnostic lines remain escaped in a monospace block; unsupported reports fall back to their full diagnostic text. Intermediate-hop losses are not treated as confirmed WAN outages.
- Security custom-HTML results retain their original colors and neutral Recent events count within the common shell. Renderer output is quoted-printable encoded; missing/failed rendering preserves the prior text/custom-HTML sending path.
- Installer 1.0.0a38, package 20261018-r46, 46 targets including the new private-library renderer. Uninstaller 1.0.0a5 removes the renderer with notification modules. No schedule, trigger, SMTP credential, database or firewall policy changes; dashboard regeneration is unnecessary.


## r47 — 2026-10-18
- New Number Format 1.0.0a1 loads before inline page initialization and presents quantities as 1.234,56. Exact large integer strings retain BigInt precision; bytes/rates retain their existing unit bases. Machine data, identifiers and calculations are unchanged.
- Dashboard 2.0.0a21, Firewall dashboard 2.0.0a24, Pingtool 2.0.0a22 and Traffic Manager 2.0.0a18: uniform current/average metrics, sizes, rates, quota values, sample/point counts, percentage labels, signed history counters, diffs and chart locales/tooltips. Narrow shared regrouping to explicitly identified integer counters to avoid interpreting decimal text as counts.
- Security page 1.0.0a14 / UI 1.0.0a9: uniform comparison percentages and list deltas; existing storage scaling retained. Shared UI CSS 1.0.0a11 / JS 1.0.0a13 refresh cache tokens and add full-width Security overview styling.
- Settings page/controller 1.0.0a3 / typed schema 1.0.0a2: fieldset sections, presets with Custom fallback, full-hour choices, visible bounds/defaults/units and linked range descriptions. Localized number inputs are parsed explicitly into typed JSON; invalid grouping, fractions in integer fields and out-of-range values are rejected. Existing custom settings, unsaved edits, server validation, revision checks and policy guard remain.
- Dashboard replaces the Security text link with a full-width live card for firewall health, web privileges, free storage and recent event count. Snapshot failures remain unknown rather than implying a stopped service; shared refresh updates the card.
- Installer 1.0.0a39, package 20261018-r47, 47 targets including the shared formatter. Generated Ping/Traffic templates refresh on their next run or explicit force. No database, credential, collection schedule or firewall policy changes.

## r48 — 2026-10-19

- Settings page/controller 1.0.0a4: place a visible field title above every boolean control, matching the title/control structure used by selects and text inputs. Keep the checkbox and its Enabled/Disabled state together in a bordered row with the same minimum height as other widgets.
- Associate each title and control with the existing checkbox ID; update the visual state caption on change. Preserve field IDs, configuration values, validation, administrator authorization and save behavior.
- Installer 1.0.0a40, package 20261019-r48, unchanged 47 targets. Reload Settings after installation; generated monitor templates do not require regeneration.

## r49 — 2026-10-19

- Security Engine 1.0.0a11: expand warning/rejected blocklist rows in the scheduled security email with explicit outcome, installed prefix count, recorded cause and cached-source warning, last update attempt and last successful installation with configured timezone.
- Distinguish a cached installation from a prefix-count threshold warning; format installed counts with dot grouping and changes with comma decimals. Explain that installation timestamps do not establish cached source freshness and report unknown age when no successful installation is recorded.
- Never display a rejected candidate's -100% change as an installed-list loss. Retained installed state and unverified installed state remain distinct. Escape diagnostics in HTML, preserve line breaks, include all details in plain text and retain existing health colors/Recent events.
- Installer 1.0.0a41, package 20261019-r49, unchanged 47 targets. No downloader, source selection, retry, acceptance policy or schedule changes. No test email is sent by installation.

## r50 — 2026-10-20

- Dashboard 2.0.0a22: remove the redundant Security & Health action button and descriptive paragraph; retain the native title link as the sole navigation target within the overview.
- Shared UI CSS 1.0.0a12: align the four Security values with existing monitor card typography and label/value rows, grouped in two columns on wide screens and one below 900px. Each column ends without a redundant row rule; retain one existing checked-time footer and stale/error messages.
- Scope the shared card padding override to the home Dashboard, avoiding stacked outer/inner padding in all four cards. Retain semantic health colors, full-width Security card, data source and unified refresh. Only the Dashboard cache token changes because the CSS changes are home-specific.
- Installer 1.0.0a42, package 20261020-r50, unchanged 47 targets. Refresh the Dashboard after install; no generated monitor templates or operational settings change.
