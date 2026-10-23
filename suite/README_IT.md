# KeenTool 2.0.0 stabile

La documentazione pubblica è in inglese: vedere README.md e docs/INSTALL.md.

Per aggiornare l'alpha già installata:

```sh
/opt/bin/bash ./install.sh --plan --mode upgrade
/opt/bin/bash ./install.sh --apply --mode upgrade
```

Non usare --configure-web sul tuo router se HTTPS e isolamento web sono già configurati. La migrazione conserva configurazioni esterne, credenziali, database e cron esistenti. Il percorso legacy degli helper rimane disponibile per il rollback dell'alpha, mentre la release stabile usa /opt/lib/keentool.

Al termine:

```sh
/opt/bin/bash /opt/bin/pingtool.sh force
/opt/bin/bash /opt/bin/traffic_manager.sh ppp0 force
/opt/bin/bash /opt/bin/firewall_stats.sh force
```

Riavviare il menu KeenTool e usare Ctrl+F5 sulle pagine aperte. Il backup verificato e il comando di rollback vengono stampati dall'installer. Prima di abilitare nuove regole, verificare la configurazione firewall. L'installer non applica le regole automaticamente.
