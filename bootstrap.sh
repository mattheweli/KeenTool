#!/opt/bin/bash
# KeenTool stable bootstrap 1.0.2. Downloaded over trusted GitHub HTTPS; verify its source before running.
set -Eeuo pipefail
umask 077
export PATH=${KT_PATH:-/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin}
for essential in mktemp cat rm;do
 command -v "$essential" >/dev/null || { printf 'Missing bootstrap command: %s. Restore the router BusyBox utilities before migration.
' "$essential" >&2;exit 1; }
done
work=$(mktemp -d "${KT_UPDATE_TMP:-/opt/tmp}/keentool-bootstrap.XXXXXX")
child=''
trap 'rm -rf "$work"' EXIT
cancel(){ trap - INT TERM;[ -z "$child" ] || { kill -TERM "$child" 2>/dev/null || :;wait "$child" || :; };exit 143; }
trap cancel INT TERM
cat > "$work/dependencies.sh" <<'KT_BOOTSTRAP_DEPS'
#!/opt/bin/bash
# KeenTool dependency preflight 1.0.0. Shared by installer and generated bootstrap.
# Inspect capabilities first. Package-manager changes require explicit consent.
kt_dep_add() {
    KT_DEP_ISSUES+=("$1")
    local package=$2
    [[ " ${KT_DEP_PACKAGES[*]} " = *" $package "* ]] || KT_DEP_PACKAGES+=("$package")
}
kt_dep_scan() {
    local scope=$1 name package candidate output root=${KT_INSTALL_ROOT:-}
    KT_DEP_ISSUES=();KT_DEP_PACKAGES=();KT_DEP_PHP=''
    for candidate in "${KT_UPDATE_PHP:-}" "$root/opt/bin/php-cli" "$root/opt/bin/php8" "$root/opt/bin/php";do
        [ -n "$candidate" ] && [ -x "$candidate" ] || continue
        if "$candidate" -r 'exit(PHP_SAPI==="cli"&&PHP_VERSION_ID>=80000?0:1);' >/dev/null 2>&1;then KT_DEP_PHP=$candidate;break;fi
    done
    [ -n "$KT_DEP_PHP" ] || kt_dep_add 'PHP CLI 8.0+ is missing, too old or cannot start (php-cgi does not replace CLI)' php8-cli
    for name in curl gzip sha256sum mktemp cat mkdir rm chmod;do
        command -v "$name" >/dev/null 2>&1 && continue
        case "$name" in curl)package=curl;;gzip)package=gzip;;sha256sum)package=coreutils-sha256sum;;mktemp)package=coreutils-mktemp;;*)package=busybox;;esac
        kt_dep_add "Missing bootstrap command: $name" "$package"
    done
    if [ "$scope" = suite ];then
        while read -r name package;do
            command -v "$name" >/dev/null 2>&1 || kt_dep_add "Missing suite command: $name" "$package"
        done <<'KT_DEP_COMMANDS'
