from pathlib import Path
import subprocess
import tempfile

s = (Path(__file__).resolve().parents[1] / 'projects/keenetic-pingtool/scripts/pingtool.sh').read_text()
helpers = s[s.index('notification_wan()'):s.index('WAN_V4=$(notification_wan')]

def run(code):
    result = subprocess.run(['bash', '-c', helpers + '\n' + code], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    return result.stdout

assert run('WAN_LABEL=ppp0; notification_wan 4 8.8.8.8') == 'ppp0'
assert run('WAN_LABEL=""; ip(){ echo "8.8.8.8 via 1.2.3.4 dev ppp1 src 1.2.3.5"; };notification_wan 4 8.8.8.8') == 'ppp1'
assert run('WAN_LABEL=""; ip(){ return 1; };notification_wan 6 ::1') == 'WAN unknown'
m = run('recovery_message "ppp0 · IPv4" 1000 2777 8.8.8.8')
assert '29m 37s (1777 seconds)' in m and 'not a measured continuous outage' in m
assert '100% packet loss' in m and 'Target: 8.8.8.8' in m
for began, end in [('2777', '1000'), ('corrupt', '1000')]:
    assert 'unavailable' in run(f'recovery_message "ppp0 · IPv6" {began} {end} ::1')

# Execute the production transitions with a real executable mail stub, never SMTP.
block = s[s.index('for family in v4 v6; do'):s.index('# GENERATE DATA.JS')]
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    mail = root / 'mail'
    mail.write_text('#!/bin/bash\nprintf "SUBJECT: %s\\n%s\\n" "$1" "$2" >> "$DB_DIR/mail.log"\n')
    mail.chmod(0o755)
    setup = helpers + f'''
export DB_DIR="{td}"
INCIDENT_LOG="$DB_DIR/log"; EMAIL_MOD="$DB_DIR/mail"; EMAIL_ALERTS=true
ENABLE_IPV6=true; LABEL_V4="ppp0 · IPv4"; LABEL_V6="ppp0 · IPv6"
PING_TARGET=8.8.8.8; PING_TARGET_V6=2001:4860:4860::8888
LOSS=0; LOSS_V6=0; IS_HIGH_V4=0; IS_HIGH_V6=0
step() {{
{block}
wait
}}
'''
    # The reported warning followed by a healthy check must produce no recovery email.
    code = setup + '''
NOW=1000; LOSS=3.226; step
NOW=2800; LOSS=0; step
NOW=3000; IS_HIGH_V4=1; step
NOW=4800; IS_HIGH_V4=0; step
# An old mixed incident timestamp cannot prove complete loss.
printf '1\\n' > "$DB_DIR/incident_v4.ts"
NOW=5000; step
'''
    run(code)
    assert not (root / 'mail.log').exists()
    assert 'warning cleared' in (root / 'log').read_text()
    assert not (root / 'incident_v4.ts').exists()

    # Count from complete loss, not the earlier warning; partial replies restore reachability.
    run(setup + '''
NOW=6000; LOSS=3.226; step
NOW=6100; LOSS=100; step
NOW=6200; step
NOW=6300; LOSS=5; IS_HIGH_V4=1; step
NOW=6400; LOSS=0; IS_HIGH_V4=0; step
NOW=6500; step
''')
    messages = (root / 'mail.log').read_text()
    assert messages.count('SUBJECT:') == 1
    assert '3m 20s (200 seconds)' in messages and 'Current packet loss: 5%' in messages
    assert 'Ping target reachable again: ppp0 · IPv4' in messages
    assert not (root / 'ping_unreachable_v4.state').exists()

    # Families remain independent, and each incident produces one email only.
    run(setup + '''
NOW=7000; LOSS_V6=100; step
NOW=7100; LOSS=100; step
NOW=7200; LOSS_V6=0; step
NOW=7300; LOSS=0; step
NOW=7400; step
''')
    messages = (root / 'mail.log').read_text()
    assert messages.count('SUBJECT:') == 3
    assert messages.count('Ping target reachable again: ppp0 · IPv6') == 1
    assert messages.count('3m 20s (200 seconds)') == 3

    # A target change must not announce recovery of the previous target.
    run(setup + '''
NOW=8000; LOSS=100; step
NOW=8100; LOSS=0; PING_TARGET=1.1.1.1; step
''')
    assert (root / 'mail.log').read_text().count('SUBJECT:') == 3

    # Existing explicit outage state survives separate scheduled script invocations.
    run(setup + 'NOW=9000; LOSS_V6=100; step')
    run(setup + 'NOW=9100; step')
    assert (root / 'mail.log').read_text().count('SUBJECT:') == 4

    # Invalid/backward timestamps retain a recovery event without inventing a duration.
    for timestamp in ['corrupt', '99999']:
        (root / 'ping_unreachable_v4.state').write_text(timestamp + '\n8.8.8.8\n')
        run(setup + 'NOW=10000; step')
    assert (root / 'mail.log').read_text().count('Sampled interval unavailable') == 2

assert '"Ping Alert: $LABEL_V4"' in s and '"Ping Alert: $LABEL_V6"' in s
print('PASS: warning-only email suppression, legacy migration, complete-loss timing, partial recovery, deduplication, IPv4/IPv6 independence, persistent state, target changes, clock errors and WAN labels; no SMTP.')
