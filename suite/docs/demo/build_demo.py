#!/usr/bin/env python3
"""Build actual KeenTool pages with synthetic, non-router data for documentation."""
from pathlib import Path
import json,math,os,shutil,subprocess,sys,datetime,html
root=Path(__file__).resolve().parents[2];out=Path(sys.argv[1]).resolve();vendor=Path(os.environ['KT_DOC_VENDOR']);out.mkdir(parents=True,exist_ok=True)
for folder in ['assets','firewall','security','settings','ping','vnstat','run']: (out/folder).mkdir(exist_ok=True)
shutil.copytree(root/'assets',out/'assets',dirs_exist_ok=True)
for rel,dest in [('projects/KeenTool/index.html','index.html'),('projects/keenetic-firewall/www/index.html','firewall/index.html'),('projects/security/index.html','security/index.html'),('projects/settings/index.html','settings/index.html')]:shutil.copy(root/rel,out/dest)
for folder in ['ping','vnstat']:
 for p in vendor.glob('*.js'):shutil.copy(p,out/folder/p.name)
for p in vendor.iterdir():shutil.copy(p,out/'assets'/p.name)
now=int(datetime.datetime(2026,10,23,16,tzinfo=datetime.timezone.utc).timestamp());stamp='23/10/2026, 18:00:00'
def js(path,name,obj): (out/path).write_text('window.'+name+' = '+json.dumps(obj)+';\n')
traffic={'vnstatversion':'2.13','jsonversion':'2','interfaces':[{'name':'ppp0','created':{'date':{'year':2026,'month':6,'day':1}},'updated':{'date':{'year':2026,'month':10,'day':23},'time':{'hour':18,'minute':0}},'traffic':{}}]}
tr=traffic['interfaces'][0]['traffic'];tr['total']={'rx':1480*10**9,'tx':218*10**9}
for key,count in [('day',23),('month',6),('year',1),('hour',24),('fiveminute',24),('top',10)]:
 rows=[]
 for i in range(count):
  date={'year':2026,'month':i+5 if key=='month' else 10,'day':i+1 if key in ['day','top'] else 23};base={'month':72,'year':1500,'hour':.65,'fiveminute':.06}.get(key,3.8)
  rows.append({'id':i,'date':date,'time':{'hour':i%24,'minute':i*5%60},'rx':int((base+base*.35*math.sin(i*.7))*10**9),'tx':int((base*.17+base*.05*math.cos(i))*10**9)})
 tr[key]=rows
fixture=out/'traffic-fixture.json';fixture.write_text(json.dumps(traffic));fake=out/'vnstat-fixture';fake.write_text('#!/usr/bin/env python3\nimport os,sys\nfrom pathlib import Path\nif "--json" in sys.argv:print(Path(os.environ["KT_DOC_TRAFFIC"]).read_text())\n');fake.chmod(0o755)
env=dict(os.environ,KT_COMMON=str(root/'support/common.sh'),KT_RUN_DIR=str(out/'run'),KT_VNSTAT=str(fake),KT_PHP_CLI=os.environ['KT_DOC_PHP'],KT_DOC_TRAFFIC=str(fixture),TZ='Europe/Rome')
subprocess.run(['bash',str(root/'projects/Traffic_manager/Script/traffic_manager.sh'),'ppp0',str(out/'vnstat'),'force'],env=env,check=True)
text=(root/'projects/keenetic-pingtool/scripts/pingtool.sh').read_text();ping=text.split("cat <<'HTML_EOF' > \"$HTML_FILE\"\n",1)[1].split('\nHTML_EOF',1)[0];(out/'ping/index.html').write_text(ping)
hist=[{'x':(now-86400+i*600)*1000,'p':round(18+2.8*math.sin(i*.17)+.7*math.cos(i),3),'j':round(.35+abs(math.sin(i*.3))*.65,3),'l':.0 if i%29 else .7,'peak_p':26,'peak_l':1.2} for i in range(145)]
period={'samples':2880,'p':18.2,'j':.7,'l':.02,'first':now-86400,'last':now}
js('ping/data.js','PING_DATA',{'updated':stamp,'config':{'ipv6':True},'targets':{'v4':'1.1.1.1','v6':'2606:4700:4700::1111'},'current':{'v4':{'ping':18.4,'jitter':.4,'loss':0},'v6':{'ping':16.8,'jitter':.3,'loss':0}},'averages':{'v4':{'p':18.2,'j':.7,'l':.02},'v6':{'p':16.4,'j':.5,'l':0}},'periods':{f:{k:period for k in ['1','24','168','720','max']} for f in ['v4','v6']},'history':{f+k:hist for f in ['v4','v6'] for k in ['','_1','_168','_720','_max']}})
row='<tr><td>23/10/2026</td><td class="num">12.480</td><td>Recorded hits</td></tr>'
tables={k:row for k in ['top_days','hourly','daily','monthly','yearly']}
for periodkey in ['24h','30d','1y','all']:
 for kind in ['trap','other','nets','geo','ipv6','ports','brute']:tables[kind+'_'+periodkey]=''.join('<tr><td class="num">'+str(hits)+'</td><td><a href="https://www.abuseipdb.com/check/'+ip+'">'+ip+'</a></td><td>443/tcp · 22/tcp</td></tr>' for ip,hits in [('203.0.113.17',423),('198.51.100.24',286),('192.0.2.80',184)])
