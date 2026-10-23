#!/opt/bin/bash
# KEENTOOL EMAIL MODULE v2.0.0
# Release: 2026-10-22 | Stable. See CHANGELOG.md for release details.

# ==============================================================================
# KEENTOOL EMAIL MODULE v1.0.1
# Description: Shared utility to send email notifications via curl.
# Usage: email_sender.mod "Subject" "Message Body" ["HTML Alternative"]
# ==============================================================================

SUBJECT="$1"
BODY="$2"
HTML_BODY="${3:-}"

# Configuration Paths (Shared with Keentool)
CONF="/opt/etc/keentool/mail/email.conf"
PASS_FILE="/opt/etc/keentool/mail/emailpw.enc"
KEY=$(cat /opt/etc/keentool/mail/encryption.key 2>/dev/null || printf 'keentool_internal_secret')

# 1. Check if configuration exists
if [ -f "$CONF" ] && [ -f "$PASS_FILE" ]; then
    . "$CONF"
    
    # 2. Decrypt Password
    export KT_MAIL_KEY="$KEY"
    PASS=$(/opt/bin/openssl aes-256-cbc -pbkdf2 -d -in "$PASS_FILE" -pass env:KT_MAIL_KEY 2>/dev/null)
    
    if [ -z "$PASS" ]; then
        logger -t "EmailMod" "Error: Password decryption failed."
        exit 1
    fi
    
    # 3. Prepare Email Content
    umask 077
    MAIL_FILE=$(mktemp /tmp/keentool_mail.XXXXXX) || exit 1
    trap 'rm -f "$MAIL_FILE"' EXIT
    # Existing callers may use escaped newlines; decode them once before rendering.
    [ -n "$HTML_BODY" ] || BODY=$(printf '%b' "$BODY")
    HTML_ENCODING=8bit
    LAYOUT="/opt/lib/keentool-mail/mail_layout.php"
    if [ -f "$LAYOUT" ]; then
        for PHP_CLI in /opt/bin/php-cli /opt/bin/php8 /opt/bin/php; do
            [ -x "$PHP_CLI" ] || continue
            "$PHP_CLI" -n -r 'exit(PHP_SAPI === "cli" ? 0 : 1);' >/dev/null 2>&1 || continue
            if RENDERED=$(printf '%s\0%s\0%s' "$SUBJECT" "$BODY" "$HTML_BODY" | "$PHP_CLI" -n "$LAYOUT" --quoted-printable) && [ -n "$RENDERED" ]; then
                HTML_BODY=$RENDERED;HTML_ENCODING=quoted-printable
            fi
            break
        done
    fi
    {
        printf 'Subject: [Keenetic] %s\r\nFrom: "KeenTool" <%s>\r\nTo: <%s>\r\nMIME-Version: 1.0\r\n' "$SUBJECT" "$FROM_ADDRESS" "$TO_ADDRESS"
        if [ -n "$HTML_BODY" ]; then
            BOUNDARY="keentool_${MAIL_FILE##*/}_$$"
            printf 'Content-Type: multipart/alternative; boundary="%s"\r\n\r\n' "$BOUNDARY"
            printf -- '--%s\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit\r\n\r\n%s\r\n' "$BOUNDARY" "$BODY"
            printf -- '--%s\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Transfer-Encoding: %s\r\n\r\n%s\r\n' "$BOUNDARY" "$HTML_ENCODING" "$HTML_BODY"
            printf -- '--%s--\r\n' "$BOUNDARY"
        else
            printf 'Content-Type: text/plain; charset=UTF-8\r\n\r\n%s\n' "$BODY"
        fi
    } > "$MAIL_FILE"
    
    # 4. Send via cURL
    curl --connect-timeout 10 --max-time 45 --url "$PROTOCOL://$SMTP_SERVER:$SMTP_PORT" \
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

