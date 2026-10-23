from pathlib import Path
import tempfile,subprocess,os,json,sqlite3,time,shutil
root=Path(__file__).resolve().parents[1]
php=os.environ.get('KT_TEST_PHP','/tmp/keentool-security-runtime/root/usr/bin/php8.3')
engine=root/'support/security_engine.php'
mock=r'''#!/usr/bin/env python3
import sys,os,json,ipaddress
from pathlib import Path
p=Path(os.environ['KT_SECURITY_ROOT']);a=sys.argv[1:];name=Path(sys.argv[0]).name;f=p/'kernel.json';s=json.loads(f.read_text())
def save():f.write_text(json.dumps(s))
if name=='ip':
 if '-o' in a:print('2: br0 inet 10.128.1.1/24 scope global br0')
 elif 'br0' in a and '-4' in a:print('10.128.1.0/24 proto kernel scope link')
elif name in ['iptables-save','ip6tables-save']:
 suffix='6' if name.startswith('ip6') else '';print('*filter')
 for chain in ['BLOCKLIST_IN','BLOCKLIST_FWD']:print('-A '+chain+suffix+' -m set --match-set KTManualBan'+suffix+' src -j DROP')
 print('COMMIT')
elif name=='ipset':
 op=a[0];sets=s['sets'];target=a[1] if len(a)>1 else ''
 if op=='list':
  if '-n' in a:target=a[-1]
  if target not in sets:sys.exit(1)
  print('Name: '+target+'\nNumber of entries: '+str(len(sets[target]))+'\nReferences: 2')
 elif op=='create':sets.setdefault(target,{});save()
 elif op=='test':
  matched=False
  for net in sets.get(target,{}):
   n=ipaddress.ip_network(net,strict=False);q=ipaddress.ip_network(a[2],strict=False)
   if n.version==q.version and q.subnet_of(n):matched=True
  sys.exit(0 if matched else 1)
 elif op=='add':
  if target not in sets:sys.exit(1)
  ttl=int(a[a.index('timeout')+1]) if 'timeout' in a else 0;sets[target][a[2]]=ttl;save()
 elif op=='del':
  if a[2] not in sets.get(target,{}):sys.exit(1)
  del sets[target][a[2]];save()
 elif op=='save':
  if target not in sets:sys.exit(1)
  print('create '+target+' hash:net counters')
  for net,ttl in sets[target].items():print('add '+target+' '+net+' timeout '+str(ttl)+' packets 7 bytes 350')
elif name=='id':sys.exit(1)
elif name=='pidof':sys.exit(1)
else:sys.exit(1)
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td);bin=p/'bin';bin.mkdir();tool=bin/'mock';tool.write_text(mock);tool.chmod(0o755)
 for name in ['ip','ipset','iptables-save','ip6tables-save','id','pidof']:(bin/name).symlink_to(tool)
 (bin/'sqlite3').symlink_to('/tmp/keentool-security-runtime/root/usr/bin/sqlite3')
 for path in ['opt/bin','opt/etc','opt/lib/keentool','opt/etc/ndm/netfilter.d','proc/sys/kernel/random','opt/var/www/firewall','opt/var/backups/keentool-alpha','opt/var/log']: (p/path).mkdir(parents=True,exist_ok=True)
 (p/'proc/sys/kernel/random/boot_id').write_text('fixture-boot')
 (p/'opt/bin/bash').symlink_to('/bin/bash')
 conf=p/'opt/etc/firewall.conf';conf.write_text('ENABLE_FIREWALL="true"\nENABLE_IPV6="true"\nENABLE_MANUAL="true"\n')
 h=p/'opt/bin/firewall_health';h.write_text('#!/bin/bash\nv=$(sed -n \'s/^ENABLE_FIREWALL="\\(.*\\)"/\\1/p\' "'+str(conf)+'")\nprintf \'{"enabled":%s,"healthy":true,"applied":true,"ipv4_ok":true,"ipv6_ok":true}\\n\' "$v"\n');h.chmod(0o755)
 for path in ['opt/lib/keentool/firewall_guard','opt/etc/ndm/netfilter.d/100-firewall.sh']:
  f=p/path;f.write_text('#!/bin/bash\nexit 0\n');f.chmod(0o755)
 sets={name:{} for name in ['FirewallWhite','FirewallWhite6','FirewallBlock','FirewallBlock6','GeoBlock','GeoBlock6','AutoBan','AutoBan6','Blacklist','Blacklist6','VPNBlock']}
 sets['FirewallWhite']['198.51.100.77']=0
 (p/'kernel.json').write_text(json.dumps({'sets':sets}))
 c=sqlite3.connect(p/'opt/etc/firewall_stats.db');c.executescript('CREATE TABLE ip_drops(ip TEXT,count INTEGER,timestamp INTEGER,list_type TEXT);CREATE TABLE ip_info(ip TEXT PRIMARY KEY,country TEXT,risk INTEGER,domain TEXT,target_port TEXT,port_history TEXT);')
 now=int(time.time());c.execute('INSERT INTO ip_info VALUES(?,?,?,?,?,?)',('203.0.113.9','US',10,'example.test','443/tcp','443/tcp,53/udp'))
 for count,seconds in [(15,60),(5,90000),(7,650000)]:c.execute('INSERT INTO ip_drops VALUES(?,?,?,?)',('203.0.113.9',count,now-seconds,'main'))
 c.commit();c.close()
 env=dict(os.environ,KT_SECURITY_ROOT=str(p),KT_PATH=str(bin)+':'+os.environ['PATH'],PATH=str(bin)+':'+os.environ['PATH'])
 def call(mode,*args,payload=None,ok=True):
  r=subprocess.run([php,'-n','-d','disable_functions=filter_var',str(engine),mode,*args],input=json.dumps(payload) if payload is not None else None,env=env,capture_output=True,text=True,timeout=30)
  if ok:assert r.returncode==0,r.stdout+r.stderr
  else:assert r.returncode!=0,r.stdout+r.stderr
  return r
 def request(action,**kw):return json.loads(call('request',payload={'action':action,'actor':'198.51.100.5',**kw}).stdout)
 call('init')
 for invalid in ['185.98.170.55:80','185.98.170.999','185.098.170.55',' 185.98.170.55','fe80::1%br0','203.0.113.0/33','2001:db8::/129','203.0.113.1/24/2']:
  call('request',payload={'action':'lookup','actor':'198.51.100.5','ip':invalid},ok=False)
 for actor,address in [('198.51.100.6','185.98.170.55'),('198.51.100.7','2001:db8::55')]:
  value=json.loads(call('request',payload={'action':'lookup','actor':actor,'ip':address}).stdout);assert value['status']=='success' and value['ip']==address
 for target in ['198.51.100.5','198.51.100.0/24','10.128.1.8','0.0.0.0/0','::/0','198.51.100.77','203.0.113.9;id']:
  call('request',payload={'action':'ban','actor':'198.51.100.5','ip':target,'duration':900},ok=False)
 call('request',payload={'action':'ban','actor':'198.51.100.5','ip':'203.0.113.9','duration':'900'},ok=False)
 result=request('ban',ip='203.0.113.9',duration=900,note='temporary test')
 assert now+850<result['expires']<now+1000
 info=request('lookup',ip='203.0.113.9');assert 'KTManualBan' in info['lists'] and info['matches'][0]['timeout_remaining']==900
 assert info['metadata']['country']=='US';assert sum(r['hits'] for r in info['counters'])==27;assert info['rules']
 assert request('unban',ip='203.0.113.9')['remaining']==[]
 request('ban',ip='203.0.113.9',duration=0)
 call('request',payload={'action':'ban','actor':'198.51.100.5','ip':'203.0.113.9','duration':900},ok=False)
 request('unban',ip='203.0.113.9')
 request('ban',ip='203.0.113.9',duration=900)
 bans=p/'opt/etc/keentool/security/manual-bans.json';v=json.loads(bans.read_text());v['203.0.113.9']['expires']=1;v['203.0.113.9']['mono_deadline']=1;bans.write_text(json.dumps(v));call('reconcile');assert not json.loads(bans.read_text())
 result=request('disable');guard=result['pending_id'];assert 'false' in conf.read_text();request('confirm_policy',pending_id=guard);assert not (p/'opt/etc/keentool/security/pending.json').exists()
 result=request('enable');pending=p/'opt/etc/keentool/security/pending.json';v=json.loads(pending.read_text());v['expires']=1;pending.write_text(json.dumps(v));call('guard',result['pending_id']);assert 'false' in conf.read_text();assert not pending.exists()
 result=request('enable');conf.write_text(conf.read_text()+'# concurrent edit\n');v=json.loads(pending.read_text());v['expires']=1;pending.write_text(json.dumps(v));call('guard',result['pending_id'],ok=False);assert '# concurrent edit' in conf.read_text();pending.unlink()
 call('list-event','GeoBlock','50000','1000','normal','installed');lists=json.loads((p/'opt/etc/keentool/security/lists.json').read_text());assert lists['GeoBlock']['warning'] and lists['GeoBlock']['result']=='installed'
 call('list-event','GeoBlock','50000','1000','baseline','installed');assert not json.loads((p/'opt/etc/keentool/security/lists.json').read_text())['GeoBlock']['warning']
 call('list-event','GeoBlock6','900','0','normal','rejected','download_http','ipdeny.com (cn): HTTP 404. No valid cache; installed list retained.','')
 row=json.loads((p/'opt/etc/keentool/security/lists.json').read_text())['GeoBlock6'];assert row['installed']==900 and row['error_code']=='download_http' and 'HTTP 404' in row['detail']
 call('list-event','GeoBlock6','900','900','normal','installed','installed','Validated list installed.','Timeout; cached source used.')
 row=json.loads((p/'opt/etc/keentool/security/lists.json').read_text())['GeoBlock6'];assert row['warning'] and row['source_warning'] and not row['size_warning']
 call('tick');events=json.loads((p/'opt/var/www/firewall/security-data.json').read_text())['events'];assert any(e.get('target')=='GeoBlock6' and 'HTTP 404' in e.get('detail','') for e in events);assert all('note' not in e and 'actor' not in e for e in events)
 call('list-event','GeoBlock6','900','500','normal','rejected','rollback_failed','Kernel state uncertain.','');assert json.loads((p/'opt/etc/keentool/security/lists.json').read_text())['GeoBlock6']['installed'] is None
 call('tick');snapshot=json.loads((p/'opt/var/www/firewall/security-data.json').read_text());assert snapshot['comparisons']['day']['summary']=={'current':15,'previous':5};assert snapshot['comparisons']['week']['summary']=={'current':20,'previous':7};assert all('actor' not in e and 'note' not in e for e in snapshot['events'])
 # Unknown placeholders and case variants must merge before top-country ranking.
 c=sqlite3.connect(p/'opt/etc/firewall_stats.db')
 for index,country in enumerate([None,'','XX',' xx ','--','??','us',' US ']):
  ip='192.0.2.'+str(index+1);c.execute('INSERT INTO ip_info(ip,country) VALUES(?,?)',(ip,country));c.execute('INSERT INTO ip_drops VALUES(?,?,?,?)',(ip,1,now-60,'main'))
 c.execute('INSERT INTO ip_drops VALUES(?,?,?,?)',('192.0.2.99',1,now-60,'main'))
 c.execute('INSERT INTO ip_drops VALUES(?,?,?,?)',('203.0.113.9',1000,now+86400,'main'));c.commit();c.close()
 call('tick');comparison=json.loads((p/'opt/var/www/firewall/security-data.json').read_text())['comparisons']['day'];countries={r['country']:r for r in comparison['countries']}
 assert len(countries)==len(comparison['countries']);assert countries['XX']['current']==7;assert countries['US']['current']==17;assert comparison['summary']=={'current':24,'previous':5}
 assert comparison['current_start']==comparison['previous_end'];assert comparison['current_end']-comparison['current_start']==86400;assert comparison['previous_end']-comparison['previous_start']==86400
 call('settings',payload={'management_networks':['203.0.113.0/24'],'geo_shrink_percent':95});call('request',payload={'action':'ban','actor':'198.51.100.5','ip':'203.0.113.9','duration':900},ok=False)
 call('settings',payload={'unknown':1},ok=False)
 call('request',payload={'action':'run','command':'id'},ok=False)
 # Only a verified archive manifest can create the backup attestation.
 manifest=''.join('a'*64+'  '+name+'\n' for name in ['sys_backup_20261015_110000.tar.gz','opt_backup_20261015_110000.tar.gz','sqlite_backup_20261015_110000.tar.gz'])
 r=subprocess.run([php,'-n','-d','disable_functions=filter_var',str(engine),'backup-event','20261015_110000'],input=manifest,env=env,capture_output=True,text=True);assert r.returncode==0,r.stderr
 assert json.loads(call('status').stdout)['latest_verified_smb_backup']['verified_at_upload']
 call('event','wan','ppp0 recovered','observed event',str(now-23))
 audit=[json.loads(line) for line in (p/'opt/var/log/keentool-security/audit.jsonl').read_text().splitlines()];assert audit[-1]['time']==now-23 and audit[-1]['recorded_at']>=now
 # Large decoded captures retain only the requested final rows.
 tcp=bin/'tcpdump';tcp.write_text('#!/usr/bin/env python3\nfor i in range(1500):print("2026-10-15 10:00:00.000001 packet "+str(i))\n');tcp.chmod(0o755)
 cap=p/'opt/var/log/keentool-firewall/fw_syn_ring.pcap';cap.parent.mkdir(parents=True);cap.write_bytes(b'fixture')
 log=request('livelog',lines=12);assert len(log['log'].splitlines())==12 and log['log'].endswith('packet 1499');assert log['sampled']
 # Root-only source logs remain private and unchanged across bounded public reads and rotation.
 messages=p/'opt/var/log/messages';messages.write_text(''.join('line '+str(i)+'\n' for i in range(30000)));messages.chmod(0o600)
 original=messages.read_bytes();mode=messages.stat().st_mode
 preview=request('systemlog',log_id='main');assert preview['partial_preview'] and preview['log'].rstrip().endswith('line 29999') and len(preview['log'].splitlines())<=1000
 assert messages.read_bytes()==original and messages.stat().st_mode==mode
 messages.rename(messages.with_suffix('.1'));messages.write_text('after rotation\n');messages.chmod(0o600)
 assert request('systemlog',log_id='main')['log']=='after rotation\n'
 call('request',payload={'action':'systemlog','log_id':'../../etc/passwd'},ok=False)
 messages.unlink();messages.symlink_to(p/'opt/etc/firewall.conf');call('request',payload={'action':'systemlog','log_id':'main'},ok=False)
 messages.unlink();messages.write_text('restored\n');messages.chmod(0o600)
 # Typed web settings use fixed files, revisions and the existing firewall guardian.
 lib=p/'opt/lib/keentool-security';lib.mkdir(exist_ok=True);(lib/'settings_engine.php').write_text((root/'support/settings_engine.php').read_text())
 ping=p/'opt/etc/pingtool.conf';ping.write_text('# preserve comment\nENABLE_IPV6="true"\nPING_DURATION=30\nRETENTION_DAYS=45\nMAX_DISPLAY_POINTS=2000\nCUSTOM_KEEP="untouched"\n')
 dash=p/'opt/etc/keentool/dashboard.conf';dash.write_text('MONTHLY_QUOTA_GB="500"\nVNSTAT_ALIASES="WAN"\nEN_VPN="yes"\nPRIVATE_CUSTOM="do-not-return"\n')
 settings=request('settings_get');assert len(json.dumps(settings).encode())<48000;assert len(settings['groups']['security']['fields']['digest_hour']['choices'])==24;assert settings['groups']['firewall']['fields']['BAN_TIMEOUT']['presets'][0]['label']=='Permanent';assert settings['groups']['ping']['fields']['MAX_DISPLAY_POINTS']['section']=='History and charts';assert settings['groups']['ping']['values']['WAN_MONITOR_INTERVAL']==5;assert 'do-not-return' not in json.dumps(settings) and all('error' not in g for g in settings['groups'].values()),settings
 def save_settings(group,values,revision=None,ok=True):
  if revision is None:revision=request('settings_get')['groups'][group]['revision']
  result=call('request',payload={'action':'settings_save','actor':'198.51.100.5','group':group,'revision':revision,'values':values},ok=ok)
  return json.loads(result.stdout) if ok else result
 before=ping.read_bytes();rev=settings['groups']['ping']['revision']
 for values in [{'MAX_DISPLAY_POINTS':99999},{'WAN_LABEL':'x$(id)'},{'ENABLE_IPV6':'false'},{'WAN_SYSLOG_FILE':'/etc/passwd'},{'RETENTION_DAYS':44},{'PING_TARGET':'2001:db8::1'}]:save_settings('ping',values,ok=False);assert ping.read_bytes()==before
 save_settings('ping',{'MAX_DISPLAY_POINTS':4000});assert 'CUSTOM_KEEP="untouched"' in ping.read_text() and '# preserve comment' in ping.read_text() and ping.stat().st_mode & 0o777==0o600
 save_settings('ping',{'PING_DURATION':25},revision=rev,ok=False)
 save_settings('traffic',{'MONTHLY_QUOTA_GB':750.5});assert 'EN_VPN="yes"' in dash.read_text() and 'PRIVATE_CUSTOM="do-not-return"' in dash.read_text()
 save_settings('security',{'management_networks':'10.9.8.7/24','monitor_interval':90})
 stored=json.loads((p/'opt/etc/keentool/security/settings.json').read_text());assert stored['management_networks']==['10.9.8.0/24'] and stored['monitor_interval']==90
 fw=save_settings('firewall',{'BANNED_COUNTRIES':'cn kp','GEOIP_V6_EXCLUDE_COUNTRIES':'kp','FW_LOG_RATE':3});assert fw['pending_id'] and pending.exists()
 assert request('settings_get')['pending']['pending_id']==fw['pending_id']
 save_settings('traffic',{'MONTHLY_QUOTA_GB':100},ok=False)
 request('confirm_policy',pending_id=fw['pending_id']);assert not pending.exists()
 old_fw=conf.read_bytes();fw=save_settings('firewall',{'ENABLE_FIREWALL':False});assert 'ENABLE_FIREWALL="false"' in conf.read_text()
 request('rollback_policy',pending_id=fw['pending_id']);assert conf.read_bytes()==old_fw
 save_settings('firewall',{'GEOIP_V6_EXCLUDE_COUNTRIES':'us'},ok=False)
 assert list((p/'opt/var/backups/keentool-settings').glob('*/firewall.conf'))
 # Exercise the real detached guardian independently of the CLI request process.
 (p/'opt/lib/keentool-security').mkdir(exist_ok=True)
 (p/'opt/lib/keentool-security/security_engine.php').write_text(engine.read_text())
 (p/'opt/bin/php-cli').symlink_to(php)
 cli=(root/'support/firewall_security').read_text().replace('/opt',str(p)+'/opt')
 (p/'opt/bin/firewall_security').write_text(cli);(p/'opt/bin/firewall_security').chmod(0o755)
 guard=(root/'support/firewall_guard').read_text().replace('/opt',str(p)+'/opt')
 (p/'opt/lib/keentool/firewall_guard').write_text(guard)
 result=request('disable');v=json.loads(pending.read_text());v['expires']=1;pending.write_text(json.dumps(v))
 for _ in range(60):
  if not pending.exists():break
  time.sleep(.1)
 assert not pending.exists(),'detached guardian did not restore the prior policy: '+(p/'opt/var/log/keentool-security/guard.log').read_text()
 assert 'ENABLE_FIREWALL="true"' in conf.read_text()
 # Daily queue retains HTML alongside text, delivers both, and retries failed transport.
 call('settings',payload={'email_enabled':False,'digest_hour':0})
 queue=p/'opt/etc/keentool/security/notifications.json';queue.write_text('{}')
 monitor=p/'opt/etc/keentool/security/monitor.json';state=json.loads(monitor.read_text());state['digest_date']='2000-01-01';monitor.write_text(json.dumps(state))
 call('tick');queued=json.loads(queue.read_text());assert len(queued)==1
 digest=next(iter(queued.values()));assert 'KeenTool security summary' in digest['html'];assert ' bytes' not in digest['body'];assert 'Recent events: ' in digest['body']
 maildir=p/'opt/etc/keentool/mail';maildir.mkdir(parents=True,exist_ok=True)
 for name in ['email.conf','emailpw.enc']:(maildir/name).write_text('fixture')
 sender=p/'opt/bin/email_sender.mod';capture=p/'mail-arguments.json'
 sender.write_text('#!/usr/bin/env python3\nimport sys,json\nfrom pathlib import Path\nPath('+repr(str(capture))+').write_text(json.dumps(sys.argv[1:]))\nsys.exit(1)\n');sender.chmod(0o755)
 call('settings',payload={'email_enabled':True});call('tick');assert json.loads(queue.read_text())==queued
 assert json.loads(capture.read_text())==[digest['subject'],digest['body'],digest['html']]
 sender.write_text(sender.read_text().replace('sys.exit(1)','sys.exit(0)'));call('tick');assert not json.loads(queue.read_text())
 call('settings',payload={'email_enabled':False})
 print('PASS: real PHP engine + SQLite, protected client/management/whitelist CIDRs, injection rejection, TTL/permanent bans, expiry/unban/persistence, diagnostics, confirmation/rollback/conflict, GeoIP warnings/baselines, complete comparisons, public/private audit and settings validation.')
