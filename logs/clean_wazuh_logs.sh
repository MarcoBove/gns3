#!/bin/bash

# Array dei file da svuotare
LOG_FILES=(
    "/var/ossec/logs/archives/archives.log"
    "/var/ossec/logs/archives/archives.json"
    "/var/ossec/logs/alerts/alerts.log"
    "/var/ossec/logs/alerts/alerts.json"
)

echo "--- Inizio pulizia log Wazuh ---"

# Ciclo per svuotare ogni file nell'elenco
for FILE in "${LOG_FILES[@]}"; do
    if [ -f "$FILE" ]; then
        truncate -s 0 "$FILE"
        echo "[OK] Svuotato: $FILE"
    else
        echo "[SKIP] File non trovato: $FILE"
    fi
done

echo "--- Pulizia completata ---"
