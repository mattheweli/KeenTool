#!/opt/bin/bash
# KEENTOOL TELEGRAM MODULE v2.0.0
# Release: 2026-10-22 | Stable. See CHANGELOG.md for release details.

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

    TEXT=$(printf '%s\n\n%s' "$SUBJECT" "$BODY")
    RESPONSE=$(curl -fsS --connect-timeout 10 --max-time 20 -X POST "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
        --data-urlencode "chat_id=$TG_CHAT_ID" --data-urlencode "text=$TEXT") || exit 1
    printf '%s' "$RESPONSE" | grep -q '"ok":true' || exit 1
else
    exit 0
fi
