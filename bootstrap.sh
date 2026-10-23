#!/opt/bin/bash
# KeenTool stable bootstrap 1.0.0. Downloaded over trusted GitHub HTTPS; verify its source before running.
set -Eeuo pipefail
umask 077
export PATH=${KT_PATH:-/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin}
work=$(mktemp -d "${KT_UPDATE_TMP:-/opt/tmp}/keentool-bootstrap.XXXXXX")
child=''
trap 'rm -rf "$work"' EXIT
cancel(){ trap - INT TERM;[ -z "$child" ] || { kill -TERM "$child" 2>/dev/null || :;wait "$child" || :; };exit 143; }
trap cancel INT TERM
cat > "$work/release_update.php" <<'KT_BOOTSTRAP_PHP'
<?php
// KeenTool release verification/extraction 1.0.0. CLI only; downloaded code is never evaluated here.
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
try{
 $action=$argv[1]??'';
 if($action==='flag'){requireValue(stableVersion($argv[3]??''),'Invalid version flag');$tmp=tempnam(dirname($argv[2]),'.kt-version-');requireValue($tmp!==false,'Cannot stage version flag');try{requireValue(file_put_contents($tmp,$argv[3]."\n")!==false&&chmod($tmp,0600)&&rename($tmp,$argv[2]),'Cannot store version flag');}finally{if(is_file($tmp))unlink($tmp);}}
 elseif($action==='metadata'){echo implode("\t",metadata(json_decode(stream_get_contents(STDIN),true),$argv[2],$argv[3]));}
 elseif($action==='checksum'){
  $s=trim(file_get_contents($argv[2]));$name='keentool-'.$argv[4].'.tar.gz';requireValue(preg_match('/^([0-9a-f]{64})  '.preg_quote($name,'/').'$/D',$s,$m),'Invalid checksum sidecar');$hash=hash_file('sha256',$argv[3]);requireValue(hash_equals($m[1],$hash),'Release archive SHA-256 mismatch');if(($argv[5]??'-')!=='-')requireValue(hash_equals('sha256:'.$hash,$argv[5]),'GitHub asset digest mismatch');echo $hash;
 }elseif($action==='extract'){extractVerified($argv[2],$argv[3]);}
 else throw new InvalidArgumentException('Unsupported verification action');
}catch(Throwable $e){fwrite(STDERR,$e->getMessage()."\n");exit(1);}

