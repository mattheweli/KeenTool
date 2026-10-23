/* Security page v1.0.0. Same-origin administrator session; writes remain broker-gated. */
let adminCsrf='',adminAuthenticated=false,modalRequest=0,currentModalDownloadName='ip_diagnostics.txt';
function showAdminState(active){
 adminAuthenticated=!!active;
 document.getElementById('admin_state').textContent=active?'Administrator':'Read-only';
 document.getElementById('admin_login_button').hidden=!!active;document.getElementById('admin_logout_button').hidden=!active;
 document.querySelectorAll('[data-admin-only]').forEach(el=>el.hidden=!active);
 if(!active)document.getElementById('security_audit')?.replaceChildren();
 if(window.onAdminStateChange)window.onAdminStateChange(!!active);
}
async function authRequest(action,payload){
 const options={credentials:'same-origin',cache:'no-store',headers:{}};
 if(payload!==undefined){options.method='POST';options.headers={'Content-Type':'application/json','X-KT-CSRF':adminCsrf};options.body=JSON.stringify({action,...payload});}
 const response=await fetch('/firewall/firewall_api.php'+(payload===undefined?'?action='+encodeURIComponent(action):''),options),data=await response.json();
 if(response.status===401)showAdminState(false);
 if(!response.ok||data.status!=='success')throw Error(data.message||'Request failed');return data;
}
async function refreshAdminAuth(){const data=await authRequest('auth_status');adminCsrf=data.csrf;showAdminState(data.authenticated);}
async function openAdminLogin(){try{if(location.protocol!=='https:')throw Error('Open the dashboard over HTTPS');await refreshAdminAuth();if(adminAuthenticated)return;document.getElementById('admin_login_error').textContent='';document.getElementById('admin_password').value='';document.getElementById('admin_dialog').showModal();document.getElementById('admin_password').focus();}catch(e){alert(e.message);}}
async function adminLogout(){try{await refreshAdminAuth();await authRequest('logout',{});adminCsrf='';showAdminState(false);}catch(e){alert(e.message);}}
document.getElementById('admin_login_form').addEventListener('submit',async event=>{
 event.preventDefault();const button=event.submitter;if(button)button.disabled=true;
 try{const data=await authRequest('login',{password:document.getElementById('admin_password').value});adminCsrf=data.csrf;showAdminState(data.authenticated);document.getElementById('admin_password').value='';document.getElementById('admin_dialog').close();if(window.loadSecurityOverview)await window.loadSecurityOverview();}
 catch(e){document.getElementById('admin_login_error').textContent=e.message;}finally{if(button)button.disabled=false;}
});
async function fwFetch(url){const parsed=new URL(url,location.href);if(parsed.origin!==location.origin||parsed.pathname!=='/firewall/firewall_api.php')throw Error('Invalid diagnostic endpoint');const response=await fetch(parsed,{credentials:'same-origin',cache:'no-store'});if(!response.ok){const data=await response.json();throw Error(data.message||'Diagnostic request failed');}return response;}
async function unbanIP(ip){try{await refreshAdminAuth();if(!adminAuthenticated){await openAdminLogin();return;}if(!confirm('Remove the manual/dynamic ban for '+ip+'?'))return;const result=await authRequest('unban',{ip});alert(result.remaining?.length?'Removed manual/dynamic entry; still listed in: '+result.remaining.join(', '):'Ban removed');await window.loadSecurityOverview();}catch(e){alert(e.message);}}
function closeModal(){modalRequest++;const modal=document.getElementById('ipModal');if(modal)modal.style.display='none';}
async function copyIPList(){try{await navigator.clipboard.writeText(document.getElementById('modalBody').innerText);}catch(e){alert('Clipboard unavailable; select and copy the diagnostic text.');}}
function downloadIPList(){const url=URL.createObjectURL(new Blob([document.getElementById('modalBody').innerText],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=currentModalDownloadName;document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);}
document.addEventListener('keydown',event=>{if(event.key==='Escape')closeModal();});
document.getElementById('ipModal')?.addEventListener('click',event=>{if(event.target.id==='ipModal')closeModal();});
refreshAdminAuth().catch(e=>{document.getElementById('admin_state').textContent='Admin status unavailable';console.warn(e.message);});
