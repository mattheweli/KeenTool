"""Exercise actual MIME generation and transport failure without sending SMTP."""
from pathlib import Path
from email import policy
from email.parser import BytesParser
import os
import subprocess
import tempfile
import shutil

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
    base = Path(td)
    maildir = base / 'opt/etc/keentool/mail'
    maildir.mkdir(parents=True)
    (base / 'opt/bin').mkdir()
    (maildir / 'email.conf').write_text('FROM_ADDRESS=from@example.test\nTO_ADDRESS=to@example.test\nPROTOCOL=smtps\nSMTP_SERVER=smtp.example.test\nSMTP_PORT=465\nSMTP_USER=fixture\n')
    (maildir / 'emailpw.enc').write_text('encrypted fixture')
    openssl = base / 'opt/bin/openssl'
    openssl.write_text('#!/bin/bash\nprintf fixture-password\n')
    openssl.chmod(0o755)
    curl = base / 'curl'
    curl.write_text('''#!/usr/bin/env python3
import os,sys
from pathlib import Path
args=sys.argv[1:];p=Path(args[args.index('--upload-file')+1])
assert p.stat().st_mode & 0o777 == 0o600
Path(os.environ['MAIL_CAPTURE']).write_bytes(p.read_bytes())
sys.exit(int(os.environ.get('FAIL_SMTP','0')))
''')
    curl.chmod(0o755)
    script = base / 'email_sender'
    script.write_text((root / 'projects/KeenTool/email_sender.mod').read_text().replace('/opt/', str(base / 'opt') + '/').replace('/tmp/keentool_mail.', str(base / 'message.')))
    capture = base / 'captured.eml'
    env = dict(os.environ, PATH=str(base) + ':' + os.environ['PATH'], MAIL_CAPTURE=str(capture))
    def send(*args, fail=False):
        result = subprocess.run(['bash', str(script), *args], env={**env, 'FAIL_SMTP': '1' if fail else '0'}, capture_output=True, text=True)
        assert result.returncode == (1 if fail else 0), result.stderr
        assert not list(base.glob('message.*'))
        return BytesParser(policy=policy.default).parsebytes(capture.read_bytes())
    legacy = send('Legacy ping alert', r'Warning\nTarget: 8.8.8.8')
    assert legacy.get_content_type() == 'text/plain'
    assert 'Warning\nTarget: 8.8.8.8' in legacy.get_content()
    plain = 'Free storage: 116,9 GB\nRecent events: 10'
    html = '<html><body><strong style="color:#00843d">116,9 GB</strong><p>Recent events: 10</p></body></html>'
    message = send('Daily summary', plain, html)
    assert message.get_content_type() == 'multipart/alternative'
    assert [part.get_content_type() for part in message.iter_parts()] == ['text/plain', 'text/html']
    assert message.get_body(preferencelist=('plain',)).get_content().strip() == plain
    assert message.get_body(preferencelist=('html',)).get_content().strip() == html
    assert not message.defects and all(not part.defects for part in message.walk())
    send('Failure', plain, html, fail=True)
    # Installed renderer upgrades existing two-argument callers without changing their text.
    renderer = base / 'opt/lib/keentool-mail/mail_layout.php'
    renderer.parent.mkdir(parents=True)
    shutil.copyfile(root / 'support/mail_layout.php', renderer)
    php = os.environ.get('KT_TEST_PHP', '/tmp/keentool-security-runtime/root/usr/bin/php8.3')
    (base / 'opt/bin/php-cli').symlink_to(php)
    source = r'Target: 8.8.8.8\nLatency: 20.090 ms (Threshold: 30 ms)\nPacket Loss: 3.226%'
    message = send('Ping Alert: ppp0 · IPv4', source)
    assert message.get_content_type() == 'multipart/alternative'
    assert message.get_body(preferencelist=('plain',)).get_content().strip() == source.replace(r'\n', '\n')
    alternative = message.get_body(preferencelist=('html',))
    assert alternative['Content-Transfer-Encoding'] == 'quoted-printable'
    assert 'KEENTOOL' in alternative.get_content() and '8.8.8.8' in alternative.get_content()
    assert '<table' in alternative.get_content() and '3.226%' in alternative.get_content()
    assert max(map(len, alternative.get_payload().splitlines())) <= 76
    message = send('Daily summary', plain, html)
    assert '116,9 GB' in message.get_body(preferencelist=('html',)).get_content()
    assert message.get_body(preferencelist=('plain',)).get_content().strip() == plain
    send('Failure with layout', plain, html, fail=True)
    renderer.write_text('<?php exit(1);')
    message = send('Fallback after rendering failure', source)
    assert message.get_content_type() == 'text/plain'
    assert 'Packet Loss: 3.226%' in message.get_content()
    message = send('Custom fallback', plain, html)
    assert message.get_body(preferencelist=('html',)).get_content().strip() == html

print('PASS: complete shared layout via real PHP, encoded HTML/plain MIME, two-argument legacy callers, custom security HTML, missing/failed renderer fallback, private temporary files, cleanup and failed SMTP status; transport mocked.')
