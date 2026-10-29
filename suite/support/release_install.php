<?php
// KeenTool release file transaction 1.0.6. CLI only; no database or firewall rewrites.
if (PHP_SAPI !== 'cli') exit(1);
umask(0077);

function ktCliSection($title){echo "\n".$title."\n".str_repeat('-',min(78,strlen($title)))."\n";}
function ktCliText($text,$prefix='  '){
 $width=max(20,78-strlen($prefix));$wrapped=wordwrap((string)$text,$width,"\n",false);
 echo $prefix.str_replace("\n","\n".str_repeat(' ',strlen($prefix)),$wrapped)."\n";
}

function rootpath($p){return rtrim(getenv('KT_INSTALL_ROOT')?:'','/').$p;}
function checked($v,$message){if(!$v)throw new RuntimeException($message);return $v;}
function regular($p){for($a=$p;$a!==dirname($a);$a=dirname($a))if(is_link($a))throw new RuntimeException('Symlink path rejected: '.$a);if(file_exists($p)&&!is_file($p))throw new RuntimeException('Regular file required: '.$p);}
function commandRun($args){$p=proc_open($args,[0=>['pipe','r'],1=>['pipe','w'],2=>['pipe','w']],$io);checked(is_resource($p),'Cannot launch command');fclose($io[0]);$s=stream_get_contents($io[1]);$e=stream_get_contents($io[2]);fclose($io[1]);fclose($io[2]);$rc=proc_close($p);return [$rc,$s,$e];}
// Inspect expanded lighttpd settings; only simple dedicated listeners can migrate.
function httpsState(){
 $main=rootpath('/opt/etc/lighttpd/lighttpd.conf');regular($main);
 if(!is_file($main))return ['state'=>'manual','detail'=>'No existing lighttpd configuration.'];
 [$rc,$expanded,$error]=commandRun(['lighttpd','-p','-f',$main]);
 if($rc!==0)return ['state'=>'manual','detail'=>'Cannot inspect expanded lighttpd configuration.'];
 // Preserve quoted strings while removing line comments from the expanded config.
 $clean='';$quoted=false;$escaped=false;
 for($i=0,$n=strlen($expanded);$i<$n;$i++){$c=$expanded[$i];
  if(!$quoted&&$c==='#'){while($i<$n&&$expanded[$i]!=="\n")$i++;$clean.="\n";continue;}
  $clean.=$c;if($c==='"'&&!$escaped)$quoted=!$quoted;
  $escaped=$quoted&&$c==='\\'&&!$escaped;
 }
 if(preg_match('/\bssl\.engine\s*=\s*"enable"/',$clean))return ['state'=>'configured','detail'=>'Existing TLS configuration detected; listener preserved.'];
 if(is_file(rootpath('/opt/etc/keentool/security/web-hardened')))return ['state'=>'manual','detail'=>'Existing isolated web listener requires reviewed TLS configuration.'];
 if(preg_match('/\$[A-Za-z_]+\s*\[|\bssl\.[A-Za-z_-]+\s*=/',$clean))return ['state'=>'manual','detail'=>'Custom socket, virtual-host or TLS settings require manual review.'];
 preg_match_all('/^\s*server\.port\s*=\s*([0-9]+)\s*$/m',$clean,$ports);
 preg_match_all('/^\s*server\.document-root\s*=\s*"([^"\r\n]+)"\s*$/m',$clean,$roots);
 if(count($ports[1])!==1||count($roots[1])!==1||!in_array(rtrim($roots[1][0],'/'),['/opt/var/www',rootpath('/opt/var/www')],true))return ['state'=>'manual','detail'=>'Cannot identify one dedicated KeenTool listener and document root.'];
 $port=(int)$ports[1][0];if($port<1||$port>65535)return ['state'=>'manual','detail'=>'Invalid listener port.'];
 preg_match_all('/^\s*server\.bind\s*=\s*"([^"\r\n]+)"\s*$/m',$clean,$binds);
 if(count($binds[1])>1)return ['state'=>'manual','detail'=>'Multiple bind addresses require manual review.'];
 $bind=$binds[1][0]??'0.0.0.0';$address=$bind==='0.0.0.0'?'127.0.0.1':($bind==='::'?'::1':$bind);
 if(@inet_pton($address)===false)return ['state'=>'manual','detail'=>'A nonnumeric bind address requires manual review.'];
 $host=str_contains($address,':')?'['.$address.']':$address;
 return ['state'=>'plain','port'=>$port,'probe'=>'https://'.$host.':'.$port.'/','openssl'=>preg_match('/"mod_openssl"/',$clean)===1,'detail'=>'HTTP-only listener on port '.$port.'; administrator login requires HTTPS.'];
}
function preflightHttps($p){
 $dir=rtrim(sys_get_temp_dir(),'/').'/.kt-tls-'.bin2hex(random_bytes(8));checked(mkdir($dir,0700),'Cannot create private TLS staging directory');$dirs=[];
 try{
  $cert=rootpath('/opt/etc/keentool/tls/server.pem');$testCert=$cert;
  if(!file_exists($cert)){$testCert=$dir.'/server.pem';putAtomic($testCert,['certificate'=>true,'mode'=>0600],$dirs);}
  $main=rootpath('/opt/etc/lighttpd/lighttpd.conf');$candidate=str_replace('/opt/etc/keentool/tls/server.pem',$testCert,$p['items'][$main]['content']);
  checked(file_put_contents($dir.'/lighttpd.conf',$candidate)!==false,'Cannot stage TLS configuration');
  [$rc,$out,$error]=commandRun(['lighttpd','-tt','-f',$dir.'/lighttpd.conf']);checked($rc===0,'TLS preflight failed; live configuration unchanged: '.$error);
 }finally{foreach(glob($dir.'/*') as $file)if(is_file($file))unlink($file);rmdir($dir);}
}
function literalSettings($file,$defaults){
 if(!is_file($file))return $defaults;
 $s=file_get_contents($file);$out=$defaults;
 foreach($defaults as $key=>$default){
  if(!preg_match('/^'.preg_quote($key,'/').'=(.*)$/m',$s,$m))continue;
  $v=trim($m[1]);
  if(preg_match('/^"([^"`\\\\]*)"\s*(?:#.*)?$/',$v,$q)||preg_match("/^'([^']*)'\\s*(?:#.*)?$/",$v,$q)){$value=$q[1];if(str_contains($value,'$('))throw new RuntimeException('Shell expression requires manual migration: '.$key);$out[$key]=preg_replace_callback('/\$(?:\{([A-Z_]+)\}|([A-Z_]+))/',function($m)use($out){$key=$m[1]?:$m[2];checked(array_key_exists($key,$out),'Unknown inline variable: '.$key);return (string)$out[$key];},$value);}
  elseif(preg_match('/^([0-9]+|true|false)\s*(?:#.*)?$/',$v,$q))$out[$key]=$q[1];
  else throw new RuntimeException('Cannot safely migrate '.$key.' from '.$file.'; create an external configuration first.');
 }
 return $out;
}
function shellConfig($values){$text="# KeenTool stable configuration; preserved by package updates.\n";foreach($values as $k=>$v)$text.=$k.'="'.str_replace(['\\','"','$','`'],['\\\\','\\"','\\$','\\`'],(string)$v).'"'."\n";return $text;}
function plan($base,$mode,$iface,$web,$logging){
 checked(in_array($web,[0,1,2],true),'Invalid web migration mode');
 checked(!is_file(rootpath('/opt/etc/keentool/firewall-upgrade.pending')),'A guarded firewall migration is pending; recover or confirm it first.');checked(is_file($base.'/INSTALL.tsv'),'Missing package manifest');checked(!is_file(rootpath('/opt/etc/keentool/security/pending.json')),'Confirm or roll back the pending firewall change before installing.');checked(!$web||!is_file(rootpath('/opt/etc/keentool/security/web-hardened')),'Preserve the existing isolated listener; omit --configure-web.');$items=[];
 foreach(file($base.'/INSTALL.tsv',FILE_IGNORE_NEW_LINES|FILE_SKIP_EMPTY_LINES) as $line){
  $a=explode("\t",$line);checked(count($a)===3,'Malformed install manifest');[$src,$dest,$perm]=$a;
  checked(preg_match('~^[A-Za-z0-9_./-]+$~D',$src)&&!in_array('..',explode('/',$src),true),'Invalid source');
  checked(str_starts_with($dest,'/opt/')&&!in_array('..',explode('/',$dest),true)&&preg_match('/^0?[0-7]{3}$/D',$perm),'Invalid destination or permissions');
  checked(is_file($base.'/'.$src)&&!is_link($base.'/'.$src),'Missing source: '.$src);$target=rootpath($dest);regular($target);checked(!isset($items[$target]),'Duplicate destination');
  if($dest==='/opt/etc/ndm/netfilter.d/100-firewall.sh'&&getenv('KT_INSTALL_DEFER_FIREWALL')==='1')continue;
  $items[$target]=['source'=>$base.'/'.$src,'mode'=>octdec($perm)];
 }
 $existing=is_file(rootpath('/opt/bin/keentool'))||is_file(rootpath('/opt/bin/pingtool.sh'))||is_file(rootpath('/opt/bin/firewall_monitor'));
 $detected=$existing?'upgrade':'fresh';if($mode==='auto')$mode=$detected;
 checked(in_array($mode,['fresh','upgrade'],true),'Mode must be auto, fresh or upgrade');checked($mode===$detected,'Requested mode does not match the detected installation: '.$detected);
 checked($iface===''||preg_match('/^[A-Za-z0-9_.:-]{1,32}$/D',$iface),'Invalid interface');
 $config=[];$ping=rootpath('/opt/etc/pingtool.conf');
 if(!file_exists($ping)){
  $values=literalSettings(rootpath('/opt/bin/pingtool.sh'),['ENABLE_IPV6'=>'true','EMAIL_ALERTS'=>'false','WAN_LABEL'=>$iface,'WAN_SYSLOG_FILE'=>'/opt/var/log/messages','WAN_SYSLOG_ENABLED'=>'true','WAN_MONITOR_INTERVAL'=>'30','PING_TARGET'=>'8.8.8.8','PING_TARGET_V6'=>'2001:4860:4860::8888','PING_DURATION'=>'30','TRIGGER_LATENCY'=>'30','RETENTION_DAYS'=>'45','MAX_DISPLAY_POINTS'=>'2000','DB_DIR'=>'/opt/etc/pingtool','DB_FILE'=>'/opt/etc/pingtool/pingtool.db','WEB_DIR'=>'/opt/var/www/ping']);
  $config[$ping]=shellConfig($values);
 }
 $fw=rootpath('/opt/etc/firewall.conf');if(!file_exists($fw))$config[$fw]=shellConfig(['ENABLE_FIREWALL'=>'false','ENABLE_IPV6'=>'true','ENABLE_MANUAL'=>'true','ENABLE_AUTOBAN'=>'true','ENABLE_CONNLIMIT'=>'true','ENABLE_BRUTEFORCE'=>'true','ENABLE_FWD_PROTECTION'=>'false','TCP_SERVICES'=>'','UDP_SERVICES'=>'','BANNED_COUNTRIES'=>'','BAN_TIMEOUT'=>'604800']);
 $history=rootpath('/opt/etc/keentool/firewall-history.conf');if(!file_exists($history))$config[$history]=shellConfig($mode==='fresh'?['HISTORY_ENABLED'=>'true','HISTORY_RAW_DAYS'=>'2','HISTORY_HOURLY_DAYS'=>'7','HISTORY_DAILY_DAYS'=>'365','HISTORY_COMPACT'=>'true']:['HISTORY_ENABLED'=>'true','HISTORY_RAW_DAYS'=>'7','HISTORY_HOURLY_DAYS'=>'30','HISTORY_DAILY_DAYS'=>'0','HISTORY_COMPACT'=>'false']);
 $dashboard=rootpath('/opt/etc/keentool/dashboard.conf');if(!file_exists($dashboard))$config[$dashboard]=shellConfig(literalSettings(rootpath('/opt/bin/traffic_manager.sh'),['MONTHLY_QUOTA_GB'=>'0']));
 $cron=rootpath('/opt/etc/crontab');$old=is_file($cron)?file_get_contents($cron):'';
 // New installations get defaults; upgrades retain every existing schedule verbatim.
 if($mode==='fresh'){
  checked($iface!=='','Fresh installation requires --interface (for example ppp0)');$next=rtrim($old,"\n").($old!==''?"\n":'');
  foreach(['pingtool.sh'=>"12,42 * * * * root /opt/bin/pingtool.sh >> /opt/var/log/connmon.log 2>&1",'traffic_manager.sh'=>"*/10 * * * * root /opt/bin/traffic_manager.sh '$iface' >> /opt/var/log/t_manager.log 2>&1",'firewall_stats.sh'=>"*/5 * * * * root /opt/bin/firewall_stats.sh >> /opt/var/log/firewall-stats.log 2>&1",'update_blocklist.sh'=>"0 4 * * * root /opt/bin/update_blocklist.sh >> /opt/var/log/firewall-update.log 2>&1"] as $tool=>$job)if(!str_contains($old,'/opt/bin/'.$tool))$next.=$job."\n";
  if($next!==$old)$config[$cron]=$next;
 }
 $ulog=rootpath('/opt/etc/ulogd.conf');$captureChange=false;
 if(is_file($ulog)&&!$logging){
  $s=file_get_contents($ulog);$next=preg_replace('~(file\s*=\s*["\'])/tmp/fw_syn_ring\.pcap(["\'])~','$1/opt/var/log/keentool-firewall/fw_syn_ring.pcap$2',$s);
  if($next!==$s){$config[$ulog]=$next;$captureChange=true;}
  checked(str_contains($next,'/opt/var/log/keentool-firewall/fw_syn_ring.pcap'),'Custom ulogd capture path: configure the KeenTool PCAP path before installation.');
 }else{
  $config[$ulog]="[global]\nlogfile=\"/opt/var/log/ulogd.log\"\nloglevel=3\nplugin=\"/opt/lib/ulogd/ulogd_inppkt_NFLOG.so\"\nplugin=\"/opt/lib/ulogd/ulogd_raw2packet_BASE.so\"\nplugin=\"/opt/lib/ulogd/ulogd_output_PCAP.so\"\nstack=log1:NFLOG,base1:BASE,pcap1:PCAP\n[log1]\ngroup=1\n[pcap1]\nfile=\"/opt/var/log/keentool-firewall/fw_syn_ring.pcap\"\nsync=1\n";$captureChange=true;
 }
 $cert=rootpath('/opt/etc/keentool/tls/server.pem');$tls=null;
 if($web===2){
  $tls=httpsState();checked($tls['state']==='plain','HTTPS migration unavailable: '.$tls['detail']);
  $main=rootpath('/opt/etc/lighttpd/lighttpd.conf');
  $config[$main]=rtrim(file_get_contents($main),"\n")."\n\n# KeenTool HTTPS migration: existing port, PHP and includes preserved.\n".($tls['openssl']?'':"server.modules += ( \"mod_openssl\" )\n")."ssl.engine = \"enable\"\nssl.pemfile = \"/opt/etc/keentool/tls/server.pem\"\n";
 }elseif($web===1){
  $config[rootpath('/opt/etc/lighttpd/lighttpd.conf')]="# KeenTool dedicated HTTPS listener; previous configuration is in the release backup.\nserver.modules = ( \"mod_access\", \"mod_alias\", \"mod_fastcgi\", \"mod_openssl\" )\nserver.document-root = \"/opt/var/www\"\nserver.port = 8080\nserver.pid-file = \"/opt/var/run/lighttpd.pid\"\nserver.errorlog = \"/opt/var/log/lighttpd/error.log\"\nserver.upload-dirs = ( \"/opt/tmp\" )\nindex-file.names = ( \"index.php\", \"index.html\" )\nstatic-file.exclude-extensions = ( \".php\", \".pl\", \".cgi\", \".fcgi\" )\nssl.engine = \"enable\"\nssl.pemfile = \"/opt/etc/keentool/tls/server.pem\"\nfastcgi.server = ( \".php\" => (( \"socket\" => \"/opt/var/run/keentool-php.sock\", \"bin-path\" => \"/opt/bin/php-cgi\", \"max-procs\" => 1, \"broken-scriptfilename\" => \"enable\", \"bin-environment\" => (\"PHP_FCGI_CHILDREN\" => \"0\", \"PHP_FCGI_MAX_REQUESTS\" => \"1000\") )))\n".(is_file(rootpath('/opt/etc/lighttpd/mime.conf'))?"include \"/opt/etc/lighttpd/mime.conf\"\n":'');
 }
 foreach($config as $target=>$text){regular($target);$items[$target]=['content'=>$text,'mode'=>0600];}
 if($web)regular($cert);
 if($web&&!file_exists($cert)){$items[$cert]=['certificate'=>true,'mode'=>0600];}
 $record=rootpath('/opt/etc/keentool/installed-release.json');regular($record);$items[$record]=['content'=>file_get_contents($base.'/RELEASE.json'),'mode'=>0600];
 $init=[];foreach(['lighttpd','ulogd','vnstat'] as $service){$scripts=array_values(array_filter(glob(rootpath('/opt/etc/init.d/S*'.$service.'*')),fn($p)=>is_file($p)&&is_executable($p)&&!is_link($p)));if(($service==='lighttpd'&&$web)||($service==='ulogd'&&$captureChange)||($service==='vnstat'&&$mode==='fresh'))checked(count($scripts)===1,'Exactly one '.$service.' init script required');$init[$service]=$scripts[0]??null;}
 return ['mode'=>$mode,'base'=>$base,'items'=>$items,'web'=>$web,'tls'=>$tls,'capture_change'=>$captureChange,'init'=>$init,'root'=>rtrim(getenv('KT_INSTALL_ROOT')?:'','/')];
}