KT_BOOTSTRAP_PHP
cat > "$work/keentool_update" <<'KT_BOOTSTRAP_SH'
#!/opt/bin/bash
# KeenTool remote release updater 1.0.0 — 2026-10-22.
set -Eeuo pipefail
export PATH=${KT_PATH:-/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin}
umask 077
check=false;yes=false;reinstall=false;local_package=''
while [ "$#" -gt 0 ];do
 case "$1" in --check)check=true;; --yes)yes=true;; --reinstall)reinstall=true;; --local)shift;local_package=${1:-};; /*)local_package=$1;; --help)echo 'Usage: keentool --update [--check|--yes|--reinstall|--local /absolute/package/path]';exit 0;; *)echo "Unknown update option: $1" >&2;exit 2;;esac;shift
done
bash_bin=${KT_UPDATE_BASH:-/opt/bin/bash}
if [ -n "$local_package" ];then
 [[ "$local_package" = /* ]] && [ -f "$local_package/RELEASE.json" ] && [ -f "$local_package/install.sh" ] || { echo 'Pass an extracted complete release directory' >&2;exit 1; }
 (cd "$local_package" && sha256sum -c CHECKSUMS.sha256) >/dev/null
 [ "$check" != true ] || { "$bash_bin" "$local_package/install.sh" --plan --mode upgrade;exit; }
 exec "$bash_bin" "$local_package/install.sh" --apply --mode upgrade
fi
helper=${KT_UPDATE_HELPER:-/opt/lib/keentool/release_update.php}
[ -f "$helper" ] || { echo 'Remote updater runtime missing; install the complete suite or use the standalone bootstrap.' >&2;exit 1; }
php_cli='';for candidate in "${KT_UPDATE_PHP:-}" /opt/bin/php-cli /opt/bin/php8 /opt/bin/php;do
 [ -n "$candidate" ] && [ -x "$candidate" ] || continue
 if "$candidate" -r 'exit(PHP_SAPI === "cli" ? 0 : 1);' >/dev/null 2>&1;then php_cli=$candidate;break;fi
done
[ -n "$php_cli" ] || { echo 'PHP CLI is required for release verification' >&2;exit 1; }
for tool in curl gzip;do command -v "$tool" >/dev/null || { echo "Missing updater dependency: $tool" >&2;exit 1; };done
work=$(mktemp -d "${KT_UPDATE_TMP:-/opt/tmp}/keentool-update.XXXXXX")
trap 'rm -rf "$work"' EXIT
curl_opts=(-fsSL --proto '=https' --proto-redir '=https' --connect-timeout 10 --max-time 180 --retry 2)
status='';rc=0
status=$(curl "${curl_opts[@]}" --max-filesize 1048576 -H 'Accept: application/vnd.github+json' -w '%{http_code}' 'https://api.github.com/repos/mattheweli/KeenTool/releases/latest' -o "$work/release.json") || rc=$?
if [ "$status" = 404 ];then echo 'No published stable KeenTool release is available yet.';exit 0;fi
[ "$rc" = 0 ] && [ "$status" = 200 ] || { echo "GitHub release check failed (HTTP $status, curl $rc); installed files are unchanged." >&2;exit 1; }
info=$("$php_cli" "$helper" metadata "${KT_UPDATE_INSTALLED:-/opt/etc/keentool/installed-release.json}" "${KT_UPDATE_LEGACY:-/opt/bin/keentool}" < "$work/release.json")
IFS=$'\t' read -r version current available archive_url checksum_url digest <<< "$info"
if [ "$reinstall" = true ] && [ "$current" = "$version" ];then available=1;fi
if [ "$available" != 1 ];then rm -f "${KT_UPDATE_FLAG:-/tmp/keentool_new_ver}";echo "KeenTool suite $current is current (latest stable: $version).";exit 0;fi
"$php_cli" "$helper" flag "${KT_UPDATE_FLAG:-/tmp/keentool_new_ver}" "$version"
echo "KeenTool suite update available: $current -> $version"
[ "$check" != true ] || exit 0
if [ "$yes" != true ];then
 [ -t 0 ] || { echo 'Run keentool --update interactively, or use --yes to install explicitly.';exit 0; }
 read -r -p 'Download, verify and install the complete release? [y/N] ' answer
 [[ "$answer" = y || "$answer" = Y ]] || exit 0
fi
[ "$(id -u)" = 0 ] || { echo 'Run the upgrade as root' >&2;exit 1; }
curl "${curl_opts[@]}" --max-filesize 1024 "$checksum_url" -o "$work/archive.sha256"
curl "${curl_opts[@]}" --max-filesize 33554432 "$archive_url" -o "$work/archive.tar.gz"
"$php_cli" "$helper" checksum "$work/archive.sha256" "$work/archive.tar.gz" "$version" "$digest" >/dev/null
mkdir -m 700 "$work/package"
# Validate paths/types and every file checksum while extracting into an empty private directory.
gzip -dc "$work/archive.tar.gz" | "$php_cli" "$helper" extract "$work/package" "$version" >/dev/null
[ "${KT_UPDATE_BOOTSTRAP:-false}" != true ] || echo 'Bootstrap verified. Existing public/alpha installation will use the same migration installer.'
"$bash_bin" "$work/package/install.sh" --plan --mode upgrade
child=''
cancel(){ trap - INT TERM;[ -z "$child" ] || { kill -TERM "$child" 2>/dev/null || :;wait "$child" || :; };exit 143; }
trap cancel INT TERM
"$bash_bin" "$work/package/install.sh" --apply --mode upgrade & child=$!
wait "$child";child=''
trap - INT TERM
rm -f "${KT_UPDATE_FLAG:-/tmp/keentool_new_ver}"
echo 'Verified GitHub release installed. Review the installer backup path and refresh generated pages.'

KT_BOOTSTRAP_SH
KT_UPDATE_BOOTSTRAP=true KT_UPDATE_HELPER="$work/release_update.php" "${KT_UPDATE_BASH:-/opt/bin/bash}" "$work/keentool_update" --reinstall "$@" <&0 & child=$!
wait "$child";child=''
trap - INT TERM
