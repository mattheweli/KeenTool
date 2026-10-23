# Runtime detection happens before sourcing any coordinated-suite libraries.
kt_runtime_ready() {
 [ -r "${KT_COMMON:-/opt/lib/keentool/common.sh}" ] &&
 [ -r "${KT_UPDATE_INSTALLED:-/opt/etc/keentool/installed-release.json}" ] &&
 [ -r "${KT_UPDATE_COMMAND:-/opt/bin/keentool_update}" ] &&
 [ -r "${KT_UPDATE_HELPER:-/opt/lib/keentool/release_update.php}" ]
}
kt_embedded_bootstrap() {
@BOOTSTRAP@
}
if ! kt_runtime_ready;then
 kt_migration_menu=false
 kt_migration_args=()
 case "${1:-}" in
  '') kt_migration_menu=true;;
  --check-updates) kt_migration_args=(--check);;
  --update|-update) shift;kt_migration_args=("$@");;
  --help|-h)
   echo 'KeenTool requires the coordinated suite runtime.'
   echo 'Run keentool to migrate interactively, keentool --check-updates to check, or keentool --update --yes to explicitly install.'
   exit 0;;
  *) echo 'Complete suite migration required. Run keentool interactively before using this command.' >&2;exit 2;;
 esac
 echo 'Legacy or incomplete KeenTool installation detected. The complete suite must be installed before opening the new menu.'
 kt_bootstrap_pid=''
 trap '[ -z "$kt_bootstrap_pid" ] || { kill -TERM "$kt_bootstrap_pid" 2>/dev/null || :;wait "$kt_bootstrap_pid" || :; };exit 143' INT TERM
 # Do not put this call in an if/|| condition: its subshell uses errexit.
 kt_embedded_bootstrap "${kt_migration_args[@]}" <&0 & kt_bootstrap_pid=$!
 wait "$kt_bootstrap_pid";kt_migration_result=$?
 kt_bootstrap_pid='';trap - INT TERM
 [ "$kt_migration_result" = 0 ] || exit "$kt_migration_result"
 if kt_runtime_ready;then
  if [ "$kt_migration_menu" = true ];then
   exec "${KT_UPDATE_BASH:-/opt/bin/bash}" "${KT_MANAGER_PATH:-/opt/bin/keentool}"
  fi
 else
  echo 'The migration has not been installed. Run keentool again to retry; existing configuration and databases are retained.'
 fi
 exit 0
fi