function showPlan($p){
 $groups=['Install'=>[],'Update'=>[],'Permissions'=>[],'Matching'=>[]];
 foreach($p['items'] as $path=>$item){
  if(!file_exists($path))$kind='Install';
  else{$expected=isset($item['source'])?hash_file('sha256',$item['source']):(isset($item['content'])?hash('sha256',$item['content']):null);
   $kind=$expected===null||!is_readable($path)||@hash_file('sha256',$path)!==$expected?'Update':(((fileperms($path)&0777)!==$item['mode'])?'Permissions':'Matching');}
  $groups[$kind][]=$path;
 }
 ktCliSection('Installation plan');echo 'Mode: '.$p['mode']."\n";
 ktCliText(sprintf('Targets: %d | Install: %d | Update: %d | Permissions: %d | Matching: %d',count($p['items']),count($groups['Install']),count($groups['Update']),count($groups['Permissions']),count($groups['Matching'])));
 foreach(['Install','Update','Permissions'] as $kind){if(!$groups[$kind])continue;ktCliSection($kind.' ('.count($groups[$kind]).')');foreach($groups[$kind] as $path)ktCliText($path,'  - ');}
 if($groups['Matching'])ktCliText('Already matching: '.count($groups['Matching']).' targets (included in the coordinated transaction).');
 ktCliSection('Configuration');ktCliText('HTTPS: '.($p['web']===2?'enable TLS on existing port '.$p['tls']['port']:($p['web']?'configure listener on 8080':'preserve existing listener')));
 if(getenv('KT_INSTALL_DEFER_FIREWALL')==='1')ktCliText('Firewall rules migration deferred: retain the previous hook until guarded apply is confirmed.');
 ktCliText('Existing credentials, databases and upgrade schedules are preserved.');
}
function removeRecoveryTree($path){
 if(is_dir($path)&&!is_link($path)){foreach(new DirectoryIterator($path) as $item)if(!$item->isDot())removeRecoveryTree($item->getPathname());checked(rmdir($path),'Cannot remove temporary recovery directory');}
 else checked(unlink($path),'Cannot remove temporary recovery file');
}
function discardRecovery($backup){
 checked(is_dir($backup)&&!is_link($backup),'Temporary recovery directory required');$real=realpath($backup);$parent=realpath(rootpath('/opt/var/lib/keentool-release/transactions'));
 checked($parent!==false&&dirname($real)===$parent&&preg_match('/^[0-9]{8}_[0-9]{6}-[0-9]+-[a-f0-9]{6}$/D',basename($real)),'Refusing to remove an unrelated backup');
 $m=backupVerify($real);checked(($m['retain_backup']??true)===false,'Retained backups cannot be discarded automatically');removeRecoveryTree($real);
}

