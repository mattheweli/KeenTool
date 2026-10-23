from pathlib import Path
import tempfile,subprocess,os,json,socket,threading,re
root=Path(__file__).resolve().parents[1];runtime=Path('/tmp/keentool-security-runtime/root/usr/bin');php=str(runtime/'php8.3');cgi=str(runtime/'php-cgi8.3')
with tempfile.TemporaryDirectory() as td:
 p=Path(td);admin=p/'opt/etc/keentool/admin';(admin/'sessions').mkdir(parents=True);(p/'opt/lib/keentool-admin').mkdir(parents=True);sockdir=p/'opt/var/run/keentool-security';sockdir.mkdir(parents=True)
 auth=(root/'projects/keenetic-firewall/www/admin_auth.php').read_text().replace('<?php','<?php namespace Fixture;',1).replace('/opt/',str(p)+'/opt/');(p/'opt/lib/keentool-admin/admin_auth.php').write_text(auth)
 shim=r'''<?php namespace Fixture;
 class TestStream {
  public $context;private $reply='';private $offset=0;
  function stream_open($path,$mode,$options,&$opened){return true;}
  function stream_write($line){$v=json_decode($line,true);file_put_contents(getenv('KT_CAPTURE'),json_encode($v)."\n",FILE_APPEND);$this->reply=json_encode(['status'=>'success','ip'=>$v['ip']??null,'lists'=>[],'duration'=>$v['duration']??null])."\n";if(($v['action']??'')==='systemlog'&&getenv('KT_LOG_REPLY'))$this->reply=json_encode(json_decode(file_get_contents(getenv('KT_LOG_REPLY')),true))."\n";$this->offset=0;return strlen($line);}
  function stream_read($count){$v=substr($this->reply,$this->offset,$count);$this->offset+=strlen($v);return $v;}
  function stream_eof(){return $this->offset>=strlen($this->reply);}
  function stream_stat(){return [];}
  function stream_set_option($option,$arg1,$arg2){return true;}
 }
 stream_wrapper_register('ktfixture',TestStream::class);
 function stream_socket_client($address,&$errno=null,&$error=null,$timeout=null){return fopen('ktfixture://broker','r+');}
 ?>'''
 api=p/'api.php';api.write_text(shim+(root/'projects/keenetic-firewall/www/firewall_api.php').read_text().replace('<?php','<?php namespace Fixture;',1).replace('/opt/',str(p)+'/opt/'))
 password='A-long-test-password-123';hashv=subprocess.check_output([php,'-n','-r','echo password_hash($argv[1],PASSWORD_BCRYPT,["cost"=>4]);',password],text=True)
 (admin/'credentials.json').write_text(json.dumps({'hash':hashv,'revision':'a'*64}));(admin/'attempts.json').write_text('{}')
 capture=p/'requests.jsonl'
 cookie=''
 def call(action,body=None,csrf=None,https=True,origin=None,token=None):
  env=dict(os.environ,SCRIPT_FILENAME=str(api),REDIRECT_STATUS='200',REQUEST_METHOD='POST' if body is not None else 'GET',QUERY_STRING='action='+action,HTTP_HOST='router.test:8080',REMOTE_ADDR='198.51.100.5',HTTPS='on' if https else 'off',REQUEST_SCHEME='https' if https else 'http',HTTP_COOKIE=cookie,KT_CAPTURE=str(capture))
  if (p/'log-reply.json').exists():env['KT_LOG_REPLY']=str(p/'log-reply.json')
  if origin:env['HTTP_ORIGIN']=origin
  if csrf:env['HTTP_X_KT_CSRF']=csrf
  if token:env['HTTP_X_KT_TOKEN']=token
  payload=json.dumps({'action':action,**body}) if body is not None else '';env['CONTENT_TYPE']='application/json';env['CONTENT_LENGTH']=str(len(payload))
  r=subprocess.run([cgi,'-n'],input=payload,text=True,env=env,capture_output=True,timeout=10);assert r.returncode==0,r.stderr
  head,text=r.stdout.replace('\r\n','\n').split('\n\n',1);return head,json.loads(text)
 h,d=call('lookup',https=False);assert d['status']=='error' and '403' in h
 h,d=call('lookup',origin='https://evil.test');assert d['status']=='error' and '403' in h
 h,d=call('ban',{'ip':'203.0.113.9','duration':900});assert d['status']=='error' and '401' in h
 h,d=call('audit');assert d['status']=='error' and '401' in h
 h,d=call('settings_get');assert '401' in h
 h,d=call('settings_save',{'group':'ping','revision':'a'*64,'values':{'MAX_DISPLAY_POINTS':4000}});assert '401' in h
 h,d=call('auth_status');cookie=re.search(r'Set-Cookie: (KT_FW_ADMIN=[^;]+)',h,re.I).group(1);csrf=d['csrf'];assert not d['authenticated'];assert 'httponly' in h.lower() and 'secure' in h.lower() and 'samesite=strict' in h.lower()
 h,d=call('login',{'password':password},csrf='bad');assert d['status']=='error'
 h,d=call('login',{'password':password},csrf=csrf);assert d['authenticated'];csrf=d['csrf'];m=re.search(r'Set-Cookie: (KT_FW_ADMIN=[^;]+)',h,re.I);cookie=m.group(1) if m else cookie
 h,d=call('ban',{'ip':'203.0.113.9','duration':900,'note':'private note'},csrf='bad');assert d['status']=='error'
 h,d=call('ban',{'ip':'203.0.113.9','duration':900,'note':'private note'},csrf=csrf);assert d['status']=='success'
 requests=[json.loads(line) for line in capture.read_text().splitlines()]
 assert requests[-1]['duration']==900 and requests[-1]['actor']=='198.51.100.5';assert requests[-1]['action']=='ban'
 assert all('password' not in r and 'csrf' not in r for r in requests)
 h,d=call('settings_get');assert d['status']=='success'
 h,d=call('settings_save');assert '405' in h
 h,d=call('settings_save',{'group':'ping','revision':'a'*64,'values':{'MAX_DISPLAY_POINTS':4000}},csrf='bad');assert '403' in h
 h,d=call('settings_save',{'group':'ping','revision':'a'*64,'values':{'MAX_DISPLAY_POINTS':4000}},csrf=csrf);assert d['status']=='success'
 forwarded=json.loads(capture.read_text().splitlines()[-1]);assert forwarded['values']=={'MAX_DISPLAY_POINTS':4000} and forwarded['group']=='ping' and 'csrf' not in forwarded
 h,d=call('confirm_policy',{'pending_id':'a'*48},csrf=csrf);assert d['status']=='success'
 h,d=call('logout',{},csrf=csrf);assert not d['authenticated']
 h,d=call('audit');assert '401' in h
 h,d=call('systemlog&log_id=main&cursor=fixture-cursor');assert d['status']=='success'
 requests=[json.loads(line) for line in capture.read_text().splitlines()];assert requests[-1]['action']=='systemlog' and requests[-1]['log_id']=='main' and requests[-1]['cursor']=='fixture-cursor'
 h,d=call('arbitrary_shell',{'command':'id'});assert d['status']=='error'
 code='require '+json.dumps(str(p/'opt/lib/keentool-admin/admin_auth.php'))+';$s=["revision"=>str_repeat("a",64),"born"=>time(),"seen"=>time(),"boot"=>Fixture\\kt_admin_boot()];$_SESSION=$s;if(!Fixture\\kt_admin_active())exit(1);$_SESSION=$s;$_SESSION["seen"]=time()+3600;if(Fixture\\kt_admin_active())exit(2);$_SESSION=$s;$_SESSION["boot"]="another-boot";if(Fixture\\kt_admin_active())exit(3);'
 r=subprocess.run([php,'-n','-r',code],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 # Send a real encoded log frame through PHP-CGI, not only a tiny broker fixture.
 logs=p/'opt/var/log';logs.mkdir(parents=True,exist_ok=True)
 (logs/'messages').write_text(('quote" slash/ backslash\\ à🙂\x00\t'+'x'*1000+'\n')*1000)
 frame=subprocess.run([php,'-n',str(root/'support/security_engine.php'),'request'],input=json.dumps({'action':'systemlog','log_id':'main'}),env=dict(os.environ,KT_SECURITY_ROOT=str(p)),capture_output=True,text=True)
 assert frame.returncode==0,frame.stderr
 (p/'log-reply.json').write_text(frame.stdout)
 h,d=call('systemlog&log_id=main');assert d['status']=='success' and d['log'] and len(json.dumps(d,separators=(',',':')).encode())<49000
 h,d=call('log_sizes');assert d['status']=='success'
 print('PASS: real PHP-CGI with broker transport stub: HTTPS/origin enforcement, guest write/private-audit denial, secure session cookies, password login/rotation, CSRF for ban/confirmation/logout, bounded broker payload and no credentials forwarded.')
