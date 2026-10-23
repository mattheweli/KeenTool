<?php
// FIREWALL ADMIN PASSWORD SETTER v1.0.0 — local CLI only, never place in web root.
// Changelog: a1: CLI-only bcrypt password storage outside web root and session revision invalidation.
if (PHP_SAPI !== 'cli') { http_response_code(403); exit(1); }
if (!function_exists('session_start')) { fwrite(STDERR, "Install php8-mod-session\n"); exit(1); }
$password = stream_get_contents(STDIN); $password = rtrim($password, "\r\n");
if (strlen($password) < 12 || strlen($password) > 72) { fwrite(STDERR, "Password must contain 12–72 bytes\n"); exit(1); }
$dir = '/opt/etc/keentool/admin';
umask(0077);
if (!is_dir($dir) && !mkdir($dir,0700,true)) exit(1);
if (!is_dir($dir.'/sessions') && !mkdir($dir.'/sessions',0700)) exit(1);
$hash = password_hash($password, PASSWORD_BCRYPT, ['cost'=>12]);
$data = json_encode(['hash'=>$hash,'revision'=>bin2hex(random_bytes(32))]);
$tmp = tempnam($dir,'credentials_');
if (!$tmp || file_put_contents($tmp,$data) !== strlen($data) || !chmod($tmp,0600) || !rename($tmp,$dir.'/credentials.json')) exit(1);
if (is_file('/opt/etc/keentool/security/web-hardened')) {
    if (!chgrp($dir.'/credentials.json','ktweb') || !chmod($dir.'/credentials.json',0640)) { fwrite(STDERR,"Cannot grant web group credential read access\n");exit(1); }
}
echo "Admin password configured; previous sessions revoked.\n";
