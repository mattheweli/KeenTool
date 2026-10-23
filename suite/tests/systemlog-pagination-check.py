from pathlib import Path
import tempfile,subprocess,os,json,base64
root=Path(__file__).resolve().parents[1];php='/tmp/keentool-security-runtime/root/usr/bin/php8.3'
with tempfile.TemporaryDirectory() as td:
 p=Path(td);logs=p/'opt/var/log';logs.mkdir(parents=True);file=logs/'messages'
 env=dict(os.environ,KT_SECURITY_ROOT=str(p))
 def call(cursor=None,ok=True,log_id='main'):
  data={'action':'systemlog','log_id':log_id}
  if cursor is not None:data['cursor']=cursor
  r=subprocess.run([php,'-n',str(root/'support/security_engine.php'),'request'],input=json.dumps(data),env=env,capture_output=True,text=True)
  if not ok:assert r.returncode!=0;return
  assert r.returncode==0,r.stderr
  assert len(r.stdout.encode())<49000,len(r.stdout.encode())
  # Simulate the observed 64 KiB response cut: each new complete frame survives it.
  assert json.loads(r.stdout[:65528])==json.loads(r.stdout)
  return json.loads(r.stdout)
 def all_pages(original,append=False):
  result=call();suffix=result['log'];pages=1
  if append:
   with file.open('ab') as f:f.write(b'new append outside original snapshot\n')
  while result['has_more']:
   previous=result['next_cursor'];result=call(previous);assert not result.get('reset_required'),result
   assert result['next_cursor']!=previous
   assert result['loaded_bytes']<=32768 and len(result['log'].splitlines())<=1000
   suffix=result['log']+suffix;pages+=1;assert pages<100
  assert suffix.encode()==original,(len(suffix.encode()),len(original))
  return pages
 original=''.join(f'{i:05d} entry à 日本語 🙂 payload\n' for i in range(18000)).encode();file.write_bytes(original);file.chmod(0o600)
 assert all_pages(original,append=True)>=18 and file.stat().st_mode & 0o777==0o600
 meta=subprocess.run([php,'-n',str(root/'support/security_engine.php'),'request'],input=json.dumps({'action':'log_sizes'}),env=env,capture_output=True,text=True)
 sizes=json.loads(meta.stdout);assert sizes['sizes']['main']==file.stat().st_size and sizes['sizes']['vpn'] is None and len(meta.stdout)<2000

 # Very long multibyte lines and trailing/blank lines must also be reconstructed exactly.
 for text in ['🙂'*80000+'\n', 'é'*80000, ('\\\"/\x00\x01\t'*6000)+'\n', '\n'*2100, '', 'one line\n', 'one line']:
  original=text.encode();file.write_bytes(original);all_pages(original)
 original=('old content\n'*3000).encode();file.write_bytes(original);first=call();cursor=first['next_cursor'];assert cursor
 file.rename(logs/'messages.1');file.write_bytes(b'new file\n');assert call(cursor)['reset_required']
 file.write_bytes(original);cursor=call()['next_cursor'];file.write_bytes(b'truncated\n');assert call(cursor)['reset_required']
 file.write_bytes(original);cursor=call()['next_cursor'];file.write_bytes(b'X'*len(original));assert call(cursor)['reset_required']
 for cursor in ['../etc/passwd','x'*1025,base64.urlsafe_b64encode(b'{}').decode().rstrip('=')]:call(cursor,ok=False)
 call(log_id='../../etc/passwd',ok=False)
 file.write_bytes(original);cursor=call()['next_cursor'];call(cursor,ok=False,log_id='vpn')
 # The existing broker can pace continuation requests separately from new full-view loads.
 code='define("KT_ENGINE_TEST",true);require '+json.dumps(str(root/'support/security_engine.php'))+';$first=kdispatch(["action"=>"systemlog","log_id"=>"main"]);kdispatch(["action"=>"systemlog","log_id"=>"main","cursor"=>$first["next_cursor"]]);try{kdispatch(["action"=>"systemlog","log_id"=>"main","cursor"=>$first["next_cursor"]]);exit(2);}catch(Throwable $e){if($e->getCode()!==429)throw $e;}usleep(70000);$next=kdispatch(["action"=>"systemlog","log_id"=>"main","cursor"=>$first["next_cursor"]]);if($next["status"]!=="success")exit(3);'
 r=subprocess.run([php,'-n','-r',code],env=env,capture_output=True,text=True);assert r.returncode==0,r.stderr

print('PASS: real PHP log pagination reconstructs complete UTF-8/blank/long-line logs, bounded pages without duplicates/gaps, stable append snapshot, rotation/copytruncate reset, cursor/path validation and unchanged private mode.')
