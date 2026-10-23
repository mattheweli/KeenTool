"""Check the production size/digest functions without router commands or SMTP."""
from pathlib import Path
import json
import os
import subprocess
root = Path(__file__).resolve().parents[1]
php = os.environ.get('KT_TEST_PHP', '/tmp/keentool-security-runtime/root/usr/bin/php8.3')
s = (root / 'support/security_engine.php').read_text()
helpers = s[s.index('function kstorageSize('):s.index('function ktick()')]
fixtures = [0, 999, 1000, 999999, 1048576, 116938457088, 1000000000000, None, False, -1]
code = helpers + '\ndate_default_timezone_set("Europe/Rome");$input=json_decode(stream_get_contents(STDIN),true);$sizes=array_map("kstorageSize",$input["sizes"]);echo json_encode(["sizes"=>$sizes,"digest"=>kdigest($input["system"],$input["events"])]);'
def run(system):
    result = subprocess.run([php, '-n', '-r', code], input=json.dumps({'sizes': fixtures, 'system': system, 'events': [{}] * 10}), text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)
system = {'firewall': {'healthy': True}, 'web_privileges': 'unprivileged detected', 'disk': {'free': 116938457088, 'total': 200000000000}, 'lists': {'GeoBlock': {'warning': True, 'result': 'installed', 'delta_percent': 0}, '<bad&list>': {'result': 'rejected', 'installed': 12}}}
data = run(system)
assert data['sizes'] == ['0 B', '999 B', '1 KB', '1 MB', '1 MB', '116,9 GB', '1 TB', 'Unavailable', 'Unavailable', 'Unavailable']
digest = data['digest']
assert 'Free storage: 116,9 GB' in digest['body'] and digest['body'].endswith('Recent events: 10')
assert 'Installed prefix-count change: 0% (not address coverage).' in digest['body']
assert '#00843d' in digest['html'] and '#966000' in digest['html'] and '#bd3030' in digest['html']
assert '&lt;bad&amp;list&gt;' in digest['html'] and '<bad&list>' not in digest['html']
assert '<p style="margin:16px 0 0">Recent events: 10</p>' in digest['html']
unknown = run({})['digest'];assert 'Not verified' in unknown['body'] and 'Free storage: Unavailable' in unknown['body'];assert '#00843d' not in unknown['html'] and '#bd3030' not in unknown['html']
failed = run({'firewall': {'healthy': False}, 'web_privileges': 'root detected', 'disk': {'free': 4, 'total': 100}})['digest'];assert failed['html'].count('color:#bd3030') == 3
lists = {
    'GeoBlock': {'installed': 32359, 'delta_percent': 0, 'time': 1792375298, 'last_success': 1792375298, 'result': 'installed', 'warning': True, 'size_warning': False, 'detail': 'Validated prefixes installed and saved successfully.', 'source_warning': 'ipdeny.com (ru): download failed (curl exit 92, HTTP 200). Previous cached source used.'},
    'GeoBlock6': {'installed': 21257, 'new': 0, 'delta_percent': -100, 'time': 1792375332, 'last_success': None, 'result': 'rejected', 'detail': 'ipdeny.com (kp): HTTP 404 returned by the source. No valid cache is available; installed list retained.'},
    'FirewallBlock': {'result': 'installed', 'warning': False},
}
report = run({'lists': lists})['digest']
assert 'GeoBlock: Installed with cached source data.' in report['body']
assert 'Installed prefixes: 32.359' in report['body'] and 'Installed prefixes: 21.257' in report['body']
assert 'curl exit 92, HTTP 200' in report['body'] and 'ipdeny.com (kp): HTTP 404' in report['body']
assert '19/10/2026 04:01:38 CEST' in report['body'] and '19/10/2026 04:02:12 CEST' in report['body']
assert 'Last successful installation: Not recorded; list age unknown.' in report['body']
assert 'Cached source age is not recorded' in report['body']
assert '-100%' not in report['body'] and 'FirewallBlock:' not in report['body']
assert '<br>' in report['html']
older = run({'lists': {'GeoBlock6': {**lists['GeoBlock6'], 'last_success': 1792375298, 'detail': '<script>bad & source</script>'}}})['digest']
assert 'Last successful installation: 19/10/2026 04:01:38 CEST' in older['body']
assert '&lt;script&gt;bad &amp; source&lt;/script&gt;' in older['html'] and '<script>' not in older['html']
size = run({'lists': {'GeoBlock': {'result': 'installed', 'warning': True, 'size_warning': True, 'installed': 321000, 'delta_percent': 1000.5}}})['digest']
assert 'Installed with a prefix-count warning.' in size['body'] and '+1.000,5%' in size['body']
assert 'variation exceeded the configured warning threshold' in size['body']
assert 'Last update attempt: Not recorded.' in size['body']
unverified = run({'lists': {'GeoBlock6': {'result': 'rejected', 'installed': None}}})['digest']
assert 'installed state unverified' in unverified['body'] and 'Installed prefixes: Not verified' in unverified['body']
print('PASS: size scaling, health colors, cached/rejected/size-warning list outcomes, grouped counts and localized changes, attempt/success dates with timezone, unknown freshness, rejected candidate suppression, HTML escaping/line breaks and neutral Recent events; no SMTP.')
