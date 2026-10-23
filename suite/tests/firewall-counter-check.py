from pathlib import Path
import tempfile,subprocess,sqlite3,os
root=Path(__file__).resolve().parents[1];s=(root/'projects/keenetic-firewall/scripts/firewall_stats.sh').read_text();loop=s[s.index('for TARGET in $TARGETS; do'):s.index('# 5. COLLECT TRAP')];helper=s[s.index('collect_trap_counter() {'):s.index('# IPv4 Trap Processing')]
with tempfile.TemporaryDirectory() as td:
 p=Path(td);bin=p/'bin';bin.mkdir();(bin/'sqlite3').symlink_to('/tmp/keentool-security-runtime/root/usr/bin/sqlite3')
 db=p/'stats.db';c=sqlite3.connect(db);c.execute('CREATE TABLE drops(timestamp INTEGER,list_name TEXT,count INTEGER)');c.close()
 fixture=r'''
iptables(){
 chain=${2%6}
 case "$chain" in
 BLOCKLIST_IN) printf '2 20 NFLOG all -- any any any any match-set FirewallBlock src\n900 9000 DROP all -- any any any any match-set FirewallBlock src\n';;
 BLOCKLIST_FWD) printf '1 10 NFLOG all -- any any any any match-set FirewallBlock src\n100 1000 DROP all -- any any any any match-set FirewallBlock src\n';;
 BLACKLIST)printf '2 20 NFLOG all -- any any any any match-set Blacklist src\n50 500 DROP all -- any any any any match-set Blacklist src\n';;
 SCAN_TRAP)printf '7 70 DROP all -- any any any any\n';;
 FW_CHK_CONN)printf '11 110 DROP all -- any any any any\n';;
 FW_CHK_BRUTE)printf '13 130 DROP all -- any any any any\n';;
 esac
}
ipset(){ printf 'Name: %s\nMembers:\n203.0.113.9 packets 7 bytes 350\n' "$2"; }
'''
 code=fixture+'\nNOW=100;NEW_DROPS_MANUAL=0;NEW_DROPS_MANUAL6=0;NEW_DROPS_TRAP=0;NEW_DROPS_TRAP6=0;DB_FILE="$1";TARGETS="FirewallBlock|iptables| Blacklist|iptables|"\n'+loop.replace('/tmp/fw_last_',str(p)+'/last_')+'\n'+helper+'\nprintf "TRAP=%s\\n" "$(collect_trap_counter iptables \'\')"\n'
 r=subprocess.run(['bash','-c',code,'test',str(db)],env=dict(os.environ,PATH=str(bin)+':'+os.environ['PATH']),capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 c=sqlite3.connect(db);assert dict(c.execute('SELECT list_name,count FROM drops'))=={'FirewallBlock':1000,'Blacklist':50};c.close();assert 'TRAP=31' in r.stdout
 print('PASS: full DROP totals ignore sampled NFLOG counters, shared legacy manual chain is counted once, scan/connlimit/bruteforce drops are combined.')
