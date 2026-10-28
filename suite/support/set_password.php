<?php
// FIREWALL ADMIN PASSWORD SETTER v1.0.1 — local CLI only, never place in web root.
// Changelog: preserve existing credentials during migration; serialize password writes; retain hidden stdin-only input.
if (PHP_SAPI !== 'cli') { http_response_code(403); exit(1); }
if (!function_exists('session_start')) { fwrite(STDERR, "Install php8-mod-session\n"); exit(1); }
$password = stream_get_contents(STDIN); $password = rtrim($password, "\r\n");
if (strpos($password, "\0") !== false) { fwrite(STDERR, "Password cannot contain a null byte\n"); exit(1); }
if (strlen($password) < 12 || strlen($password) > 72) { fwrite(STDERR, "Password must contain 12–72 bytes\n"); exit(1); }
$onlyMissing = ($argv[1] ?? '') === '--if-missing';
if (count($argv) > ($onlyMissing ? 2 : 1)) exit(2);
$root = rtrim(getenv('KT_INSTALL_ROOT') ?: '', '/');
$dir = $root . '/opt/etc/keentool/admin';
umask(0077);
if (!is_dir($dir) && !mkdir($dir,0700,true)) exit(1);
$lock = fopen($dir.'/password.lock', 'c');
if (!$lock || !flock($lock, LOCK_EX) || !chmod($dir.'/password.lock',0600)) exit(1);
if ($onlyMissing && (file_exists($dir.'/credentials.json') || is_link($dir.'/credentials.json'))) {
    echo "Existing admin credentials preserved; no password was replaced.\n"; exit(0);
}
if (!is_dir($dir.'/sessions') && !mkdir($dir.'/sessions',0700)) exit(1);
$hash = password_hash($password, PASSWORD_BCRYPT, ['cost'=>12]);
if (!is_string($hash) || $hash === '') exit(1);
$data = json_encode(['hash'=>$hash,'revision'=>bin2hex(random_bytes(32))]);
$tmp = tempnam($dir,'credentials_');
if (!$tmp || file_put_contents($tmp,$data) !== strlen($data) || !chmod($tmp,0600) || !rename($tmp,$dir.'/credentials.json')) exit(1);
if (is_file($root.'/opt/etc/keentool/security/web-hardened')) {
    if (!chgrp($dir.'/credentials.json','ktweb') || !chmod($dir.'/credentials.json',0640)) { fwrite(STDERR,"Cannot grant web group credential read access\n");exit(1); }
}
echo "Admin password configured; previous sessions revoked.\n";
