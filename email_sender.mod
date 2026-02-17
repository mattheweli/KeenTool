#!/bin/sh
# ==============================================================================
# KEENTOOL EMAIL MODULE v1.0.1
# Description: Shared utility to send email notifications via curl.
# Usage: email_sender.mod "Subject" "Message Body"
# ==============================================================================

SUBJECT="$1"
BODY="$2"

# Configuration Paths (Shared with Keentool)
CONF="/opt/etc/keentool/mail/email.conf"
PASS_FILE="/opt/etc/keentool/mail/emailpw.enc"
KEY="keentool_internal_secret"

# 1. Check if configuration exists
if [ -f "$CONF" ] && [ -f "$PASS_FILE" ]; then
    . "$CONF"
    
    # 2. Decrypt Password
    PASS=$(/opt/bin/openssl aes-256-cbc -pbkdf2 -d -in "$PASS_FILE" -pass pass:$KEY 2>/dev/null)
    
    if [ -z "$PASS" ]; then
        logger -t "EmailMod" "Error: Password decryption failed."
        exit 1
    fi
    
    # 3. Prepare Email Content
    MAIL_FILE="/tmp/keentool_mail_out.txt"
    echo -e "Subject: [Keenetic] $SUBJECT\r\nFrom: \"KeenTool\" <$FROM_ADDRESS>\r\nTo: <$TO_ADDRESS>\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\n$BODY" > "$MAIL_FILE"
    
    # 4. Send via cURL
    curl --url "$PROTOCOL://$SMTP_SERVER:$SMTP_PORT" \
         --mail-from "$FROM_ADDRESS" \
         --mail-rcpt "$TO_ADDRESS" \
         --upload-file "$MAIL_FILE" \
         --ssl-reqd \
         --user "$SMTP_USER:$PASS" \
         --silent --show-error
         
    RES=$?
    rm -f "$MAIL_FILE"
    
    if [ $RES -eq 0 ]; then
        exit 0
    else
        logger -t "EmailMod" "Curl Error: $RES"
        exit 1
    fi
else
    exit 0
fi