lists={'main':115416,'main6':910,'manual':6,'manual6':2,'vpn':12,'trap_ips':1250,'trap6_ips':380,'geo':32359,'geo6':21257}
for key in ['v4','v6','manual','manual6','vpn','trap','trap6','geo','geo6']:lists['diff_'+key]='+12' if key=='v4' else '0'
fw={'updated':stamp,'ipv6_status':'true','uptime':'12 days, 04:18','lifetime':1842056,'lists':lists,'tables':tables,'averages':{'hourly':520,'daily':12480,'monthly':354000,'yearly':1842056},'geography':{period:{'total':12480,'countries':{cc:{'hits':hits,'sources':max(1,hits//12),'rows':[]} for cc,hits in [('US',3880),('DE',2410),('NL',1620),('FR',1180),('GB',920),('JP',740),('CA',530),('BR',370),('AU',830)]}} for period in ['24h','30d','1y','all']}}
js('firewall/firewall_data.js','FW_DATA',fw)
system={'time':now,'monitor_interval':300,'firewall':{'healthy':True,'enabled':True},'disk':{'free':116938457088,'total':220000000000},'databases':{'firewall_stats.db':30748672,'ping.db':7800832},'services':{'crond':True,'vnstatd':True,'ulogd':True,'WAN monitor':True},'web_privileges':'unprivileged detected','isolation_configured':True,'latest_verified_source_backup':now-43200,'backup_note':'Source checksums verified.','bypasses':{'BYPASS_INTERFACES':'tun+ wg+'},'management_networks':['192.0.2.0/24'],'manual_bans':{},'lists':{name:{'installed':count,'delta_percent':.1,'result':'installed','warning':False,'time':now-43200,'detail':'Validated prefixes installed and saved successfully.'} for name,count in [('FirewallBlock',115416),('FirewallBlock6',910),('GeoBlock',32359),('GeoBlock6',21257)]}}
comparison={'seconds':86400,'current_end':now,'current_start':now-86400,'previous_start':now-172800,'summary':{'current':12480,'previous':13840},'countries':[{'country':c,'current':n,'previous':int(n*1.1)} for c,n in [('US',3880),('DE',2410),('NL',1620),('XX',830)]],'ports':[{'port':p,'current':n,'previous':int(n*.8)} for p,n in [('443/tcp',2800),('22/tcp',1920),('3389/tcp',850)]]}
snapshot={'system':system,'events':[{'time':now-i*1800,'category':c,'event':e,'target':t,'outcome':'ok','detail':d} for i,(c,e,t,d) in enumerate([('blocklist','Blocklist update','FirewallBlock','Validated prefixes installed.'),('health','Firewall verified','IPv4 / IPv6','Owned rule chains match.'),('wan','PPP connection recovered','ppp0','Example PPP event; no live router data.'),('backup','Source backup verified','KeenTool','Checksums verified.')])],'comparisons':{'day':comparison,'week':{**comparison,'seconds':604800}}}
(out/'firewall/security-data.json').write_text(json.dumps(snapshot))
# Render the actual CLI menu with stubbed read-only status/configuration providers.
source=(root/'projects/SMB_Backup_tool/Script/smb_backup_tool.sh').read_text();header=source.split('header() {',1)[1].split('\n}\n',1)[0];menu=source.split('show_menu() {',1)[1].split('\n}\n',1)[0]
script='clear(){ :; };get_cron_status(){ echo ACTIVE; };load_config(){ :; };VERSION=2.0.0;CONFIG_STATUS=OK;SMB_HOST=192.0.2.10;SMB_SHARE=Backups;SMB_SUBDIR=Router;AUTO_PURGE=true;RETENTION_DAYS=90;CRON_LABEL="Daily at 03:00";\nheader(){'+header+'\n}\nshow_menu(){'+menu+'\n}\nshow_menu\n'
result=subprocess.run(['bash','-c',script],input='e\n',text=True,capture_output=True,check=True)
(out/'smb.html').write_text('<!doctype html><html><head><meta charset="utf-8"><title>SMB Backup Tool · example terminal</title></head><body style="margin:0;padding:40px;background:#101923;color:#dce9f4;font:18px/1.7 monospace"><div style="color:#65bde8;margin-bottom:28px">KeenTool / SMB Backup Tool · example terminal session</div><pre>'+html.escape(result.stdout)+'</pre><p style="color:#9cb1c5">Synthetic configuration · documentation example · no backup was executed</p></body></html>')
print(out)
