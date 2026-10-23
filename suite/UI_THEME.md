# Keenetic-inspired dashboard theme — 1.0.0a1

Reference: the router screenshots and supplied styles-6AAEF17.css. Shared local CSS/JS uses the reference blue #0097dc, light dashboard background #edeef0, white cards, thin borders, Roboto/system font stack, outline controls and table separators. No Angular runtime, vendor logo font, router cookies or additional CDN dependencies are introduced. Existing chart/map/font dependencies remain unchanged.

Desktop: fixed header and compact sidebar. Mobile: horizontally scrollable top navigation, wrapped controls, responsive cards and local table scrolling. System dark-mode preference is supported; keyboard focus and reduced motion are respected.

Pages: dashboard 2.0.0a4; Traffic Manager 2.0.0a3; Pingtool 2.0.0a4; firewall dashboard 2.0.0a6.

Shared navigation highlights the active page. Data age is reported from the existing router timestamp (30-minute warning), with a missing-data notice when no timestamp is available. Charts have an explicit reset zoom control. List counts get thousands separators, without changing stored values.

Ping: remembered history period remains next to auto-refresh; optional latency/loss peak curves supplement mean curves. Exact raw-sample coverage and samples/points counts remain distinct. Averages and retention are unchanged.

Traffic: named interface picker next to refresh, remembers the interface when available. Existing tabs and all traffic totals/graphs remain available.

Firewall: explicit configured/linked-rule protection state, clear list-vs-drop description, public read-only log search, TCP/UDP/ICMP filters, pause and follow latest. Search operates on the last 1000 loaded lines. Manual refresh works while paused. Save visible log exports the filtered view. Admin mutations still require the existing session/CSRF checks and guest IP forms remain hidden.

Install using install.sh --apply, then regenerate ping/traffic/firewall dashboards as documented in README_IT.md. Reload with Ctrl+F5. The installer backs up replaced files, tracks newly created shared assets and can roll back both. After rollback, regenerate generated dashboards using the restored scripts.

Validation: Bash and generated inline JavaScript syntax, Ping SQL/selection/peak datasets, admin guest/login/logout/CSRF, log search/protocol/pause/follow, isolated installer/new-asset rollback. No visual browser verification was completed locally because a browser runtime could not be made available; review the actual router pages on desktop and mobile.

## UI 1.0.0a2
Full viewport width replaces inherited 1200/1400px body caps. Hide menu / Show menu preserves the preference across pages and resizes charts. Traffic summaries use responsive grid cells with a separate data column and fixed 88px chart column; narrow screens wrap whole cells instead of spilling charts across borders. Doughnuts represent actual traffic only, with the same blue received/green sent palette for current and past periods. Volume tooltips are enabled; forecasts remain in text. All Time now has a matching doughnut.

## UI 1.0.0a3
Decorative heading/log emoji removed; functional SVG navigation icons remain. One local SVG favicon is used across pages. Log viewers share #17202b background and #d6e3ed text, monospace font, 12px/1.7 line spacing and horizontal scrolling. The dashboard's old neon-green !important override is removed. Entry counts use the primary blue; risk/status badges retain meaningful red/green. Jitter and zero loss use neutral text; nonzero loss remains highlighted.
