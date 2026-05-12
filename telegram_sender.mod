#!/bin/sh
# ==============================================================================
# KEENTOOL TELEGRAM MODULE v1.0.0
# Description: Shared utility to send Telegram notifications via curl.
# Usage: telegram_sender.mod "Subject" "Message Body"
# ==============================================================================

SUBJECT="$1"
BODY="$2"

CONF="/opt/etc/keentool/telegram/telegram.conf"

if [ -f "$CONF" ]; then
    sed -i 's/\r$//' "$CONF"
    . "$CONF"
    
    if [ -z "$TG_BOT_TOKEN" ] || [ -z "$TG_CHAT_ID" ]; then
        logger -t "TelegramMod" "Error: Missing Token or Chat ID."
        exit 1
    fi

    # Telegram formatting (Subject in bold)
    # Replace standard line breaks with %0A for URL encoding
    FORMATTED_BODY=$(echo "$BODY" | sed ':a;N;$!ba;s/\n/%0A/g')
    TEXT="*${SUBJECT}*%0A${FORMATTED_BODY}"

    curl -s -X POST "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
        -d chat_id="${TG_CHAT_ID}" \
        -d text="${TEXT}" \
        -d parse_mode="Markdown" > /dev/null
        
    RES=$?
    if [ $RES -eq 0 ]; then
        exit 0
    else
        logger -t "TelegramMod" "Curl Error: $RES"
        exit 1
    fi
else
    exit 0
fi
