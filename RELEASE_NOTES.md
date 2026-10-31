# KeenTool coordinated package 2.0.23

## Coordinated package 2.0.23 / Firewall 4.0.12 — 2026-10-31

- Align CNT headings and values to the left in the Firewall threat tables. Use the counter's intrinsic width instead of a fixed-width reservation, so smaller values leave more room for source addresses.
- Keep grouped values through 999.999.999 readable on one line. Allow flexible metadata widths in narrower two-column layouts and reserve space for nine-digit grouped HITS totals in the port tables.
- Extend Chromium checks with grouped nine-digit counters, left-alignment and text containment assertions, and a comparison proving that CNT shrinks when only short counters are displayed. Preserve the actual exported port-badge regression checks and all 64 viewport/density/period combinations.

Package 2.0.23; Firewall component 4.0.12; Firewall dashboard 2.0.5. KeenTool manager remains 2.0.12, Main Dashboard 2.0.4, Stats 4.0.2 and hook 3.0.1. Filtering policy, stored data, credentials and schedules are unchanged.

Update through KeenTool u, then reload the Firewall page (Ctrl+F5). No manual statistics regeneration is required.
