<?php
// KeenTool release verification/extraction 1.0.3. CLI only; downloaded code is never evaluated here.
if(PHP_SAPI!=='cli')exit(1);
umask(0077);
function requireValue($ok,$message){if(!$ok)throw new RuntimeException($message);}
function stableVersion($s){return is_string($s)&&preg_match('/^[0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6}$/D',$s);}
function currentVersion($file,$legacy){
 $j=is_file($file)?json_decode((string)file_get_contents($file),true):null;
 if(is_array($j)&&stableVersion($j['version']??null))return $j['version'];
 if(is_file($legacy)&&preg_match('/(?<![0-9.])([0-9]+\.[0-9]+\.[0-9]+(?:a[0-9]+)?)\b/',substr(file_get_contents($legacy),0,4096),$m))return $m[1];
 return '0.0.0';
}
function newer($latest,$current){
 preg_match('/^([0-9]+\.[0-9]+\.[0-9]+)(a[0-9]+)?$/D',$current,$m);$base=$m[1]??'0.0.0';
 $a=array_map('intval',explode('.',$latest));$b=array_map('intval',explode('.',$base));return $a>$b||($a===$b&&!empty($m[2]));
}
function metadata($release,$installed,$legacy){
 requireValue(is_array($release)&&($release['draft']??true)===false&&($release['prerelease']??true)===false,'Only a published stable release is eligible');
 $tag=$release['tag_name']??'';requireValue(is_string($tag)&&str_starts_with($tag,'v')&&stableVersion(substr($tag,1)),'Invalid stable release tag');$version=substr($tag,1);$name='keentool-'.$version.'.tar.gz';$found=[];
 foreach($release['assets']??[] as $asset){
  if(!in_array($asset['name']??'',[$name,$name.'.sha256'],true))continue;
  requireValue(!isset($found[$asset['name']]),'Duplicate release asset');
  $expected='https://github.com/mattheweli/KeenTool/releases/download/'.$tag.'/'.$asset['name'];
  requireValue(($asset['browser_download_url']??null)===$expected&&($asset['state']??'')==='uploaded','Unexpected release asset URL/state');
  requireValue(is_int($asset['size']??null)&&$asset['size']>0&&$asset['size']<=33554432,'Release asset exceeds the download limit');$found[$asset['name']]=$asset;
 }
 requireValue(isset($found[$name],$found[$name.'.sha256']),'The stable release needs the complete suite archive and SHA-256 sidecar');
 requireValue($found[$name.'.sha256']['size']<=1024,'Unexpected checksum asset size');
 $digest=$found[$name]['digest']??'';requireValue($digest===''||preg_match('/^sha256:[0-9a-f]{64}$/D',$digest),'Unsupported asset digest');
 $current=currentVersion($installed,$legacy);
 return [$version,$current,newer($version,$current)?'1':'0',$found[$name]['browser_download_url'],$found[$name.'.sha256']['browser_download_url'],$digest?:'-'];
}
// Lightweight metadata is bound to the selected published release and GitHub asset digest.
function overviewAsset($release){
 $version=substr($release['tag_name'],1);$name='keentool-'.$version.'-manifest.json';$found=null;
 foreach($release['assets']??[] as $asset){if(($asset['name']??'')!==$name)continue;
  requireValue($found===null,'Duplicate overview asset');$found=$asset;
  requireValue(($asset['browser_download_url']??'')==='https://github.com/mattheweli/KeenTool/releases/download/v'.$version.'/'.$name&&($asset['state']??'')==='uploaded','Unexpected overview asset URL/state');
  requireValue(is_int($asset['size']??null)&&$asset['size']>0&&$asset['size']<=65536,'Overview asset exceeds the download limit');
  requireValue(preg_match('/^sha256:[0-9a-f]{64}$/D',$asset['digest']??''),'Overview asset needs a GitHub SHA-256 digest');
 }
 return $found?[$found['browser_download_url'],$found['digest']]:['-','-'];
}
function verifiedOverview($path,$version,$digest){
 requireValue(hash_equals('sha256:'.hash_file('sha256',$path),$digest),'Overview SHA-256 mismatch');
 $j=json_decode(file_get_contents($path),true,512,JSON_THROW_ON_ERROR);
 requireValue(($j['suite']??'')==='KeenTool'&&($j['version']??'')===$version&&($j['channel']??'')==='stable','Overview release mismatch');
 foreach(['KeenTool','keenetic-firewall','keenetic-pingtool','Traffic_manager','SMB_Backup_tool'] as $name)requireValue(stableVersion($j['components'][$name]??null),'Missing overview component: '.$name);

 foreach($j['changes']??[] as $line)requireValue(is_string($line)&&strlen($line)<=1000&&!preg_match('/[\x00-\x1f\x7f]/',$line),'Unsafe release note');
 return $j;
}
function fileVersion($path){
 if(!is_file($path)||is_link($path)||!is_readable($path))return 'missing';
 $text=file_get_contents($path,false,null,0,4096);return preg_match('/\bv([0-9]+\.[0-9]+\.[0-9]+)\b/',$text,$m)?$m[1]:'unknown';
}
function overviewAudit($j,$scope,$root){
 $issues=[];$checked=0;$seen=[];
 foreach($j['targets']??[] as $t){
  requireValue(is_array($t)&&is_string($t['source']??null)&&preg_match('~^[A-Za-z0-9_./-]+$~D',$t['source'])&&!in_array('..',explode('/',$t['source']),true),'Invalid target source');
  $path=$t['path']??'';requireValue(is_string($path)&&preg_match('~^/opt/[A-Za-z0-9_./-]+$~D',$path)&&!in_array('..',explode('/',$path),true)&&!isset($seen[$path]),'Invalid or duplicate target path');$seen[$path]=true;
  requireValue(preg_match('/^[0-7]{3}$/D',$t['mode']??'')&&preg_match('/^[a-f0-9]{64}$/D',$t['sha256']??''),'Invalid target mode or hash');
  requireValue(in_array($t['owner']??'',array_merge(array_keys($j['components']),['shared']),true),'Unknown target owner');
  requireValue(($t['version']??'')==='-'||stableVersion($t['version']??null),'Invalid target version');
  if($scope!==''&&$t['owner']!==$scope&&$t['owner']!=='shared')continue;
  $checked++;$local=rtrim($root,'/').$path;$reason=null;
  if(is_link($local))$reason='unexpected symbolic link';
  elseif(!is_file($local))$reason='missing';
  elseif(!is_readable($local))$reason='unreadable';
  elseif(!hash_equals($t['sha256'],hash_file('sha256',$local)))$reason='content differs';
  elseif((fileperms($local)&0777)!==octdec($t['mode']))$reason='permissions differ';
  if($reason!==null)$issues[]=['path'=>$path,'reason'=>$reason,'installed'=>fileVersion($local),'available'=>$t['version']];
 }
 if(isset($j['targets']))requireValue($checked>0,'No verification targets for selected component');
 return ['verified'=>isset($j['targets']),'checked'=>$checked,'issues'=>$issues];
}
function overviewStatus($j,$installedFile,$legacy,$scope,$selectionOnly=false,$root=''){
 $installed=is_file($installedFile)?json_decode(file_get_contents($installedFile),true):[];$current=currentVersion($installedFile,$legacy);
 $names=['KeenTool','keenetic-firewall','keenetic-pingtool','Traffic_manager','SMB_Backup_tool'];if(isset($j['components']['Dashboard']))$names[]='Dashboard';
 requireValue($scope===''||in_array($scope,$names,true),'Unknown overview scope');$selected=false;$changed=[];$newerComponents=[];$audit=overviewAudit($j,$scope,$root);
 foreach($names as $name){$local=$installed['components'][$name]??($name==='KeenTool'?$current:'unknown');
  if($name==='Dashboard')$local=fileVersion(rtrim($root,'/').'/opt/var/www/index.html');
  requireValue(is_string($local),'Invalid installed component version');$remote=$j['components'][$name];
  $known=stableVersion($local)||preg_match('/^[0-9]+\.[0-9]+\.[0-9]+a[0-9]+$/D',$local);if($known&&version_compare($local,$remote,'>'))$newerComponents[]=$name;
  $upgrade=!$known||newer($remote,$local);if($upgrade)$changed[]=$name.': '.$local.' -> '.$remote;
  if(($scope===''||$scope===$name)&&$upgrade)$selected=true;
  if(!$selectionOnly&&($scope===''||$scope===$name))printf("%-20s installed %-12s available %-12s %s\n",$name,$local,$remote,$upgrade?'UPDATE AVAILABLE':($local===$remote?'VERSION CURRENT':'LOCAL VERSION NEWER'));
 }
 if($audit['issues'])$selected=true;
 if(version_compare($current,$j['version'],'>')||$newerComponents)$selected=false;
 if($selectionOnly){echo $selected?'1':'0';return;}
 if($audit['verified']){
  echo 'Files verified: '.$audit['checked'].'; differences: '.count($audit['issues']).".\n";
  foreach($audit['issues'] as $issue)echo ' - '.$issue['path'].': '.$issue['reason'].' (installed '.$issue['installed'].'; available '.$issue['available'].")\n";
 }else echo "Installed files have not been verified: this older overview contains versions only.\n";
 if($newerComponents)echo 'Coordinated update blocked: newer installed components ('.implode(', ',$newerComponents)."). Downgrades are not permitted.\n";
 if(!$selected){echo $audit['verified']?"Selected component versions and files match, or a downgrade is blocked.\n":"No newer component version found; file verification is still required.\n";return;}
 echo "\nChanges in the coordinated installation:\n";foreach($changed as $line)echo ' - '.$line."\n";
 if($audit['issues'])echo ' - Repair '.count($audit['issues'])." missing, modified or incorrectly permissioned files in the selected scope.\n";
 echo 'Shared runtime and installer: coordinated suite '.$current.' -> '.$j['version'].".\n";
 echo "Installation applies the complete verified package, including unchanged components, to keep shared files compatible.\n";
 foreach($j['changes']??[] as $line)echo ' - '.$line."\n";
}
function exactRead($stream,$size){$out='';while(strlen($out)<$size&&!feof($stream)){$v=fread($stream,$size-strlen($out));requireValue($v!==false,'Archive read failed');$out.=$v;}requireValue(strlen($out)===$size,'Truncated archive');return $out;}
function octalNumber($s){$s=trim($s,"\0 ");requireValue($s===''||preg_match('/^[0-7]{1,12}$/D',$s),'Unsupported archive numeric field');return $s===''?0:octdec($s);}
function relativeName($name,$prefix){
 requireValue(str_starts_with($name,$prefix),'Archive root mismatch');$rel=substr($name,strlen($prefix));
 requireValue($rel!==''&&strlen($rel)<=220&&preg_match('~^[A-Za-z0-9_./-]+$~D',$rel)&&!in_array('..',explode('/',$rel),true)&&!in_array('.',explode('/',$rel),true)&&!str_contains($rel,'//'),'Unsafe archive path');return rtrim($rel,'/');
}
function extractVerified($dest,$version){
 requireValue(stableVersion($version)&&is_dir($dest)&&count(scandir($dest))===2,'Empty private staging directory required');$prefix='keentool-'.$version.'/';$files=[];$pendingPath=null;$total=0;$count=0;$ended=false;
 while(!feof(STDIN)){
  $h=exactRead(STDIN,512);$total+=512;requireValue($total<=134217728,'Expanded archive exceeds the limit');
  if($h===str_repeat("\0",512)){
   requireValue(exactRead(STDIN,512)===$h,'Invalid archive terminator');
   while(!feof(STDIN)){$tail=fread(STDIN,65536);requireValue($tail!==false&&trim($tail,"\0")==='','Unexpected archive trailer');$total+=strlen($tail);requireValue($total<=134217728,'Expanded archive exceeds the limit');}$ended=true;break;
  }
  $stored=octalNumber(substr($h,148,8));$check=substr_replace($h,str_repeat(' ',8),148,8);requireValue(array_sum(unpack('C*',$check))===$stored,'Archive header checksum mismatch');
  $size=octalNumber(substr($h,124,12));requireValue($size<=8388608,'Archive member exceeds the limit');$kind=$h[156];
  $name=rtrim(substr($h,0,100),"\0");$pre=rtrim(substr($h,345,155),"\0");if($pre!=='')$name=$pre.'/'.$name;
  if($kind==='x'){
   requireValue($size<=8192&&$pendingPath===null,'Unsupported extended header');$payload=exactRead(STDIN,$size);$at=0;
   while($at<strlen($payload)){
    requireValue(preg_match('/\G([0-9]+) ([^=\n]+)=/A',$payload,$m,0,$at),'Malformed extended header');$length=(int)$m[1];requireValue($length>strlen($m[0])&&$at+$length<=strlen($payload),'Invalid extended header length');$record=substr($payload,$at,$length);requireValue(str_ends_with($record,"\n"),'Invalid extended header record');$value=substr($record,strlen($m[0]),-1);
    if($m[2]==='path'){$pendingPath=$value;}else requireValue(in_array($m[2],['mtime','atime','ctime','uid','gid','uname','gname'],true),'Unsupported extended archive key');$at+=$length;
   }
  }else{
   requireValue(in_array($kind,["\0",'0','5'],true),'Archive links and special files are forbidden');if($pendingPath!==null){$name=$pendingPath;$pendingPath=null;}
   if($name===rtrim($prefix,'/')||$name===$prefix){requireValue($kind==='5'&&$size===0,'Invalid archive root');}
   else{
    $rel=relativeName($name,$prefix);$target=$dest.'/'.$rel;
    if($kind==='5'){requireValue($size===0,'Invalid directory member');if(!is_dir($target))requireValue(mkdir($target,0700,true),'Cannot create archive directory');}
    else{
     requireValue(!isset($files[$rel])&&!file_exists($target),'Duplicate archive member');requireValue(++$count<=1024,'Archive contains too many files');if(!is_dir(dirname($target)))requireValue(mkdir(dirname($target),0700,true),'Cannot create parent directory');$f=fopen($target,'xb');requireValue($f!==false,'Cannot create staged file');$remaining=$size;$hash=hash_init('sha256');
     try{while($remaining){$data=exactRead(STDIN,min(65536,$remaining));requireValue(fwrite($f,$data)===strlen($data),'Staging write failed');hash_update($hash,$data);$remaining-=strlen($data);}}finally{fclose($f);}
     $files[$rel]=hash_final($hash);chmod($target,0600);
    }
   }
  }
  if($kind==='x'||$kind==='5'){} // Regular payloads were streamed above.
  $pad=(512-$size%512)%512;if($pad)exactRead(STDIN,$pad);$total+=$size+$pad;
 }
 requireValue($ended&&$pendingPath===null,'Incomplete archive');requireValue(isset($files['CHECKSUMS.sha256'],$files['RELEASE.json'],$files['install.sh'],$files['support/release_install.php']),'Incomplete suite archive');
 $manifest=file_get_contents($dest.'/CHECKSUMS.sha256');$seen=[];
 foreach(explode("\n",trim($manifest)) as $line){requireValue(preg_match('/^([0-9a-f]{64})  (.+)$/D',$line,$m),'Invalid file checksum manifest');$rel=relativeName($prefix.$m[2],$prefix);requireValue(!isset($seen[$rel])&&isset($files[$rel])&&hash_equals($files[$rel],$m[1]),'Package file checksum mismatch: '.$rel);$seen[$rel]=true;}
 unset($files['CHECKSUMS.sha256']);requireValue(count($files)===count($seen),'Unlisted archive content');
 $release=json_decode(file_get_contents($dest.'/RELEASE.json'),true);requireValue(is_array($release)&&($release['suite']??'')==='KeenTool'&&($release['version']??'')===$version&&($release['channel']??'')==='stable','Package metadata does not match the selected release');echo $dest;
}
function componentStatus($base,$installedFile,$component,$root){
 $candidate=json_decode(file_get_contents($base.'/RELEASE.json'),true,512,JSON_THROW_ON_ERROR);$installed=is_file($installedFile)?json_decode(file_get_contents($installedFile),true):[];
 $allowed=['','KeenTool','Dashboard','keenetic-firewall','keenetic-pingtool','Traffic_manager','SMB_Backup_tool'];requireValue(in_array($component,$allowed,true),'Unknown component');
 $remote=$candidate['components'][$component]??($component===''?$candidate['version']:null);$local=$installed['components'][$component]??'unknown';requireValue(stableVersion($remote),'Component version is missing from the verified release');
 if($component==='')echo 'Complete package: installed '.currentVersion($installedFile,'').' ; available '.$remote."\n";else echo $component.': installed '.$local.'; available '.$remote.' (coordinated suite '.$candidate['version'].")\n";
 // Independent script versions are not interchangeable with the repository/suite version.
 $files=$component==='keenetic-firewall'?['scripts/firewall_stats.sh','scripts/firewall_monitor','scripts/firewall_manager.sh','scripts/100-firewall.sh']:[];
 foreach($files as $file){$src=$base.'/projects/'.$component.'/'.$file;requireValue(is_file($src),'Incomplete component source');$text=substr(file_get_contents($src),0,4096);preg_match('/\bv([0-9]+\.[0-9]+\.[0-9]+)\b/',$text,$m);echo '  '.basename($file).': release '.($m[1]??'unversioned')."\n";}
 $scopes=is_file($base.'/FILE_SCOPES.json')?json_decode(file_get_contents($base.'/FILE_SCOPES.json'),true):[];
 $issues=[];foreach(file($base.'/INSTALL.tsv',FILE_IGNORE_NEW_LINES|FILE_SKIP_EMPTY_LINES) as $line){
  $parts=explode("\t",$line);requireValue(count($parts)===3,'Invalid installation manifest');[$source,$path,$mode]=$parts;
  $owner=$scopes[$source]??(str_starts_with($source,'projects/'.$component.'/')?$component:'shared');if($component!==''&&$owner!==$component&&$owner!=='shared')continue;
  requireValue(preg_match('~^[A-Za-z0-9_./-]+$~D',$source)&&!in_array('..',explode('/',$source),true)&&str_starts_with($path,'/opt/')&&!in_array('..',explode('/',$path),true),'Unsafe installation path');
  requireValue(preg_match('/^[0-7]{3}$/D',$mode),'Invalid installation mode');$source=$base.'/'.$source;$path=rtrim($root,'/').$path;
  requireValue(is_file($source)&&!is_link($source),'Missing package target');
  if(is_link($path)||!is_file($path)||!hash_equals(hash_file('sha256',$source),hash_file('sha256',$path))||((fileperms($path)&0777)!==octdec($mode)))$issues[]=$parts[1];
 }
 if(!$issues)echo "All installed package files match the verified release.\n";
 else {echo count($issues)." package files are missing, different or have unexpected permissions; a complete verified reinstall will repair them.\n";foreach(array_slice($issues,0,8) as $path)echo ' - '.$path."\n";}
}
try{
 $action=$argv[1]??'';
 if($action==='flag'){requireValue(stableVersion($argv[3]??''),'Invalid version flag');$tmp=tempnam(dirname($argv[2]),'.kt-version-');requireValue($tmp!==false,'Cannot stage version flag');try{requireValue(file_put_contents($tmp,$argv[3]."\n")!==false&&chmod($tmp,0600)&&rename($tmp,$argv[2]),'Cannot store version flag');}finally{if(is_file($tmp))unlink($tmp);}}
 elseif($action==='metadata'){echo implode("\t",metadata(json_decode(stream_get_contents(STDIN),true),$argv[2],$argv[3]));}
 elseif($action==='overview-asset'){echo implode("\t",overviewAsset(json_decode(stream_get_contents(STDIN),true,512,JSON_THROW_ON_ERROR)));}
 elseif($action==='overview'||$action==='selection'){
  $j=verifiedOverview($argv[2],$argv[3],$argv[4]);overviewStatus($j,$argv[5],$argv[6],$argv[7]??'',$action==='selection',$argv[8]??'');
 }elseif($action==='overview-safe'){
  $j=verifiedOverview($argv[2],$argv[3],$argv[4]);$installed=is_file($argv[5])?json_decode(file_get_contents($argv[5]),true):[];
  foreach($installed['components']??[] as $name=>$local)if(isset($j['components'][$name]))requireValue(is_string($local)&&!version_compare($local,$j['components'][$name],'>'),'Refusing to downgrade installed component: '.$name);
 }elseif($action==='overview-match'){
  $j=verifiedOverview($argv[2],$argv[3],$argv[4]);$candidate=json_decode(file_get_contents($argv[5].'/RELEASE.json'),true,512,JSON_THROW_ON_ERROR);
  requireValue(($candidate['components']??null)==$j['components'],'Archive component versions do not match the approved overview');
  if(isset($j['targets'])){
   $scopes=json_decode(file_get_contents($argv[5].'/FILE_SCOPES.json'),true,512,JSON_THROW_ON_ERROR);$targets=[];
   foreach(file($argv[5].'/INSTALL.tsv',FILE_IGNORE_NEW_LINES|FILE_SKIP_EMPTY_LINES) as $line){[$source,$path,$mode]=explode("\t",$line);$targets[$source]=[$path,$mode,$scopes[$source],hash_file('sha256',$argv[5].'/'.$source)];}
   requireValue(count($targets)===count($j['targets']),'Overview installation target count mismatch');
   foreach($j['targets'] as $t)requireValue(($targets[$t['source']]??null)===[$t['path'],$t['mode'],$t['owner'],$t['sha256']],'Overview installation target mismatch: '.$t['source']);
  }
 }elseif($action==='checksum'){
  $s=trim(file_get_contents($argv[2]));$name='keentool-'.$argv[4].'.tar.gz';requireValue(preg_match('/^([0-9a-f]{64})  '.preg_quote($name,'/').'$/D',$s,$m),'Invalid checksum sidecar');$hash=hash_file('sha256',$argv[3]);requireValue(hash_equals($m[1],$hash),'Release archive SHA-256 mismatch');if(($argv[5]??'-')!=='-')requireValue(hash_equals('sha256:'.$hash,$argv[5]),'GitHub asset digest mismatch');echo $hash;
 }elseif($action==='component'){componentStatus($argv[2],$argv[3],$argv[4],$argv[5]??'');}
 elseif($action==='extract'){extractVerified($argv[2],$argv[3]);}
 else throw new InvalidArgumentException('Unsupported verification action');
}catch(Throwable $e){fwrite(STDERR,$e->getMessage()."\n");exit(1);}
