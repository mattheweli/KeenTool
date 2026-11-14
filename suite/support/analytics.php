<?php
// KeenTool installation analytics v1.0.0. CLI-only, bounded best-effort Legacy transport.
if (PHP_SAPI !== 'cli') exit(1);
umask(0077);
function kaPath($p){return rtrim(getenv('KT_INSTALL_ROOT')?:'','/').$p;}
function kaRead($p,$default=[]){
 if(!file_exists($p))return $default;
 if(is_link($p)||!is_file($p)||filesize($p)>131072)throw new RuntimeException('Invalid analytics state file');
 $d=json_decode(file_get_contents($p),true,512,JSON_THROW_ON_ERROR);
 if(!is_array($d))throw new RuntimeException('Invalid analytics state');return $d;
}
function kaWrite($p,$data){
 if(is_link($p))throw new RuntimeException('Analytics symlink rejected');
 $t=tempnam(dirname($p),'.analytics-');if($t===false)throw new RuntimeException('Cannot stage analytics state');
 try{if(file_put_contents($t,json_encode($data,JSON_PRETTY_PRINT|JSON_THROW_ON_ERROR)."\n")===false||!chmod($t,0600)||!rename($t,$p))throw new RuntimeException('Cannot save analytics state');}finally{if(is_file($t))unlink($t);}
}
function kaId(){
 $p=kaPath('/opt/etc/keentool.id');
 if(file_exists($p)||is_link($p)){
  if(is_link($p)||!is_file($p)||filesize($p)>256)throw new RuntimeException('Invalid existing Legacy analytics ID; left unchanged');
  $id=trim(file_get_contents($p));if($id!==''){
   if(!preg_match('/^[a-zA-Z0-9_-]{8,128}$/D',$id))throw new RuntimeException('Invalid existing Legacy analytics ID; left unchanged');
   return $id;
  }
 }
 $h=bin2hex(random_bytes(16));$id=substr($h,0,8).'-'.substr($h,8,4).'-'.substr($h,12,4).'-'.substr($h,16,4).'-'.substr($h,20);
 $t=tempnam(dirname($p),'.keentool-id-');if($t===false)throw new RuntimeException('Cannot stage analytics ID');
 try{if(file_put_contents($t,$id."\n")===false||!chmod($t,0600)||!rename($t,$p))throw new RuntimeException('Cannot save analytics ID');}finally{if(is_file($t))unlink($t);}
 return $id;
}
function kaSend($event,$id){
 $mock=getenv('KT_ANALYTICS_CURL')?:'';
 // Isolated installer/rollback fixtures must never send real analytics.
 if(getenv('KT_INSTALL_ROOT')&&!$mock)return false;
 $curl=$mock?:'curl';
 $url='https://keentoolstats.laniakear.workers.dev/track/'.$event['type'].'?'.http_build_query(['uid'=>$id],'','&',PHP_QUERY_RFC3986);
 $args=[$curl,'-q','--fail','--silent','--show-error','--proto','=https','--connect-timeout','2','--max-time','3','--output','/dev/null','--write-out','%{http_code}',$url];
 $p=proc_open($args,[0=>['file','/dev/null','r'],1=>['pipe','w'],2=>['file','/dev/null','w']],$pipes);
 if(!is_resource($p))return false;
 $code=stream_get_contents($pipes[1]);fclose($pipes[1]);return proc_close($p)===0&&preg_match('/^2[0-9]{2}$/D',$code)===1;
}
function kaFlush(&$state,$file){
 if(empty($state['pending']))return;
 $event=$state['pending'][0];$id=kaId();
 if(kaSend($event,$id)){
  array_shift($state['pending']);$state['sent'][$event['key']]=time();$state['last_delivery']='sent';
  if(count($state['sent'])>256)$state['sent']=array_slice($state['sent'],-256,null,true);
 }else $state['last_delivery']='pending';
 kaWrite($file,$state);
}
function kaMain($args){
 $action=$args[1]??'status';if(!in_array($action,['status','on','off','record','retry'],true))throw new RuntimeException('Usage: keentool --analytics [status|on|off|retry]');
 $dir=kaPath('/opt/etc/keentool');$config=$dir.'/analytics.json';$file=$dir.'/analytics-state.json';
 if(is_link($dir))throw new RuntimeException('Analytics directory symlink rejected');
 if(!is_dir($dir)&&!mkdir($dir,0700,true))throw new RuntimeException('Cannot create analytics directory');
 if(is_link($dir.'/analytics.lock'))throw new RuntimeException('Analytics lock symlink rejected');
 $lock=fopen($dir.'/analytics.lock','c');if(!$lock||!flock($lock,LOCK_EX|LOCK_NB))return;
 try{
  $cfg=kaRead($config,['enabled'=>true]);if(!is_bool($cfg['enabled']??null))throw new RuntimeException('Invalid analytics enabled setting');
  $state=kaRead($file,['pending'=>[],'sent'=>[]]);
  if(!is_array($state['pending']??null)||!is_array($state['sent']??null))throw new RuntimeException('Invalid analytics delivery state');
  if(count($state['pending'])>16||count($state['sent'])>256)throw new RuntimeException('Analytics state limit exceeded');
  foreach($state['pending'] as $event){
   if(!is_array($event)||!in_array($event['type']??'', ['install','update'],true)||!preg_match('/^[0-9]+\.[0-9]+\.[0-9]+$/D',$event['version']??'')||($event['key']??'')!==$event['type'].':'.$event['version'])throw new RuntimeException('Invalid queued analytics event');
  }
  if($action==='status'){
   printf("Installation analytics: %s\n",$cfg['enabled']?'enabled':'disabled');
   printf("Pending events: %d\nLast delivery: %s\n",count($state['pending']),$state['last_delivery']??'not attempted');return;
  }
  if($action==='on'||$action==='off'){
   kaWrite($config,['enabled'=>$action==='on']);if($action==='off'){$state['pending']=[];kaWrite($file,$state);}
   echo 'Installation analytics '.($action==='on'?'enabled':'disabled').".\n";return;
  }
  if(!$cfg['enabled'])return;
  if($action==='record'){
   $type=$args[2]??'';$version=$args[3]??'';$previous=$args[4]??'';
   if(!in_array($type,['install','update'],true)||!preg_match('/^[0-9]+\.[0-9]+\.[0-9]+$/D',$version))throw new RuntimeException('Invalid analytics event');
   if($previous!==$version){
    $key=$type.':'.$version;
    if(!isset($state['sent'][$key])&&!in_array($key,array_column($state['pending'],'key'),true)){
     // Create/reuse the Legacy ID before queuing, never replace an invalid ID silently.
     kaId();$state['pending'][]=['key'=>$key,'type'=>$type,'version'=>$version];
     $state['pending']=array_slice($state['pending'],-16);kaWrite($file,$state);
    }
   }
  }
  // One bounded attempt per successful installation or explicit retry.
  kaFlush($state,$file);
 }finally{flock($lock,LOCK_UN);fclose($lock);}
}
try{kaMain($argv);}catch(Throwable $e){fwrite(STDERR,'Analytics: '.$e->getMessage()."\n");exit(1);}
