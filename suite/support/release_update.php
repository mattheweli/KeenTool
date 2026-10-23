<?php
// KeenTool release verification/extraction 1.0.1. CLI only; downloaded code is never evaluated here.
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
 $allowed=['KeenTool','keenetic-firewall','keenetic-pingtool','Traffic_manager','SMB_Backup_tool'];requireValue(in_array($component,$allowed,true),'Unknown component');
 $remote=$candidate['components'][$component]??null;$local=$installed['components'][$component]??'unknown';requireValue(stableVersion($remote),'Component version is missing from the verified release');
 echo $component.': installed '.$local.'; available '.$remote.' (coordinated suite '.$candidate['version'].")\n";
 // Independent script versions are not interchangeable with the repository/suite version.
 $files=$component==='keenetic-firewall'?['scripts/firewall_stats.sh','scripts/firewall_monitor','scripts/firewall_manager.sh','scripts/100-firewall.sh']:[];
 foreach($files as $file){$src=$base.'/projects/'.$component.'/'.$file;requireValue(is_file($src),'Incomplete component source');$text=substr(file_get_contents($src),0,4096);preg_match('/\bv([0-9]+\.[0-9]+\.[0-9]+)\b/',$text,$m);echo '  '.basename($file).': release '.($m[1]??'unversioned')."\n";}
 $issues=[];foreach(file($base.'/INSTALL.tsv',FILE_IGNORE_NEW_LINES|FILE_SKIP_EMPTY_LINES) as $line){
  $parts=explode("\t",$line);requireValue(count($parts)===3,'Invalid installation manifest');[$source,$path,$mode]=$parts;
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
 elseif($action==='checksum'){
  $s=trim(file_get_contents($argv[2]));$name='keentool-'.$argv[4].'.tar.gz';requireValue(preg_match('/^([0-9a-f]{64})  '.preg_quote($name,'/').'$/D',$s,$m),'Invalid checksum sidecar');$hash=hash_file('sha256',$argv[3]);requireValue(hash_equals($m[1],$hash),'Release archive SHA-256 mismatch');if(($argv[5]??'-')!=='-')requireValue(hash_equals('sha256:'.$hash,$argv[5]),'GitHub asset digest mismatch');echo $hash;
 }elseif($action==='component'){componentStatus($argv[2],$argv[3],$argv[4],$argv[5]??'');}
 elseif($action==='extract'){extractVerified($argv[2],$argv[3]);}
 else throw new InvalidArgumentException('Unsupported verification action');
}catch(Throwable $e){fwrite(STDERR,$e->getMessage()."\n");exit(1);}