function ensureDir($path,&$dirs){if(is_dir($path))return;ensureDir(dirname($path),$dirs);checked(mkdir($path,0755),'Cannot create '.$path);$dirs[]=$path;}
function putAtomic($path,$item,&$dirs){
 ensureDir(dirname($path),$dirs);$tmp=tempnam(dirname($path),'.kt-release-');checked($tmp!==false,'Cannot stage file');
 try{
  if(isset($item['certificate'])){
   [$rc,$out,$err]=commandRun(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','825','-subj','/CN=KeenTool','-keyout',$tmp.'.key','-out',$tmp.'.crt']);checked($rc===0,'TLS generation failed: '.$err);
   checked(file_put_contents($tmp,file_get_contents($tmp.'.key').file_get_contents($tmp.'.crt'))!==false,'Cannot write certificate');
  }elseif(isset($item['source']))checked(copy($item['source'],$tmp),'Cannot copy source');else checked(file_put_contents($tmp,$item['content'])===strlen($item['content']),'Cannot stage content');
  checked(chmod($tmp,$item['mode']),'Cannot set permissions');checked(rename($tmp,$path),'Cannot install '.$path);
 }finally{foreach([$tmp,$tmp.'.key',$tmp.'.crt'] as $p)if(is_file($p))unlink($p);}
}
function backupVerify($backup){
 $m=json_decode((string)file_get_contents($backup.'/transaction.json'),true);checked(is_array($m)&&($m['format']??0)===1,'Invalid transaction backup');
 checked(($m['root']??null)===rtrim(getenv('KT_INSTALL_ROOT')?:'','/'),'Backup root mismatch');
 foreach($m['before'] as $path=>$row){regular($path);if($row!==null)checked(hash_file('sha256',$backup.'/files'.$path)===$row['sha256'],'Backup checksum mismatch: '.$path);}
 return $m;
}
function restore($backup){
 $m=backupVerify($backup);$dirs=[];
 foreach($m['before'] as $path=>$row){
  if($row===null){if(is_file($path))checked(unlink($path),'Cannot remove new file');continue;}
  putAtomic($path,['source'=>$backup.'/files'.$path,'mode'=>$row['mode']],$dirs);checked(chown($path,$row['uid'])&&chgrp($path,$row['gid']),'Cannot restore ownership');
 }
 foreach(array_reverse($m['created_dirs']??[]) as $dir)if(is_dir($dir))@rmdir($dir);
 echo "Previous package files and changed configuration restored. Databases and collected history retained.\n";
}
try{
 $action=$argv[1]??'';
 if($action==='firewall-state'){
  $conf=rootpath('/opt/etc/firewall.conf');$hook=rootpath('/opt/etc/ndm/netfilter.d/100-firewall.sh');
  $settings=literalSettings($conf,['ENABLE_FIREWALL'=>'false']);$enabled=$settings['ENABLE_FIREWALL'];checked(in_array($enabled,['true','false'],true),'Invalid firewall enable setting');
  $changed=is_file($hook)&&hash_file('sha256',$hook)!==hash_file('sha256',$argv[2].'/projects/keenetic-firewall/scripts/100-firewall.sh');$healthy=false;
  if(is_file(rootpath('/opt/bin/firewall_health'))){[$status]=commandRun(['timeout','20','bash',rootpath('/opt/bin/firewall_health'),'--quiet']);$healthy=$status===0;}
  $recordPath=rootpath('/opt/etc/keentool/installed-release.json');$record=is_file($recordPath)&&!is_link($recordPath)?json_decode((string)file_get_contents($recordPath),true):null;
  $baselinePath=$argv[2].'/FIREWALL_HOOK_BASELINES.json';$baseline=is_file($baselinePath)?json_decode((string)file_get_contents($baselinePath),true):null;
  $known=is_file($hook)&&!is_link($hook)&&is_array($baseline)&&($baseline['format']??null)===1&&in_array(hash_file('sha256',$hook),$baseline['sha256']??[],true);
  $fwVersion=is_array($record)?($record['components']['keenetic-firewall']??null):null;
  $managed=is_array($record)&&($record['suite']??null)==='KeenTool'&&is_string($fwVersion)&&preg_match('/^[0-9]+\.[0-9]+\.[0-9]+$/D',$fwVersion)&&version_compare($fwVersion,'4.0.3','>=');
  $incoming=(string)file_get_contents($argv[2].'/projects/keenetic-firewall/scripts/100-firewall.sh');$compatible=str_contains($incoming,'KT_FW_UPGRADE_TOKEN');
  echo json_encode(['enabled'=>$enabled==='true','hook_exists'=>is_file($hook)&&!is_link($hook),'needed'=>$enabled==='true'&&($changed||!$healthy),'auto_apply'=>$enabled==='true'&&$healthy&&$known&&$managed&&$compatible],JSON_THROW_ON_ERROR);exit;
 }
 if($action==='https-state'){echo json_encode(httpsState(),JSON_THROW_ON_ERROR);exit;}
 if($action==='discard'){discardRecovery($argv[2]);exit;}
 if($action==='rollback'){restore($argv[2]);exit;}
 if($action==='verify-backup'){backupVerify($argv[2]);exit;}
 if($action==='commit'){
  $backup=$argv[2];$p=backupVerify($backup);$dirs=[];
  try{foreach($p['items'] as $path=>$item)putAtomic($path,$item,$dirs);}
  finally{$p['created_dirs']=$dirs;checked(file_put_contents($backup.'/transaction.json',json_encode($p,JSON_PRETTY_PRINT))!==false,'Cannot record directories');}
  exit;
 }
 $base=realpath($argv[2]??'');checked($base!==false,'Invalid package path');$p=plan($base,$argv[3]??'auto',$argv[4]??'',(int)($argv[5]??'0'),($argv[6]??'0')==='1');
 if($action==='plan'){showPlan($p);exit;}
 if($action==='https-preflight'){checked($p['web']===2,'HTTPS migration plan required');preflightHttps($p);exit;}
 checked($action==='prepare','Unsupported transaction action');$policy=$argv[7]??'keep';checked(in_array($policy,['keep','discard'],true),'Invalid backup retention policy');
 $p['retain_backup']=$policy==='keep';$parent=$p['retain_backup']?'/opt/var/backups/keentool-release/':'/opt/var/lib/keentool-release/transactions/';
 $backup=rootpath($parent).date('Ymd_His').'-'.getmypid().'-'.bin2hex(random_bytes(3));checked(mkdir($backup.'/files',0700,true),'Cannot create recovery copies');$p['before']=[];$p['created_dirs']=[];
 foreach($p['items'] as $path=>$item){
  if(!file_exists($path)){$p['before'][$path]=null;continue;}
  $st=stat($path);$dest=$backup.'/files'.$path;if(!is_dir(dirname($dest)))checked(mkdir(dirname($dest),0700,true),'Cannot create backup directory');checked(copy($path,$dest),'Cannot back up file');$hash=hash_file('sha256',$path);checked(hash_file('sha256',$dest)===$hash,'Backup verification failed');$p['before'][$path]=['sha256'=>$hash,'mode'=>$st['mode']&0777,'uid'=>$st['uid'],'gid'=>$st['gid']];
 }
 $ledger=[];foreach($p['before'] as $path=>$row)if($row!==null)$ledger['files'.$path]=$row['sha256'];checked(copy($base.'/INSTALL.tsv',$backup.'/INSTALL.tsv'),'Cannot save manifest');checked(file_put_contents($backup.'/checksums.json',json_encode($ledger))!==false,'Cannot save checksum ledger');
 checked(copy($base.'/support/release_install.php',$backup.'/release_install.php'),'Cannot save rollback engine');checked(copy($base.'/rollback.sh',$backup.'/rollback.sh'),'Cannot save rollback entry point');checked(file_put_contents($backup.'/transaction.json',json_encode(['format'=>1]+$p,JSON_PRETTY_PRINT))!==false,'Cannot save transaction');echo $backup;
}catch(Throwable $e){fwrite(STDERR,$e->getMessage()."\n");exit(1);}
