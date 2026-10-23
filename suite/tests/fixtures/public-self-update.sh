# Original interactive updater from mattheweli/KeenTool, GPL-3.0.
# Baseline: 8d640c8b06968b0f24ce41feb1bc5b0a89c3f541 (1.3.4).
action_self_update() {
    header; echo -e "${BOLD}Checking Keentool status...${RESET}"
    IFS='|' read -r N P R F <<EOF
$T_SELF
EOF
    TMP_FILE="/tmp/keentool.tmp"
    echo -n " -> Contacting GitHub ($R)... "; curl -s -L "$BASE_URL/$R/main/$F" -o "$TMP_FILE"
    
    if [ ! -s "$TMP_FILE" ]; then 
        echo -e "${RED}Failed.${RESET}"; rm -f "$TMP_FILE"; pause; return
    fi
    
    sed -i 's/\r$//' "$TMP_FILE"
    L_VER=$(get_version "$P"); R_VER=$(get_version "$TMP_FILE"); ver_compare "$R_VER" "$L_VER"; RES=$?
    
    echo -e " ${GREEN}OK${RESET}"; echo ""
    if [ $RES -eq 1 ]; then
        echo -e "${MAGENTA}Update: v$L_VER -> v$R_VER${RESET}"
        echo -n " -> Apply & Restart? (y/n): "; read -r ans
        if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then 
            mv "$TMP_FILE" "$P"; apply_perms "$P"
            # Remove flag if exists
            rm -f "/tmp/keentool_new_ver"
            send_analytics "update"
            echo -e "${GREEN}Updated.${RESET}"; sleep 1; exec "$P"
        else rm -f "$TMP_FILE"; pause; fi
    elif [ $RES -eq 2 ]; then
        echo -e "${YELLOW}Local is Newer (Dev).${RESET}"; rm -f "$TMP_FILE"; pause
    else
        if [ "$(get_md5 "$P")" != "$(get_md5 "$TMP_FILE")" ]; then
            echo -e "${CYAN}MD5 Differs.${RESET}"
            echo -n " -> Force Reinstall? (y/n): "; read -r ans
            if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then 
                mv "$TMP_FILE" "$P"; apply_perms "$P"
                echo "Reinstalling..."; sleep 1; exec "$P"
            else rm -f "$TMP_FILE"; pause; fi
        else echo -e "${GREEN}Up to date.${RESET}"; rm -f "$TMP_FILE"; pause; fi
    fi
}
