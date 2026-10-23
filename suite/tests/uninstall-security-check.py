from pathlib import Path
import tempfile,subprocess,os
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
 p=Path(td);opt=p/'opt';events=p/'events'
 for d in ['bin','etc/keentool/security','etc/ndm/netfilter.d','lib/keentool','lib/keentool-security','var/www/firewall','var/www/security','etc/init.d']:(opt/d).mkdir(parents=True,exist_ok=True)
 (opt/'bin/bash').symlink_to('/bin/bash')
 for name in ['firewall_security','keentool_security_service']:
  f=opt/'bin'/name;f.write_text('#!/bin/bash\nprintf "%s %s\\n" "'+name+'" "$*" >> "'+str(events)+'"\n');f.chmod(0o755)
 hook=opt/'etc/ndm/netfilter.d/100-firewall.sh';hook.write_text('#!/bin/bash\necho hook-disable >> "'+str(events)+'"\n');hook.chmod(0o755)
 for name in ['iptables','ip6tables']:
  f=opt/'bin'/name;f.write_text('#!/bin/bash\nexit 1\n');f.chmod(0o755)
 f=opt/'bin/ipset';f.write_text('#!/bin/bash\necho "$*" >> "'+str(events)+'"\nexit 0\n');f.chmod(0o755)
 (opt/'lib/keentool/rollback-test.sh').write_text('#!/bin/bash\n')
 (opt/'etc/keentool/security/web-hardened').write_text('fixture')
 (opt/'etc/keentool/security/settings.json').write_text('{}')
 script=p/'uninstall.sh';script.write_text((root/'support/uninstall.sh').read_text().replace('/opt',str(opt)))
 common=p/'common.sh';common.write_text('kt_init(){ KT_WORKDIR="'+str(p/'work')+'";mkdir -p "$KT_WORKDIR"; };kt_sqlite(){ :; }\n')
 env=dict(os.environ,KT_COMMON=str(common))
 r=subprocess.run(['bash',str(script),'--tool','firewall','--keep-data'],env=env,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr;assert not events.exists()
 r=subprocess.run(['bash',str(script),'--tool','firewall','--keep-data','--apply'],env=env,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 lines=events.read_text().splitlines();assert lines.index('firewall_security harden-web --rollback')<lines.index('keentool_security_service stop')<lines.index('hook-disable')
 assert not (opt/'var/www/security').exists()
 assert any(x=='destroy KTManualBan' for x in lines);assert not (opt/'bin/firewall_security').exists();assert (opt/'etc/keentool/security/settings.json').exists()
 print('PASS: uninstall preview does not stop services; apply restores web isolation before broker shutdown/kernel teardown, removes managed sets/helpers and retains security data.')