bash bash
ip iproute2
logger busybox
readlink coreutils-readlink
dirname coreutils-dirname
basename coreutils-basename
ps procps-ng-ps
iptables iptables
ip6tables iptables
iptables-save iptables
ip6tables-save iptables
iptables-restore iptables
ip6tables-restore iptables
ipset ipset
sqlite3 sqlite3-cli
vnstat vnstat2
vnstatd vnstat2
tcpdump tcpdump
iprange iprange
openssl openssl-util
lighttpd lighttpd
ping iputils-ping
mtr mtr
ulogd ulogd
smbclient samba4-client
tar tar
grep grep
awk gawk
sed sed
sort coreutils-sort
uniq coreutils-uniq
cut coreutils-cut
head coreutils-head
tail coreutils-tail
wc coreutils-wc
tr coreutils-tr
find findutils
cmp diffutils
date coreutils-date
du coreutils-du
pidof busybox
id coreutils-id
cp coreutils-cp
mv coreutils-mv
rmdir coreutils-rmdir
sleep coreutils-sleep
touch coreutils-touch
timeout coreutils-timeout
KT_DEP_COMMANDS
        if command -v opkg >/dev/null 2>&1;then
            for package in lighttpd-mod-fastcgi lighttpd-mod-openssl ulogd-mod-nflog ulogd-mod-pcap;do
                output=$(opkg status "$package" 2>/dev/null) || output=''
                [[ "$output" =~ Status:[[:space:]]+install[[:space:]]+[^[:space:]]+[[:space:]]+installed ]] || kt_dep_add "Missing Entware runtime module: $package" "$package"
            done
        fi
        command -v crond >/dev/null 2>&1 || command -v cron >/dev/null 2>&1 || kt_dep_add 'Cron executable is missing' cron
        if [ -n "$KT_DEP_PHP" ];then
            output=$("$KT_DEP_PHP" -r 'foreach(["inet_pton","inet_ntop","proc_open","stream_socket_server","session_start","password_hash","random_bytes","hash_file","disk_free_space"] as $f)if(!function_exists($f))echo $f," ";' 2>/dev/null) || output='PHP capability check failed'
            if [ -n "$output" ];then
                package=php8-cli;[[ "$output" != *session_start* ]] || package=php8-mod-session
                kt_dep_add "Unavailable PHP CLI functions: $output" "$package"
            fi
        fi
        candidate="$root/opt/bin/php-cgi"
        if [ ! -x "$candidate" ] || ! output=$("$candidate" -v 2>&1) || [[ ! "$output" =~ PHP[[:space:]]+([0-9]+)\. ]] || [ "${BASH_REMATCH[1]:-0}" -lt 8 ];then kt_dep_add 'PHP CGI 8.0+ is missing, too old or cannot start' php8-cgi;fi
        if command -v sqlite3 >/dev/null 2>&1;then
            output=$(sqlite3 -json :memory: 'SELECT 1 AS ok;' 2>/dev/null) || output=''
            [[ "$output" = *'"ok":1'* ]] || kt_dep_add 'SQLite CLI JSON output is unavailable' sqlite3-cli
        fi
    fi
    [ "${#KT_DEP_ISSUES[@]}" = 0 ]
}
kt_dep_ensure() {
    local scope=$1 policy=${2:-ask} issue answer
    kt_dep_scan "$scope" && return 0
    printf 'Dependency preflight (%s):\n' "$scope" >&2
    for issue in "${KT_DEP_ISSUES[@]}";do printf ' - %s\n' "$issue" >&2;done
    printf 'Required Entware packages: %s\n' "${KT_DEP_PACKAGES[*]}" >&2
    [ "$policy" != check ] || return 1
    [ "$policy" = yes ] || {
        [ -t 0 ] || { echo 'No packages installed. Install the listed packages, or rerun with --install-deps explicitly.' >&2;return 1; }
        read -r -p 'Install these missing dependencies through opkg? [y/N] ' answer
        [[ "$answer" = y || "$answer" = Y ]] || return 1
    }
    [ "$(id -u)" = 0 ] && command -v opkg >/dev/null 2>&1 || { echo 'Root and opkg are required to install dependencies.' >&2;return 1; }
    # Do not upgrade all packages, stop services or change web/firewall configuration.
    opkg update && opkg install "${KT_DEP_PACKAGES[@]}" || { echo 'Dependency installation failed; suite files are unchanged.' >&2;return 1; }
    kt_dep_scan "$scope" || {
        echo 'Dependencies are still unavailable after installation. An installed but broken executable may need library repair:' >&2
        for issue in "${KT_DEP_ISSUES[@]}";do printf ' - %s\n' "$issue" >&2;done
        return 1
    }
}

