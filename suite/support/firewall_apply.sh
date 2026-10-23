#!/opt/bin/bash
# FIREWALL APPLY v1.0.0 — 2026-10-22, stable
# Build/test owned-chain batches; commit per family with --noflush, recover owned rules on failure.
# IPv4 and IPv6 are separate kernel commits; recovery is explicitly checked.
FW_CHAINS='BLOCKLIST_IN BLOCKLIST_FWD SCAN_TRAP BLACKLIST FW_CHK_CONN FW_CHK_BRUTE'
FW_RUNTIME=${KT_FW_RUNTIME:-/opt/etc/keentool/firewall-runtime}
fw_owned() { local c;for c in $FW_CHAINS;do [ "$1" != "$c" ] && [ "$1" != "${c}6" ] || return 0;done;return 1; }
fw_stage_begin() {
 FW_STAGE_ERROR=0
 : > "$KT_WORKDIR/rules4";: > "$KT_WORKDIR/rules6"
}
fw_stage() {
 local family=$1;shift
 [ "${1:-}" != -w ] || shift
 case "${1:-}" in
  -N|-F) fw_owned "${2:-}" || { FW_STAGE_ERROR=1;return 1; };return 0;;
  -C) return 1;;
  -D|-I|-X) return 0;; # Links and teardown are generated from the live snapshot.
  -A) fw_owned "${2:-}" || { FW_STAGE_ERROR=1;return 1; };;
  *) FW_STAGE_ERROR=1;return 1;;
 esac
 local arg
 for arg in "$@";do [[ "$arg" != *[[:space:]]* ]] || { FW_STAGE_ERROR=1;return 1; };done
 printf '%s ' "$@" >> "$KT_WORKDIR/rules$family";printf '\n' >> "$KT_WORKDIR/rules$family"
}
fw_signature() {
 awk -v names="$FW_CHAINS" 'BEGIN{n=split(names,a," ");for(i=1;i<=n;i++){o[a[i]]=1;o[a[i]"6"]=1}} /^:/ {c=substr($1,2);if(o[c])print c} $1=="-A" {pos[$2]++;if(o[$2])print;else if(NF==4&&$3=="-j"&&o[$4])print $0,"position",pos[$2]}' "$1"
}
fw_saved_signature() {
 awk -v names="$FW_CHAINS" 'BEGIN{n=split(names,a," ");for(i=1;i<=n;i++){o[a[i]]=1;o[a[i]"6"]=1}} /^:/ {c=substr($1,2);if(o[c])chains[c]=1} $1=="-A"{pos[$2]++;if(o[$2])rules[$2]=rules[$2] $0 "\n";else if(NF==4&&$3=="-j"&&o[$4])links=links $0 " position " pos[$2] "\n"} END{for(i=1;i<=n;i++){c=a[i];if(chains[c])printf "%s\n%s",c,rules[c];c=a[i]"6";if(chains[c])printf "%s\n%s",c,rules[c]}printf "%s",links}' "$1"
}
fw_snapshot() { command "$1-save" -t filter > "$2" && grep -q '^COMMIT$' "$2"; }
fw_links() {
 # Exact unconditional links only. Refuse unknown external references before mutation.
 awk -v suffix="$2" '$1=="-A" && ($2=="INPUT" || $2=="FORWARD") && NF==4 && $3=="-j" && ($4=="BLOCKLIST_IN"suffix || $4=="BLOCKLIST_FWD"suffix) {print}' "$1"
}
fw_batch() {
 local snap=$1 family=$2 active=$3 mode=$4 out=$5 suffix='' c line parent pos
 [ "$family" = 4 ] || suffix=6
 {
  echo '*filter'
  for c in $FW_CHAINS;do
   if [ "$active" = true ] || grep -q "^:$c$suffix " "$snap";then printf ':%s - [0:0]\n' "$c$suffix";fi
  done
  fw_links "$snap" "$suffix" | sed 's/^-A /-D /'
  if [ "$mode" = previous ];then
   awk -v names="$FW_CHAINS" -v suffix="$suffix" 'BEGIN{n=split(names,a," ");for(i=1;i<=n;i++)owned[a[i]suffix]=1} $1=="-A" && owned[$2] {print}' "$snap"
   # Reinsert old links at their previous positions, retaining foreign rules.
   awk -v suffix="$suffix" '$1=="-A" {pos[$2]++;if(($2=="INPUT"||$2=="FORWARD")&&NF==4&&$3=="-j"&&($4=="BLOCKLIST_IN"suffix||$4=="BLOCKLIST_FWD"suffix))print "-I",$2,pos[$2],$3,$4}' "$snap"
  elif [ "$active" = true ];then
   cat "$KT_WORKDIR/rules$family"
   printf -- '-I INPUT 1 -j BLOCKLIST_IN%s\n-I FORWARD 1 -j BLOCKLIST_FWD%s\n' "$suffix" "$suffix"
  fi
  if [ "$active" != true ];then
   for c in $FW_CHAINS;do grep -q "^:$c$suffix " "$snap" && printf -- '-X %s\n' "$c$suffix";done
  fi
  echo COMMIT
 } > "$out"
}
fw_restore_batch() {
 local tool=$1 file=$2 test=${3:-false}
 local -a args=(--noflush)
 [ "$test" != true ] || args+=(--test)
 # Old Keenetic xtables does not accept restore -w. Detect support instead of assuming it.
 if command "$tool-restore" --help 2>&1 | grep -q -- '--wait';then args+=(-w);fi
 command "$tool-restore" "${args[@]}" < "$file"
}
fw_verify() {
 local tool=$1 rules=$2 active=$3 suffix='' line c expected actual snapshot
 [ "$tool" != ip6tables ] || suffix=6
 snapshot=$(command "$tool-save" -t filter) || return 1
 if [ "$active" != true ];then
  for c in $FW_CHAINS;do ! grep -q "^:$c$suffix " <<< "$snapshot" || return 1;done
  return 0
 fi
 for c in $FW_CHAINS;do
  grep -q "^:$c$suffix " <<< "$snapshot" || return 1
  expected=$(awk -v c="$c$suffix" '$1=="-A"&&$2==c {n++} END{print n+0}' "$rules")
  actual=$(awk -v c="$c$suffix" '$1=="-A"&&$2==c {n++} END{print n+0}' <<< "$snapshot")
  [ "$actual" = "$expected" ] || return 1
 done
 local -a rule
 while IFS= read -r line;do
  read -r -a rule <<< "$line";rule[0]=-C
  command "$tool" "${rule[@]}" >/dev/null 2>&1 || return 1
 done < "$rules"
 for line in "INPUT BLOCKLIST_IN$suffix" "FORWARD BLOCKLIST_FWD$suffix";do
  read -r parent c <<< "$line"
  [ "$(awk -v p="$parent" -v c="$c" '$1=="-A"&&$2==p&&NF==4&&$3=="-j"&&$4==c{n++}END{print n+0}' <<< "$snapshot")" = 1 ] || return 1
 done
}
fw_recover_transaction() {
 local family tool c suffix
  for family in 6 4;do
   [ "$family" != 4 ] || [ "$changed4" = true ] || continue
   [ "$family" != 6 ] || [ "$changed6" = true ] || continue
   tool=iptables;[ "$family" = 4 ] || tool=ip6tables
   # Snapshot current state so rollback removes the currently installed links.
   fw_snapshot "$tool" "$KT_WORKDIR/failed$family" || { kt_log "CRITICAL: cannot snapshot $tool for rollback";continue; }
   fw_batch "$KT_WORKDIR/before$family" "$family" true previous "$KT_WORKDIR/rollback$family.base"
   # Replace link deletions with the current links; the rest restores only our chains.
   { echo '*filter';sed -n '/^:/p' "$KT_WORKDIR/rollback$family.base";fw_links "$KT_WORKDIR/failed$family" "$( [ "$family" = 4 ] || printf 6 )" | sed 's/^-A /-D /';sed -n '/^-A /p;/^-I /p' "$KT_WORKDIR/rollback$family.base"
     for c in $FW_CHAINS;do suffix='';[ "$family" = 4 ] || suffix=6
      if ! grep -q "^:$c$suffix " "$KT_WORKDIR/before$family";then printf -- '-X %s\n' "$c$suffix";fi
     done;echo COMMIT;
   } > "$KT_WORKDIR/rollback$family"
   if ! fw_restore_batch "$tool" "$KT_WORKDIR/rollback$family";then kt_log "CRITICAL: $tool rollback failed; inspect rules immediately"
   else
    fw_snapshot "$tool" "$KT_WORKDIR/restored$family" || return 1
    fw_signature "$KT_WORKDIR/before$family" > "$KT_WORKDIR/before.sig"
    fw_signature "$KT_WORKDIR/restored$family" > "$KT_WORKDIR/after.sig"
    if cmp -s "$KT_WORKDIR/before.sig" "$KT_WORKDIR/after.sig";then kt_log "$tool owned rules restored and verified after failed apply"
    else kt_log "CRITICAL: $tool rollback verification failed; inspect rules immediately";fi
   fi
  done
 return 1
}
fw_publish_metadata() {
 local family tool file
 mkdir -p "$KT_WORKDIR/metadata-new" || return 1
 for family in 4 6;do
  cp "$KT_WORKDIR/rules$family" "$KT_WORKDIR/metadata-new/rules$family" || return 1
  tool=iptables;[ "$family" = 4 ] || tool=ip6tables
  fw_snapshot "$tool" "$KT_WORKDIR/final$family" || return 1
  fw_saved_signature "$KT_WORKDIR/final$family" > "$KT_WORKDIR/metadata-new/canonical$family" || return 1
 done
 printf '%s\n' "$FW_CONFIG_HASH" > "$KT_WORKDIR/metadata-new/config.sha" || return 1
 printf '%s\n' "$enabled" > "$KT_WORKDIR/metadata-new/enabled" || return 1
 printf '%s\n' "$ipv6" > "$KT_WORKDIR/metadata-new/ipv6" || return 1
 rm -f "$FW_RUNTIME/ready" || return 1
 for file in rules4 rules6 canonical4 canonical6 config.sha enabled ipv6;do
  cp "$KT_WORKDIR/metadata-new/$file" "$FW_RUNTIME/$file.tmp" && mv "$FW_RUNTIME/$file.tmp" "$FW_RUNTIME/$file" || return 1
 done
 touch "$FW_RUNTIME/ready"
}
fw_apply() {
 local enabled=$1 ipv6=$2 tool family active snapshot file failed=0 changed4=false changed6=false
 [ "$FW_STAGE_ERROR" = 0 ] || { kt_log 'Invalid staged rule arguments';return 1; }
 # Preflight both families before committing either one.
 for family in 4 6;do
  tool=iptables;[ "$family" = 4 ] || tool=ip6tables
  active=$enabled;[ "$family" = 4 ] || [ "$ipv6" = true ] || active=false
  snapshot="$KT_WORKDIR/before$family"
  fw_snapshot "$tool" "$snapshot" || { kt_log "Cannot snapshot $tool filter table";return 1; }
  # Reject references to owned chains that this hook did not create.
  if awk -v names="$FW_CHAINS" -v suffix="$( [ "$family" = 4 ] || printf 6 )" 'BEGIN{n=split(names,a," ");for(i=1;i<=n;i++)o[a[i]suffix]=1} $1=="-A"&&!o[$2]{for(i=3;i<NF;i++)if(($i=="-j"||$i=="-g")&&o[$(i+1)]&&!(NF==4&&$3=="-j"&&($2=="INPUT"||$2=="FORWARD")&&($(i+1)=="BLOCKLIST_IN"suffix||$(i+1)=="BLOCKLIST_FWD"suffix)))bad=1} END{exit bad?0:1}' "$snapshot";then
   kt_log "Unexpected external reference to owned $tool chain; previous rules retained";return 1
  fi
  fw_batch "$snapshot" "$family" "$active" current "$KT_WORKDIR/apply$family"
  fw_restore_batch "$tool" "$KT_WORKDIR/apply$family" true || { kt_log "$tool candidate validation failed; previous rules retained";return 1; }
 done
 mkdir -p "$FW_RUNTIME" && chmod 700 "$FW_RUNTIME" || { kt_log 'Cannot prepare private apply state; previous rules retained';return 1; }
 local probe
 probe=$(mktemp "$FW_RUNTIME/.probe.XXXXXX") || return 1;rm -f "$probe"
 mkdir -p "$KT_WORKDIR/metadata-before" || return 1
 for file in rules4 rules6 canonical4 canonical6 config.sha enabled ipv6 ready;do
  [ ! -f "$FW_RUNTIME/$file" ] || cp "$FW_RUNTIME/$file" "$KT_WORKDIR/metadata-before/$file" || return 1
 done
 [ "${FW_CONFIG_HASH:-}" = "$(sha256sum "${KT_FW_CONF:-/opt/etc/firewall.conf}" 2>/dev/null | awk '{print $1}')" ] || { kt_log 'Configuration changed during staging; previous rules retained';return 1; }
 for family in 4 6;do
  tool=iptables;[ "$family" = 4 ] || tool=ip6tables
  active=$enabled;[ "$family" = 4 ] || [ "$ipv6" = true ] || active=false
  # A router reload between preflight and commit invalidates our parent-link snapshot.
  fw_snapshot "$tool" "$KT_WORKDIR/current$family" || { failed=1;break; }
  sed '/^#/d;s/\[[0-9]*:[0-9]*\]/[0:0]/g' "$KT_WORKDIR/before$family" > "$KT_WORKDIR/before$family.norm"
  sed '/^#/d;s/\[[0-9]*:[0-9]*\]/[0:0]/g' "$KT_WORKDIR/current$family" > "$KT_WORKDIR/current$family.norm"
  cmp -s "$KT_WORKDIR/before$family.norm" "$KT_WORKDIR/current$family.norm" || { kt_log "$tool changed during preflight; retry the hook";failed=1;break; }
  if [ "$family" = 4 ];then changed4=true;else changed6=true;fi
  if ! fw_restore_batch "$tool" "$KT_WORKDIR/apply$family" || ! fw_verify "$tool" "$KT_WORKDIR/rules$family" "$active";then failed=1;break;fi
 done
 if [ "$failed" = 1 ];then fw_recover_transaction;return 1;fi
 if ! fw_publish_metadata;then
  kt_log 'Apply metadata failed; recovering previous owned rules and metadata'
  fw_recover_transaction || :
  rm -f "$FW_RUNTIME/ready"
  for file in rules4 rules6 canonical4 canonical6 config.sha enabled ipv6;do
   if [ -f "$KT_WORKDIR/metadata-before/$file" ];then cp "$KT_WORKDIR/metadata-before/$file" "$FW_RUNTIME/$file" || kt_log "CRITICAL: cannot recover $file metadata"
   else rm -f "$FW_RUNTIME/$file";fi
  done
  [ ! -f "$KT_WORKDIR/metadata-before/ready" ] || cp "$KT_WORKDIR/metadata-before/ready" "$FW_RUNTIME/ready"
  return 1
 fi
 kt_log 'Owned firewall rules applied and verified for both families'
}
