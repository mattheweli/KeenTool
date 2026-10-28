#!/opt/bin/bash
# FIREWALL STATE v1.0.0 — 2026-10-22
# Existing sets: restore add records only, preserving current capacity and rule references.
# Checkpoint dynamic sets; restore once per boot even if another hook created empty sets.
# Restore saved timeout values unchanged, matching upstream. Never reconstruct bans from history DB.
FW_STATE_DIR=${KT_FW_STATE_DIR:-/opt/etc/keentool/firewall-state}
FW_BOOT_DIR=${KT_FW_BOOT_DIR:-/tmp}
FW_SAVE_ROOT=${KT_FW_SAVE_ROOT:-/opt/etc}
fw_checkpoint_state() {
 local set tmp bad=0 size
 mkdir -p "$FW_STATE_DIR" || return 1;chmod 700 "$FW_STATE_DIR"
 for set in AutoBan AutoBan6 VPNBlock;do
  command ipset list -n "$set" >/dev/null 2>&1 || continue
  size=$(command ipset list "$set" 2>/dev/null | awk '/^Number of entries:/ {print $4}')
  if [ "${size:-0}" = 0 ] && [ "$(cat "$FW_BOOT_DIR/fw-restored-$set" 2>/dev/null)" != complete-v2 ];then
   echo "Skip empty $set checkpoint before boot restore" >&2;continue
  fi
  tmp=$(mktemp "$FW_STATE_DIR/$set.XXXXXX") || return 1
  if command ipset save "$set" > "$tmp" && [ -s "$tmp" ];then chmod 600 "$tmp";mv "$tmp" "$FW_STATE_DIR/$set.save"
  else rm -f "$tmp";bad=1;fi
 done
 return "$bad"
}
fw_restore_state() {
 local set saved size now tmp bad=0 raw_ts saved_ts exists set_bad
 mkdir -p "$FW_BOOT_DIR" || return 1
 now=$(date +%s)
 for set in FirewallBlock FirewallBlock6 GeoBlock GeoBlock6 AutoBan AutoBan6 Blacklist Blacklist6 VPNBlock;do
  [ "$(cat "$FW_BOOT_DIR/fw-restored-$set" 2>/dev/null)" != complete-v2 ] || continue
  set_bad=0
  [[ "$set" != *6 ]] || [ "${ENABLE_IPV6:-true}" = true ] || continue
  size=$(command ipset list "$set" 2>/dev/null | awk '/^Number of entries:/ {print $4}')
  case "$set" in
   FirewallBlock) saved="$FW_SAVE_ROOT/firewall_blocklist.save";;
   FirewallBlock6) saved="$FW_SAVE_ROOT/firewall_blocklist6.save";;
   GeoBlock) saved="$FW_SAVE_ROOT/firewall_geoblock.save";;
   GeoBlock6) saved="$FW_SAVE_ROOT/firewall_geoblock6.save";;
   Blacklist) saved="$FW_SAVE_ROOT/Blacklist.backup";;
   Blacklist6) saved="$FW_SAVE_ROOT/Blacklist6.backup";;
   *) saved="$FW_STATE_DIR/$set.save";;
  esac
  if [[ "$set" = AutoBan* ]] && [ -s "$FW_SAVE_ROOT/firewall_autoban.save" ] && grep -qE "^(create|add) $set " "$FW_SAVE_ROOT/firewall_autoban.save";then
   raw_ts=$(kt_stat %Y "$FW_SAVE_ROOT/firewall_autoban.save" 2>/dev/null || echo 0)
   saved_ts=$(kt_stat %Y "$saved" 2>/dev/null || echo 0)
   if [ "$raw_ts" -ge "$saved_ts" ];then saved="$FW_SAVE_ROOT/firewall_autoban.save";fi
  fi
  if [ -s "$saved" ];then
   if ! grep -qE "^(create|add) $set " "$saved";then echo "Invalid saved state for $set (retained): $saved" >&2;bad=1;continue;fi
   tmp=$(mktemp "$FW_BOOT_DIR/fw-restore.XXXXXX") || return 1
   exists=false
   command ipset list -n "$set" >/dev/null 2>&1 && exists=true
   awk -v set="$set" -v exists="$exists" '$2==set && ($1=="add" || ($1=="create" && exists!="true")) {print}' "$saved" > "$tmp"
   if [ -s "$tmp" ] && ! command ipset restore -exist < "$tmp";then echo "Restore failed: $set (saved state retained)" >&2;bad=1;rm -f "$tmp";continue;fi
   rm -f "$tmp"
  fi
  # Preserve legacy VPN list restoration, even when an earlier hook created an empty set.
  if [ "$set" = VPNBlock ] && [ -s "$FW_SAVE_ROOT/vpn_banned_ips.txt" ];then
   command ipset create VPNBlock hash:ip counters -exist || { bad=1;continue; }
   while read -r ip;do [ -z "$ip" ] || command ipset add VPNBlock "$ip" -exist || { bad=1;set_bad=1; };done < "$FW_SAVE_ROOT/vpn_banned_ips.txt"
  fi
  # Scanner-owned VPN bans carry absolute expiry in their persistent state.
  if [ "$set" = VPNBlock ] && [ -s "$FW_SAVE_ROOT/keentool/vpn/bans" ];then
   command ipset create VPNBlock hash:ip counters -exist || { bad=1;continue; }
   while read -r expiry ip;do
    [[ "$expiry" =~ ^[0-9]+$ ]] || continue
    if [ "$expiry" -gt "$now" ];then command ipset add VPNBlock "$ip" -exist || { bad=1;set_bad=1; }
    else command ipset del VPNBlock "$ip" 2>/dev/null || :;fi
   done < "$FW_SAVE_ROOT/keentool/vpn/bans"
  fi
  [ "$set_bad" = 0 ] && printf 'complete-v2\n' > "$FW_BOOT_DIR/fw-restored-$set"
 done
 return "$bad"
}

fw_archive_capture() {
 local file=/opt/var/log/keentool-firewall/fw_syn_ring.pcap tmp size
 [ -s "$file" ] || return 0
 size=$(wc -c < "$file");[ "$size" -gt 24 ] || return 0
 tmp=$(mktemp "${file}.archive.XXXXXX") || return 1
 if cp "$file" "$tmp";then chmod 600 "$tmp";mv "$tmp" "${file}.processed.$(date +%s).$$"
 else rm -f "$tmp";return 1;fi
}