KT_BOOTSTRAP_DEPS
cat > "$work/release_update.php" <<'KT_BOOTSTRAP_PHP'
<?php
// KeenTool release verification/extraction 1.0.2. CLI only; downloaded code is never evaluated here.
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
 requireValue($j['components']['KeenTool']===$version,'Inconsistent manager version');
 foreach($j['changes']??[] as $line)requireValue(is_string($line)&&strlen($line)<=1000&&!preg_match('/[\x00-\x1f\x7f]/',$line),'Unsafe release note');
 return $j;
}
function overviewStatus($j,$installedFile,$legacy,$scope,$selectionOnly=false){
 $installed=is_file($installedFile)?json_decode(file_get_contents($installedFile),true):[];$current=currentVersion($installedFile,$legacy);
 $names=['KeenTool','keenetic-firewall','keenetic-pingtool','Traffic_manager','SMB_Backup_tool'];requireValue($scope===''||in_array($scope,$names,true),'Unknown overview scope');$selected=false;$changed=[];$newerComponents=[];
 foreach($names as $name){$local=$installed['components'][$name]??($name==='KeenTool'?$current:'unknown');requireValue(is_string($local),'Invalid installed component version');
  $remote=$j['components'][$name];if($local!=='unknown'&&version_compare($local,$remote,'>'))$newerComponents[]=$name;$upgrade=$local==='unknown'||newer($remote,$local);if($upgrade)$changed[]=$name.': '.$local.' -> '.$remote;
  if(($scope===''||$scope===$name)&&$upgrade)$selected=true;
  if(!$selectionOnly&&($scope===''||$scope===$name))printf("%-20s installed %-12s available %-12s %s\n",$name,$local,$remote,$upgrade?'UPDATE AVAILABLE':($local===$remote?'CURRENT':'LOCAL VERSION NEWER'));
 }
 // A component cannot authorize downgrading a newer coordinated installation.
 if(version_compare($current,$j['version'],'>')||$newerComponents)$selected=false;
 if(!$selectionOnly&&$newerComponents)echo 'Coordinated update blocked: newer installed components ('.implode(', ',$newerComponents)."). Downgrades are not permitted.\n";
 if($selectionOnly){echo $selected?'1':'0';return;}
 if(!$selected){echo "No update is available for the selected scope.\n";return;}
 echo "\nChanges in the coordinated installation:\n";foreach($changed as $line)echo ' - '.$line."\n";
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
 elseif($action==='overview-asset'){echo implode("\t",overviewAsset(json_decode(stream_get_contents(STDIN),true,512,JSON_THROW_ON_ERROR)));}
 elseif($action==='overview'||$action==='selection'){
  $j=verifiedOverview($argv[2],$argv[3],$argv[4]);overviewStatus($j,$argv[5],$argv[6],$argv[7]??'',$action==='selection');
 }elseif($action==='overview-safe'){
  $j=verifiedOverview($argv[2],$argv[3],$argv[4]);$installed=is_file($argv[5])?json_decode(file_get_contents($argv[5]),true):[];
  foreach($installed['components']??[] as $name=>$local)if(isset($j['components'][$name]))requireValue(is_string($local)&&!version_compare($local,$j['components'][$name],'>'),'Refusing to downgrade installed component: '.$name);
 }elseif($action==='overview-match'){
  $j=verifiedOverview($argv[2],$argv[3],$argv[4]);$candidate=json_decode(file_get_contents($argv[5].'/RELEASE.json'),true,512,JSON_THROW_ON_ERROR);
  requireValue(($candidate['components']??null)==$j['components'],'Archive component versions do not match the approved overview');
 }elseif($action==='checksum'){
  $s=trim(file_get_contents($argv[2]));$name='keentool-'.$argv[4].'.tar.gz';requireValue(preg_match('/^([0-9a-f]{64})  '.preg_quote($name,'/').'$/D',$s,$m),'Invalid checksum sidecar');$hash=hash_file('sha256',$argv[3]);requireValue(hash_equals($m[1],$hash),'Release archive SHA-256 mismatch');if(($argv[5]??'-')!=='-')requireValue(hash_equals('sha256:'.$hash,$argv[5]),'GitHub asset digest mismatch');echo $hash;
 }elseif($action==='component'){componentStatus($argv[2],$argv[3],$argv[4],$argv[5]??'');}
 elseif($action==='extract'){extractVerified($argv[2],$argv[3]);}
 else throw new InvalidArgumentException('Unsupported verification action');
}catch(Throwable $e){fwrite(STDERR,$e->getMessage()."\n");exit(1);}

KT_BOOTSTRAP_PHP
cat > "$work/keentool_update" <<'KT_BOOTSTRAP_SH'
#!/opt/bin/bash
# KeenTool remote release updater 1.0.2 — 2026-10-23.
set -Eeuo pipefail
export PATH=${KT_PATH:-/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin}
umask 077
check=false;yes=false;reinstall=false;install_deps=false;component='';local_package='';repair=false
while [ "$#" -gt 0 ];do
 case "$1" in --check)check=true;; --repair)repair=true;; --yes)yes=true;; --reinstall)reinstall=true;; --install-deps)install_deps=true;; --component)[ "$#" -gt 1 ] || { echo '--component requires a name' >&2;exit 2; };shift;component=$1;; --local)shift;local_package=${1:-};; /*)local_package=$1;; --help)echo 'Usage: keentool --update [--check|--repair|--yes|--reinstall|--install-deps|--component NAME|--local /absolute/package/path]';exit 0;; *)echo "Unknown update option: $1" >&2;exit 2;;esac;shift
done
case "$component" in ''|KeenTool|keenetic-firewall|keenetic-pingtool|Traffic_manager|SMB_Backup_tool);;*)echo 'Unknown suite component' >&2;exit 2;;esac
[ "$check" != true ] || [ "$install_deps" != true ] || { echo '--install-deps cannot be used with --check' >&2;exit 2; }
bash_bin=${KT_UPDATE_BASH:-/opt/bin/bash}
if [ -n "$local_package" ];then
 [[ "$local_package" = /* ]] && [ -f "$local_package/RELEASE.json" ] && [ -f "$local_package/install.sh" ] || { echo 'Pass an extracted complete release directory' >&2;exit 1; }
 (cd "$local_package" && sha256sum -c CHECKSUMS.sha256) >/dev/null
 [ "$check" != true ] || { "$bash_bin" "$local_package/install.sh" --plan --mode upgrade;exit; }
 local_args=();[ "$install_deps" != true ] || local_args=(--install-deps)
 exec "$bash_bin" "$local_package/install.sh" --apply --mode upgrade "${local_args[@]}"
fi
helper=${KT_UPDATE_HELPER:-/opt/lib/keentool/release_update.php}
[ -f "$helper" ] || { echo 'Remote updater runtime missing; install the complete suite or use the standalone bootstrap.' >&2;exit 1; }
dependency_lib=${KT_DEPENDENCIES:-/opt/lib/keentool/dependencies.sh}
[ -r "$dependency_lib" ] || { echo 'Dependency runtime missing; use the current standalone bootstrap.' >&2;exit 1; }
. "$dependency_lib"
dep_policy=ask;[ "$check" != true ] || dep_policy=check;[ "$install_deps" != true ] || { [ "$check" != true ] || { echo '--install-deps cannot be used with --check' >&2;exit 2; };dep_policy=yes; }
kt_dep_ensure bootstrap "$dep_policy" || exit 1
php_cli=$KT_DEP_PHP
work=$(mktemp -d "${KT_UPDATE_TMP:-/opt/tmp}/keentool-update.XXXXXX")
trap 'rm -rf "$work"' EXIT
curl_opts=(-fsSL --proto '=https' --proto-redir '=https' --connect-timeout 10 --max-time 180 --retry 2)
status='';rc=0
status=$(curl "${curl_opts[@]}" --max-filesize 1048576 -H 'Accept: application/vnd.github+json' -w '%{http_code}' 'https://api.github.com/repos/mattheweli/KeenTool/releases/latest' -o "$work/release.json") || rc=$?
if [ "$status" = 404 ];then echo 'No published stable KeenTool release is available yet.';exit 0;fi
[ "$rc" = 0 ] && [ "$status" = 200 ] || { echo "GitHub release check failed (HTTP $status, curl $rc); installed files are unchanged." >&2;exit 1; }
info=$("$php_cli" "$helper" metadata "${KT_UPDATE_INSTALLED:-/opt/etc/keentool/installed-release.json}" "${KT_UPDATE_LEGACY:-/opt/bin/keentool}" < "$work/release.json")
IFS=$'\t' read -r version current available archive_url checksum_url digest <<< "$info"
# Checks fetch only release metadata and its small component overview; no package audit.
overview_info=$("$php_cli" "$helper" overview-asset < "$work/release.json")
IFS=$'\t' read -r overview_url overview_digest <<< "$overview_info"
[ -n "${overview_url:-}" ] && [ -n "${overview_digest:-}" ] || { echo 'Invalid release overview metadata' >&2;exit 1; }
if "$php_cli" -r 'exit(version_compare($argv[1],$argv[2],">")?0:1);' "$current" "$version";then
 echo 'Local suite is newer; this release cannot downgrade it.';exit 0
fi
if [ "$overview_url" != '-' ];then
 curl "${curl_opts[@]}" --max-filesize 65536 "$overview_url" -o "$work/overview.json"
 "$php_cli" "$helper" overview "$work/overview.json" "$version" "$overview_digest" "${KT_UPDATE_INSTALLED:-/opt/etc/keentool/installed-release.json}" "${KT_UPDATE_LEGACY:-/opt/bin/keentool}" "$component"
 available=$("$php_cli" "$helper" selection "$work/overview.json" "$version" "$overview_digest" "${KT_UPDATE_INSTALLED:-/opt/etc/keentool/installed-release.json}" "${KT_UPDATE_LEGACY:-/opt/bin/keentool}" "$component")
else
 if [ -n "$component" ] && [ "$repair" != true ];then
  echo 'This older release has no component overview. Use Check all updates or explicitly verify/repair the package.';exit 0
 fi
 echo "KeenTool suite: installed $current; available $version"
 echo 'This release predates component overviews; the complete coordinated suite is selected.'
fi
if [ "$available" = 1 ];then "$php_cli" "$helper" flag "${KT_UPDATE_FLAG:-/tmp/keentool_new_ver}" "$version";
elif [ -z "$component" ];then
 rm -f "${KT_UPDATE_FLAG:-/tmp/keentool_new_ver}"
 [ "$overview_url" != '-' ] || echo "KeenTool suite $current is current (latest stable: $version)."
fi
if [ "$check" = true ] && [ "$repair" != true ];then exit 0;fi
if [ "$available" != 1 ] && [ "$reinstall" != true ] && [ "$repair" != true ];then exit 0;fi
if [ -f "$work/overview.json" ];then
 "$php_cli" "$helper" overview-safe "$work/overview.json" "$version" "$overview_digest" "${KT_UPDATE_INSTALLED:-/opt/etc/keentool/installed-release.json}"
fi
confirm(){
 [ "$yes" != true ] || return 0
 [ -t 0 ] || { echo 'Run interactively to confirm, or use --yes explicitly.';return 1; }
 local answer;read -r -p "$1 [y/N] " answer
 [[ "$answer" = y || "$answer" = Y ]]
}
if [ "$repair" = true ];then
 echo 'Explicit file verification compares all installed program files with the latest verified package; settings and databases are excluded.'
 confirm 'Download the complete package for file verification?' || exit 0
else
 [ "$reinstall" != true ] || echo 'Explicit reinstall requested: the complete coordinated package will be installed.'
 confirm 'Apply this coordinated update (download, verify and install)?' || exit 0
fi
curl "${curl_opts[@]}" --max-filesize 1024 "$checksum_url" -o "$work/archive.sha256"
curl "${curl_opts[@]}" --max-filesize 33554432 "$archive_url" -o "$work/archive.tar.gz"
"$php_cli" "$helper" checksum "$work/archive.sha256" "$work/archive.tar.gz" "$version" "$digest" >/dev/null
mkdir -m 700 "$work/package"
# Validate paths/types and every file checksum while extracting into an empty private directory.
gzip -dc "$work/archive.tar.gz" | "$php_cli" "$helper" extract "$work/package" "$version" >/dev/null
if [ -f "$work/overview.json" ];then
 "$php_cli" "$helper" overview-match "$work/overview.json" "$version" "$overview_digest" "$work/package"
fi
if [ "$repair" = true ];then
 audit=$("$php_cli" "$helper" component "$work/package" "${KT_UPDATE_INSTALLED:-/opt/etc/keentool/installed-release.json}" "${component:-KeenTool}" "${KT_INSTALL_ROOT:-}")
 printf '%s\n' "$audit"
 [ "$check" != true ] || exit 0
 [[ "$audit" != *'All installed package files match the verified release.'* ]] || exit 0
 confirm 'Apply the complete verified package to repair these program files?' || exit 0
fi
[ "$(id -u)" = 0 ] || { echo 'Run the upgrade as root' >&2;exit 1; }
if [ -r "$work/package/support/dependencies.sh" ];then
    . "$work/package/support/dependencies.sh"
    kt_dep_ensure suite "$dep_policy" || exit 1
fi
[ "${KT_UPDATE_BOOTSTRAP:-false}" != true ] || echo 'Bootstrap verified. Existing public/alpha installation will use the same migration installer.'
"$bash_bin" "$work/package/install.sh" --plan --mode upgrade
child=''
cancel(){ trap - INT TERM;[ -z "$child" ] || { kill -TERM "$child" 2>/dev/null || :;wait "$child" || :; };exit 143; }
trap cancel INT TERM
"$bash_bin" "$work/package/install.sh" --apply --mode upgrade & child=$!
wait "$child";child=''
trap - INT TERM
rm -f "${KT_UPDATE_FLAG:-/tmp/keentool_new_ver}"
if [ -n "${KT_UPDATE_RECEIPT:-}" ];then "$php_cli" "$helper" flag "$KT_UPDATE_RECEIPT" "$version";fi
echo 'Verified GitHub release installed. Review the installer backup path and refresh generated pages.'

KT_BOOTSTRAP_SH
KT_UPDATE_BOOTSTRAP=true KT_DEPENDENCIES="$work/dependencies.sh" KT_UPDATE_HELPER="$work/release_update.php" "${KT_UPDATE_BASH:-/opt/bin/bash}" "$work/keentool_update" --reinstall "$@" <&0 & child=$!
wait "$child";child=''
trap - INT TERM
